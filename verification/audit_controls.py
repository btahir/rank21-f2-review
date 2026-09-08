#!/usr/bin/env python3
"""Negative controls and dependency map for the restricted chain and the independent global checker.

Part 1 corrupts the global payload in seventeen ways and requires the independent checker to reject each.
Part 2 reports, for every strengthened bound, the smallest set of earlier upgrades it needs.
"""
from pathlib import Path
import copy, gzip, io, json, sys, contextlib
from itertools import combinations
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
from restricted import chain, global_check as gc, core

ALL = {70: 14, 206: 15, 313: 17, 423: 18, 444: 18, 486: 19, 487: 19, 488: 19, 490: 19, 491: 19, 494: 20}
EST = chain.established_bounds(core.PUBLISHED, ALL)

def mutations():
    payload = json.loads(gzip.decompress((P / 'compact/payload.json.gz').read_bytes()))
    def leaf(node):
        if isinstance(node, dict):
            if node.get('kind') == 'rational_bound':
                return node
            for v in node.values():
                r = leaf(v)
                if r is not None:
                    return r
    def prem(m, i):
        return next(x for x in m['premises'] if x['index'] == i)
    muts = {}
    def add(name, fn):
        m = copy.deepcopy(payload); fn(m); muts[name] = m
    add('drop premise 494', lambda m: m.__setitem__('premises', [x for x in m['premises'] if x['index'] != 494]))
    add('weaken 494 to published 19', lambda m: prem(m, 494).__setitem__('assumed_lower_bound', 19))
    add('weaken 486 to published 18', lambda m: prem(m, 486).__setitem__('assumed_lower_bound', 18))
    add('inflate 70 beyond what is established', lambda m: prem(m, 70).__setitem__('assumed_lower_bound', 15))
    add('row uses bound above its premise', lambda m: m['cases'][2]['rows'][0].__setitem__('bound_used', m['cases'][2]['rows'][0]['bound_used'] + 1))
    add('singular action matrix', lambda m: m['cases'][2]['rows'][5].__setitem__('actions', [[1, 273, 0]]))
    add('delete none-branch', lambda m: m['cases'][0]['tree'].__delitem__('none'))
    add('wrong witness action', lambda m: m['cases'][3]['tree']['witnesses'][0].__setitem__(1, (m['cases'][3]['tree']['witnesses'][0][1] + 1) % len(m['cases'][3]['actions'])))
    add('drop a dual row weight', lambda m: leaf(m['cases'][0]['tree']).__setitem__('rows', leaf(m['cases'][0]['tree'])['rows'][:-1]))
    add('misstate total_upper', lambda m: leaf(m['cases'][4]['tree']).__setitem__('total_upper', [leaf(m['cases'][4]['tree'])['total_upper'][0] + 1, leaf(m['cases'][4]['tree'])['total_upper'][1]]))
    add('drop an initial propagation', lambda m: m['cases'][2].__setitem__('initial_zero_rows', m['cases'][2]['initial_zero_rows'][:-1]))
    add('drop pair case 14', lambda m: m.__setitem__('cases', m['cases'][:-1]))
    add('direct pair cites weaker premise 485', lambda m: m['direct_pairs'][0].__setitem__('premise', 485))
    add('wrong target', lambda m: m['cases'][1].__setitem__('target', 18))
    add('wrong markers for case 8', lambda m: m['cases'][2].__setitem__('markers', [10, 12]))
    add('propagate an unsaturated row', lambda m: leaf(m['cases'][3]['tree']).__setitem__('propagation', leaf(m['cases'][3]['tree'])['propagation'] + [0]))
    add('rational leaf claims bound above target', lambda m: leaf(m['cases'][5]['tree']).__setitem__('total_upper', [99, 1]))
    results = {}
    for name, m in muts.items():
        blob = gzip.compress(json.dumps(m).encode())
        original = core.ROOT / 'verification/compact/payload.json.gz'
        # run the checker on the mutated payload without touching the file: monkeypatch the reader
        real = Path.read_bytes
        def fake(self, _blob=blob, _orig=original, _real=real):
            return _blob if self == _orig else _real(self)
        Path.read_bytes = fake
        try:
            gc.run(EST); results[name] = 'ACCEPTED'
        except (ValueError, AssertionError, KeyError, IndexError, TypeError) as e:
            results[name] = 'rejected'
        finally:
            Path.read_bytes = real
    return results

def dependency_map():
    def attempt(fn, up):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(chain.established_bounds(core.PUBLISHED, up))
            return True
        except (ValueError, AssertionError):
            return False
    def minimal(fn, candidates):
        if attempt(fn, {}):
            return 'published bounds only'
        for k in range(1, len(candidates) + 1):
            for sub in combinations(candidates, k):
                if attempt(fn, {i: ALL[i] for i in sub}):
                    return sorted(sub)
        return 'FAILS'
    out = {'70': 'published bounds only (own Koszul flattening)'}
    out['206'] = minimal(chain._hyperplanes_206, [70])
    cert = core.load('003-rebuild-five-dimensional__certificate.json.gz'); proof = core.load('003-rebuild-five-dimensional__count-proof.json.gz')
    out['313'] = minimal(lambda est: chain._interval(313, 16, cert['rows'], proof, est, parent_basis=cert['parent_basis']), [70, 206])
    for p in (423, 444):
        geo = core.load('004-six-dimensional__geometry-%d.json.gz' % p); pr = core.load('004-six-dimensional__six-count-proof-%d.json.gz' % p)
        out[str(p)] = minimal(lambda est, geo=geo, pr=pr, p=p: chain._interval(p, 17, geo['inequalities'], pr, est), [70, 206, 313])
    for p in (486, 487, 488, 490, 491):
        geo = core.load('006-seven-dimensional__geometry-%d.json.gz' % p); pr = core.load('006-seven-dimensional__seven-count-proof-%d.json.gz' % p)
        out[str(p)] = minimal(lambda est, geo=geo, pr=pr, p=p: chain._interval(p, 18, geo['inequalities'], pr, est), [70, 206, 313, 423, 444])
    out['494'] = minimal(chain._orbital_494, [70, 486, 487, 488, 490, 491])
    return out

if __name__ == '__main__':
    r = mutations()
    accepted = [k for k, v in r.items() if v == 'ACCEPTED']
    print(json.dumps({'mutation_controls': r, 'accepted': accepted}, indent=2))
    if accepted:
        raise SystemExit('independent global checker accepted a corrupted certificate')
    print(json.dumps({'minimal_upgrade_dependencies': dependency_map()}, indent=2))
