"""Second, independently written checker for the global reduction in ``verification/compact/payload.json.gz``.

It re-derives every geometric object itself (group orbits, pair coverage, transported annihilators, marker
subtraction, initial propagation, branch witnesses) and replays the seven trees with exact fractions.  It takes the
premise bounds it is allowed to assume as an explicit map so that a caller can bind them to established values.
"""
import time, json, gzip
from .core import ROOT, CATALOG, MUL, TR, INV, GL, mrank, span, independent, check_orbit_tree

def require(ok, why):
    if not ok:
        raise ValueError(why)

def run(allowed_bounds):
    """allowed_bounds: {catalog index: bound the caller has established}.  Every payload premise must be <= it."""
    t0 = time.perf_counter()
    P = json.loads(gzip.decompress((ROOT / 'verification/compact/payload.json.gz').read_bytes()))
    premises = {}
    for p in P['premises']:
        i, b = p['index'], p['assumed_lower_bound']
        require(independent(p['annihilator_basis']), 'dependent annihilator basis')
        H = span(p['annihilator_basis'])
        require(H == span(CATALOG[i]['constraints']), 'premise %d annihilator differs from the catalog' % i)
        require(b <= allowed_bounds[i], 'premise %d assumes %d but only %d is established' % (i, b, allowed_bounds[i]))
        premises[i] = (H, b)
    require(len(premises) == 110 and premises[495] == (frozenset({0}), 20), 'premise list mismatch')
    R = 20
    cache = {}
    def act(g):
        g = tuple(g)
        if g not in cache:
            L, Rm, t = g; require(L in INV and Rm in INV and t in (0, 1), 'action is not a tensor symmetry')
            cache[g] = [MUL[MUL[L][TR[u] if t else u]][Rm] for u in range(512)]
        return cache[g]
    r1 = [u for u in range(1, 512) if mrank(u) == 1]; r2 = [u for u in range(1, 512) if mrank(u) == 2]; r3 = [u for u in range(1, 512) if mrank(u) == 3]
    require((len(r1), len(r2), len(r3)) == (49, 294, 168), 'rank class sizes')
    for i, need in ((492, 19), (493, 19), (494, 20)):
        H, b = premises[i]; (u,) = [x for x in H if x]
        require(b >= need and mrank(u) == {492: 1, 493: 2, 494: 3}[i], 'singleton premise %d too weak' % i)
    reps = [(10, b) for b in (11, 12, 19, 20, 68, 96, 258)]
    orb = [set(), set(), set()]; porb = [set() for _ in reps]
    for t in (0, 1):
        for L in GL:
            for Rm in GL:
                im = lambda u: MUL[MUL[L][TR[u] if t else u]][Rm]
                orb[0].add(im(1)); orb[1].add(im(10)); orb[2].add(im(273))
                for k, (a, b) in enumerate(reps):
                    porb[k].add(tuple(sorted((im(a), im(b)))))
    require(orb == [set(r1), set(r2), set(r3)], 'rank classes are not single orbits')
    allpairs = {(a, b) for i, a in enumerate(r2) for b in r2[i + 1:]}
    cov = set()
    for o in porb:
        require(not (cov & o), 'pair orbits overlap'); cov |= o
    require(cov == allpairs and len(cov) == 43071, 'pair orbits do not cover all pairs')
    require(P['pair_representatives'] == [list(r) for r in reps], 'representatives mismatch')
    for d in P['direct_pairs']:
        H, b = premises[d['premise']]
        require(span(d['pair']) == H and b >= 19 and set(d['pair']) <= set(r2), 'direct pair case invalid')
    require([tuple(d['pair']) for d in P['direct_pairs']] == [(10, 68), (10, 96)], 'direct pairs mismatch')
    active = sorted(r1 + r2)
    def geometry(row, domain, markers):
        H, b = premises[row['premise']]; bu = row['bound_used']
        require(isinstance(bu, int) and 0 <= bu <= b, 'row uses a bound above its premise')
        for g in row['actions']:
            a = act(g); H = frozenset(a[u] for u in H)
        return [j for j, f in enumerate(domain) if f in H], R - bu - sum(f in H for f in markers)
    cases = []; total_nodes = 0; total_leaves = 0
    for case in P['cases']:
        name = case['name']; markers = case['markers']; domain = case['domain']; target = case['target']; sel = case['initial_selected']
        if name == 'rank1':
            require(markers == [] and domain == r1 and target == 20 and sel == [0] and domain[0] == 1, 'rank1 case setup')
        elif name == 'single-rank2':
            require(markers == [10] and domain == r1 and target == 19 and sel == [], 'single-rank2 case setup')
        else:
            k = int(name); require(k in (8, 9, 10, 11, 14) and list(markers) == list(reps[k - 8]) and target == 18 and sel == [], 'pair case setup')
            free = set(active) - set(markers)
            for row in case['initial_zero_rows']:
                sup, cap = geometry(row, active, [])
                S = {active[j] for j in sup}
                require(len(S & set(markers)) == cap and S & free, 'initial propagation on an unsaturated row')
                free -= S
            require(domain == sorted(free), 'initial domain mismatch')
        require(target == R - len(markers), 'target mismatch')
        supports = []; rhs = []
        for row in case['rows']:
            sup, cap = geometry(row, domain, markers); require(cap >= 0, 'negative capacity')
            supports.append(sup); rhs.append(cap)
        pos = {f: i for i, f in enumerate(domain)}
        perms = []
        for g in case['actions']:
            a = act(g)
            require({a[m] for m in markers} == set(markers) and {a[f] for f in domain} == set(domain), 'branch action moves markers or domain')
            perms.append([pos[a[f]] for f in domain])
        stats, _, _ = check_orbit_tree(case['tree'], supports, rhs, perms, len(domain), target, sel)
        require(stats['nodes'] == case['expected_nodes'] and stats['leaves'] == case['expected_leaves'], 'tree size mismatch')
        total_nodes += stats['nodes']; total_leaves += stats['leaves']
        cases.append(dict(name=name, domain=len(domain), rows=len(supports), actions=len(perms), **stats))
    require([c['name'] for c in P['cases']] == ['rank1', 'single-rank2', '8', '9', '10', '11', '14'], 'case list mismatch')
    return dict(passed=True, premises=len(premises), pair_coverage=len(cov), cases=cases, nodes=total_nodes, leaves=total_leaves,
                seconds=round(time.perf_counter() - t0, 2))
