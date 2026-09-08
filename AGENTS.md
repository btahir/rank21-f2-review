# Independent review repository

This is a review draft for a candidate tensor-rank lower bound over F2. Prioritize finding errors over confirming the claim. Read README.md, docs/REVIEW_GUIDE.md, docs/VERIFICATION.md, and paper/main.tex.

The compact global certificate (`--mode compact`) is conditional on 110 explicitly listed restricted lower bounds; `--mode full` replays those premises. Never describe a compact run or a hash check as verifying the premises, and never describe any run as human peer review. Distinguish fresh computation, imported historical evidence, source-code review, independent implementation, external peer review, and literature/priority checks.

Preserve certificate bytes and evidence provenance. Write new results under reports/local/; do not overwrite recorded runs. Put proposed fixes in separate commits and document how they affect soundness. Do not change expected outputs merely to make a test pass.

Review all physical symmetry, orbit coverage, multiplicity, projection, exact arithmetic, dependency and branch-coverage obligations. The subset of proof-used inequalities need not itself be symmetry closed; any reliance on this fact must be justified for actual tensor decompositions.

No external messages, public visibility changes, preprint submissions or publication unless the user explicitly authorizes them. Keep answers concise. Do not attribute authorship or external endorsement to an LLM or an agent reviewer.
