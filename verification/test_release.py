"""Local relocation/privacy checks; writes no repository files by default."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys,tempfile,time
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;R=P.parent
if not __debug__:raise RuntimeError('Run without -O')
def main():
 started=time.perf_counter();files=[p for base in(P,R/'evidence')for p in base.rglob('*')if p.is_file()and '__pycache__'not in p.parts]
 for p in files:
  assert not p.is_symlink()and p.stat().st_size<90_000_000
  assert p.suffix not in ('.pyc','.dylib','.so','.o')
  if p.name.endswith('.json.gz'):raw=gzip.decompress(p.read_bytes())
  elif p.suffix in ('.md','.py','.json','.cpp','.txt'):raw=p.read_bytes()
  else:continue
  for bad in (b'/'+b'Users/',b'/'+b'home/',b'file'+b'://'):assert bad not in raw,(str(p),bad)
 with tempfile.TemporaryDirectory(prefix='rank21-release-relocation-')as td:
  dest=Path(td)
  shutil.copytree(P,dest/'verification',ignore=shutil.ignore_patterns('__pycache__'))
  shutil.copytree(R/'evidence',dest/'evidence',ignore=shutil.ignore_patterns('__pycache__'))
  run=subprocess.run([sys.executable,str(dest/'verification/verify.py')],cwd=dest.parent,capture_output=True,text=True,timeout=60,check=True)
  result=json.loads(run.stdout);assert result['passed']and result['nodes']==9683 and not result['lower_bound_premises_replayed']
  bad=subprocess.run([sys.executable,'-O',str(dest/'verification/verify.py')],cwd=dest.parent,capture_output=True,text=True,timeout=10)
  assert bad.returncode!=0 and 'without -O'in bad.stderr
  assert not list((dest/'verification').rglob('*.pyc'))
 print(json.dumps({'passed':True,'files_scanned':len(files),'relocated_compact_nodes':result['nodes'],'relocated_compact_seconds':result['seconds'],'optimized_mode_rejected':True,'no_cache_written':True,'seconds':time.perf_counter()-started},indent=2))
if __name__=='__main__':main()
