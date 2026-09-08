# What the portable commands verify

Run from the repository root with Python 3.10 or newer:

```sh
python3 verification/verify.py
```

This standard-library command reconstructs the geometry used by seven exact count trees, checks rational inequalities and exhaustive branches, checks retained physical tensor actions, and enumerates all 43,071 rank-two pairs. It verifies 9,683 nodes and 4,845 leaves. **Its conclusion is conditional on 110 explicit restricted-rank lower bounds. It does not prove those premises.** It prints `lower_bound_premises_replayed: false` on success.

The assumptions are readable in [PREMISES.md](../evidence/PREMISES.md), with their annihilator bases in [PREMISES.json](../evidence/PREMISES.json). These distinguish Wang's published bounds from strengthened bounds found in this campaign. Eleven strengthened restrictions occur in the complete dependency chain; some are intermediate rather than direct compact assumptions.

Commands print results and do not write reports unless `--output PATH` is supplied. They make no network requests. Do not use Python `-O`, which disables assertions; the entry point rejects it.

## Independent count arithmetic and failure controls

```sh
python3 verification/verify.py --mode independent-counts
python3 verification/verify.py --mode controls
```

The first rechecks all seven trees with a separately authored `fractions.Fraction` implementation. It checks integer assignments, propagation, state-preserving permutation witnesses, exhaustive branches and rational inequalities. This mode assumes its row geometry and physical symmetries; run the default mode for those checks. It does not prove any restricted-rank premise.

The second runs the positive compact proof and rejects missing or weakened premises, a missing actual tree branch, and an empty rational dual. These controls invoke mathematical checking in memory rather than merely triggering a file hash mismatch.

The default integer-LCM implementation and the Fraction implementation are separate local implementations of the same proof rules. The compact geometry checker was written in the campaign. This is not outside peer review or an independent mathematical discovery.

## Fresh published-certificate replay

```sh
python3 verification/verify.py --mode published --seconds 600
```

This optional command requires a C++17 compiler (`c++`, `clang++`, `g++`, or `CXX`). It requires no Python packages. It compiles the included native source into a temporary directory, starts an empty verification ledger, and replays all 496 entries of Wang's pinned public certificate. Compilation products are deleted on exit. The native kernel is single-threaded. The time limit applies to mathematical replay; compilation has a separate 60-second cap.

The packaged replay was tested locally: all 496 entries passed in approximately 36 seconds including compilation. This establishes the published lower bounds, including the published global bound 20. **It does not establish the eleven strengthened restrictions or turn the conditional compact result into a complete portable proof of 21.** The output explicitly reports `strengthened_restricted_premises_replayed: false` and `full_rank21_proof_replayed: false`.

The native checker is the campaign's previously audited implementation; packaging it does not provide another independently authored checker. The separate external Beuchert checker is not used: a bounded audit found that its unmodified backtracking traversal accepted incomplete payloads. This issue is not a rejection of Wang's certificate. The native implementation rejected equivalent empty and truncated controls.

## Remaining full-replay boundary

Review-critical inputs for all strengthened restrictions are in `evidence/restricted/` as gzip-compressed JSON:

- Index 70: its basis is in the published catalog; the campaign uses an explicit Koszul flattening of rank 27 to establish lower bound 14. A portable Koszul verifier is not yet included.
- Index 206: the 15 hyperplane witnesses and Koszul ranks used in the bound 15.
- Index 313: all 372 restriction rows and the seven-node interval-count proof for bound 17.
- Indices 423 and 444: six-dimensional geometry and exact count proofs for bounds 18.
- Indices 486, 487, 488, 490 and 491: seven-dimensional geometry and exact count proofs for bounds 19.
- Index 494: singleton capacities, reduced geometry, physical symmetries and the 169-node orbital tree for bound 20.

The missing release component is a portable executable that reconstructs and validates these upgraded geometries/Koszul maps, rechecks their exact trees, closes their dependencies against a freshly replayed published ledger, and binds the resulting bounds to the compact assumptions. Earlier local checks performed that work across campaign scripts; saved local pass reports are not substituted for this missing portable integration.

The compressed evidence omits historical status-ledger fields and machine-local provenance paths while preserving mathematical geometry and proof trees. Original and packaged SHA-256 hashes are recorded in `evidence/restricted/provenance.json`. Large discovery tables and unsuccessful search traces are unnecessary for the compact proof and are omitted. Hashes establish integrity and lineage, not mathematical validity.

No Linux/Windows compatibility run has yet been performed. The portable Python command has been relocated and tested on the local macOS environment; the native source uses standard C++17 and builds its library for the current platform.
