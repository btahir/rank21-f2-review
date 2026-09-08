# Independent audit: R_F2(<3,3,3>) >= 21

Date: 7 September 2026. Checkout: commit 3c36724 (single commit). Environment: macOS (Darwin 25.6), Python 3.14.3, Apple clang.
Auditor: Claude (Fable 5.1), an LLM-performed review. The checkers were written from the paper's mathematical
statements without importing or copying repository verification code. They now live in `verification/restricted/`
(`core.py`, `chain.py`, `global_check.py`) and run inside `verify.py --mode full`; the mutation tests and dependency
map are `verification/audit_controls.py`.

## Verdict

**Full argument independently verified**, with one external reliance: the 496 published restricted-rank bounds in
Wang's pinned catalog (arXiv:2603.07280v11, commit 0ab0562f). I replayed those with the repository's bundled checker
(native C++ and, separately, pure Python) and hand-reviewed the soundness of its leaf rule, but did not write a third
implementation of Wang's `.btp` format.

The repository presents the theorem as *conditional* on 110 premises and explicitly says the eleven strengthened bounds
are not replayed by the portable command. This audit discharges that condition: every strengthened bound was
re-derived from the raw evidence in `evidence/restricted/` with independent code, and the global reduction was
re-verified with an independent checker. No error was found in the mathematics, the geometry, or the certificates.

## What was independently established

| Step | Claim | Evidence used | My check |
|---|---|---|---|
| 70 | R >= 14 (published 13) | catalog basis only | Own Koszul flattening: 27x27 matrix has F2-rank 27, so >= ceil(27/2)=14. Also scanned all dim-3 catalog spaces: 70 is the only one where Koszul beats the catalog. |
| 206 | R >= 15 (published 14) | 002-published-cone | Reconstructed all 15 hyperplanes of the 4-dim space, mapped each to its catalog orbit with the supplied witness, recomputed Koszul ranks; sum of bounds 198, 14r >= 198 gives r >= 15. Needs 70>=14 (two hyperplanes are in orbit 70). |
| 313 | R >= 17 (published 16) | 003-rebuild-five-dimensional | Reconstructed 372 rows from coordinate-dual bases, orbit maps and catalog bounds; caps from singleton rows; own interval-tree checker, 7 nodes / 4 leaves. Needs 70 and 206. |
| 423, 444 | R >= 18 (published 17) | 004-six-dimensional | 2,823 rows each reconstructed; trees 7/4 and 413/207 nodes/leaves. **Published bounds suffice** (no upgrade needed). |
| 486,487,488,490,491 | R >= 19 (published 18) | 006-seven-dimensional | 29,210 rows each; trees 13, 9, 31, 21, 1 nodes. Minimal upgrades needed: 486:{423}; 487:{423,444}; 488:{70,423,444}; 490:{70,444}; 491:{444}. |
| 494 | R >= 20 (published 19) | 007-eight-dimensional (5 files) | Derived the binary domain from 255 singleton restrictions (206 capacity-0 forms come from upgrades 487/488/490/491), reconstructed 47,884 rows on the 49 active forms, validated all 336 automorphisms of the 8-dim space and their induced form permutations (accepting a permutation only if induced by the map or its inverse), own orbit-tree checker: 169 nodes / 85 leaves. Needs 70, 487, 488, 490, 491 (not 486, 206, 313). |
| Global | 110 premises => R >= 21 | verification/compact/payload.json.gz | Own re-implementation: premise spans equal catalog constraints; own enumeration of the 56,448 coefficient maps gives the rank-1/rank-2/rank-3 orbits and the 7 pair orbits (441, 3528, 294, 7056, 3528, 14112, 14112) partitioning all 43,071 rank-two pairs; direct pair cases; row geometry with marker subtraction; initial propagations; branch witnesses preserving markers/domain/state; exact Fraction leaf duals. 9,683 nodes / 4,845 leaves, all seven cases refuted. |

Minimal strengthened chain actually required for the theorem: {70, 423, 444, 486, 487, 488, 490, 491, 494}.
Upgrades 206 and 313 are verified but not needed by any later step.

Hand-checked mathematics: trace-pairing identification with <3,3,3>; restriction-count inequality; distinctness and
exclusion of invertible first factors from hyperplane premises (over F2, span{U}={0,U}); tensor preservation for both
coefficient actions U->LUR and U->LU^TR (transpose case swaps B and C); orbit-branch coverage for actual decompositions
(Remark on row subsets not needing symmetry closure is correct); rational-leaf soundness; the WLOG "exactly r terms,
all first factors nonzero" step in both the interval trees (via minimality) and Wang's backtracking rule (via term splitting).

## Repository commands (fresh runs)

`verify.py` default: passed, 9,683 nodes, `lower_bound_premises_replayed: false`. `--mode independent-counts`: passed.
`--mode controls`: four malformed inputs rejected. `--mode published --seconds 600`: all 496 entries, bound 20 for
entry 495, 35.6 s. `test_release.py`: passed. Outputs saved alongside this report.

## Robustness of my checkers (mutation tests, `mutation_tests.py`)

17 corruptions of the global payload were tried: dropped/weakened/inflated premises, bound_used above premise, singular
action, deleted child branch, wrong witness, dropped dual weight, misstated total_upper, dropped initial propagation,
dropped case, weaker direct-pair premise, wrong target, wrong markers, propagation on unsaturated row. All rejected
except "remove one point and its witness from an orbit", which my checker accepts. That acceptance is correct: a
smaller orbit is still an exhaustive split, and the none-child is checked with the removed variable left free
(a strictly weaker state); the subtree still verified under that weaker state.

## Concerns (none invalidating)

1. External reliance on Wang's catalog. Both replay implementations shipped here come from the same campaign. The
   leaf rule (chosen forms + child bound >= parent bound, strict child restriction, orbit map inside the symmetry group,
   sorted enumeration of the first-factor multiset) is sound on inspection, and the term-splitting argument makes
   "exactly b-1 nonzero-first-factor terms" WLOG. A third-party checker of the `.btp` format would close this.
2. `docs/RESTRICTED_CHAIN.md` says the 206 evidence uses the direct-right convention. In fact 8 of its 15 witnesses
   match the catalog space only under inverse-right and 7 only under direct-right. Both are valid group elements, so
   nothing is unsound, but the specification is inaccurate; a strict reimplementation following the doc verbatim would
   fail on 8 hyperplanes. My checker accepts either convention and requires exact span equality.
3. The documented dependency chain ("eleven upgrades") overstates what is needed; see the minimal chain above.
4. Priority: arXiv:2603.07280 v11 (29 Aug 2026) and the upstream README state 20 for this format; a web search found
   no published 21. Absence of a search hit is not proof of priority. Laderman's 23 remains the upper bound.
5. This audit, like the campaign, was performed by an LLM; it is independent code and reasoning, not human peer review.

## Follow-up applied to the repository after this audit

- The restricted-chain replay and the independent global checker were integrated as `verify.py --mode restricted`,
  `--mode independent-global` and `--mode full`, so the unconditional result is reproducible with one command.
- The convention statement for the 206 evidence in `docs/RESTRICTED_CHAIN.md` was corrected, and the minimal
  dependency chain was documented.
- README and documentation were rewritten for readers without the campaign's context; typographic errors
  (missing spaces before numbers) were fixed throughout.
