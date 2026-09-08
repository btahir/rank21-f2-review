# Reviewer guide

The purpose of review is to establish whether rank 21 follows, not to reproduce a success message. Report concrete
errors, missing premises, unsupported transitions and verification gaps before discussing significance.

## Where to start

1. Read [README.md](../README.md) for context and [CLAIM_STATUS.md](CLAIM_STATUS.md) for the exact boundary.
2. Read the paper: [paper/main.tex](../paper/main.tex). Sections 2 to 5 contain every mathematical step; the appendix
   lists the 110 premises with their annihilator bases.
3. Run `python3 verification/verify.py --mode full` in a fresh checkout and read
   [VERIFICATION.md](VERIFICATION.md) to see what each stage did and did not establish.
4. Read the checkers. The primary ones are `verification/compact/check.py` (150 lines) and
   `verification/restricted/chain.py` (170 lines). The [2026-09-07 audit](audits/2026-09-07-independent-audit.md)
   records one full pass through this process.

## Definitions to hold fixed

- The target is exact bilinear tensor rank of $\operatorname{tr}(ABC)$ over F₂ for $3\times3$ matrices. Additions and
  scalar maps are free. This is not border rank and not a bound over other fields.
- A premise is a mathematical object: an annihilator subspace $H$ of $3\times3$ matrices over F₂ (9-bit row-major
  encoding), and a lower bound on the rank of the tensor restricted, in its first input, to $\operatorname{ann}(H)$.
  Catalog indices are labels, not definitions.
- "Published" means Wang's pinned catalog value; "strengthened" means the campaign's higher value. Both are replayed
  by `--mode full`; neither is assumed from a saved flag.

## Proof obligations to check

1. The trace pairing identifies the tensor with $\langle3,3,3\rangle$. Restricting the first input to
   $\operatorname{ann}(H)$ kills exactly the terms whose first factor lies in $H$, counting repetitions.
2. The global bound 20 allows reduction to a minimal 20-term decomposition. The hyperplane premises give multiplicity
   at most 1; strengthened entry 494 excludes invertible first factors. Both statements are specific to length 20.
3. The coefficient actions $U\mapsto LUR$ and $U\mapsto LU^{\mathsf T}R$ are induced by symmetries of the tensor
   (the transpose case swaps the second and third inputs). Check the dual convention.
4. The normal forms cover all rank-one forms, all rank-two forms, and every unordered pair of distinct rank-two forms.
5. Marker contributions are subtracted before projecting; an initial zero propagation must cite a saturated row.
6. Every orbit branch has both children and a valid witness for every orbit member preserving selected, zero and marker
   sets. Witnesses act on actual decompositions; the retained row subset need not be symmetry closed.
7. Rational leaves: nonnegative weights, positive denominators, coefficient of every variable at least 1, exact upper
   bound strictly below the target. No floating point anywhere in acceptance.
8. Each strengthened bound is built only from bounds established before it (see the dependency map printed by
   `audit_controls.py`).
9. Wang's leaf rule: at a leaf, the chosen forms plus the child bound must reach the parent bound; the child is a
   strict restriction in the catalog; the orbit map is a symmetry. Term splitting makes "exactly $b-1$ terms with
   nonzero first factors" a safe assumption.
10. Priority depends on literature as well as correctness.

## Reporting

State the checkout commit, environment, commands run, and which code you implemented yourself versus reused. For each
concern give the file and line or the mathematical step, a minimal counterexample if possible, and whether it
invalidates the claim or only limits the evidence. End with exactly one of: *error found*, *conditional argument
verified*, *prerequisites partially verified*, *full argument independently verified*.

Write outputs under `reports/local/` (ignored by git) or, for a record meant to be kept, under `docs/audits/`.
Do not modify certificates or evidence files; put proposed fixes in separate commits and explain their effect on soundness.
