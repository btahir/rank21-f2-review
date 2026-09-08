"""Build the LaTeX review draft using an installed Tectonic executable."""
from pathlib import Path
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
engine = shutil.which('tectonic')
if not engine:
    raise SystemExit('Tectonic is required; install it separately, then rerun this script.')
build = ROOT / '.build' / 'paper'
build.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env['XDG_CACHE_HOME'] = str(ROOT / '.build' / 'cache')
subprocess.run([engine, '--untrusted', '--keep-logs', '--outdir', str(build),
                str(ROOT / 'paper' / 'main.tex')], cwd=ROOT / 'paper', env=env, check=True)
shutil.copyfile(build / 'main.pdf', ROOT / 'paper' / 'main.pdf')
print('Built paper/main.pdf')
