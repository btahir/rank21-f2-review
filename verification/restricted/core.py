"""Standalone F2 / catalog / certificate-tree library for replaying the strengthened restricted bounds.

Written independently of ``verification/compact`` and ``verification/published`` during the 2026-09-07 audit.
It shares no code with those checkers.  Matrices over F2 are 9-bit integers, bit 3*i+j = entry (i,j);
the tensor is T(A,B,C) = tr(ABC).
"""
from pathlib import Path
from fractions import Fraction
import re, ast, struct, gzip, json

ROOT = Path(__file__).resolve().parents[2]

def mm(a, b):
    out = 0
    for i in range(3):
        for j in range(3):
            v = 0
            for k in range(3):
                v ^= ((a >> (3*i+k)) & 1) & ((b >> (3*k+j)) & 1)
            out |= v << (3*i+j)
    return out

MUL = [[mm(a, b) for b in range(512)] for a in range(512)]
TR = [sum(((a >> (3*i+j)) & 1) << (3*j+i) for i in range(3) for j in range(3)) for a in range(512)]
I3 = 273
GL = [a for a in range(512) if any(MUL[a][b] == I3 for b in range(512))]
INV = {a: next(b for b in range(512) if MUL[a][b] == I3 and MUL[b][a] == I3) for a in GL}
assert len(GL) == 168

def f2rank(vectors):
    piv = {}
    for x in vectors:
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    return len(piv)

def mrank(a):
    return f2rank([a & 7, (a >> 3) & 7, (a >> 6) & 7])

def span(vectors):
    s = {0}
    for x in vectors:
        s |= {y ^ x for y in s}
    return frozenset(s)

def independent(vectors):
    return f2rank(vectors) == len(vectors)

def parity(x):
    return bin(x).count('1') & 1

def kernel(constraints):
    """K = {A : <h,A> = 0 for all h in constraints}, returned as the whole subspace."""
    return frozenset(x for x in range(512) if all(parity(x & h) == 0 for h in constraints))

def act_space(space, L, R, t):
    """Image of a set of matrices under X -> L (X^T if t else X) R."""
    return frozenset(MUL[MUL[L][TR[x] if t else x]][R] for x in space)

def rref_basis(space):
    """Ordered basis: reduced row echelon form with the highest set bit as pivot, increasing pivot order."""
    piv = {}
    for x in sorted(space):
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    for j in sorted(piv):
        for k in sorted(piv):
            if k != j and piv[k] >> j & 1:
                piv[k] ^= piv[j]
    return [piv[j] for j in sorted(piv)]

# ---- pinned published catalog (own parser of the protobuf text dump) ----
def read_catalog():
    text = (ROOT / 'evidence/published/upstream-certificate.pb.txt').read_text()
    out = []
    for b in text.split('constrained_tensors {')[1:]:
        m = re.search(r'^\s*index: (\d+)', b, re.M)
        idx = int(m[1]) if m else 0
        q = re.search(r'^\s*constraints: ("(?:\\.|[^"\\])*")', b, re.M)
        raw = ast.literal_eval('b' + q[1]) if q else b''
        cons = tuple(struct.unpack('<' + 'H' * (len(raw) // 2), raw))
        m = re.search(r'^\s*rank_lower_bound: (\d+)', b, re.M)
        out.append(dict(index=idx, constraints=cons, bound=int(m[1]) if m else 0))
    if [r['index'] for r in out] != list(range(496)):
        raise ValueError('catalog must contain entries 0..495 in order')
    return out

CATALOG = read_catalog()
KERNELS = {i: kernel(r['constraints']) for i, r in enumerate(CATALOG)}
KERNEL_INDEX = {}
for _i, _k in KERNELS.items():
    if _k in KERNEL_INDEX:
        raise ValueError('duplicate catalog space')
    KERNEL_INDEX[_k] = _i
PUBLISHED = {i: r['bound'] for i, r in enumerate(CATALOG)}

def load(name):
    return json.loads(gzip.decompress((ROOT / 'evidence/restricted' / name).read_bytes()))

def coord_to_matrix(basis, x):
    m = 0
    for i, b in enumerate(basis):
        if x >> i & 1:
            m ^= b
    return m

def coord_kernel(basis, H):
    """K_H = { sum x_i B_i : parity(x & h) = 0 for all h in H } for coordinate-dual forms H."""
    d = len(basis)
    return frozenset(coord_to_matrix(basis, x) for x in range(1 << d) if all(parity(x & h) == 0 for h in H))

def find_catalog(space, witness=None):
    """Catalog index of a first-input subspace.  A witness (left, right, transpose) is tried under both the
    direct-right and inverse-right conventions; both are valid tensor symmetries.  The mapped subspace must equal a
    catalog space exactly.  Without a usable witness, the full 56,448-element group is searched."""
    if witness is not None:
        L, R, t = witness['left'], witness['right'], witness['transpose']
        if L not in INV or R not in INV or t not in (0, 1):
            raise ValueError('witness is not an invertible symmetry')
        for conv, RR in (('inverse', INV[R]), ('direct', R)):
            img = act_space(space, L, RR, t)
            if img in KERNEL_INDEX:
                return KERNEL_INDEX[img], conv
    for t in (0, 1):
        for L in GL:
            for R in GL:
                img = act_space(space, L, R, t)
                if img in KERNEL_INDEX:
                    return KERNEL_INDEX[img], 'search'
    raise ValueError('subspace is not in the catalog')

def koszul_bound(space):
    """Koszul flattening for a 3-dimensional first-input space: rank of the 27x27 map B* x A -> C x Lambda^2 A.
    A rank-one tensor contributes rank at most two, so R >= ceil(rank / 2)."""
    basis = []
    for x in sorted(space):
        if x and f2rank(basis + [x]) > len(basis):
            basis.append(x)
    if len(basis) != 3:
        raise ValueError('Koszul bound needs a 3-dimensional space')
    def trace(a):
        return ((a >> 0) ^ (a >> 4) ^ (a >> 8)) & 1
    T = [[[trace(MUL[MUL[basis[i]][1 << b]][1 << c]) for c in range(9)] for b in range(9)] for i in range(3)]
    rows = []
    for c in range(9):
        for (i, j) in ((0, 1), (0, 2), (1, 2)):
            v = 0
            for b in range(9):
                for s in range(3):
                    if ((s == i) * T[j][b][c]) ^ ((s == j) * T[i][b][c]):
                        v |= 1 << (3*b + s)
            rows.append(v)
    r = f2rank(rows)
    return r, (r + 1) // 2

def _weights(lst, limit):
    out = {}
    for (i, a, b) in lst:
        if not (all(isinstance(t, int) for t in (i, a, b)) and 0 <= i < limit and i not in out and a >= 0 and b > 0):
            raise ValueError('invalid dual weight')
        out[i] = Fraction(a, b)
    return out

def check_interval_tree(tree, supports, rhs, caps, target):
    """Refute integer multiplicity vectors c with 0 <= c_i <= caps_i, sum c_i = target, sum_{i in S_j} c_i <= rhs_j."""
    n = len(caps)
    stats = {'nodes': 0, 'leaves': 0, 'branch': 0, 'rational_bound': 0, 'lower_violation': 0}
    used = set()
    def walk(node, low, high):
        stats['nodes'] += 1
        kind = node['kind']
        if kind == 'branch':
            v, cut = node['variable'], node['cut']
            assert isinstance(v, int) and isinstance(cut, int) and 0 <= v < n
            assert low[v] <= cut < high[v], 'cut does not split the interval'
            stats['branch'] += 1
            h2 = list(high); h2[v] = cut
            walk(node['le'], low, h2)
            l2 = list(low); l2[v] = cut + 1
            walk(node['ge'], l2, high)
            return
        stats['leaves'] += 1
        stats[kind] += 1
        if kind == 'lower_violation':
            j = node['row']
            assert sum(low[i] for i in supports[j]) > rhs[j], 'lower violation is not real'
            used.add(j)
            return
        assert kind == 'rational_bound', kind
        y = _weights(node['rows'], len(supports)); z = _weights(node['upper'], n); w = _weights(node['lower'], n)
        coeff = [Fraction(0)] * n
        U = Fraction(0)
        for j, yj in y.items():
            for i in supports[j]:
                coeff[i] += yj
            U += yj * rhs[j]
            if yj:
                used.add(j)
        for i, zi in z.items():
            coeff[i] += zi; U += zi * high[i]
        for i, wi in w.items():
            coeff[i] -= wi; U -= wi * low[i]
        assert all(c >= 1 for c in coeff), 'dual coefficient below 1'
        tu = node['total_upper']
        assert U == Fraction(tu[0], tu[1]), 'total_upper mismatch'
        assert U < target, 'leaf does not refute the target'
    walk(tree, [0] * n, list(caps))
    return stats, used

def check_orbit_tree(tree, supports, rhs, perms, n, target, initial_selected=()):
    """Refute 0/1 vectors x with sum x_i = target and sum_{i in S_j} x_i <= rhs_j, using symmetry branches whose
    witnesses are permutations that fix the current selected/zero pattern."""
    stats = {'nodes': 0, 'leaves': 0, 'orbit_branch': 0, 'rational_bound': 0, 'violation': 0, 'capacity': 0, 'propagations': 0}
    used_rows = set(); used_perms = set()
    supports = [frozenset(s) for s in supports]
    def walk(node, state):
        stats['nodes'] += 1
        state = list(state)
        for j in node.get('propagation', []):
            S = supports[j]
            assert sum(state[i] == 1 for i in S) == rhs[j], 'propagation on an unsaturated row'
            free = [i for i in S if state[i] == -1]
            assert free, 'propagation without effect'
            for i in free:
                state[i] = 0
            used_rows.add(j); stats['propagations'] += 1
        kind = node['kind']
        if kind == 'orbit_branch':
            orbit = node['orbit']; rep = node['representative']
            assert isinstance(rep, int) and rep in orbit and len(set(orbit)) == len(orbit) and orbit
            assert all(isinstance(i, int) and 0 <= i < n and state[i] == -1 for i in orbit)
            wit = node['witnesses']
            assert sorted(p for p, g in wit) == sorted(orbit), 'witness list does not cover the orbit'
            for p, g in wit:
                perm = perms[g]
                assert perm[p] == rep, 'witness does not send the point to the representative'
                assert all(state[perm[i]] == state[i] for i in range(n)), 'witness does not preserve the state'
                used_perms.add(g)
            stats['orbit_branch'] += 1
            none = list(state)
            for i in orbit:
                none[i] = 0
            some = list(state); some[rep] = 1
            walk(node['none'], none); walk(node['some'], some)
            return
        stats['leaves'] += 1; stats[kind] += 1
        if kind == 'violation':
            j = node['row']
            assert sum(state[i] == 1 for i in supports[j]) > rhs[j]
            used_rows.add(j); return
        if kind == 'capacity':
            assert sum(v != 0 for v in state) < target; return
        assert kind == 'rational_bound', kind
        y = _weights(node['rows'], len(supports)); z = _weights(node['upper'], n); w = _weights(node['lower'], n)
        coeff = [Fraction(0)] * n; U = Fraction(0)
        for j, yj in y.items():
            for i in supports[j]:
                coeff[i] += yj
            U += yj * rhs[j]
            if yj:
                used_rows.add(j)
        for i, zi in z.items():
            coeff[i] += zi
            if state[i] != 0:
                U += zi
        for i, wi in w.items():
            coeff[i] -= wi
            if state[i] == 1:
                U -= wi
        assert all(c >= 1 for c in coeff), 'dual coefficient below 1'
        tu = node['total_upper']
        assert U == Fraction(tu[0], tu[1]), 'total_upper mismatch'
        assert U < target, 'leaf does not refute the target'
    state = [-1] * n
    for i in initial_selected:
        state[i] = 1
    walk(tree, state)
    return stats, used_rows, used_perms
