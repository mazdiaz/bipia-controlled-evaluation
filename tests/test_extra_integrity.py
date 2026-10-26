import ast
import asyncio
from functools import partial
from pathlib import Path
import random
import statistics
import subprocess
import sys

import pytest

from preflight.data import blob
from preflight.scoring import registry
from preflight.analysis import paired_analysis
from preflight.runner import Ledger, MockModel, run_mock
from tests_helper import tiny_plan


def test_entire_scorer_map_against_inert_original_registration():
    repo = Path('vendor/BIPIA')
    tree = ast.parse(blob(repo,'bipia/metrics/regist.py'))
    names = ['format_fn_factry','task_irrelevant_regist_fn','task_relevant_regist_fn','targeted_regist_fn']
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    from collections import OrderedDict
    ns = dict(OrderedDict=OrderedDict,partial=partial,prompt_format_fn=lambda *args:args)
    for name in ['ModelEval','EmojiEval','LanguageEval','MatchRefEval']:
        ns[name] = type(name,(),{})
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<inert-original-registration>','exec'),ns)
    original = {}
    for fn in names[1:]:
        original.update(ns[fn]({}))
    reg = registry(repo)
    assert reg.keys()==original.keys()
    kindmap = {'ModelEval':'model','EmojiEval':'emoji','LanguageEval':'language','MatchRefEval':'fuzzy'}
    for name,entry in original.items():
        cls = entry.func if isinstance(entry,partial) else entry
        assert reg[name]['kind']==kindmap[cls.__name__]
        if cls.__name__=='ModelEval':
            # Original closure preserves the exact unformatted judge rubric.
            assert reg[name]['judge_prompt']==entry.keywords['format_fn'].__closure__[0].cell_contents
        elif cls.__name__=='LanguageEval':
            assert reg[name]['target_lang']==entry.keywords['target_lang']
        elif cls.__name__=='MatchRefEval':
            assert reg[name]['reference']==entry.keywords['reference']


def test_bootstrap_one_weight_per_source_exact_hand_calculation():
    rows = [dict(case_id=str(i),task='email',source_group_id=str(i//3),attack_family='f',position='start',R=i//3,NF=0) for i in range(6)]
    rng = random.Random(19)
    w0,w1 = rng.expovariate(1),rng.expovariate(1)
    expected = w1/(w0+w1)
    report = paired_analysis(rows,seed=19,repetitions=1)
    assert report['ci95'] == pytest.approx([expected,expected])


def test_terminal_transport_error_and_actual_async_cancellation(tmp_path):
    p = tiny_plan()
    key = p[0]['invocation_id']
    ledger = Ledger(tmp_path/'cancel.db',p)

    async def cancel_in_flight():
        task = asyncio.create_task(run_mock(ledger,MockModel({key:['delay']}),timeout=.2,concurrency=1))
        await asyncio.sleep(.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    asyncio.run(cancel_in_flight())
    assert ledger.results()[0]['status']=='running'
    ledger.close()
    ledger = Ledger(tmp_path/'cancel.db',p)
    asyncio.run(run_mock(ledger,MockModel({key:['error']})))
    row = ledger.results()[0]
    assert row['status']=='transport_error' and row['attempts']==3
    assert row['response'] is None


def test_abrupt_subprocess_exit_preserves_plan_and_recovers(tmp_path):
    path = tmp_path/'crash.db'
    code = "from preflight.runner import Ledger; from tests_helper import tiny_plan; import os,sys; p=tiny_plan(); l=Ledger(sys.argv[1],p); l.begin(p[0]['invocation_id']); os._exit(17)"
    result = subprocess.run([sys.executable,'-c',code,str(path)],check=False,capture_output=True)
    assert result.returncode==17, result.stderr
    p = tiny_plan()
    ledger = Ledger(path,p)
    assert len(ledger.results())==len(p)
    assert ledger.results()[0]['status']=='pending'
    asyncio.run(run_mock(ledger,MockModel()))
    assert ledger.results()[0]['attempts']==2
    assert all(r['status']=='ok' for r in ledger.results())
