# Claim status

## The claim

$\mathrm{R}_{\mathbb F_2}(\langle 3,3,3\rangle) \ge 21$: no bilinear algorithm with 20 or fewer multiplications
computes the product of two 3×3 matrices over the two-element field.

Not claimed: the exact rank (21, 22 or 23 remain possible), any bound over other fields or for border rank, an improved
exponent of matrix multiplication, a faster practical algorithm, external acceptance, or priority.

## Structure of the evidence

| Layer | Content | Verified by |
|---|---|---|
| Wang's catalog | 496 restricted lower bounds with certificates, including the global bound 20 | Wang's published framework; replayed here by the campaign's C++ and Python checkers |
| Strengthened bounds | Eleven catalog entries raised by one: 70, 206, 313, 423, 444, 486, 487, 488, 490, 491, 494 | Campaign checkers (original), then the 2026-09-07 audit with independent code |
| Global reduction | 110 premises ⇒ rank ≥ 21, via 7 exact trees | Campaign checker, separate fraction replay, and the audit's independent checker |

The eleven strengthened values are local improvements and must not be attributed to Wang. Only nine are needed for the
theorem: 206 and 313 are verified but not used by any later step.

## Verification history

- Original campaign (2026): fresh published-certificate replays, construction of the strengthened bounds, local
  checks of geometry and trees, aggregate integrity check over 179 linked files. Discovery used floating-point LP and
  symmetry-guided search; all final certificates use exact integer or rational arithmetic.
- 2026-09-07 independent audit ([report](audits/2026-09-07-independent-audit.md)): every strengthened bound
  re-derived from the raw evidence with newly written code; the global reduction re-verified with an independently
  written checker that rejects 17 mutation controls; two documentation errors found and fixed; no mathematical error found.
  Its code now ships as `verification/restricted/` and runs inside `verify.py --mode full`.

Both the campaign and the audit were performed by LLM agents. Agreement between them rules out most implementation
bugs but is not human peer review.

## External checker note

A standalone checker for Wang's format obtained from Zenodo record 20752782 was found, during the campaign, to accept
exhausted backtracking data: it accepted an empty proof with a claimed bound of 1000 and a genuine 13-leaf proof with
its last leaf removed. The campaign's native checker rejected the same inputs. That code is not used or redistributed
here. The observation is evidence against relying on that implementation; it is not evidence against Wang's certificate.

## Outstanding gates

1. A checker for Wang's certificate format written outside this project, run against the pinned archive.
2. A formal proof of the counting layer (rows, trees, dual certificates) in a proof assistant.
3. Human mathematical review, ideally including the framework's author.
4. Novelty and priority: Wang's v11 (29 August 2026) and the upstream README state 20; a web search on 2026-09-07
   found no published 21. Absence of a search hit is not proof of priority.
5. Final author metadata on the paper before any submission (the repository itself is MIT licensed).
