#!/usr/bin/env python3
"""Verification entry point.  See docs/VERIFICATION.md for what each mode establishes.

  compact             conditional global reduction (assumes the 110 listed restricted bounds)      ~2 s
  independent-counts  second exact-arithmetic replay of the seven global trees                      ~2 s
  controls            malformed certificates must be rejected                                       ~10 s
  restricted          replay the eleven strengthened restricted bounds from evidence/restricted     ~20 s
  independent-global  second, independently written global checker bound to established premises   ~5 s
  published           fresh replay of Wang's 496-entry certificate (needs a C++17 compiler)         ~40 s
  full                published + restricted + global with premises bound to replayed values        ~70 s
"""
from pathlib import Path
import argparse, gzip, hashlib, importlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, time
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent; ROOT = P.parent
if not __debug__:
    raise RuntimeError('Run without -O: exact assertions are required.')

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m

def compact():
    for name, digest in json.loads((P / 'compact/manifest.json').read_text()).items():
        if Path(name).name != name:
            raise ValueError('invalid compact manifest name')
        if hashlib.sha256((P / 'compact' / name).read_bytes()).hexdigest() != digest:
            raise ValueError('compact manifest mismatch: ' + name)
    sys.path.insert(0, str(P / 'compact'))
    m = module(P / 'compact/check.py', 'compact_checker'); raw = (P / 'compact/payload.json.gz').read_bytes()
    expected = json.loads((P / 'compact/provenance.json').read_text())['payload_sha256']
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('payload hash mismatch')
    return m, json.loads(gzip.decompress(raw))

def restricted_package():
    if str(P) not in sys.path:
        sys.path.insert(0, str(P))
    return importlib.import_module('restricted.chain'), importlib.import_module('restricted.global_check')

def published(seconds):
    if seconds <= 0:
        raise ValueError('seconds must be positive')
    for item in json.loads((ROOT / 'evidence/provenance.json').read_text())['published_inputs']:
        raw = (ROOT / item['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('published input hash mismatch')
    sys.path.insert(0, str(P / 'published')); m = module(P / 'published/fast_verifier.py', 'portable_native')
    m.pc.ROOT = ROOT / 'evidence/published'
    compiler = os.environ.get('CXX') or shutil.which('c++') or shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        raise RuntimeError('Published replay requires a C++17 compiler; no package installation is performed.')
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='rank21-published-') as td:
        lib = Path(td) / ('checker.dylib' if sys.platform == 'darwin' else 'checker.so')
        cmd = [compiler, '-std=c++17', '-O3', '-shared', '-fPIC', str(P / 'published/native_checker.cpp'), '-o', str(lib)]
        subprocess.run(cmd, check=True, timeout=60, capture_output=True, text=True)
        m.LIBRARY_PATH = lib; v = m.Verifier(m.pc.read_catalog(), m.pc.read_archive(), total_seconds=seconds)
        for i in range(496):
            v.verify(i)
        return dict(passed=True, mode='published', published_entries_replayed=len(v.verified),
                    global_published_lower_bound=v.verified[495]['bound'], strengthened_restricted_premises_replayed=False,
                    full_rank21_proof_replayed=False, seconds=time.perf_counter() - started, ledger=list(v.verified.values()))

def counts(payload):
    m = module(P / 'fraction_tree.py', 'separate_fraction_checker'); out = []
    from functools import lru_cache
    @lru_cache(None)
    def action(g, x):
        L, R, t = g
        def mat(a, b):
            return sum(((sum(((a >> (3*i+k)) & 1) * ((b >> (3*k+j)) & 1) for k in range(3)) % 2) << (3*i+j)) for i in range(3) for j in range(3))
        if t:
            x = sum(((x >> (3*i+j)) & 1) << (3*j+i) for i in range(3) for j in range(3))
        return mat(mat(L, x), R)
    for c in payload['cases']:
        pos = {x: i for i, x in enumerate(c['domain'])}; perms = [[pos[action(tuple(g), x)] for x in c['domain']] for g in c['actions']]
        initial = [-1] * len(pos)
        for i in c['initial_selected']:
            initial[i] = 1
        r = m.check_tree(c['tree'], [x['support'] for x in c['rows']], [x['rhs'] for x in c['rows']], perms, len(pos), c['target'], initial)
        assert all(r['stats'][k] == c['expected_' + k] for k in ('nodes', 'leaves'))
        out.append({'case': c['name'], **r['stats']})
    return dict(passed=True, mode='independent-counts', cases=out, geometry_replayed=False, lower_bound_premises_replayed=False)

def controls():
    import copy
    m, p = compact(); positive = m.run(p); tests = {}
    for name in ('missing_premise', 'weakened_premise', 'missing_tree_branch', 'empty_leaf_dual'):
        bad = copy.deepcopy(p)
        if name == 'missing_premise':
            bad['premises'] = [x for x in bad['premises'] if x['index'] != 494]
        elif name == 'weakened_premise':
            next(x for x in bad['premises'] if x['index'] == 494)['assumed_lower_bound'] = 19
        elif name == 'missing_tree_branch':
            tree = bad['cases'][0]['tree']; key = next(k for k in ('none', 'some', 'zero', 'one', 'left', 'right') if k in tree); del tree[key]
        else:
            tree = bad['cases'][0]['tree']
            def leaf(x):
                if isinstance(x, dict):
                    if x.get('kind') == 'rational_bound':
                        return x
                    for v in x.values():
                        r = leaf(v)
                        if r is not None:
                            return r
                if isinstance(x, list):
                    for v in x:
                        r = leaf(v)
                        if r is not None:
                            return r
            target = leaf(tree)
            if target is None:
                raise ValueError('control needs actual rational leaf schema')
            target.update(rows=[], upper=[], lower=[], total_upper=[0, 1])
        try:
            m.run(bad)
        except (ValueError, KeyError, AssertionError, TypeError):
            tests[name] = 'rejected'
        else:
            raise AssertionError('malformed certificate accepted: ' + name)
    return dict(passed=True, mode='controls', controls=tests, positive_nodes=positive['nodes'], lower_bound_premises_replayed=False)

def catalog_bounds():
    chain, _ = restricted_package()
    return dict(chain.PUBLISHED)

def restricted(bounds=None, source='pinned catalog file (bounds not replayed in this mode)'):
    chain, _ = restricted_package()
    started = time.perf_counter()
    upgrades, details = chain.verify_chain(bounds or catalog_bounds())
    return dict(passed=True, mode='restricted', published_bounds_source=source, upgrades=upgrades, details=details,
                seconds=time.perf_counter() - started)

def independent_global(bounds=None, source='pinned catalog file plus replayed upgrades'):
    chain, gc = restricted_package()
    base = bounds or catalog_bounds()
    upgrades, _ = chain.verify_chain(base)
    r = gc.run(chain.established_bounds(base, upgrades))
    return dict(mode='independent-global', published_bounds_source=source, **r)

def full(seconds):
    started = time.perf_counter()
    pub = published(seconds)
    bounds = {e['index']: e['bound'] for e in pub['ledger']}
    if set(bounds) != set(range(496)) or bounds[495] != 20:
        raise ValueError('published replay did not establish all 496 entries')
    chain, gc = restricted_package()
    upgrades, details = chain.verify_chain(bounds)
    est = chain.established_bounds(bounds, upgrades)
    m, p = compact()
    for prem in p['premises']:
        if prem['assumed_lower_bound'] > est[prem['index']]:
            raise ValueError('compact premise %d is not established' % prem['index'])
        if chain.span(prem['annihilator_basis']) != chain.span(chain.core.CATALOG[prem["index"]]["constraints"]):
            raise ValueError('compact premise %d annihilator differs from the catalog' % prem['index'])
    primary = m.run(p)
    second = gc.run(est)
    return dict(passed=True, mode='full', claim='rank_F2(3x3 matrix multiplication) >= 21',
                published_entries_replayed=pub['published_entries_replayed'], global_published_lower_bound=bounds[495],
                strengthened_restricted_premises_replayed=True, upgrades=upgrades, lower_bound_premises_replayed=True,
                full_rank21_proof_replayed=True, compact_nodes=primary['nodes'], independent_global_nodes=second['nodes'],
                seconds=time.perf_counter() - started)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--mode', choices=['compact', 'independent-counts', 'controls', 'restricted', 'independent-global', 'published', 'full'], default='compact')
    ap.add_argument('--output', type=Path); ap.add_argument('--seconds', type=int, default=600); a = ap.parse_args()
    if a.mode == 'published':
        r = published(a.seconds)
    elif a.mode == 'full':
        r = full(a.seconds)
    elif a.mode == 'independent-counts':
        _, p = compact(); r = counts(p)
    elif a.mode == 'controls':
        r = controls()
    elif a.mode == 'restricted':
        r = restricted()
    elif a.mode == 'independent-global':
        r = independent_global()
    else:
        m, p = compact(); r = m.run(p)
    text = json.dumps(r, indent=2)
    if a.output:
        a.output.write_text(text + '\n')
    print(json.dumps({k: v for k, v in r.items() if k not in ('ledger', 'details')}, indent=2))

if __name__ == '__main__':
    main()
