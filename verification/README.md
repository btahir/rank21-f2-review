# Verification entry point

From the repository root:

```sh
python3 verification/verify.py
python3 verification/verify.py --mode independent-counts
python3 verification/verify.py --mode controls
python3 verification/verify.py --mode published --seconds 600
```

See [the exact verification boundary](../docs/VERIFICATION.md). Default mode is conditional on 110 premises. Published mode freshly verifies the original 496-entry certificate and needs a C++17 compiler. Neither command alone, nor their combination, replays the strengthened restricted premises.

No default report writes, network requests, Python packages, bundled binaries, or platform-specific paths are required. Add `--output PATH` to save a result. Source attribution and original hashes are in `../evidence/provenance.json`; the compact bundle preserves its own attribution and manifest.
