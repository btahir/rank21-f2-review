"""Regenerate verification/RELEASE_MANIFEST.json (byte counts and SHA-256 of verification and evidence files)."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
files = []
for base in ('docs/VERIFICATION.md', 'evidence', 'verification'):
    p = ROOT / base
    for f in ([p] if p.is_file() else sorted(p.rglob('*'))):
        if f.is_file() and '__pycache__' not in f.parts and f.name != 'RELEASE_MANIFEST.json':
            raw = f.read_bytes()
            files.append(dict(path=str(f.relative_to(ROOT)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
out = dict(scope='Integrity inventory for verification/evidence and verification documentation; hashes do not prove mathematical claims.', files=files)
(ROOT / 'verification/RELEASE_MANIFEST.json').write_text(json.dumps(out, indent=2) + '\n')
print('wrote manifest with %d files' % len(files))

# Also refresh the compact bundle's own manifest (documentation edits inside verification/compact change its hashes).
compact = ROOT / 'verification/compact/manifest.json'
m = json.loads(compact.read_text())
for name in m:
    m[name] = hashlib.sha256((compact.parent / name).read_bytes()).hexdigest()
compact.write_text(json.dumps(m, indent=2) + '\n')
print('refreshed compact manifest')
