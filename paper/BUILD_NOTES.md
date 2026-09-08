# Paper build and review notes

The editable draft is `main.tex`, with `references.bib` and the generated `premises-table.tex`. `table-provenance.json` identifies the exact 110-premise source and the five rows stronger than the pinned published catalog. The table was checked row-by-row against that source.

From the repository root, use the documented build command:

```sh
python3 scripts/build_paper.py
```

The local build used Tectonic 0.17.0 and produced `paper/main.pdf` (11 pages). All overfull-box and undefined-reference errors were resolved. All pages were rendered with bundled Poppler; the full contact sheet and detailed reproduction, provenance, and appendix pages were visually inspected. Build intermediates and page renders are under the ignored `.build` directory.

The draft uses the neutral author `Review draft`, supplies no affiliation, and discloses substantial Codex assistance. Its theorem assumes all 110 enumerated restricted bounds. It distinguishes that portable implication from the broader campaign's reported complete local proof chain. Optional published-catalog replay does not close the strengthened-premise boundary.

Primary references were checked against Wang's arXiv version 11 (29 August 2026) and pinned source metadata. Theorem 1 of that version states the lower bound 20; the paper makes no guarantee of novelty or external acceptance.
