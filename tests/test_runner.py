import asyncio
from collections import Counter
import json
import sqlite3

import pytest

from preflight.runner import Ledger, MockModel, run_mock, plan, validate_join


def synthetic_plan(n=8):
    return plan([dict(case_id=f'c{i}', task='email', context=f'context {i}', question='Q') for i in range(n)], seed=13)


def test_plan_keys_order_and_hashes():
    p = synthetic_plan()
    assert p == synthetic_plan()
    assert len({r['invocation_id'] for r in p}) == 32
    for i in range(0, len(p), 4):
        assert len({r['case_id'] for r in p[i:i+4]}) == 1
        assert {r['arm'] for r in p[i:i+4]} == {'B0', 'N-L', 'N-F', 'R'}


def test_mock_failures_order_resume_and_association(tmp_path):
    p = synthetic_plan()
    db = tmp_path/'run.db'
    ledger = Ledger(db, p)
    keys = [r['invocation_id'] for r in p]
    script = {keys[0]: ['error', 'ok'], keys[1]: ['timeout']*3,
              keys[2]: ['empty'], keys[3]: ['truncated'], keys[4]: ['wrong_key'],
              keys[5]: ['delay', 'ok']}
    model = MockModel(script)
    asyncio.run(run_mock(ledger, model, timeout=.1))
    rows = ledger.results()
    assert validate_join(p, rows)['misattributed'] == 0
    assert rows[0]['status'] == 'ok' and rows[0]['attempts'] == 2
    assert rows[1]['status'] == 'timeout' and rows[1]['attempts'] == 3
    assert rows[2]['status'] == 'empty'
    assert rows[3]['status'] == 'truncated'
    assert rows[4]['status'] == 'key_mismatch'
    assert rows[5]['status'] == 'ok' and rows[5]['attempts'] == 2
    assert [h['invocation_id'] for h in ledger.history() if h['status']=='ok'] != [r['invocation_id'] for r in p if r['invocation_id'] not in keys[1:5]]
    for row in rows:
        if row['status'] == 'ok':
            assert row['response'] == 'MOCK:'+row['invocation_id']
    previous = ledger.results()
    asyncio.run(run_mock(Ledger(db, p), MockModel()))
    assert ledger.results() == previous
    assert all(r['status'] != 'pending' for r in rows)


def test_interrupt_pending_explicit_and_resume(tmp_path):
    p = synthetic_plan()
    ledger = Ledger(tmp_path/'run.db', p)
    # Seed one in-flight request to represent process death between dispatch and reply.
    ledger.begin(p[0]['invocation_id'])
    ledger.close()
    ledger = Ledger(tmp_path/'run.db', p)
    assert ledger.results()[0]['status'] == 'pending'
    assert ledger.results()[0]['attempts'] == 1
    assert len(ledger.results()) == len(p)
    asyncio.run(run_mock(ledger, MockModel(), stop_after=3))
    assert Counter(r['status'] for r in ledger.results())['pending'] == len(p)-3
    asyncio.run(run_mock(ledger, MockModel()))
    assert all(r['status'] == 'ok' for r in ledger.results())
    assert any(h['status'] == 'interrupted' for h in ledger.history())


def test_stale_plan_duplicate_and_foreign_results_rejected(tmp_path):
    p = synthetic_plan()
    Ledger(tmp_path/'run.db', p).close()
    q = json.loads(json.dumps(p))
    q[0]['prompt_sha256'] = 'different'
    with pytest.raises(ValueError, match='plan'):
        Ledger(tmp_path/'run.db', q)
    with pytest.raises(ValueError, match='duplicate'):
        Ledger(tmp_path/'duplicate.db', p+[p[0]])
    with pytest.raises(ValueError):
        validate_join(p, [dict(invocation_id='foreign')])
