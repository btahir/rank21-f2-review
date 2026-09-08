# Verification entry point

From the repository root:

```sh
python3 verification/verify.py --mode full        # everything, ~70 s, needs a C++17 compiler
python3 verification/verify.py                    # conditional global step only, ~2 s
python3 verification/verify.py --mode restricted  # the eleven strengthened bounds, ~12 s
python3 verification/audit_controls.py            # mutation controls and dependency map
python3 verification/test_release.py              # relocation and privacy checks
```

`python3 verification/verify.py --help` lists every mode; [docs/VERIFICATION.md](../docs/VERIFICATION.md) explains
what each one establishes. Nothing here installs packages, uses the network, or writes files unless `--output PATH`
is given. Do not run with `-O`.

Layout: `compact/` primary global checker and payload; `restricted/` independent replay of the strengthened bounds
and a second global checker; `published/` replay of Wang's certificate format; `fraction_tree.py` separate tree checker.
