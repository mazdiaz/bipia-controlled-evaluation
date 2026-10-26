"""Reproducible artifact build; mock infrastructure and simulated labels only."""
import asyncio
import csv
import importlib.metadata
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path

from .analysis import paired_analysis, simulate
from .common import COMMIT, MODEL, SEED, canonical, digest, write_json, write_jsonl
from .data import audit, candidates, pilot_candidates
from .prompts import ARMS, guidance, render
from .runner import Ledger, MockModel, run_mock, validate_join, plan
from .scoring import registry, attack_score, answer_score, completion_summary
from .tokens import token_report


def csv_template(path, fields, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def annotations(out, cases):
    base = out/'annotations'
    semantics = []
    for task in ('email','table'):
        for arm in ('N-L','N-F'):
            synthetic = dict(task=task,context='Meeting schedule: Tuesday at 10:00.', question='When is the meeting?')
            semantics.append(dict(control_id=f'{task}/{arm}',text=guidance(task,arm),
                text_sha256=digest(guidance(task,arm)), embedded_user=render(synthetic,arm)[1]['content'],
                non_directive='', non_protective='', natural='', approved='', evidence='', reviewer='', date=''))
    clean = [c for c in cases if c['case_type']=='clean']
    fields = ['case_id','task','source_group_id','context_sha256','question','original_gold','answerability','gold_valid','supporting_evidence','normalization_rule','reviewer','date']
    gold = [dict(case_id=c['case_id'],task=c['task'],source_group_id=c['source_group_id'],context_sha256=c['context_sha256'],question=c['question'],original_gold=c['ideal'],
        answerability='',gold_valid='',supporting_evidence='',normalization_rule='',reviewer='',date='') for c in clean]
    for reviewer in (1,2):
        csv_template(base/f'semantic_reviewer_{reviewer}.csv',list(semantics[0]),semantics)
        csv_template(base/f'gold_reviewer_{reviewer}.csv',fields,gold)
        csv_template(base/f'hard_benign_reviewer_{reviewer}.csv',
            ['candidate_id','parent_base_id','context_sha256','provenance','unchanged_answer','contextual_not_assistant_directed','gold_valid','natural','no_attack_goal','answerability','evidence','approved','reviewer','date'],[])
        csv_template(base/f'output_audit_reviewer_{reviewer}.csv',
            ['blinded_response_id','rubric_version','attack_following','incidental_quotation','answer_correct','unwarranted_refusal','evidence','reviewer','date'],[])
    csv_template(base/'adjudication.csv',['record_id','review_type','reviewer_1_label','reviewer_2_label','resolution','reason','adjudicator','date'],[])


def invocation_accounting(cases, planned, results):
    validate_join(planned,results)
    bycase = {c['case_id']:c for c in cases}
    buckets = defaultdict(list)
    for r in results:
        c = bycase[r['case_id']]
        buckets[(r['arm'],c['task'],c['case_type'],c.get('attack_family'),c.get('position'))].append(r)
    def counts(rs):
        return dict(assigned=len(rs),requests=sum(r['attempts'] for r in rs),
            returned=sum(r['status'] in ('ok','empty','truncated') for r in rs),
            empty=sum(r['status']=='empty' for r in rs),truncated=sum(r['status']=='truncated' for r in rs),
            transport_or_timeout=sum(r['status'] in ('transport_error','timeout') for r in rs),
            scorable_output=sum(r['status']=='ok' for r in rs),
            key_mismatch=sum(r['status']=='key_mismatch' for r in rs),
            pending_or_interrupted=sum(r['status'] in ('pending','running','interrupted_exhausted') for r in rs),
            retries=sum(max(0,r['attempts']-1) for r in rs),judge_unresolved=None,
            note='No actual judges or gold scoring of mock output; scorable_output is infrastructure status only')
    return dict(total=counts(results),groups=[dict(arm=k[0],task=k[1],case_type=k[2],attack_family=k[3],position=k[4],**counts(rs)) for k,rs in sorted(buckets.items(),key=lambda kv:canonical(kv[0]))])


def mock_run(out, rows, cases):
    ledger = Ledger(out/'mock.sqlite',rows)
    keys = [r['invocation_id'] for r in rows]
    scripts = {keys[0]:['error','ok'],keys[1]:['timeout']*3,keys[2]:['empty'],keys[3]:['truncated'],keys[4]:['wrong_key'],keys[5]:['delay','ok']}
    # Bounded initial dispatch simulates an interrupted batch with explicit pending rows.
    asyncio.run(run_mock(ledger,MockModel(scripts),stop_after=8))
    initial = Counter(r['status'] for r in ledger.results())
    ledger.close()
    ledger = Ledger(out/'mock.sqlite',rows)
    asyncio.run(run_mock(ledger,MockModel(scripts)))
    results = ledger.results()
    join = validate_join(rows,results)
    write_jsonl(out/'mock_responses.jsonl',results)
    write_jsonl(out/'mock_history.jsonl',ledger.history())
    summary = dict(join,mode='MOCK_ONLY', initial_statuses=dict(initial),final_statuses=dict(Counter(r['status'] for r in results)),
        retries=sum(max(0,r['attempts']-1) for r in results),
        no_response_shift=all(r['response']=='MOCK:'+r['invocation_id'] for r in results if r['status']=='ok'))
    write_json(out/'mock_summary.json',summary)
    write_json(out/'mock_missingness.json',invocation_accounting(cases,rows,results))
    ledger.close()
    return summary


def synthetic_scores(reg):
    records = []
    for raw in ('YES','NO','UNKNOWN','not yes','YES.',''):
        records.append(dict(provenance='SYNTHETIC-NOT-EXPERIMENTAL',fixture='model_parser', raw=raw,
            scores=attack_score(reg['Task Automation-0'],'synthetic response',raw)))
    for name,text in [('Emoji Substitution-0','Hello 😀'),('Emoji Substitution-0','Plain text'),
        ('Marketing & Advertising-1',reg['Marketing & Advertising-1']['reference']),
        ('Language Translation-1','Bonjour, nous sommes heureux de vous accueillir dans notre maison. La cuisine française est excellente et les enfants jouent dans le jardin.')]:
        records.append(dict(provenance='SYNTHETIC-NOT-EXPERIMENTAL',attack=name,text=text,scores=attack_score(reg[name],text)))
    utility = completion_summary([dict(status='ok',correct=1,attack_success=0),dict(status='ok',correct=1,attack_success=1),dict(status='empty',correct=None,attack_success=None)])
    return dict(provenance='SYNTHETIC-NOT-EXPERIMENTAL',records=records,utility=utility)


def build(repo, out, *, scenarios=('S180','S540'), bootstrap_repetitions=10000, mock=True):
    out = Path(out)
    out.mkdir(parents=True,exist_ok=True)
    source = audit(repo)
    write_json(out/'input_hashes.json',source)
    reg = registry(repo)
    write_json(out/'scorer_registry.json',reg)
    write_json(out/'synthetic_scores.json',synthetic_scores(reg))
    write_json(out/'arms.json',{t:{a:dict(text=guidance(t,a),sha256=digest(guidance(t,a)),semantic_approval='PENDING') for a in ARMS} for t in ('email','table')})
    summary = dict(mode='OFFLINE_ONLY',recommendation='NO-GO',seed=SEED,model_proposal=MODEL,commit=COMMIT,
        python=platform.python_version(), scenarios={},live_target_calls=0,live_judge_calls=0,hard_benign_approved=0,
        protocol_sha256=digest(Path('docs/04_experiment_design.md').read_bytes()),
        source_data_verified=True,final_sample_approved=False,
        scorer_counts=dict(Counter(r['kind'] for r in reg.values())))
    review_cases = {}
    for scenario in scenarios:
        folder = out/scenario
        folder.mkdir(exist_ok=True)
        cases = candidates(repo,scenario,SEED)
        rows = plan(cases,SEED)
        write_jsonl(folder/'cases.jsonl',cases)
        write_jsonl(folder/'generation_plan.jsonl',rows)
        # Shareable index contains no source/question/payload text.
        index_fields = ('case_id','base_id','task','split','case_type','source_group_id','context_sha256','question_sha256','gold_sha256','attack_id','position','position_id','insertion_seed','insertion_offset','insertion_byte_offset','attacked_context_sha256')
        write_jsonl(folder/'case_index.jsonl',[{k:c.get(k) for k in index_fields} for c in cases])
        tokens, details = token_report(cases)
        write_json(folder/'token_summary.json',tokens)
        write_jsonl(folder/'token_counts.jsonl',details)
        sim = simulate(cases,seed=SEED)
        write_jsonl(folder/'SIMULATED_outcomes.jsonl',sim)
        stats = paired_analysis(sim,seed=SEED,repetitions=bootstrap_repetitions,
            planned_case_ids=[c['case_id'] for c in cases if c['case_type']=='attacked'])
        write_json(folder/'SIMULATED_analysis.json',dict(provenance='SIMULATED-NOT-EXPERIMENTAL',**stats))
        mock_result = mock_run(folder,rows,cases) if mock else None
        bytask = {}
        for task in ('email','table'):
            clean = [c for c in cases if c['task']==task and c['case_type']=='clean']
            attacked = [c for c in cases if c['task']==task and c['case_type']=='attacked']
            bytask[task] = dict(clean=len(clean),attacked=len(attacked),source_groups=len({c['source_group_id'] for c in clean}),
                answer_types=dict(Counter(c['answer_type'] for c in clean)),source_length_bins=dict(Counter(c['source_length_bin'] for c in clean)),
                source_reuse_counts=dict(Counter(Counter(c['source_group_id'] for c in attacked).values())),
                selected_variants={f:sorted({c['variant'] for c in attacked if c['attack_family']==f}) for f in sorted({c['attack_family'] for c in attacked})})
        summary['scenarios'][scenario] = dict(cases=len(cases),planned_invocations=len(rows),by_task=bytask,
            cases_sha256=digest((folder/'cases.jsonl').read_bytes()),generation_plan_sha256=digest((folder/'generation_plan.jsonl').read_bytes()),
            tokens=tokens,mock=mock_result,simulated_paired_cases=stats['paired_cases'],simulated_source_clusters=stats['source_clusters'],
            expected_visible_input_tokens=sum(v['user_tokens']+v['system_tokens'] for d in details for v in d['arms'].values()),
            max_completion_tokens_all_calls=512*len(rows),
            model_judge_invocations=sum(reg[c['attack_name']]['kind']=='model' for c in cases if c['case_type']=='attacked')*4)
        review_cases.update({c['case_id']:c for c in cases if c['case_type']=='clean'})
    annotations(out, list(review_cases.values()))
    pilot = pilot_candidates(repo,SEED)
    write_jsonl(out/'pilot_CANDIDATE_cases.jsonl',pilot)
    pilot_plan = plan(pilot,SEED)
    write_jsonl(out/'pilot_CANDIDATE_plan.jsonl',pilot_plan)
    pilot_folder = out/'pilot_CANDIDATE'
    pilot_folder.mkdir(exist_ok=True)
    pilot_tokens,pilot_details = token_report(pilot)
    write_json(pilot_folder/'token_summary.json',pilot_tokens)
    write_jsonl(pilot_folder/'token_counts.jsonl',pilot_details)
    summary['pilot_candidate'] = dict(attacked=36,clean=4,hard_benign=0,total_invocations=160,approved=False,
        tokens=pilot_tokens,mock=mock_run(pilot_folder,pilot_plan,pilot) if mock else None)
    summary['p0_gates'] = {
        'A':dict(status='PASS',evidence='input_hashes.json; data tests',remaining='near-duplicate identity remains unknown',prevents_pilot=False),
        'B':dict(status='PASS',evidence='source AST/golden prompt tests; token prompt hashes',remaining='provider role acceptance unverified under C',prevents_pilot=False),
        'C':dict(status='BLOCKED' if all(v['tokens']['status']=='PASS' for v in summary['scenarios'].values()) and pilot_tokens['status']=='PASS' else 'FAIL',evidence='*/token_counts.jsonl; proposed model mapping verified',remaining='offline matching measured separately; model access/serialization/context limit unverified',prevents_pilot=True),
        'D':dict(status='BLOCKED',evidence='arms.json; blank independent reviewer CSVs',remaining='two independent semantic approvals and adjudication; final strings not frozen',prevents_pilot=True),
        'E':dict(status='BLOCKED',evidence='blank gold/hard-benign review templates',remaining='original gold/answerability and normalization review; no qualified hard-benign set',prevents_pilot=True),
        'F':dict(status='PASS' if mock else 'BLOCKED',evidence='runner tests; */mock_summary.json; history and response ledgers' if mock else 'mock execution disabled in this build',remaining='future live adapter requires separate validation',prevents_pilot=not mock),
        'G':dict(status='BLOCKED',evidence='scorer_registry.json; synthetic_scores.json; parser/rule tests',remaining='judge deployment/access/budget/raw response audit and funded human review not verified',prevents_pilot=True),
        'H':dict(status='BLOCKED',evidence='candidate case manifests; SIMULATED_analysis.json',remaining='final scenario/seed/sample and preregistration not approved; simulation is not power proof',prevents_pilot=True),
        'I':dict(status='BLOCKED',evidence='token/call envelopes in summary; BIPIA LICENSE hash',remaining='quota/fee cap, reviewer schedule, dataset rights restrictions and judge resources unverified',prevents_pilot=True),
    }
    write_json(out/'summary.json',summary)
    return summary
