"""Relocatable conditional global certificate checker: Python standard library only.

The enumerated restricted-rank premises are INPUT ASSUMPTIONS, not proved here.
"""
from pathlib import Path
from functools import lru_cache
import gzip,json,hashlib,time,argparse
from integer_tree import verify
if not __debug__:raise RuntimeError("Run without -O: exact assertions are required")
P=Path(__file__).resolve().parent

def require(ok,why='invalid certificate'):
 if not ok:raise ValueError(why)
def span(basis):
 s={0}
 for x in basis:
  require(type(x)is int and 0<x<512 and x not in s,'dependent/out-of-range basis');s|={y^x for y in tuple(s)}
 return frozenset(s)
def rank(x):return (len(span_independent([x&7,x>>3&7,x>>6&7])).bit_length()-1)
def span_independent(basis):
 s={0}
 for x in basis:s|={y^x for y in tuple(s)}
 return s
def mat(a,b):
 out=0
 for i in range(3):
  row=(a>>(3*i))&7;v=0
  for k in range(3):
   if row>>k&1:v^=(b>>(3*k))&7
  out|=v<<(3*i)
 return out
def trans(a):return sum(((a>>(3*i+j))&1)<<(3*j+i)for i in range(3)for j in range(3))
def run(payload):
 started=time.perf_counter();require(payload['format']==1)
 gl=[a for a in range(512)if rank(a)==3];require(len(gl)==168)
 mult=[[mat(a,b)for b in range(512)]for a in range(512)];tr=[trans(x)for x in range(512)]
 inverse={a:next(b for b in gl if mult[a][b]==mult[b][a]==273)for a in gl}
 active=[a for a in range(1,512)if rank(a)<3];r1=[a for a in active if rank(a)==1];r2=[a for a in active if rank(a)==2]
 require((len(r1),len(r2),len(active))==(49,294,343))
 premises={}
 for p in payload['premises']:
  i=p['index'];b=p['assumed_lower_bound'];require(type(i)is int and 0<=i<496 and i not in premises and type(b)is int and 0<=b<=32)
  premises[i]=(span(p['annihilator_basis']),b)
 require(premises[495][0]=={0}and premises[495][1]>=20)
 for i,r,b in [(492,1,19),(493,2,19),(494,3,20)]:
  H,L=premises[i];require(len(H)==2 and rank(next(x for x in H if x))==r and L>=b)
 @lru_cache(None)
 def action(g):
  require(len(g)==3);L,R,t=g;require(L in inverse and R in inverse and type(t)is int and t in(0,1))
  return tuple(mult[mult[L][tr[x]if t else x]][R]for x in range(512))
 @lru_cache(None)
 def physical(g):
  image=action(g);L,R,t=g;Li,Ri=inverse[L],inverse[R]
  require(len(set(image))==512)
  basis=[1<<i for i in range(9)]
  if not t:
   av=[mult[mult[tr[L]][a]][tr[R]]for a in basis];bv=[mult[tr[Ri]][b]for b in basis];cv=[mult[c][tr[Li]]for c in basis]
  else:
   av=[mult[mult[R][tr[a]]][L]for a in basis]
   # B' depends on C, and C' on B for the transposition symmetry.
   bv=[mult[Li][tr[c]]for c in basis];cv=[mult[tr[b]][Ri]for b in basis]
  for i,u in enumerate(basis):
   for j,a in enumerate(basis):require((u&av[j]).bit_count()%2==(image[u]&a).bit_count()%2,'coefficient dual mismatch')
  trace=lambda x:((x>>0)^(x>>4)^(x>>8))&1
  for i,a in enumerate(basis):
   for j,b in enumerate(basis):
    for k,c in enumerate(basis):
     out=mult[mult[av[i]][bv[k]if t else bv[j]]][cv[j]if t else cv[k]]
     require(trace(out)==trace(mult[mult[a][b]][c]),'tensor symmetry mismatch')
  return image
 @lru_cache(None)
 def transformed(premise_index,chain):
  H,_=premises[premise_index]
  for g in chain:
   image=physical(g);H=frozenset(image[x]for x in H)
  return H
 def geometry(row,domain,markers):
  i=row['premise'];b=row['bound_used'];require(type(b)is int and 0<=b<=premises[i][1])
  H=transformed(i,tuple(tuple(g)for g in row['actions']))
  return [j for j,f in enumerate(domain)if f in H],20-b-sum(f in H for f in markers)
 # Enumerate the whole physical group rather than trusting a saved orbit-size sum.
 reps=payload['pair_representatives'];require(reps==[[10,b]for b in [11,12,19,20,68,96,258]])
 orbits=[set()for _ in reps];single=[set(),set(),set()]
 for t in(0,1):
  for L in gl:
   for R in gl:
    def image(x):return mult[mult[L][tr[x]if t else x]][R]
    for k,x in enumerate([1,10,273]):single[k].add(image(x))
    for k,(a,b)in enumerate(reps):orbits[k].add(tuple(sorted((image(a),image(b)))))
 require(single==[set(r1),set(r2),set(gl)])
 expected={(a,b)for j,a in enumerate(r2)for b in r2[j+1:]};covered=set()
 for orbit,size in zip(orbits,payload['pair_orbit_sizes']):
  require(len(orbit)==size and not(covered&orbit));covered|=orbit
 require(covered==expected and len(covered)==43071)
 # These normal matrices directly span the two rank19 catalog annihilators.
 require(payload['direct_pairs']==[dict(pair=[10,68],premise=486),dict(pair=[10,96],premise=488)])
 for direct in payload['direct_pairs']:
  H,L=premises[direct['premise']];require(H==span(direct['pair'])and L>=19)
 reports=[];names=[]
 for case in payload['cases']:
  name=case['name'];names.append(name);markers=case['markers'];domain=case['domain'];target=case['target'];selected=case['initial_selected']
  if name=='rank1':require(markers==[]and domain==r1 and target==20 and selected==[0]and domain[0]==1)
  elif name=='single-rank2':require(markers==[10]and domain==r1 and target==19 and selected==[])
  else:
   k=int(name);require(k in[8,9,10,11,14]and markers==reps[k-8]and target==18 and selected==[])
   free=set(active)-set(markers)
   for row in case['initial_zero_rows']:
    support,cap=geometry(row,active,[]);support={active[j]for j in support}
    require(len(support&set(markers))==cap and support&free,'invalid initial zero propagation');free-=support
   require(domain==sorted(free),'initial domain mismatch')
  require(len(domain)==len(set(domain)))
  supports=[];caps=[]
  for row in case['rows']:
   support,cap=geometry(row,domain,markers)
   require(row['support']==support and row['rhs']==cap and cap>=0,'row geometry/capacity mismatch');supports.append(support);caps.append(cap)
  perms=[];position={f:i for i,f in enumerate(domain)}
  for g in case['actions']:
   image=physical(tuple(g));require({image[x]for x in markers}==set(markers))
   require({image[x]for x in domain}==set(domain))
   if name=='rank1':require(image[1]==1)
   perms.append([position[image[x]]for x in domain])
  result=verify(case['tree'],supports,caps,perms,len(domain),target,selected)
  require(result['stats']['nodes']==case['expected_nodes']and result['stats']['leaves']==case['expected_leaves'])
  reports.append(dict(name=name,rows=len(supports),physical_branch_actions=len(perms),stats=result['stats']))
 require(names==['rank1','single-rank2','8','9','10','11','14'])
 return dict(passed=True,claim='Conditional global rank_F2(M3 multiplication)>=21, assuming every explicitly listed restricted lower bound.',lower_bound_premises_replayed=False,premises=len(premises),pair_coverage=len(covered),physical_actions_tensor_checked=physical.cache_info().currsize,cases=reports,nodes=sum(r['stats']['nodes']for r in reports),leaves=sum(r['stats']['leaves']for r in reports),seconds=time.perf_counter()-started)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
 raw=(P/'payload.json.gz').read_bytes();manifest=json.loads((P/'provenance.json').read_text());require(hashlib.sha256(raw).hexdigest()==manifest['payload_sha256'],'payload hash mismatch')
 report=run(json.loads(gzip.decompress(raw)));text=json.dumps(report,indent=2)
 if args.output:args.output.write_text(text+'\n')
 print(text)
