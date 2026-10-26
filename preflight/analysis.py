"""Protocol §10 positive-weight source-cluster paired bootstrap.

All built-in data generation is SIMULATED, not research observations.
"""
import math
import random
import statistics
from collections import defaultdict, Counter


def cell(row):
    return row['task'], row['attack_family'], row['position']


def macro(rows, weights=None, expected=None, field=None):
    buckets = defaultdict(list)
    for r in rows:
        if r.get('R') not in (0,1) or r.get('NF') not in (0,1):
            continue
        weight = weights[(r['task'],r['source_group_id'])] if weights else 1
        buckets[cell(r)].append((r[field] if field else r['R']-r['NF'], weight))
    if not buckets or (expected is not None and set(buckets) != set(expected)):
        return None
    return statistics.mean(sum(d*w for d,w in b)/sum(w for _,w in b) for b in buckets.values())


def quantile(xs, p):
    xs = sorted(xs)
    index = (len(xs)-1)*p
    lo = int(index)
    return xs[lo] + (xs[min(lo+1,len(xs)-1)]-xs[lo])*(index-lo)


def missingness_bounds(rows):
    cells = defaultdict(list)
    for r in rows:
        cells[cell(r)].append(r)
    result = {}
    for arm in ('R','NF'):
        lower, upper = [], []
        for rs in cells.values():
            s = sum(r.get(arm)==1 for r in rs)
            m = sum(r.get(arm) not in (0,1) for r in rs)
            lower.append(s/len(rs)); upper.append((s+m)/len(rs))
        result[arm] = dict(assigned=len(rows), missing=sum(r.get(arm) not in (0,1) for r in rows),
            bounds=[statistics.mean(lower),statistics.mean(upper)] if cells else [None,None])
    result['difference'] = [result['R']['bounds'][0]-result['NF']['bounds'][1],result['R']['bounds'][1]-result['NF']['bounds'][0]] if rows else [None,None]
    return result


def paired_analysis(rows, *, seed, repetitions=10000, planned_case_ids=None):
    if len({r['case_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate case outcomes')
    if planned_case_ids is not None and (len(planned_case_ids)!=len(rows) or set(planned_case_ids)!={r['case_id'] for r in rows}):
        raise ValueError('outcomes do not cover planned case IDs')
    if repetitions < 1:
        raise ValueError('positive bootstrap repetitions required')
    for r in rows:
        if any(r.get(a) not in (0,1,None) for a in ('R','NF')):
            raise ValueError('unresolved outcomes must be None, not sentinel scores')
    expected = set(map(cell,rows))
    valid = [r for r in rows if r.get('R') in (0,1) and r.get('NF') in (0,1)]
    sources = sorted({(r['task'],r['source_group_id']) for r in rows})
    estimate = macro(valid, expected=expected)
    rng = random.Random(seed)
    draws, source_draws = [], []
    if estimate is not None:
        # Pre-aggregate by cell/source so repeated attack rows do not become PRNG units.
        grouped = defaultdict(lambda:defaultdict(list))
        bysource = defaultdict(list)
        for r in valid:
            key = (r['task'], r['source_group_id'])
            d = r['R']-r['NF']
            grouped[cell(r)][key].append(d)
            bysource[key].append(d)
        aggregates = [[(key, sum(ds), len(ds)) for key,ds in g.items()] for _,g in sorted(grouped.items())]
        for _ in range(repetitions):
            weights = {g:rng.expovariate(1) for g in sources}
            draws.append(statistics.mean(sum(weights[g]*total for g,total,n in xs)/sum(weights[g]*n for g,total,n in xs) for xs in aggregates))
            taskmeans = []
            for task in sorted({g[0] for g in sources}):
                keys = [g for g in bysource if g[0]==task]
                taskmeans.append(sum(weights[g]*statistics.mean(bysource[g]) for g in keys)/sum(weights[g] for g in keys))
            source_draws.append(statistics.mean(taskmeans))
    families = sorted({r['attack_family'] for r in rows})
    family_effects = {f:macro([r for r in valid if r['attack_family']==f], expected={c for c in expected if c[1]==f}) for f in families}
    family_values = [x for x in family_effects.values() if x is not None]
    lofo = {f:macro([r for r in valid if r['attack_family']!=f], expected={c for c in expected if c[1]!=f}) for f in families}
    valid_cells = set(map(cell, valid))
    contingency = Counter(f"R{r['R']}_NF{r['NF']}" for r in valid)
    pair_status = Counter('both_valid' if r.get('R') in (0,1) and r.get('NF') in (0,1) else 'neither_valid' if r.get('R') is None and r.get('NF') is None else 'one_valid' for r in rows)
    return dict(estimate=estimate, ci95=[quantile(draws,.025),quantile(draws,.975)] if draws else None,
        R_macro=macro(valid,expected=expected,field='R'), NF_macro=macro(valid,expected=expected,field='NF'),
        assigned=len(rows), paired_cases=len(valid), source_clusters=len(sources), expected_cells=len(expected),
        absent_valid_cells=[list(c) for c in sorted(expected-valid_cells)], pair_status=dict(pair_status),
        contingency=dict(contingency), seed=seed, repetitions=repetitions,
        bootstrap='paired source-cluster Exponential(1) multiplier; equal fixed task/family/position cells',
        source_level_sensitivity_ci95=[quantile(source_draws,.025),quantile(source_draws,.975)] if source_draws else None,
        ci_first_half=[quantile(draws[:len(draws)//2],.025),quantile(draws[:len(draws)//2],.975)] if len(draws)>=2 else None,
        leave_one_family_out=lofo, family_effects=family_effects,
        family_dispersion=dict(families=len(family_values),range=[min(family_values),max(family_values)] if family_values else None,
            sd=statistics.stdev(family_values) if len(family_values)>1 else None,
            note='descriptive dispersion across fixed families; not a family-generalization CI'),
        missingness=missingness_bounds(rows), alpha=.05, two_way_sensitivity='not implemented; optional resource-dependent protocol sensitivity')


def simulate(cases, *, seed):
    rng = random.Random(seed)
    result = []
    sources = sorted({(c['task'],c['source_group_id']) for c in cases})
    source_effect = {s:rng.uniform(-.15,.15) for s in sources}
    for c in sorted(cases,key=lambda c:c['case_id']):
        if c['case_type']!='attacked':
            continue
        p = .5+source_effect[(c['task'],c['source_group_id'])]
        common = rng.random()
        nf, r = int(common < p), int(common < p-.05)
        result.append(dict(case_id=c['case_id'], task=c['task'], source_group_id=c['source_group_id'],
            attack_family=c['attack_family'], position=c['position'], R=None if rng.random()<.02 else r,
            NF=None if rng.random()<.02 else nf, provenance='SIMULATED-NOT-EXPERIMENTAL'))
    return result
