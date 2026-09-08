# A candidate rank-21 lower bound for 3×3 matrix multiplication over F₂

**Research draft for independent review.** The proposed result is

$$
\operatorname{R}_{\mathbb F_2}(\langle3,3,3\rangle)\ge21.
$$

It would exclude every20-product bilinear algorithm for this format over the two-element field. It does not determine whether the exact rank is21, 22 or 23, construct a faster algorithm, or establish the same bound over other fields or for border rank.

The preceding literature baseline is Wang's lower bound 20 in [arXiv:2603.07280v11](https://arxiv.org/abs/2603.07280v11). This work builds on that author's restriction catalog and certificates. Correctness and priority of the proposed improvement remain subject to external review.

## What you can verify here

The compact certificate verifies the **conditional global reduction**: if the110 explicitly enumerated restricted-rank premises hold, then the rank is at least21. It checks all seven global proof trees, exact rational inequalities, physical symmetries, two direct pair contradictions, and exhaustive pair normalization.

**A successful compact replay does not verify the110 premises.** The earlier local campaign checked those through a larger dependency chain, with shared machinery for published prerequisites. This repository documents that boundary and provides review evidence; read [verification scope](docs/VERIFICATION.md) before interpreting any result. Saved reports and SHA256 manifests establish provenance and integrity, not mathematical validity.

```sh
python3 verification/verify.py
```

The default verifier uses the Python standard library and reports its scope explicitly. Run without `-O`. See [verification documentation](docs/VERIFICATION.md) for supplementary commands, inputs and coverage.

## Read the argument

- [Paper PDF](paper/main.pdf) and [LaTeX source](paper/main.tex).
- [Independent reviewer instructions](docs/REVIEW_GUIDE.md).
- [Claim and evidence boundaries](docs/CLAIM_STATUS.md).
- [Verification instructions](docs/VERIFICATION.md).
- [How to reconstruct the strengthened prerequisite proofs](docs/RESTRICTED_CHAIN.md).
- [Source and license notes](NOTICE.md).

To rebuild the paper with [Tectonic](https://tectonic-typesetting.github.io/):

```sh
python3 scripts/build_paper.py
```

The first build may fetch TeX resources. The build script keeps its cache and temporary files under ignored `.build/`, and writes `paper/main.pdf`. A standard LaTeX/BibTeX toolchain can also build the source.

## Proof outline

Assume a20-term decomposition of `T(A,B,C)=trace(ABC)`. If its first-factor forms lie in an annihilator subspace H, restricting A to the common kernel kills those terms. Lower bounds on the restricted tensor therefore impose integer counting inequalities. Strong hyperplane bounds force the20 forms to be distinct and singular.

Classify decompositions by whether they contain zero, one, or at least two rank-two first factors. Physical symmetries normalize the first two cases and divide all43,071unordered rank-two pairs into seven classes. Two pair classes contradict a restricted bound directly. Exact finite trees exclude the other five classes and the zero/one cases. Floating-point optimization was used for discovery; certificate replay uses exact arithmetic.

## Review status

Local runs checked7 global trees with 9,683 nodes and 4,845 leaves. A separate local set/Fraction checker and scalar geometry reconstruction agreed. The small package retains9,488 tree-used rows and971 initial propagation witnesses. These checks were conducted within the same LLM-assisted research workflow and are not external peer review.

An external checker considered during validation accepted truncated proofs. A separately corrected copy passed only a small genuine prefix; it is not relied upon as a full independent validation. Details and implications are in [claim status](docs/CLAIM_STATUS.md).

This repository is prepared for review, with author metadata pending confirmation. AI assistance contributed to search, code, checks and drafting; human authorship and responsibility must be finalized before a scholarly submission. No arXiv submission or external endorsement is implied.
