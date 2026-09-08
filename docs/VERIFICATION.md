# What each verification mode establishes

All commands run from the repository root with Python 3.10 or newer, use only the standard library, make no
network requests, and write nothing unless `--output PATH` is given. Python's `-O` flag disables the assertions the
checkers rely on; the entry point refuses to run under it.

```sh
python3 verification/verify.py --mode MODE
```

## The one-command proof

```sh
python3 verification/verify.py --mode full
```

Runs, in order:

1. **Published replay.** Compiles `verification/published/native_checker.cpp` into a temporary directory, starts an
   empty ledger, and verifies all 496 entries of Wang's pinned certificate. Every bound in the rest of the run comes
   from this ledger, not from the catalog text file.
2. **Restricted chain.** `verification/restricted/chain.py` re-derives the eleven strengthened bounds from
   `evidence/restricted/`, in dependency order, using only bounds already established at each step.
3. **Premise binding.** Every one of the 110 premises of the compact payload must be no stronger than the bound just
   established for the same catalog entry, and its annihilator must span the same subspace as the catalog constraints.
4. **Global reduction.** Both global checkers run: the campaign's `verification/compact/check.py` and the audit's
   `verification/restricted/global_check.py`.

A successful run prints `"full_rank21_proof_replayed": true`. Needs a C++17 compiler; about 70 seconds.

## Individual modes

| Mode | Establishes | Assumes | Needs |
|---|---|---|---|
| `compact` (default) | If the 110 listed restricted bounds hold, rank ≥ 21. Reconstructs row geometry, checks 3,427 physical actions on the tensor, enumerates all 43,071 rank-two pairs, replays 7 trees (9,683 nodes) | The 110 premises in `evidence/PREMISES.md` | Python |
| `restricted` | The eleven strengthened bounds: 70→14, 206→15, 313→17, 423→18, 444→18, 486–491→19, 494→20 | Wang's published bounds as printed in the pinned catalog file | Python |
| `independent-global` | Same theorem as `compact`, via the audit's independently written checker, with premises bound to catalog bounds plus the replayed upgrades | Catalog file bounds | Python |
| `independent-counts` | The seven global trees, replayed with `fraction_tree.py` (separate exact-arithmetic implementation) | Row geometry and symmetries from the payload | Python |
| `controls` | Four corrupted payloads are rejected by the compact checker | – | Python |
| `published` | All 496 catalog bounds, including the global bound 20 | – | C++17 |
| `full` | Rank ≥ 21 with nothing assumed beyond Wang's certificate archive | – | C++17 |

Two further scripts:

- `python3 verification/audit_controls.py` corrupts the global payload in 17 ways and requires the independent
  checker to reject each, then computes the minimal set of upgrades each strengthened bound needs.
- `python3 verification/test_release.py` copies `verification/` and `evidence/` to a temporary directory, reruns the
  default mode there, checks that `-O` is refused, and scans for machine-local paths.

## Independence of the implementations

| Component | Written by | Shares code with |
|---|---|---|
| `compact/check.py`, `compact/integer_tree.py` | the original campaign | nothing outside `compact/` |
| `fraction_tree.py` | the original campaign (a separate audit round) | nothing |
| `published/published_checker.py`, `published/native_checker.cpp` | the original campaign | each other (same rule set, two languages) |
| `restricted/core.py`, `restricted/chain.py`, `restricted/global_check.py` | the 2026-09-07 audit | nothing in the repository |

Two implementations agreeing on every certificate is strong evidence against checker bugs. It is not the same as an
outside party having implemented Wang's certificate format, which remains the largest open gap.

## Evidence files

`evidence/restricted/` holds gzip-compressed JSON: coordinate-dual bases, physical bases, orbit witnesses and exact
proof trees for each strengthened bound. Legacy status-ledger fields and machine paths were removed when packaging;
`evidence/restricted/provenance.json` records the original and packaged hashes. No checker reads a saved status field.
`docs/RESTRICTED_CHAIN.md` specifies the reconstruction rules that `restricted/chain.py` implements.

Hashes in `verification/RELEASE_MANIFEST.json` and the compact manifest establish integrity of a snapshot; they are
not mathematical evidence. Regenerate the release manifest after editing verification files:

```sh
python3 scripts/update_manifest.py
```

## Platforms

Tested on macOS (Apple clang, Python 3.14). The Python modes are pure standard library; the C++ source is standard
C++17 and builds a shared library for the current platform. Linux and Windows have not been exercised.
