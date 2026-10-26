"""Offline keyed mock execution. SQLite commits preserve each planned invocation.

Single coordinator per ledger. No network implementation exists. A future live
adapter needs separate authorization and provider-specific validation.
"""
import asyncio
import json
import random
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Protocol

from .common import canonical, digest, MODEL
from .prompts import ARMS, render


def now():
    return datetime.now(timezone.utc).isoformat()


def plan(cases, seed, replicate=0):
    rng = random.Random(seed)
    cases = sorted(cases, key=lambda c: c['case_id'])
    rng.shuffle(cases)
    rows = []
    for case in cases:
        arms = list(ARMS)
        rng.shuffle(arms)
        for arm in arms:
            messages = render(case, arm)
            key = digest([case['case_id'], arm, replicate])
            rows.append(dict(invocation_id=key, case_id=case['case_id'], arm=arm,
                replicate_id=replicate, block_id=case['case_id'], dispatch_order=len(rows),
                mode='MOCK_ONLY', model_proposal=MODEL, messages=messages,
                parameters=dict(max_completion_tokens=512, temperature=0, reasoning_effort='none', tools=[]),
                prompt_sha256=digest(messages)))
    if len({r['invocation_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate planned IDs')
    return rows


class Model(Protocol):
    async def complete(self, request: dict) -> dict: ...


class Ledger:
    def __init__(self, path, rows):
        if len({r['invocation_id'] for r in rows}) != len(rows):
            raise ValueError('duplicate planned IDs')
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS invocations (
                invocation_id TEXT PRIMARY KEY, request TEXT NOT NULL, status TEXT NOT NULL,
                attempts INTEGER NOT NULL, response TEXT, error TEXT, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS history (
                event_id INTEGER PRIMARY KEY, invocation_id TEXT NOT NULL,
                status TEXT NOT NULL, detail TEXT, timestamp TEXT NOT NULL);
        ''')
        fingerprint = digest(rows)
        old = self.db.execute("SELECT value FROM metadata WHERE key='plan_hash'").fetchone()
        if old and old[0] != fingerprint:
            self.db.close()
            raise ValueError('stale or modified plan: use a separate ledger')
        with self.db:
            if not old:
                self.db.execute('INSERT INTO metadata VALUES (?,?)', ('plan_hash', fingerprint))
                self.db.executemany('INSERT INTO invocations VALUES (?,?,?,?,?,?,?)',
                    [(r['invocation_id'], canonical(r), 'pending', 0, None, None, now()) for r in rows])
            for r in self.db.execute("SELECT invocation_id FROM invocations WHERE status IN ('running','retry')").fetchall():
                self._event(r[0], 'interrupted', 'process stopped after dispatch; output unknown')
                self.db.execute("UPDATE invocations SET status='pending',error='interrupted',updated_at=? WHERE invocation_id=?", (now(),r[0]))
        self.rows = rows

    def _event(self, key, status, detail=None):
        self.db.execute('INSERT INTO history(invocation_id,status,detail,timestamp) VALUES (?,?,?,?)', (key,status,detail,now()))

    def pending(self):
        pending = {r[0] for r in self.db.execute("SELECT invocation_id FROM invocations WHERE status='pending'")}
        return [r for r in self.rows if r['invocation_id'] in pending]

    def begin(self, key):
        with self.db:
            row = self.db.execute('SELECT status,attempts FROM invocations WHERE invocation_id=?',(key,)).fetchone()
            if not row or row['status'] not in ('pending', 'retry'):
                raise ValueError('unexpected dispatch key/status')
            self.db.execute("UPDATE invocations SET status='running',attempts=attempts+1,updated_at=? WHERE invocation_id=?", (now(),key))
            self._event(key, 'dispatch')
        return row['attempts']+1

    def finish(self, key, status, response=None, error=None):
        with self.db:
            row = self.db.execute('SELECT status FROM invocations WHERE invocation_id=?',(key,)).fetchone()
            if not row or row['status'] not in ('running','pending'):
                raise ValueError('unexpected result key/status')
            self.db.execute('UPDATE invocations SET status=?,response=?,error=?,updated_at=? WHERE invocation_id=?', (status,response,error,now(),key))
            self._event(key, status, error)

    def results(self):
        index = {r['invocation_id']: dict(r) for r in self.db.execute('SELECT * FROM invocations')}
        return [dict(index[r['invocation_id']], case_id=r['case_id'], arm=r['arm'],
            replicate_id=r['replicate_id'], prompt_sha256=r['prompt_sha256'], mode='MOCK_ONLY') for r in self.rows]

    def history(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM history ORDER BY event_id')]

    def close(self):
        self.db.close()


class MockModel:
    def __init__(self, scripts=None):
        self.scripts = scripts or {}
        self.calls = defaultdict(int)

    async def complete(self, request):
        key = request['invocation_id']
        call = self.calls[key]
        self.calls[key] += 1
        actions = self.scripts.get(key, ['ok'])
        action = actions[min(call, len(actions)-1)]
        # Deliberate reverse completion order within neighboring dispatches.
        await asyncio.sleep((7-request['dispatch_order']%8)*.0001)
        if action in ('timeout', 'delay'):
            await asyncio.sleep(.5)
        if action == 'error':
            raise ConnectionError('synthetic transport error')
        return dict(invocation_id='FOREIGN' if action == 'wrong_key' else key,
            text='' if action == 'empty' else 'MOCK:'+key,
            finish_reason='length' if action == 'truncated' else 'stop', mode='MOCK_ONLY')


async def run_mock(ledger, model, *, timeout=.2, max_attempts=3, concurrency=8, stop_after=None):
    if not isinstance(model, MockModel):
        raise TypeError('offline runner accepts MockModel only')
    if max_attempts < 1 or timeout <= 0 or concurrency < 1:
        raise ValueError('invalid execution limits')
    semaphore = asyncio.Semaphore(concurrency)
    before = {r['invocation_id']: r['attempts'] for r in ledger.results()}

    async def one(request):
        key = request['invocation_id']
        async with semaphore:
            if before[key] >= max_attempts:
                ledger.finish(key, 'interrupted_exhausted', error='attempt limit reached before process death')
                return
            while True:
                attempt = ledger.begin(key)
                try:
                    reply = await asyncio.wait_for(model.complete(request), timeout)
                    if reply['invocation_id'] != key:
                        ledger.finish(key, 'key_mismatch', error=canonical(reply))
                    elif reply['finish_reason'] == 'length':
                        ledger.finish(key, 'truncated', response=reply['text'])
                    elif not reply['text'].strip():
                        ledger.finish(key, 'empty', response=reply['text'])
                    else:
                        ledger.finish(key, 'ok', response=reply['text'])
                    return
                except (TimeoutError, ConnectionError) as exc:
                    status = 'timeout' if isinstance(exc, TimeoutError) else 'transport_error'
                    ledger.finish(key, 'retry' if attempt < max_attempts else status, error=f'{status}: {exc}')
                    if attempt >= max_attempts:
                        return
    pending = ledger.pending()
    await asyncio.gather(*(one(r) for r in (pending if stop_after is None else pending[:stop_after])))


def validate_join(planned, results):
    expected = {r['invocation_id']: r for r in planned}
    actual = {r['invocation_id']: r for r in results}
    if len(expected) != len(planned) or len(actual) != len(results) or expected.keys() != actual.keys():
        raise ValueError('missing, duplicate or foreign invocation IDs')
    for key, row in actual.items():
        for field in ('case_id','arm','replicate_id','prompt_sha256'):
            if row.get(field) != expected[key][field]:
                raise ValueError(f'misattributed {field}: {key}')
    return dict(planned=len(planned), records=len(results), misattributed=0, duplicate=0, absent=0)
