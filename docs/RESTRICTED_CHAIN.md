# Reconstructing the strengthened restricted bounds

This document specifies how the eleven strengthened bounds are rebuilt from the evidence in `evidence/restricted/`.
It is implemented by `verification/restricted/chain.py` and runs as `python3 verification/verify.py --mode restricted`
(against the pinned catalog file) or inside `--mode full` (against a fresh replay of Wang's certificate). A reviewer
who wants a third implementation should follow this text, not the code.

Maintain a map of proved bounds, initially the 496 published values; extend it only after the following checks
succeed. Do not seed this map from any JSON `status`, ledger, `verified_bounds`, or claimed-result field.

## Coordinates and the common restriction check

A 3×3 matrix is an integer with row-major bit `3*i+j`. Matrix multiplication, transpose, Gaussian elimination and inner products are over F2. Catalog `constraints` are an annihilator basis. Its physical first-input space is the kernel of those linear forms. Derive an ordered basis by reduced row echelon elimination with the highest set bit as pivot, then list pivot rows in increasing pivot order. Check any supplied `parent_basis` against this independently derived basis.

For a parent basis `B=(B_0,...,B_(d-1))`, coordinate vector `x` represents the XOR of `B_i` for selected bits. Each row's coordinate-dual basis `H` specifies a smaller physical space:

```
K_H = { XOR_i x_i B_i : parity(x & h)=0 for every h in H }.
```

Enumerate at most `2^d` coordinate vectors to reconstruct it. Check independence and range of `H`, supplied `physical_basis`, and `kernel_basis` where present. The row's `orbit` identifies a catalog space. Require its left and right matrices to be invertible, and its transpose flag to be exactly 0 or 1. For the 313, six-dimensional, seven-dimensional and 494 evidence, verify equality of the entire mapped subspace under

```
X -> left * (transpose(X) if transpose else X) * inverse(right).
```

**Convention note.** The stored witnesses are not uniform: in the 206 evidence, eight of the fifteen hyperplane
witnesses match their catalog space only under `inverse(right)` and seven only under `right` directly. Both maps are
tensor symmetries, so either is acceptable; a checker should try both and require that the mapped subspace equals
the catalog space exactly. Compare spans, not basis lists. (Earlier versions of this document stated that the 206
evidence uses `right` directly; that was inaccurate.)

For hypothetical rank `r`, let `c_f` count nonzero first-factor forms `f` in parent coordinates. The valid inequality associated with `H` is

```
sum(c_f for nonzero f in span(H)) <= r - proved_bound(K_H).
```

This follows by restricting a decomposition to `K_H`: exactly the factors in `span(H)` vanish. Multiplicities are allowed until singleton inequalities prove otherwise. An exact rank-`r` decomposition has nonzero factors and sum `c_f=r`; eliminating that count proves a bound of `r+1`, provided the already established lower bound excludes smaller ranks.

## Evidence map and dependency order

All file names below are relative to `evidence/restricted/`; `.json.gz` means gzip-compressed JSON. `provenance.json` binds the packaged files to their original campaign inputs.

| Bound to establish | Included evidence | Required computation |
|---|---|---|
| 70 ≥ 14 | Catalog basis in `../published/upstream-certificate.pb.txt` | Explicit Koszul flattening below |
| 206 ≥ 15 | `002-published-cone__certificate.json.gz` | All 15 hyperplanes, orbit witnesses and Koszul ranks |
| 313 ≥ 17 | `003-rebuild-five-dimensional__certificate.json.gz`, `003-rebuild-five-dimensional__count-proof.json.gz` | 372 rows; 7-node, 4-leaf interval tree |
| 423, 444 ≥ 18 | `004-six-dimensional__geometry-{index}.json.gz`, `004-six-dimensional__six-count-proof-{index}.json.gz` | Reconstruct rows; interval trees at target 17, using published row bounds |
| 486, 487, 488, 490, 491 ≥ 19 | `006-seven-dimensional__geometry-{index}.json.gz`, `006-seven-dimensional__seven-count-proof-{index}.json.gz` | Reconstruct rows; interval trees at target 18, after the earlier upgrades |
| 494 ≥ 20 | Five `007-eight-dimensional__*.json.gz` files described below | Singleton capacities, physical symmetries, and binary orbital tree at target 19 |

Row bounds are the maximum of the freshly verified published bound and any upgrade already proved at that point in
the order above. Never use a later target's proposed bound circularly. Stored variable caps (`caps` / `root_caps`)
were computed from established bounds in the 313 and seven-dimensional files and from published bounds only in the
six-dimensional files; both are valid, and a tree that refutes the target with weaker rows also refutes it with
stronger ones.

Minimal dependencies actually used (computed by `verification/audit_controls.py`):

| Bound | Needs |
|---|---|
| 70 ≥ 14 | nothing (Koszul flattening) |
| 206 ≥ 15 | the Koszul rank 27 of two orbit-70 hyperplanes, computed inline (equivalent to 70 ≥ 14) |
| 313 ≥ 17 | 70, 206 |
| 423 ≥ 18, 444 ≥ 18 | nothing beyond published bounds |
| 486 ≥ 19 | 423 |
| 487 ≥ 19 | 423, 444 |
| 488 ≥ 19 | 70, 423, 444 |
| 490 ≥ 19 | 70, 444 |
| 491 ≥ 19 | 444 |
| 494 ≥ 20 | 70, 487, 488, 490, 491 |

The global step uses 70, 423, 486, 488 and 494 directly, so the theorem needs nine of the eleven upgrades; 206 and
313 are verified but unused.

## Koszul checks for 70 and 206

For an ordered basis of three physical matrices, form tensor slices `T_i[b,c]` from `trace(B_i * E_b * E_c)`, where `E_b,E_c` are the nine matrix units. Form the 27×27 matrix with rows `(c,(i,j))`, `i<j`, and columns `(b,s)`:

```
K[(c,(i,j)),(b,s)] = [s=i] T_j[b,c] + [s=j] T_i[b,c].
```

A rank-one tensor contributes rank at most two to this flattening, so the restricted tensor rank is at least `ceil(rank_F2(K)/2)`. For catalog 70 the exact matrix rank is 27. Check the rank-one exterior multiplication maps directly if desired: each of the seven nonzero three-bit vectors gives rank two.

For 206, reconstruct the parent basis and all 15 nonzero coordinate hyperplanes in its four-dimensional space. Check each mapped catalog space using the direct-right convention above. Recompute each 27×27 Koszul rank, and take the maximum of its Koszul bound and freshly proved catalog bound. The 15 lower bounds sum to 198. A nonzero first-factor linear form vanishes on exactly one of these hyperplanes and survives on the other 14, hence `14*r >= 198` and `r >= 15`. Require all 15 hyperplanes exactly once.

## Interval-count tree schema: 313, six and seven dimensions

There are `n=2^d-1` variables, indexed by form `f=i+1`. Derive every upper capacity from the corresponding singleton row; require one singleton for every nonzero form. Start with lower bounds zero and these upper capacities. Check the stored `caps` or `root_caps` against the derived values.

A `branch` has `variable`, `cut`, `le`, `ge`. Require `low[i] <= cut < high[i]`; recurse with `high[i]=cut` and `low[i]=cut+1` respectively. Both children are mandatory. A `lower_violation` is valid only when the sum of current lower bounds in the cited row strictly exceeds its right-hand side.

For `rational_bound`, `rows`, `upper`, `lower` contain triples `[index,numerator,denominator]`. Require distinct in-range indices, nonnegative numerators and positive denominators. With exact rational weights `y,z,w`, calculate

```
a_i = sum(y_j for rows j containing i) + z_i - w_i
U   = sum(y_j * rhs_j) + sum(z_i * high_i) - sum(w_i * low_i).
```

Require every `a_i >= 1`, `U` equal to the stored rational `total_upper`, and `U < r`. Recurse through the entire tree and compare observed node and leaf counts. No floating-point tolerance is permissible. The 313 target is 16; the six-dimensional target is 17; the seven-dimensional target is 18.

## Binary orbital proof for 494

1. `frontier-cut-final-494` contains all 255 singleton restrictions. Reconstruct each and its bound from previously closed premises. Their capacities must be 206 zeros and 49 ones, proving the binary domain rather than assuming it. Check `active_forms` against exactly those 49 surviving forms.
2. `reduced-geometry` contains the retained general inequalities and physical witnesses. Reconstruct their supports on the 49 active forms and their capacities at target 19. Match each `orbital-input.rows` entry to its witnessed row using `closure_key` and verify its exact support/rhs. The key is the coordinate-dual basis packed into successive eight-bit slots; it is an identifier, not proof of validity.
3. `symmetry-geometry-494` records physical maps `X -> L*(X or X^t)*R` with **direct right multiplication**. Require invertibility and preservation of the parent space. Reconstruct each basis image from its stored coordinate `columns`. Its induced dual map sends form `f` to the integer whose bit `i` is `parity(f & columns[i])`. Require the full recorded permutation and its restriction to `active_forms` to match `orbital-input.permutations`.
4. Check `orbital-proof` against this physically validated input with the included `verification/fraction_tree.py::check_tree`, starting with 49 unassigned variables and target 19. Expected size: 169 nodes, 85 leaves.

The count checker validates zero propagation only for saturated rows. At an `orbit_branch`, every listed point needs a permutation taking it to the representative and preserving the current zero/one/unassigned state. The `none` branch sets all listed points to zero; the `some` branch sets the representative to one. Both branches are necessary. No generic assumption that all equal-capacity variables are interchangeable is valid. Rational leaves use the same exact dual inequality as above with binary state bounds; capacity and row-violation leaves are checked directly.

Completeness of the original search tables or enumeration of every possible symmetry is not required for this proof. Every used inequality must be valid, every branch witness must preserve actual tensor decompositions, and the recorded branching must cover all remaining assignments. These are the obligations that matter.

## Final join

After all eleven upgrades have been proved, compare every compact premise's catalog index, annihilator span and
required bound against the newly constructed map, then run the global verifiers. The join must fail on any missing or
weaker premise. `verify.py --mode full` implements exactly this, and `audit_controls.py` checks that the independent
global checker rejects corrupted premises, actions, branches, witnesses and rational weights.
