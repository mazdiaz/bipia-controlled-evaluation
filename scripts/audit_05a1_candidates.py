"""Offline full-message candidate audit. No model adapter or network access."""
import json
import socket
import sys
from pathlib import Path
from preflight.common import SEED, digest, write_json, write_jsonl
from preflight.data import candidates, pilot_candidates
from preflight.prompts import TEMPLATES, guidance, render
from preflight.tokens import encoding


def main():
    def denied(*args, **kwargs):
        raise RuntimeError('05A1 token audit is offline')
    socket.socket.connect = denied
    socket.create_connection = denied
    out = Path('evidence/05A1')
    catalog_path = Path(sys.argv[1]) if len(sys.argv)>1 else out/'candidate_catalog.json'
    catalog = json.loads(catalog_path.read_text())
    enc = encoding()
    repo = Path('vendor/BIPIA')
    sets = {s:candidates(repo,s,SEED) for s in ('S180','S540')}
    sets['pilot_CANDIDATE'] = pilot_candidates(repo,SEED)
    count = lambda s: len(enc.encode(s,disallowed_special=()))
    summaries = []
    selected = None
    for candidate in catalog['attempts']:
        details = []
        for scenario,cases in sets.items():
            for c in cases:
                noun = {'email':'email','table':'form'}[c['task']]
                ref = render(c,'R')[1]['content']
                arms = {}
                for arm in ('NL','NF'):
                    text = candidate[arm].format(noun=noun)
                    user = TEMPLATES[c['task']].format(guidance=text,context=c['context'],question=c['question'])
                    arms[arm] = dict(guidance=text,guidance_sha256=digest(text),guidance_tokens=count(text),user_tokens=count(user),delta_R=count(user)-count(ref),user_sha256=digest(user))
                details.append(dict(candidate=candidate['id'],scenario=scenario,case_id=c['case_id'],task=c['task'],case_type=c['case_type'],context_sha256=digest(c['context']),question_sha256=digest(c['question']),R_tokens=count(ref),R_user_sha256=digest(ref),arms=arms))
        write_jsonl(out/f"candidate_{candidate['id']}_counts.jsonl",details)
        groups = []
        for scenario in sets:
            for task in ('email','table'):
                rows = [r for r in details if r['scenario']==scenario and r['task']==task]
                groups.append(dict(scenario=scenario,task=task,cases=len(rows),NL_deltas=sorted({r['arms']['NL']['delta_R'] for r in rows}),NF_deltas=sorted({r['arms']['NF']['delta_R'] for r in rows})))
        mismatch=sum(any(a['delta_R'] for a in r['arms'].values()) for r in details)
        summaries.append(dict(candidate=candidate['id'],cases=len(details),mismatches=mismatch,groups=groups))
        print(candidate['id'],mismatch,[(g['scenario'],g['task'],g['NL_deltas'],g['NF_deltas']) for g in groups])
        if mismatch == 0:
            selected=candidate['id']
            break
    result_name = 'candidate_results.json' if catalog_path.name=='candidate_catalog.json' else catalog_path.stem+'_results.json'
    write_json(out/result_name,dict(catalog_sha256=digest(catalog_path.read_bytes()),encoding=enc.name,selected=selected,semantic_approval='PENDING',attempts=summaries,not_evaluated=[c['id'] for c in catalog['attempts'][len(summaries):]]))

if __name__=='__main__':
    main()
