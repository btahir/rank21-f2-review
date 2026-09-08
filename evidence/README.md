# Review evidence

- `published/`: Wang’s pinned 496-entry catalog and packed backtracking proofs, unchanged, with its MIT license. The optional published command replays them from an empty ledger.
- `restricted/`: compressed JSON geometry and exact trees for the strengthened restrictions. These preserve mathematical data but omit old status-ledger and machine-local provenance metadata. `restricted/provenance.json` records original and packaged hashes.
- `PREMISES.md` and `PREMISES.json`: explicit compact assumptions and their relationship to published bounds and eleven campaign upgrades.

The restricted artifacts are replayed by `python3 verification/verify.py --mode restricted` (and inside `--mode full`); the default compact mode does not read them. No saved result flag establishes a bound. Large global discovery tables are omitted: the compact payload retains actual proof-used rows, physical witnesses, initial propagation and all seven exact trees.
