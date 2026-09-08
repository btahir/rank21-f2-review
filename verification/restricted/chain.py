"""Replay of the strengthened restricted-rank bounds from the evidence in ``evidence/restricted``.

``verify_chain(bounds)`` takes a map catalog index -> established lower bound (from a fresh replay of Wang's
certificate, or from the pinned catalog file) and returns the upgrades it proves, in dependency order:

    70 -> 14 (Koszul flattening), 206 -> 15 (hyperplane averaging), 313 -> 17, 423 -> 18, 444 -> 18,
    486/487/488/490/491 -> 19 (interval-count trees), 494 -> 20 (binary orbital tree).

Only bounds already established are ever used to build a row.  A saved status flag is never read.
"""
import time
from . import core
from .core import (KERNELS, PUBLISHED, load, span, independent, coord_kernel, coord_to_matrix, find_catalog,
                   koszul_bound, rref_basis, act_space, parity, INV, MUL, TR, check_interval_tree, check_orbit_tree)

def require(ok, why):
    if not ok:
        raise ValueError(why)

def _koszul_70(est):
    r, lb = koszul_bound(KERNELS[70])
    require(r == 27 and lb == 14, 'Koszul rank for catalog 70 is not 27')
    return dict(index=70, bound=14, method='koszul flattening', koszul_rank=r)

def _hyperplanes_206(est):
    cert = load('002-published-cone__certificate.json.gz')
    require(cert['catalog_index'] == 206, 'wrong certificate')
    K = KERNELS[206]; basis = cert['physical_parent_basis']
    require(independent(basis) and span(basis) == K and len(basis) == 4, 'parent basis does not span catalog 206')
    total = 0; seen = set(); rows = []
    for h in cert['hyperplanes']:
        f = h['form']; require(1 <= f <= 15 and f not in seen, 'bad hyperplane form'); seen.add(f)
        Kf = coord_kernel(basis, [f]); require(len(Kf) == 8 and span(h['physical_basis']) == Kf, 'hyperplane mismatch')
        _, kb = koszul_bound(Kf)
        idx, conv = find_catalog(Kf, h['orbit'])
        L = max(kb, est[idx]); total += L; rows.append((f, idx, conv, kb, est[idx], L))
    require(seen == set(range(1, 16)), 'all 15 hyperplanes are required exactly once')
    # A nonzero first factor u in K* vanishes on exactly one hyperplane (ker u), so 14 r >= sum of the 15 bounds.
    bound = -(-total // 14)
    require(bound >= 15, 'hyperplane sum too small: %d' % total)
    return dict(index=206, bound=bound, method='hyperplane averaging', hyperplane_bound_sum=total, hyperplanes=rows)

def _interval(parent, target, rows, tree_file, est, parent_basis=None, base=None):
    """Replay one interval-count tree.  Row capacities use ``est`` (every bound established so far).  The stored
    variable caps must equal the caps derived from ``est`` or from ``base`` (the published bounds alone); both are
    valid, and a tree that refutes the target under weaker rows also refutes it under stronger ones."""
    t0 = time.perf_counter()
    K = KERNELS[parent]; d = len(K).bit_length() - 1
    basis = parent_basis or rref_basis(K)
    require(independent(basis) and span(basis) == K and len(basis) == d, 'parent basis mismatch')
    n = (1 << d) - 1
    supports = []; rhs = []; singles = {}; singles_base = {}; used_bounds = {}
    for j, row in enumerate(rows):
        H = row['H']; require(all(isinstance(h, int) and 0 < h <= n for h in H) and independent(H), 'bad H')
        KH = coord_kernel(basis, H)
        if 'physical_basis' in row:
            require(span(row['physical_basis']) == KH, 'physical basis mismatch in row %d' % j)
        orbit = row['orbit']; claimed = orbit.get('catalog', orbit.get('index'))
        idx, conv = find_catalog(KH, orbit); require(idx == claimed, 'orbit mismatch in row %d' % j)
        b = est[idx]; used_bounds[j] = (idx, b)
        sup = sorted(f - 1 for f in span(H) if f)
        if 'forms' in row:
            require(sorted(x - 1 for x in row['forms']) == sup, 'support mismatch in row %d' % j)
        supports.append(sup); rhs.append(target - b); require(rhs[-1] >= 0, 'row already infeasible')
        if len(H) == 1:
            singles[H[0]] = rhs[-1]; singles_base[H[0]] = target - (base or PUBLISHED)[idx]
    require(set(singles) == set(range(1, n + 1)), 'a singleton restriction is missing')
    caps_est = [singles[f] for f in range(1, n + 1)]; caps_base = [singles_base[f] for f in range(1, n + 1)]
    caps = tree_file.get('root_caps', tree_file.get('caps'))
    require(caps == caps_est or caps == caps_base, 'stored caps match neither established nor published bounds')
    caps_source = 'established bounds' if caps == caps_est else 'published bounds only'
    stats, used = check_interval_tree(tree_file['tree'], supports, rhs, caps, target)
    require(stats['nodes'] == tree_file['nodes'] and stats['leaves'] == tree_file['leaves'], 'tree size mismatch')
    upgrades_used = sorted({used_bounds[j][0] for j in used if used_bounds[j][1] > PUBLISHED[used_bounds[j][0]]})
    return dict(index=parent, bound=target + 1, method='interval-count tree', rows=len(rows), nodes=stats['nodes'],
                leaves=stats['leaves'], caps_source=caps_source, upgraded_entries_cited_by_leaves=upgrades_used,
                seconds=round(time.perf_counter() - t0, 2))

def _orbital_494(est):
    t0 = time.perf_counter(); TARGET = 19
    require(est[494] == 19, 'catalog 494 must be established at 19 first')
    K = KERNELS[494]; require(len(K) == 256, 'bad parent')
    red = load('007-eight-dimensional__reduced-geometry.json.gz'); fr = load('007-eight-dimensional__frontier-cut-final-494.json.gz')
    sym = load('007-eight-dimensional__symmetry-geometry-494.json.gz'); oin = load('007-eight-dimensional__orbital-input.json.gz')
    proof = load('007-eight-dimensional__orbital-proof.json.gz')
    basis = red['parent_basis']; require(independent(basis) and span(basis) == K and len(basis) == 8, 'parent basis mismatch')
    coord = {coord_to_matrix(basis, x): x for x in range(256)}
    caps = {}; seen = set()
    for row in fr['inequalities']:
        (f,) = row['H']; require(f not in seen, 'duplicate singleton'); seen.add(f)
        Kf = coord_kernel(basis, [f]); require(span(row['physical_basis']) == Kf, 'singleton basis mismatch')
        idx, _ = find_catalog(Kf, row['orbit']); require(idx == row['orbit']['index'], 'singleton orbit mismatch')
        caps[f] = TARGET - est[idx]
    require(seen == set(range(1, 256)) and all(c in (0, 1) for c in caps.values()), 'domain is not binary')
    active = sorted(f for f in caps if caps[f] == 1)
    require(active == red['active_forms'] == oin['active_forms'], 'active forms mismatch')
    pos = {f: i for i, f in enumerate(active)}
    rows = red['rows']; require(len(rows) == len(oin['rows']), 'row count mismatch')
    supports = []; rhs = []
    for j, (row, orow) in enumerate(zip(rows, oin['rows'])):
        require(row['closure_key'] == orow['closure_key'], 'row alignment mismatch')
        H = row['H']; require(independent(H) and all(0 < h < 256 for h in H), 'bad H')
        KH = coord_kernel(basis, H)
        if 'physical_basis' in row:
            require(span(row['physical_basis']) == KH, 'physical basis mismatch')
        idx, _ = find_catalog(KH, row['orbit']); require(idx == row['orbit']['index'], 'orbit mismatch')
        sup = sorted(pos[f] for f in span(H) if f in pos)
        supports.append(sup); rhs.append(TARGET - est[idx]); require(rhs[-1] >= 0, 'row already infeasible')
    perms = []
    for k, a in enumerate(sym['automorphisms']):
        L, R, t = a['left'], a['right'], a['transpose']; require(L in INV and R in INV and t in (0, 1), 'bad automorphism')
        RR = next((RR for RR in (R, INV[R]) if act_space(K, L, RR, t) == K), None)
        require(RR is not None, 'map does not preserve the parent space')
        cols = [coord[MUL[MUL[L][TR[B] if t else B]][RR]] for B in basis]
        sigma = [sum(parity(f & cols[i]) << i for i in range(8)) for f in range(256)]
        inv_sigma = [0] * 256
        for f in range(256):
            inv_sigma[sigma[f]] = f
        filep = a['permutation']
        require(filep == sigma or filep == inv_sigma, 'stored permutation is not induced by the map or its inverse')
        require(all(filep[f] in pos for f in active), 'permutation does not preserve the active forms')
        p49 = [pos[filep[f]] for f in active]
        require(p49 == oin['permutations'][k], 'restricted permutation mismatch')
        perms.append(p49)
    stats, used_rows, _ = check_orbit_tree(proof['tree'], supports, rhs, perms, len(active), TARGET)
    require(stats['nodes'] == proof['nodes'] and stats['leaves'] == proof['leaves'], 'tree size mismatch')
    return dict(index=494, bound=20, method='binary orbital tree', active_forms=len(active), rows=len(rows),
                automorphisms=len(perms), nodes=stats['nodes'], leaves=stats['leaves'], seconds=round(time.perf_counter() - t0, 2))

def verify_chain(bounds):
    """bounds: {catalog index: established lower bound}.  Returns (upgrades, details)."""
    est = dict(bounds); base = dict(bounds)
    require(set(est) == set(range(496)), 'need a bound for every catalog entry')
    details = []
    def close(result):
        i, b = result['index'], result['bound']
        require(b > est[i], 'no strengthening for %d' % i)
        est[i] = b; details.append(result)
    close(_koszul_70(est))
    close(_hyperplanes_206(est))
    cert = load('003-rebuild-five-dimensional__certificate.json.gz'); proof = load('003-rebuild-five-dimensional__count-proof.json.gz')
    require(proof['parent'] == 313 and proof['assumed_rank'] == est[313] == 16 and cert['tree'] == proof['tree'], '313 evidence mismatch')
    close(_interval(313, 16, cert['rows'], proof, est, parent_basis=cert['parent_basis'], base=base))
    for p in (423, 444):
        geo = load('004-six-dimensional__geometry-%d.json.gz' % p); proof = load('004-six-dimensional__six-count-proof-%d.json.gz' % p)
        require(geo['parent'] == p == proof['parent'] and geo['rank'] == 17 == proof['assumed_rank'] == est[p], '%d evidence mismatch' % p)
        close(_interval(p, 17, geo['inequalities'], proof, est, base=base))
    for p in (486, 487, 488, 490, 491):
        geo = load('006-seven-dimensional__geometry-%d.json.gz' % p); proof = load('006-seven-dimensional__seven-count-proof-%d.json.gz' % p)
        require(geo['parent'] == p == proof['parent'] and geo['rank'] == 18 == proof['assumed_rank'] == est[p], '%d evidence mismatch' % p)
        close(_interval(p, 18, geo['inequalities'], proof, est, base=base))
    close(_orbital_494(est))
    upgrades = {d['index']: d['bound'] for d in details}
    require(upgrades == {70: 14, 206: 15, 313: 17, 423: 18, 444: 18, 486: 19, 487: 19, 488: 19, 490: 19, 491: 19, 494: 20}, 'unexpected upgrade set')
    return upgrades, details

def established_bounds(published, upgrades):
    return {i: max(published[i], upgrades.get(i, 0)) for i in range(496)}
