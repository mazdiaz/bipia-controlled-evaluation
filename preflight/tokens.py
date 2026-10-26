import importlib.metadata
import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import tiktoken

from .common import MODEL, digest
from .prompts import ARMS, SYSTEM, guidance, render


@lru_cache
def encoding():
    # Cache downloaded public tokenizer ranks locally for subsequent offline use.
    os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(Path('.tokenizer-cache').resolve()))
    enc = tiktoken.encoding_for_model(MODEL)
    if enc.name != 'o200k_base':
        raise ValueError('protocol mapping mismatch; no fallback allowed')
    return enc


def token_report(cases):
    enc = encoding()
    count = lambda s: len(enc.encode(s, disallowed_special=()))
    details, groups = [], defaultdict(list)
    for case in cases:
        arms = {}
        for arm in ARMS:
            messages = render(case, arm)
            arms[arm] = dict(user_tokens=count(messages[1]['content']), system_tokens=count(SYSTEM),
                guidance_tokens=count(guidance(case['task'], arm)), prompt_sha256=digest(messages))
        row = dict(case_id=case['case_id'], task=case['task'], case_type=case['case_type'],
            context_sha256=digest(case['context']), question_sha256=digest(case['question']), arms=arms,
            delta_NL_R=arms['N-L']['user_tokens']-arms['R']['user_tokens'],
            delta_NF_R=arms['N-F']['user_tokens']-arms['R']['user_tokens'])
        details.append(row)
        groups[(case['task'], case['case_type'])].append(row)
    grouped = {}
    for (task, kind), rows in groups.items():
        grouped[f'{task}/{kind}'] = dict(cases=len(rows),
            delta_NL_R=sorted({r['delta_NL_R'] for r in rows}),
            delta_NF_R=sorted({r['delta_NF_R'] for r in rows}),
            user_token_ranges={a: [min(r['arms'][a]['user_tokens'] for r in rows), max(r['arms'][a]['user_tokens'] for r in rows)] for a in ARMS})
    # Hash complete in-memory vocabulary/merge ranks and regex, plus public cache files.
    vocab_hash = digest([[k.hex(), v] for k, v in sorted(enc._mergeable_ranks.items(), key=lambda kv: kv[1])])
    cache = Path(os.environ['TIKTOKEN_CACHE_DIR'])
    return dict(model_proposal=MODEL, account_access='UNVERIFIED; no API calls', encoding=enc.name,
        tiktoken_version=importlib.metadata.version('tiktoken'), ranks_sha256=vocab_hash,
        regex_sha256=digest(enc._pat_str), cache_hashes={p.name: digest(p.read_bytes()) for p in sorted(cache.glob('*')) if p.is_file()},
        cases=len(details), mismatched_cases=sum(r['delta_NL_R'] != 0 or r['delta_NF_R'] != 0 for r in details),
        status='FAIL' if any(r['delta_NL_R'] or r['delta_NF_R'] for r in details) else 'PASS',
        control_revision='none; protocol primary drafts', groups=grouped), details
