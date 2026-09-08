"""Independent finite-assignment checker: no producer imports, no solver calls."""
from fractions import Fraction
from collections import Counter

def fraction_weights(raw, size):
    ans = {}
    for term in raw:
        assert len(term) == 3
        idx, num, den = term
        assert all(type(x) is int for x in term)
        assert 0 <= idx < size and idx not in ans and num >= 0 and den > 0
        ans[idx] = Fraction(num, den)
    return ans

def binary_domain(caps):
    assert all(type(c) is int and c in (0, 1) for c in caps)
    return [i for i,c in enumerate(caps) if c]

def stabilizing_map(permutation, state, point, representative):
    n = len(state)
    assert len(permutation) == n and all(type(i) is int for i in permutation)
    assert set(permutation) == set(range(n))
    assert permutation[point] == representative
    assert all(state[permutation[i]] == state[i] for i in range(n))

def check_tree(tree, supports, limits, permutations, n, target, initial_state=None):
    """States are -1 (unassigned),0,1. Symmetries must be physically checked upstream."""
    supports = [frozenset(s) for s in supports]
    assert len(limits) == len(supports)
    assert all(s <= set(range(n)) for s in supports)
    assert all(type(v) is int and v >= 0 for v in limits)
    stats = Counter(); used = set(); used_perms = set(); leaf_bounds = []
    def walk(node, state):
        stats['nodes'] += 1
        state = list(state)
        for j in node['propagation']:
            assert type(j) is int and 0 <= j < len(supports)
            s = supports[j]
            assert sum(state[i] == 1 for i in s) == limits[j]
            free = [i for i in s if state[i] == -1]
            assert free
            for i in free: state[i] = 0
            used.add(j); stats['propagations'] += 1
        kind = node['kind']
        if kind == 'orbit_branch':
            orbit = node['orbit']; rep = node['representative']
            assert type(rep) is int and rep in orbit
            assert all(type(i) is int and 0 <= i < n and state[i] == -1 for i in orbit)
            assert len(orbit) == len(set(orbit)) and orbit
            witness = node['witnesses']
            assert len(witness) == len(orbit)
            assert sorted(t[0] for t in witness) == sorted(orbit)
            for point, g in witness:
                assert type(g) is int and 0 <= g < len(permutations)
                stabilizing_map(permutations[g], state, point, rep)
                used_perms.add(g)
            no = state[:]
            for i in orbit: no[i] = 0
            yes = state[:]; yes[rep] = 1
            stats['orbit_branches'] += 1
            walk(node['none'], no); walk(node['some'], yes)
            return
        stats['leaves'] += 1; stats[kind] += 1
        if kind == 'violation':
            j = node['row']; assert type(j) is int and 0 <= j < len(supports)
            assert sum(state[i] == 1 for i in supports[j]) > limits[j]
            used.add(j)
        elif kind == 'capacity':
            assert sum(v != 0 for v in state) < target
        else:
            assert kind == 'rational_bound'
            row = fraction_weights(node['rows'], len(supports))
            upper = fraction_weights(node['upper'], n)
            lower = fraction_weights(node['lower'], n)
            coeff = [upper.get(i, Fraction(0)) - lower.get(i, Fraction(0)) for i in range(n)]
            objective = sum(w*limits[j] for j,w in row.items())
            objective += sum(w for i,w in upper.items() if state[i] != 0)
            objective -= sum(w for i,w in lower.items() if state[i] == 1)
            for j,w in row.items():
                for i in supports[j]: coeff[i] += w
                if w: used.add(j)
            assert all(c >= 1 for c in coeff)
            raw = node['total_upper']
            assert len(raw) == 2 and all(type(v) is int for v in raw) and raw[1] > 0
            assert objective == Fraction(*raw) < target
            leaf_bounds.append([objective.numerator, objective.denominator])
    state = [-1]*n if initial_state is None else list(initial_state)
    assert len(state) == n and all(type(x) is int and x in (-1,0,1) for x in state)
    walk(tree, state)
    return dict(stats=stats, used_rows=sorted(used), used_permutations=sorted(used_perms), rational_upper_bounds=leaf_bounds)
