# What is claimed, observed and unfinished

## Mathematical target

Candidate full result: `rank_F2(<3,3,3>) >= 21`.

Portable verified implication: the110 listed restricted-rank premises imply that result. The paper states the conditional implication explicitly and distinguishes it from the larger local campaign's full proof claim.

The local strengthened restricted bounds have catalog indices and values:

| Index | Bound |
|---:|---:|
|70|14|
|206|15|
|313|17|
|423|18|
|444|18|
|486|19|
|487|19|
|488|19|
|490|19|
|491|19|
|494|20|

These are local improvements; they must not be attributed to Wang as already published results. The remaining premise values and underlying geometry draw on Wang's pinned catalog. Some improvements support others transitively rather than appearing directly in the final110premise list.

## Local verification history

The source campaign records fresh published-certificate replays, reconstruction of restricted improvements, independent local checks of finite geometry and exact count trees, and an aggregate integrity/composition check over179linked files. Its global seven-tree replay checked9,683nodes and 4,845 leaves. The compact package was subsequently checked with a separate set/Fraction tree implementation and scalar row reconstruction.

Those runs are local observations. The published prerequisite replays share a Python/native checker implementation. Multiple agents, code reviews and matching results do not establish external mathematical consensus or eliminate common assumptions.

Discovery used floating-point LP and symmetry-guided searches. The final global certificates use exact integer/rational arithmetic. Failed searches and large discovery tables are retained in the original lab; they are not all part of this review repository and are not required by the compact implication.

## External checker defect

A Beuchert standalone implementation obtained from Zenodo record 20752782 silently accepted exhausted backtracking leaf data. Local controls showed acceptance of an empty proof with an impossible claimed bound 1000, and acceptance of a genuine13-leaf proof with its last required leaf removed. A separate copy changed the exhausted-data return into rejection and then verified only published entries 0–8 from an empty rank map. The native checker used in the main campaign rejected equivalent malformed inputs.

This is evidence against using that unmodified external implementation as independent certification. It does not, by itself, refute Wang's mathematical certificate or validate every rule in the corrected checker. This repository does not rely on the unmodified external implementation as a full verification. The original external code is not redistributed here.

## Outstanding gates

- Complete independent verification of all prerequisite mathematics, including dependency resolution and branch coverage.
- Reproduction by a reviewer outside the original agent workflow.
- Confirmation of novelty and priority; the reviewed Wang v11 paper states20, but absence of another result from search is not proof of priority.
- Final human author metadata, license choices for original material and responsibility for the manuscript before scholarly submission.

No claim is made of exact rank 21, a bound over arbitrary fields, a border-rank result, an improved asymptotic exponent, faster practical multiplication, prize eligibility or revenue.
