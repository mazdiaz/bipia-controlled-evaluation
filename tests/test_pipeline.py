import asyncio
import json
from pathlib import Path
import sqlite3
import pytest

from preflight.pipeline import build
from preflight.data import pilot_candidates, load_rows
from preflight.runner import Ledger, MockModel, run_mock
from preflight.analysis import paired_analysis


def test_pilot_is_train_only_and_nonoverlapping():
    repo = Path('vendor/BIPIA')
    rows = pilot_candidates(repo, 20261026)
    assert len(rows) == 40
    assert sum(r['case_type']=='attacked' for r in rows)==36
    assert all(r['split']=='train' for r in rows)
    assert not any(r.get('attack_family')=='Language Translation' for r in rows)
    for task in ('email','table'):
        assert not {r['source_group_id'] for r in rows if r['task']==task} & {r['source_group_id'] for r in load_rows(repo,task,'test')}


def test_retry_crash_resumes_and_attempt_cap(tmp_path):
    from tests_helper import tiny_plan
    p = tiny_plan()
    path = tmp_path/'retry.db'
    ledger = Ledger(path,p)
    key = p[0]['invocation_id']
    for i in range(3):
        ledger.begin(key)
        ledger.finish(key,'retry',error='synthetic error')
    ledger.close()
    ledger = Ledger(path,p)
    asyncio.run(run_mock(ledger,MockModel()))
    assert ledger.results()[0]['status']=='interrupted_exhausted'


def test_expected_cells_not_silently_inferred_from_shortened_data():
    rows = [dict(case_id='1',task='email',attack_family='f',position='start',source_group_id='g',R=0,NF=1)]
    with pytest.raises(ValueError,match='planned'):
        paired_analysis(rows,seed=1,repetitions=2,planned_case_ids=['1','2'])


def test_build_offline_artifacts(tmp_path):
    build(Path('vendor/BIPIA'),tmp_path,scenarios=('S180',),bootstrap_repetitions=20, mock=False)
    summary = json.loads((tmp_path/'summary.json').read_text())
    assert summary['recommendation']=='NO-GO'
    assert summary['scenarios']['S180']['cases']==240
    assert summary['scenarios']['S180']['planned_invocations']==960
    assert summary['scenarios']['S180']['tokens']['status']=='PASS'
    assert summary['p0_gates']['C']['status']=='BLOCKED'
    assert summary['pilot_candidate']['tokens']['cases']==40
    assert set(summary['p0_gates'])==set('ABCDEFGHI')
    assert (tmp_path/'S180/cases.jsonl').is_file()
    assert len((tmp_path/'annotations/semantic_reviewer_1.csv').read_text().splitlines())>4


def test_accounting_uses_keyed_metadata_and_retains_failed_denominators():
    from preflight.pipeline import invocation_accounting
    from tests_helper import tiny_plan
    p = tiny_plan()
    rows = [dict(r,status='timeout' if i==0 else 'ok',attempts=3 if i==0 else 1,response=None if i==0 else 'MOCK') for i,r in enumerate(p)]
    cases = [dict(case_id='1',task='email',case_type='clean',position=None,attack_family=None)]
    result = invocation_accounting(cases,p,list(reversed(rows)))
    assert result['total']['assigned']==4
    assert result['total']['requests']==6
    assert result['total']['transport_or_timeout']==1
    assert result['total']['scorable_output']==3
    assert sum(g['assigned'] for g in result['groups'])==4
