# Multiplying 3×3 matrices over F₂ needs at least 21 multiplications

**Claim.** The bilinear tensor rank of 3×3 matrix multiplication over the two-element field is at least 21:

$$\operatorname{R}_{\mathbb F_2}(\langle 3,3,3\rangle) \ge 21 .$$

**Status.** Research draft. The complete argument is machine-checked by two independently written verifiers in this
repository, replayable from source in about a minute with only Python and a C++ compiler. It has not been peer
reviewed by a human mathematician, has not been submitted anywhere, and its novelty has not been formally established.
See [Claim status](docs/CLAIM_STATUS.md) for the exact boundary.

## The problem in plain language

Multiplying two 3×3 matrices the schoolbook way uses 27 scalar multiplications. Laderman (1976) showed that 23 suffice.
Nobody knows the true minimum. Lower bounds are hard: Bläser proved 19 in 2003, and the bound stood until 2026, when
Chengu Wang's automated framework raised it to 20 over the two-element field F₂
([arXiv:2603.07280](https://arxiv.org/abs/2603.07280)). This repository pushes it to 21 over F₂, which means no
20-multiplication method exists for that field. It says nothing about other fields, border rank, or faster algorithms.

## How the proof works

The argument is a proof by contradiction, driven entirely by counting.

1. **Assume a 20-step method exists.** Each step has a "first factor", a linear form on the input matrix A, which we
   encode as a 3×3 matrix over F₂.
2. **Borrow restriction facts.** Wang's catalog lists 496 subspaces of inputs together with proven minimum step counts
   when the method only has to work on that subspace. Each fact says: at most a certain number of first factors may lie in a
   given subspace. Eleven of these facts are strengthened here by one step each, with their own certificates.
3. **Force the shape.** The strongest facts imply that all 20 first factors are distinct, singular matrices.
4. **Split into cases by symmetry.** Using the symmetry group of the tensor, every configuration reduces to one of seven
   normal forms (no rank-2 factor, one rank-2 factor, or one of five kinds of rank-2 pair). Two further pair types
   contradict a restriction fact directly.
5. **Refute each case.** For each normal form, a branch-and-bound tree with exact rational dual certificates shows the
   counting constraints cannot be satisfied. Seven trees, 9,683 nodes in total, exclude every case.

Since Wang already excluded 19 or fewer steps, and this excludes exactly 20, the minimum is at least 21.
The full write-up is in [paper/main.pdf](paper/main.pdf) (source: [paper/main.tex](paper/main.tex)).

## Quick start

Requirements: Python 3.10 or newer (standard library only) and, for the two modes that replay Wang's certificate,
any C++17 compiler (`c++`, `clang++`, or `g++`). No packages, no network. Do not run Python with `-O`.

```sh
python3 verification/verify.py --mode full
```

That single command, about 70 seconds on a laptop, replays Wang's 496 published certificates from scratch, replays the
eleven strengthened restriction bounds from the raw evidence, checks that the global argument assumes nothing beyond
what was just established, and then runs both global checkers. On success it prints
`"full_rank21_proof_replayed": true`.

Every stage can also be run on its own:

| Command | What it establishes | Time |
|---|---|---|
| `verify.py` (default `compact`) | The conditional step: the 110 listed restriction bounds imply rank ≥ 21 | 2 s |
| `verify.py --mode restricted` | The eleven strengthened restriction bounds, from `evidence/restricted/` | 12 s |
| `verify.py --mode independent-global` | Same as compact, with a second independently written checker | 5 s |
| `verify.py --mode independent-counts` | Second exact-arithmetic replay of the seven global trees | 2 s |
| `verify.py --mode controls` | Corrupted certificates are rejected | 10 s |
| `verify.py --mode published` | Wang's 496-entry certificate, fresh replay (needs C++) | 40 s |
| `verify.py --mode full` | All of the above, joined so nothing is assumed | 70 s |
| `audit_controls.py` | 17 mutation tests of the independent checker, plus the minimal dependency map | 3 min |
| `test_release.py` | Relocation and privacy checks of the release itself | 5 s |

Details of what each mode does and does not prove are in [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Repository map

| Path | Contents |
|---|---|
| `paper/` | The paper (`main.tex`, `main.pdf`), bibliography, generated premise table, build notes |
| `docs/` | Claim status, verification scope, reviewer guide, restricted-chain specification, audits |
| `verification/verify.py` | Single entry point for all verification modes |
| `verification/compact/` | Primary global checker and its payload: 7 trees, 9,488 rows, 971 propagations |
| `verification/restricted/` | Independent replay of the eleven strengthened bounds and a second global checker |
| `verification/published/` | Replay of Wang's certificate format (Python reference and C++ kernel) |
| `verification/fraction_tree.py` | Separate exact-fraction tree checker used by `independent-counts` |
| `evidence/published/` | Wang's pinned catalog and certificate archive, unmodified, MIT licensed |
| `evidence/restricted/` | Raw geometry and proof trees for the eleven strengthened bounds |
| `evidence/PREMISES.md` | The 110 assumptions of the compact step, with published versus strengthened values |
| `scripts/` | Paper build and manifest regeneration |

## What has been verified, and by whom

- **Wang's catalog (496 bounds, including the global bound 20).** External prior work with public certificates.
  Replayed here by the campaign's C++ kernel and pure-Python reference implementation. No third-party implementation
  of the certificate format has been run against it yet.
- **The eleven strengthened bounds** (catalog entries 70, 206, 313, 423, 444, 486, 487, 488, 490, 491, 494).
  Proved by the original campaign and independently re-derived from the raw evidence in the
  [2026-09-07 audit](docs/audits/2026-09-07-independent-audit.md) with freshly written code. Only nine are needed;
  206 and 313 are verified but unused by later steps.
- **The global reduction.** Checked by the campaign's checker, by a separate fraction-arithmetic replay, and by the
  audit's independently written checker, which also survives 17 mutation controls.
- **Mathematical lemmas** (trace pairing, restriction counting, symmetry transport, branch coverage, dual soundness).
  Hand-checked in the audit; not formalized in a proof assistant.

## Remaining gaps before this should be called a theorem

1. A checker for Wang's certificate format written by someone outside this project.
2. A formal proof of the finite counting layer in a proof assistant such as Lean.
3. Review by a human mathematician, ideally including the framework's author.
4. A literature and priority check beyond web search.

## Attribution and disclosure

The restriction catalog, certificate format, and the lower bound 20 are Chengu Wang's work
([paper](https://arxiv.org/abs/2603.07280), [repository](https://github.com/wcgbg/tensor-rank-lower-bound),
pinned commit `0ab0562f`, MIT license preserved in `evidence/published/UPSTREAM_LICENSE`). Wang has not reviewed or
endorsed this work. The strengthened bounds, global certificates, and this write-up were produced in an LLM-assisted
research campaign, and the independent audit was also performed by an LLM. Author metadata and a license for the
original material are still to be assigned; see [NOTICE.md](NOTICE.md).

To rebuild the paper (requires [Tectonic](https://tectonic-typesetting.github.io/)):

```sh
python3 scripts/build_paper.py
```
