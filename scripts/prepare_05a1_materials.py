"""Prepare review forms, corrected envelopes and integrity evidence offline."""
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from preflight.common import SEED, digest, write_json, write_jsonl
from preflight.data import candidates, pilot_candidates
from preflight.pipeline import csv_template
from preflight.prompts import ARMS, guidance, render
from preflight.runner import plan


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def main():
    source = Path('artifacts-05A1')
    evidence = Path('evidence/05A1')
    forms = Path('docs/review_05A1/forms')
    local = source/'review_packets'
    local.mkdir(parents=True, exist_ok=True)
    summary = json.loads((source/'summary.json').read_text())
    baseline = json.loads((evidence/'baseline_hashes.json').read_text())
    protected = [p for p in baseline if p.startswith('evidence/') or p in ('05_preflight_report.md','HANDOFF_05B.md','docs/04_experiment_design.md')]
    assert all(digest(Path(p).read_bytes()) == baseline[p] for p in protected)
    original_source = json.loads(Path('evidence/input_hashes.json').read_text())
    assert json.loads((source/'input_hashes.json').read_text()) == original_source
    integrity = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
        protected_files=len(protected), protected_files_unchanged=True,
        source_audit_identical=True, source_files=len(original_source['files']),scenarios={})
    review_bases = {}
    memberships = {}
    envelope = []
    costs = []
    for scenario in ('S180','S540','pilot_CANDIDATE'):
        folder = source/scenario
        cases_path = source/'pilot_CANDIDATE_cases.jsonl' if scenario=='pilot_CANDIDATE' else folder/'cases.jsonl'
        plan_path = source/'pilot_CANDIDATE_plan.jsonl' if scenario=='pilot_CANDIDATE' else folder/'generation_plan.jsonl'
        cases = read_jsonl(cases_path)
        regenerated = pilot_candidates(Path('vendor/BIPIA'),SEED) if scenario=='pilot_CANDIDATE' else candidates(Path('vendor/BIPIA'),scenario,SEED)
        # Check exact serialized bytes, including every context/question/payload/offset.
        temp = local/f'{scenario}_regenerated.jsonl'
        write_jsonl(temp,regenerated)
        assert temp.read_bytes() == cases_path.read_bytes()
        original_path = Path('artifacts')/('pilot_CANDIDATE_cases.jsonl' if scenario=='pilot_CANDIDATE' else f'{scenario}/cases.jsonl')
        assert original_path.read_bytes() == cases_path.read_bytes()
        write_jsonl(temp, plan(regenerated,SEED))
        assert temp.read_bytes() == plan_path.read_bytes()
        temp.unlink()
        old_path = Path('artifacts')/('pilot_CANDIDATE_plan.jsonl' if scenario=='pilot_CANDIDATE' else f'{scenario}/generation_plan.jsonl')
        old_plan = {r['invocation_id']:r for r in read_jsonl(old_path)}
        for row in read_jsonl(plan_path):
            old = old_plan[row['invocation_id']]
            assert {k:v for k,v in old.items() if k not in ('messages','prompt_sha256')} == {k:v for k,v in row.items() if k not in ('messages','prompt_sha256')}
            if row['arm'] in ('B0','R'):
                assert row == old
        # Case records and the exact render function fix all non-guidance bytes.
        integrity['scenarios'][scenario] = dict(cases=len(cases),
            cases_sha256=digest(cases_path.read_bytes()),
            original_case_bytes_identical=True, regenerated_cases_identical=True,
            regenerated_plan_identical=True, nonprompt_plan_metadata_identical=True,
            B0_R_requests_identical=True, generation_plan_sha256=digest(plan_path.read_bytes()))
        for name in ('token_counts.jsonl','token_summary.json','mock_summary.json','mock_missingness.json'):
            (evidence/scenario).mkdir(exist_ok=True)
            shutil.copyfile(folder/name,evidence/scenario/name)
        if scenario!='pilot_CANDIDATE':
            shutil.copyfile(folder/'case_index.jsonl',evidence/scenario/'case_index.jsonl')
        counts = read_jsonl(folder/'token_counts.jsonl')
        for task in ('email','table'):
            for arm in ARMS:
                vals=[r['arms'][arm] for r in counts if r['task']==task]
                envelope.append(dict(scenario=scenario,task=task,arm=arm,calls=len(vals),
                    user_tokens=sum(v['user_tokens'] for v in vals),system_tokens=sum(v['system_tokens'] for v in vals),
                    visible_input_tokens=sum(v['user_tokens']+v['system_tokens'] for v in vals),
                    min_user_tokens=min(v['user_tokens'] for v in vals),max_user_tokens=max(v['user_tokens'] for v in vals),
                    max_visible_input_per_call=max(v['user_tokens']+v['system_tokens'] for v in vals),
                    max_output_tokens=512*len(vals)))
        total=sum(v['user_tokens']+v['system_tokens'] for r in counts for v in r['arms'].values())
        judge_calls = summary['scenarios'][scenario]['model_judge_invocations'] if scenario!='pilot_CANDIDATE' else None
        if scenario=='pilot_CANDIDATE':
            from preflight.scoring import registry
            reg=registry(Path('vendor/BIPIA'))
            # The preserved registry is for held-out test attack IDs. Train pilot
            # routes must be reviewed separately, never guessed from family names.
            missing=sorted({c['attack_name'] for c in cases if c['case_type']=='attacked' and c['attack_name'] not in reg})
            write_json(evidence/'pilot_judge_routes_pending.json',dict(status='BLOCKED',unmapped_train_attack_names=missing,nominal_judge_calls=None,reason='Test registry cannot certify train-only pilot routes. Freeze separate pilot rubric before inference.'))
            judge_calls=None
        costs.append(dict(scenario=scenario,target_calls=len(cases)*4,target_visible_input_tokens=total,
            target_output_token_cap=len(cases)*4*512,max_attempts_per_target=3,
            target_calls_three_attempt_bound=len(cases)*4*3,
            target_visible_input_three_attempt_bound=total*3,target_output_three_attempt_cap=len(cases)*4*512*3,
            nominal_model_judge_calls=judge_calls,
            framing_tokens_per_target_call='',target_input_price_per_million='',target_output_price_per_million='',
            target_cache_policy='',judge_input_tokens_total='',judge_output_tokens_total='',judge_retry_allowance='',
            judge_input_price_per_million='',judge_output_price_per_million='',
            reviewer_hours='',reviewer_hourly_cost='',adjudication_cost='',output_audit_cost='',
            hard_benign_count='',hard_benign_target_input_tokens='',reserve_fraction='',tax_currency_fx='',
            account_RPM='',account_TPM='',available_credits='',approved_fee_cap='',total_estimate='',approved_by='',approved_at_utc=''))
        for case in cases:
            base=case['base_id']
            review_bases[base]=case
            memberships.setdefault(base,set()).add(scenario)
    write_json(evidence/'integrity_verification.json',integrity)
    write_json(evidence/'summary.json',summary)
    shutil.copyfile(source/'arms.json',evidence/'arms.json')
    csv_template(evidence/'target_token_envelopes.csv',list(envelope[0]),envelope)
    csv_template(evidence/'cost_estimation_template.csv',list(costs[0]),costs)
    for reviewer in (1,2):
        semantic=[]
        for task in ('email','table'):
            example=dict(task=task,context=('Meeting schedule: Tuesday at 10:00.' if task=='email' else 'Item | Quantity\nPencils | 12\nErasers | 4'),question=('When is the meeting?' if task=='email' else 'How many pencils are listed?'))
            for arm in ('N-L','N-F'):
                semantic.append(dict(form_version='05A1-v1',control_id=f'{task}/{arm}',text=guidance(task,arm),text_sha256=digest(guidance(task,arm)),embedded_user=render(example,arm)[1]['content'],
                    directs_behavior='',implies_source_truth_or_trust='',hints_answer_or_strategy='',protective_synonyms_or_negations='',fluent_descriptive='',approved='',reason='',reviewer_id='',independent_of_crafting='',date_utc=''))
        csv_template(forms/f'semantic_reviewer_{reviewer}.csv',list(semantic[0]),semantic)
        for task in ('email','table'):
            rows=[]
            raw=[]
            for base,c in sorted(review_bases.items()):
                if c['task']!=task:
                    continue
                row=dict(form_version='05A1-v1',base_id=base,scenarios=';'.join(sorted(memberships[base])),source_group_id=c['source_group_id'],context_sha256=c['context_sha256'],question_sha256=c['question_sha256'],gold_sha256=c['gold_sha256'],
                    local_record_file=f'artifacts-05A1/review_packets/{task}_source_records.jsonl',
                    answerability='',gold_valid='',supporting_evidence='',ambiguity_reason='',proposed_gold_if_invalid='',
                    approved_normalization='',approved_equivalents='',multivalue_mode='',units_currency_percent_policy='',
                    approved='',reviewer_id='',date_utc='')
                rows.append(row)
                raw.append(dict(base_id=base,context=c['original_context'],question=c['question'],original_gold=c['ideal'],context_sha256=c['context_sha256'],question_sha256=c['question_sha256'],gold_sha256=c['gold_sha256']))
            csv_template(forms/f'{task}_gold_reviewer_{reviewer}.csv',list(rows[0]),rows)
            write_jsonl(local/f'{task}_source_records.jsonl',raw)
        csv_template(forms/f'hard_benign_reviewer_{reviewer}.csv',
            ['form_version','candidate_id','parent_base_id','parent_context_sha256','candidate_context_sha256','question_sha256','original_gold_sha256','construction_method','exact_edit_or_source_span','provenance','unchanged_answer','supporting_evidence_before','supporting_evidence_after','contextual_not_assistant_directed','natural','no_attack_goal','gold_valid','answerability','approved','reason','reviewer_id','date_utc'],[])
    csv_template(forms/'hard_benign_construction.csv',['candidate_id','parent_base_id','parent_context_sha256','candidate_context_sha256','question_sha256','gold_sha256','local_context_file','construction_method','exact_edit_or_source_span','provenance','constructor_id','date_utc'],[])
    csv_template(forms/'adjudication.csv',['record_id','review_type','form_version','reviewer_1_file_sha256','reviewer_2_file_sha256','reviewer_1_label','reviewer_2_label','resolution','reason','revised_artifact_sha256','adjudicator_id','date_utc'],[])
    csv_template(forms/'access_budget_approval.csv',['check_id','model_snapshot','organization_project_redacted','evidence_path','evidence_sha256','status','reason','approved_by','date_utc'],[dict(check_id=c,model_snapshot='',organization_project_redacted='',evidence_path='',evidence_sha256='',status='',reason='',approved_by='',date_utc='') for c in ('target_metadata','target_parameters_roles_context','judge_metadata_parameters','quota','pricing_fee_cap','human_review_resources','scenario_manifest_freeze','dataset_rights','pilot_authorization')])
    write_json(evidence/'review_inventory.json',dict(semantic_forms=2,controls_per_form=4,gold_base_records_by_task=dict(Counter(c['task'] for c in review_bases.values())),hard_benign_candidates=0,judgments='ALL BLANK',raw_sources='local ignored artifacts-05A1/review_packets'))
    print('Integrity PASS; review forms blank; envelope and cost templates prepared.')
    for row in costs:
        print(row['scenario'], row['target_visible_input_tokens'],row['nominal_model_judge_calls'])


if __name__=='__main__':
    main()
