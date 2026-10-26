"""Canonical data, provenance, insertion and provisional sampling.

Insertion logic adapted from Microsoft BIPIA (MIT), pinned COMMIT.
Read Git blobs directly to avoid platform checkout newline conversions.
"""
import json
import random
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from nltk.tokenize.punkt import PunktSentenceTokenizer

from .common import COMMIT, digest

POSITIONS = ('end', 'start', 'middle')
SOURCE_FILES = [
    *(f'benchmark/{t}/{s}.jsonl' for t in ('email', 'table') for s in ('train', 'test')),
    *(f'benchmark/text_attack_{s}.json' for s in ('train', 'test')),
    'bipia/data/email.py', 'bipia/data/table.py', 'bipia/data/base.py', 'bipia/data/utils.py',
    'bipia/model/gpt.py', 'bipia/metrics/regist.py', 'bipia/metrics/eval/model.py',
    'bipia/metrics/eval/language.py', 'bipia/metrics/eval/encode.py',
    'bipia/metrics/eval/match.py', 'bipia/metrics/eval_factory.py',
    'bipia/metrics/eval/utils.py', 'bipia/metrics/eval/base.py', 'bipia/model/utils.py',
    'examples/run.py', 'defense/black_box/few_shot.py', 'LICENSE',
]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, path):
    return git(repo, 'show', f'{COMMIT}:{path}')


def load_rows(repo, task, split, development=False):
    if task not in ('email', 'table') or split not in ('train', 'test'):
        raise ValueError('unsupported task/split')
    path = f'benchmark/{task}/{split}.jsonl'
    data = [json.loads(line) for line in blob(repo, path).decode('utf-8').splitlines()]
    blob_sha = git(repo, 'rev-parse', f'{COMMIT}:{path}').decode().strip()
    rows = []
    for index, row in enumerate(data):
        if set(row) != {'context', 'question', 'ideal'} or not all(isinstance(v, str) for v in row.values()):
            raise ValueError(f'schema mismatch {path}:{index}')
        rows.append(dict(row, task=task, split=split, row_index=index,
            context_sha256=digest(row['context']), question_sha256=digest(row['question']),
            gold_sha256=digest(row['ideal']),
            source_group_id=digest([task, row['context']]),
            base_id=digest([COMMIT, path, index, row]),
            source_blob_git_sha=blob_sha))
    if development:
        if split != 'train':
            raise ValueError('development pool must be train')
        forbidden = {r['context_sha256'] for r in load_rows(repo, task, 'test')}
        rows = [r for r in rows if r['context_sha256'] not in forbidden]
    return rows


def load_attacks(repo, split, development=False):
    if split not in ('train', 'test') or (development and split != 'train'):
        raise ValueError('invalid attack split/development combination')
    attacks = json.loads(blob(repo, f'benchmark/text_attack_{split}.json'))
    result = []
    for family, payloads in attacks.items():
        if not isinstance(payloads, list) or len(payloads) != 5 or not all(isinstance(p, str) for p in payloads):
            raise ValueError('unexpected attack schema')
        if development and family == 'Language Translation':
            continue
        for variant, payload in enumerate(payloads):
            result.append(dict(attack_split=split, attack_family=family, variant=variant,
                attack_name=f'{family}-{variant}', payload=payload, payload_sha256=digest(payload),
                attack_id=digest([COMMIT, split, family, variant, payload])))
    return result


def audit(repo):
    head = git(repo, 'rev-parse', 'HEAD').decode().strip()
    if head != COMMIT:
        raise ValueError(f'wrong source commit: {head}')
    files = {}
    for path in SOURCE_FILES:
        raw = blob(repo, path)
        local = (Path(repo)/path).read_bytes()
        files[path] = dict(sha256=digest(raw), bytes=len(raw),
            git_blob_sha=git(repo, 'rev-parse', f'{COMMIT}:{path}').decode().strip(),
            working_tree_sha256=digest(local), working_tree_matches_blob=local == raw)
    tasks = {}
    for task in ('email', 'table'):
        train, test = (load_rows(repo, task, s) for s in ('train', 'test'))
        tr = {r['context_sha256'] for r in train}
        te = {r['context_sha256'] for r in test}
        overlap = sorted(tr & te)
        tasks[task] = dict(train_rows=len(train), test_rows=len(test), train_groups=len(tr),
            test_groups=len(te), overlap_groups=len(overlap), overlap_context_hashes=overlap,
            test_unknown=sum(r['ideal'] == 'unknown' for r in test),
            excluded_development_base_ids=[r['base_id'] for r in train if r['context_sha256'] in overlap],
            source_crosswalk=[{k: r[k] for k in ('split', 'row_index', 'base_id', 'source_group_id', 'context_sha256')} for r in train+test])
    attacks = {s: load_attacks(repo, s) for s in ('train', 'test')}
    families = {s: {a['attack_family'] for a in v} for s, v in attacks.items()}
    return dict(commit=head, files=files, tasks=tasks,
        attack_counts={s: len(v) for s, v in attacks.items()},
        shared_attack_families=sorted(families['train'] & families['test']),
        exact_shared_payloads=sorted({a['payload_sha256'] for a in attacks['train']} & {a['payload_sha256'] for a in attacks['test']}))


def insert(context, payload, position, seed):
    if position == 'start':
        return '\n'.join([payload, context]), 0
    if position == 'end':
        return '\n'.join([context, payload]), len(context)
    if position == 'middle':
        spans = list(PunktSentenceTokenizer().span_tokenize(context))
        start, _ = random.Random(seed).sample(spans, k=1)[0]
        return '\n'.join([context[:start], payload, context[start:]]), start
    raise ValueError('unknown insertion position')


def make_case(row, attack, position, seed):
    if (attack is None) != (position is None):
        raise ValueError('attack/position must both be specified or absent')
    context, offset = insert(row['context'], attack['payload'], position, seed) if attack else (row['context'], None)
    identity = dict(base_id=row['base_id'], case_type='attacked' if attack else 'clean',
        attack_id=attack['attack_id'] if attack else None, position=position,
        insertion_seed=seed if attack else None, context_sha256=digest(context))
    return (row | (attack or {})) | dict(case_id=digest(identity), case_type=identity['case_type'],
        schema_version='04.1', source_repo='microsoft/BIPIA', repo_commit=COMMIT,
        original_context=row['context'], context=context, attacked_context_sha256=digest(context),
        attack_id=identity['attack_id'], position=position,
        position_id=digest([position, seed, offset]) if attack else None,
        insertion_seed=seed if attack else None, insertion_offset=offset,
        insertion_byte_offset=len(row['context'][:offset].encode()) if attack else None,
        effective_relative_offset=offset/len(row['context']) if attack and row['context'] else None,
        candidate_only=True)


def answer_type(row):
    if row['task'] == 'email':
        return 'unknown' if row['ideal'] == 'unknown' else 'answerable'
    return 'numeric' if re.fullmatch(r'[\s$€£+\-\d.,%]+', row['ideal']) else 'other'


def select_sources(rows, rng):
    groups = defaultdict(list)
    for row in rows:
        groups[row['source_group_id']].append(row)
    # Source length strata: ranks of distinct contexts, not repeated QA rows.
    ordered = sorted(groups, key=lambda k: (len(groups[k][0]['context']), k))
    length_bin = {k: min(2, 3*i//len(ordered)) for i, k in enumerate(ordered)}
    selected, used = [], set()
    targets = [('unknown', 15), ('answerable', 15)] if rows[0]['task'] == 'email' else [('numeric', 15), ('other', 15)]
    for kind, count in targets:
        bins = defaultdict(list)
        for key in sorted(groups):
            eligible = [r for r in groups[key] if answer_type(r) == kind]
            if eligible:
                bins[length_bin[key]].append((key, eligible))
        for values in bins.values():
            rng.shuffle(values)
        for i in range(count):
            preferred = i % 3
            choices = [(b, k, rs) for b in sorted(bins, key=lambda b: ((b-preferred)%3)) for k, rs in bins[b] if k not in used]
            if not choices:
                raise ValueError(f'insufficient distinct {kind} sources')
            _, key, eligible = choices[0]
            chosen = dict(rng.choice(eligible), answer_type=kind, source_length_bin=length_bin[key])
            selected.append(chosen)
            used.add(key)
    rng.shuffle(selected)
    return selected


def candidates(repo, scenario, seed):
    if scenario not in ('S180', 'S540'):
        raise ValueError('scenario must be S180 or S540')
    rng = random.Random(seed)
    attacks = load_attacks(repo, 'test')
    families = sorted({a['attack_family'] for a in attacks})
    rng.shuffle(families)
    cases = []
    for task in ('email', 'table'):
        sources = select_sources(load_rows(repo, task, 'test'), rng)
        cases.extend(make_case(row, None, None, seed) for row in sources)
        for i, family in enumerate(families):
            variants = [a for a in attacks if a['attack_family'] == family]
            chosen = rng.sample(variants, 1 if scenario == 'S180' else 2)
            bases = sources[2*i:2*i+2] if scenario == 'S180' else [sources[(3*i+j)%30] for j in range(3)]
            for row in bases:
                for attack in chosen:
                    for position in POSITIONS:
                        cases.append(make_case(row, attack, position, seed))
    return sorted(cases, key=lambda c: c['case_id'])


def pilot_candidates(repo, seed):
    rng = random.Random(seed)
    attacks = load_attacks(repo, 'train', development=True)
    families = rng.sample(sorted({a['attack_family'] for a in attacks}),3)
    result = []
    for task in ('email','table'):
        pool = load_rows(repo,task,'train',development=True)
        groups = defaultdict(list)
        for r in pool:
            groups[r['source_group_id']].append(r)
        bases = [rng.choice(groups[g]) for g in rng.sample(sorted(groups),2)]
        result.extend(make_case(r,None,None,seed) for r in bases)
        for f in families:
            attack = rng.choice([a for a in attacks if a['attack_family']==f])
            result.extend(make_case(r,attack,p,seed) for r in bases for p in POSITIONS)
    return sorted(result,key=lambda c:c['case_id'])
