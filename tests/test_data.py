import ast
from collections import Counter
from pathlib import Path
import random

import pytest

from preflight.data import audit, load_rows, load_attacks, candidates, insert, make_case
from preflight.common import digest, canonical

REPO = Path('vendor/BIPIA')


def test_audit_counts_overlap_and_blobs():
    result = audit(REPO)
    assert result['commit'] == 'a004b69ec0dd446e0afd461d98cb5e96e120a5d0'
    for task, counts in [('email', (50, 50, 45, 44, 11)), ('table', (900, 100, 617, 84, 0))]:
        r = result['tasks'][task]
        assert tuple(r[k] for k in ['train_rows', 'test_rows', 'train_groups', 'test_groups', 'overlap_groups']) == counts
    assert len(result['files']) >= 16
    assert all(f['working_tree_matches_blob'] for f in result['files'].values())
    assert result['tasks']['email']['test_unknown'] == 26
    assert result['shared_attack_families'] == ['Language Translation']


def test_canonical_ids_exact_unicode():
    assert canonical({'b': 1, 'a': 'é'}) == '{"a":"é","b":1}'
    assert digest('a\n') != digest('a\r\n')
    assert digest('é') != digest('e\u0301')


@pytest.mark.parametrize('position', ['start', 'middle', 'end'])
@pytest.mark.parametrize('context', ['A sentence. Second one! Third?', '{x}\n你好 world.', 'One line'])
def test_insert_matches_upstream(position, context):
    # Execute only these three pure functions, without importing model frameworks.
    tree = ast.parse((REPO/'bipia/data/utils.py').read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'insert_'+position]
    from nltk.tokenize.punkt import PunktSentenceTokenizer
    ns = {'random': random, 'PunktSentenceTokenizer': PunktSentenceTokenizer}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<upstream-insertion>', 'exec'), ns)
    text, offset = insert(context, 'PAYLOAD', position, 20261026)
    assert text == ns['insert_'+position](context, 'PAYLOAD', 20261026)
    assert 'PAYLOAD' in text
    assert 0 <= offset <= len(context)


@pytest.mark.parametrize('scenario,n', [('S180', 180), ('S540', 540)])
def test_candidate_coverage_and_determinism(scenario, n):
    a = candidates(REPO, scenario, 20261026)
    b = candidates(REPO, scenario, 20261026)
    assert a == b
    assert len({c['case_id'] for c in a}) == n+60
    attacked = [c for c in a if c['case_type'] == 'attacked']
    assert len(attacked) == n
    assert set(c['position'] for c in attacked) == {'start', 'middle', 'end'}
    assert len(set(c['attack_family'] for c in attacked)) == 15
    for task in ['email', 'table']:
        clean = [c for c in a if c['task'] == task and c['case_type'] == 'clean']
        assert len(clean) == len({c['source_group_id'] for c in clean}) == 30
        assert {c['base_id'] for c in clean} == {c['base_id'] for c in attacked if c['task'] == task}
        if task == 'email':
            assert sum(c['ideal'] == 'unknown' for c in clean) == 15
    cells = Counter((c['task'], c['attack_family'], c['position']) for c in attacked)
    assert len(cells) == 90 and set(cells.values()) == {n//90}
    assert a != candidates(REPO, scenario, 17)


def test_train_pool_excludes_all_test_sources_and_collision_family():
    for task in ['email', 'table']:
        test = load_rows(REPO, task, 'test')
        train = load_rows(REPO, task, 'train', development=True)
        assert not {r['source_group_id'] for r in train} & {r['source_group_id'] for r in test}
    assert 'Language Translation' not in {a['attack_family'] for a in load_attacks(REPO, 'train', development=True)}
    train = load_attacks(REPO, 'train')
    test = load_attacks(REPO, 'test')
    assert len(train) == len(test) == 75
    assert not {a['attack_id'] for a in train} & {a['attack_id'] for a in test}
    row = load_rows(REPO, 'email', 'test')[0]
    assert make_case(row, None, None, 1)['case_id'] != make_case(row, test[0], 'start', 1)['case_id']
