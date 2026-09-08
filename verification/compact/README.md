# Compact conditional global certificate

Run with Python 3.10 or newer, from any directory:

```sh
python3 /path/to/bundle/check.py
```

No package, native binary, LP solver, network request or original campaign directory is needed. The checker rejects Python's assertion-disabling `-O` mode. The command prints its result; optional `--output PATH` saves it.

**This checks a conditional global reduction, not the whole proof from scratch.** It assumes the 110 explicitly listed restricted tensor lower bounds in `payload.json.gz`. It checks their application to all seven global count trees, both direct pair cases, and exhaustive pair normalization. The premise proofs are not replayed by this bundle; `lower_bound_premises_replayed` is always false here. A successful output means: if all listed rank premises hold, then rank over F2 of 3×3 matrix multiplication is at least 21. The repository-level `verification/verify.py --mode full` establishes the premises before running this bundle.

The tensor is `T(A,B,C)=trace(ABC)` over F2; matrices use nine row-major bits. For each listed annihilator basis H, the assumed bound applies to T restricted in its first input to `K={A : parity(A&h)=0 for all h in H}`. A hypothetical 20-term decomposition can have at most `20-L(K)` first-factor forms in H, counting multiplicity. Hyperplane premises 492/493/494 imply all forms are distinct and rank-three forms are absent. Global premise 495 supplies the lower bound 20, so eliminating 20 proves the conditional lower bound 21.

Physical coefficient actions are `U -> L U R` or `U -> L U^t R`, with invertible L,R. For the first, input changes are `A -> L^t A R^t`, `B -> R^{-t} B`, `C -> C L^{-t}`. For the second they are `A -> R A^t L`, `B -> L^{-1} C^t`, `C -> B^t R^{-1}`. Matrix associativity, inverse cancellation and cyclic trace prove tensor preservation for every enumerated group element. In addition, every action retained by a row or branch is checked on all 81 first-factor coefficient pairings and 729 basis triples of the trace tensor. The complete group orbits cover all 43,071 distinct rank-two pairs; row subsets need not be symmetry closed because branches cover actual tensor decompositions.

Only 9,488 rows actually cited by a tree and 971 initial zero-propagation witnesses are retained. Original row IDs and source hashes preserve provenance. Rational weights, tree structure and branch witnesses are unchanged except exact reference renumbering. The seven trees contain 9,683 nodes and 4,845 leaves. No floating point enters this checker.

The integer-LCM count checker is adapted from the separately developed local `rounds/004/audits/global-two-marker/integer_tree.py`, with explicit initial selected variables added for the all-rank-one case. The new standalone geometry/composition checker was written in this experiment. This reuse is disclosed; it is not a claim of a newly independent mathematical proof. Original restricted certificates and methods remain attributable to their original authors. The bundle is a local verification artifact, not a publication or novelty determination.

`provenance.json` records original relative file names and hashes; those files are not required for replay. `manifest.json` binds all bundled executable/data files. Editing the manifest alone cannot make invalid geometry or arithmetic pass, but hashes are integrity records, not substitutes for verification.
