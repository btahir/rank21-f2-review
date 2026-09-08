# Start here for independent review

The purpose of review is to establish whether the proposed rank 21 lower bound follows, not to reproduce a positive status string. Please report concrete errors, missing premises, unsupported transitions and verification gaps before discussing significance.

## Target and boundaries

The target is exact bilinear tensor rank for3×3 matrix multiplication over F2. Additions and scalar linear maps are not counted as bilinear products. A bound here is not a bound on every arbitrary Boolean program or on border rank.

The portable compact theorem is conditional on110 specified restricted-rank premises. Their identities are mathematical: an annihilator subspace H given by nine-bit row-major matrices, and a proposed lower bound on the first-slot restriction to ann(H). Catalog numbers alone are not definitions. Distinguish published baseline bounds from the strengthened local bounds.

Read the paper, inspect the premise table and verifier implementation, and run the documented commands in a fresh checkout. Do not infer a full proof from a saved ledger or matching digest. State the code and inputs you independently implemented versus reused.

## Specific proof obligations

1. The trace pairing identifies this trilinear tensor with matrix multiplication. Restricting the first slot kills every first factor in H, counting repetitions before any binary reduction.
2. The global lower bound 20allows reduction to a minimal20-term decomposition. The hyperplane bounds imply multiplicity at most1; strengthened catalog 494 excludes invertible first forms. These statements are specific to the assumed length 20.
3. Left/right invertible actions and transpose actions genuinely preserve the tensor. Check the first-factor dual convention and the interchange of B/C in the transpose case.
4. Normalizations cover all rank-one forms, all rank-two forms, and every unordered pair of distinct rank-two forms. There are no unexamined symmetry classes.
5. Marker contributions are subtracted from each capacity before projecting variables. Initial zero propagation uses an actually saturated inequality and cannot delete a feasible first factor otherwise.
6. A branch covers both no selected orbit member and at least one selected member, with a valid witness for every member. The action must preserve the current selected/zero sets and fixed markers. A physical symmetry must map actual decompositions; any stronger claim about an arbitrary reduced binary relaxation needs a separate justification.
7. Every rational leaf uses nonnegative weights with positive denominators, valid variable bounds and a coefficient sum that dominates the target objective. Its exact upper bound is strictly smaller than the required count. No tolerance or floating-point output establishes infeasibility.
8. All seven global trees and both direct pair contradictions use true lower-bound premises. Review the full dependency argument separately from the global composition.
9. Every prerequisite checker covers all required branches and rejects exhausted/truncated proof data. An observed defect in an external checker makes this an actual concern, not a hypothetical test case.
10. Novelty depends on prior literature and attribution as well as correctness. Search for this precise field, format, rank notion and lower bound, including unpublished manuscripts if available.

## Suggested review output

Provide the checkout commit, runtime and environment, commands run, inputs hashed, and a list of independently established facts. For each concern give the file/line or mathematical step, a minimal counterexample when possible, and whether it invalidates the claim or only limits the evidence. End with one of: error found; conditional argument verified; prerequisites partially verified; full argument independently verified. Do not collapse these outcomes into a generic PASS.

Write new outputs to `reports/local/`. Original certificates and recorded evidence should remain unchanged. A reviewer agent can begin with: “Review this repository as a skeptical computational algebra referee. Prioritize soundness, prerequisite coverage and incorrect claims of independence. Do not modify certificates. Follow docs/REVIEW_GUIDE.md and report exact scope.”
