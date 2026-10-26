"""Approval-state and reviewer coverage checks; never create human decisions."""
import csv
import json
from pathlib import Path

from preflight.common import SEED, digest
from preflight.data import candidates, pilot_candidates
from preflight.prompts import guidance


def rows(name):
    with (Path('docs/review_05A1/forms')/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def test_review_forms_are_blank_and_cover_every_candidate_base():
    repo=Path('vendor/BIPIA')
    cases=candidates(repo,'S180',SEED)+candidates(repo,'S540',SEED)+pilot_candidates(repo,SEED)
    for reviewer in (1,2):
        for task in ('email','table'):
            form=rows(f'{task}_gold_reviewer_{reviewer}.csv')
            expected={c['base_id']:c for c in cases if c['task']==task}
            assert {r['base_id'] for r in form} == set(expected)
            assert len(form)==len(expected)
            for r in form:
                assert r['approved']==r['gold_valid']==r['answerability']==r['reviewer_id']==''
                c=expected[r['base_id']]
                for field in ('context_sha256','question_sha256','gold_sha256'):
                    assert r[field]==c[field]
        semantics=rows(f'semantic_reviewer_{reviewer}.csv')
        assert len(semantics)==4
        for r in semantics:
            task,arm=r['control_id'].split('/')
            assert r['text']==guidance(task,arm)
            assert r['text_sha256']==digest(r['text'])
            for field in ('directs_behavior','implies_source_truth_or_trust','hints_answer_or_strategy',
                          'protective_synonyms_or_negations','fluent_descriptive','approved','reviewer_id'):
                assert r[field]==''
        assert rows(f'hard_benign_reviewer_{reviewer}.csv')==[]
    assert rows('adjudication.csv')==[]


def test_historical_evidence_is_byte_preserved():
    baseline=json.loads(Path('evidence/05A1/baseline_hashes.json').read_text())
    protected=[p for p in baseline if p.startswith('evidence/') or p in ('05_preflight_report.md','HANDOFF_05B.md','docs/04_experiment_design.md')]
    assert len(protected)>0
    for p in protected:
        assert digest(Path(p).read_bytes())==baseline[p],p


def test_judge_and_costs_remain_unapproved():
    proposal=json.loads(Path('config/judge_proposal_05A1.json').read_text())
    assert proposal['human_approved'] is False
    assert proposal['nominal_calls']['train_pilot'] is None
    with Path('evidence/05A1/cost_estimation_template.csv').open(encoding='utf-8-sig',newline='') as f:
        costs=list(csv.DictReader(f))
    assert {r['scenario'] for r in costs}=={'S180','S540','pilot_CANDIDATE'}
    for r in costs:
        for field in ('target_input_price_per_million','judge_input_tokens_total','available_credits',
                      'reviewer_hours','account_RPM','approved_fee_cap','total_estimate','approved_by'):
            assert r[field]==''
