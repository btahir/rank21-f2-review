"""Second exact count checker: integer LCM certificates and bitmask states, no Fraction/checker imports."""
from math import lcm
from collections import Counter

def verify(tree, supports, capacities, permutations, n, target, initial_selected=()):
 full=(1<<n)-1
 assert type(n)is int and n>0 and type(target)is int and target>0
 masks=[]
 for support in supports:
  assert len(support)==len(set(support)) and all(type(i)is int and 0<=i<n for i in support)
  masks.append(sum(1<<i for i in support))
 assert len(masks)==len(capacities) and all(type(b)is int and b>=0 for b in capacities)
 for p in permutations:assert len(p)==n and set(p)==set(range(n))and all(type(i)is int for i in p)
 statistics=Counter();used_rows=set();used_actions=set()
 def mapped(bits,p):
  out=0
  while bits:
   b=bits&-bits;out|=1<<p[b.bit_length()-1];bits-=b
  return out
 def sparse(v,limit):
  seen=set()
  for row in v:
   assert len(row)==3 and all(type(x)is int for x in row)
   i,a,b=row;assert 0<=i<limit and i not in seen and a>=0 and b>0;seen.add(i)
  return v
 def descend(node,ones,free):
  statistics['nodes']+=1;assert not(ones&free)and (ones|free)&~full==0
  for j in node['propagation']:
   assert type(j)is int and 0<=j<len(masks)
   assert (masks[j]&ones).bit_count()==capacities[j]
   remove=masks[j]&free;assert remove;free^=remove;used_rows.add(j);statistics['propagations']+=1
  kind=node['kind']
  if kind=='orbit_branch':
   orbit=node['orbit'];representative=node['representative']
   assert type(representative)is int and representative in orbit and len(orbit)==len(set(orbit))
   assert all(type(i)is int and 0<=i<n and free>>i&1 for i in orbit)
   witnesses=node['witnesses'];assert len(witnesses)==len(orbit)and sorted(w[0]for w in witnesses)==sorted(orbit)
   for i,g in witnesses:
    assert type(g)is int and 0<=g<len(permutations)
    p=permutations[g];assert p[i]==representative and mapped(ones,p)==ones and mapped(free,p)==free;used_actions.add(g)
   statistics['orbit_branches']+=1
   descend(node['none'],ones,free&~sum(1<<i for i in orbit))
   descend(node['some'],ones|(1<<representative),free&~(1<<representative));return
  statistics['leaves']+=1;statistics[kind]+=1
  if kind=='capacity':assert (ones|free).bit_count()<target;return
  if kind=='violation':
   j=node['row'];assert type(j)is int and 0<=j<len(masks)and (masks[j]&ones).bit_count()>capacities[j];used_rows.add(j);return
  assert kind=='rational_bound'
  ys=sparse(node['rows'],len(masks));zs=sparse(node['upper'],n);ws=sparse(node['lower'],n)
  claimed=node['total_upper'];assert len(claimed)==2 and all(type(x)is int for x in claimed)and claimed[1]>0
  denominator=claimed[1]
  for _,_,b in ys+zs+ws:denominator=lcm(denominator,b)
  coeff=[0]*n;bound=0
  for j,a,b in ys:
   v=a*(denominator//b);bound+=v*capacities[j]
   bits=masks[j]
   while bits:
    bit=bits&-bits;coeff[bit.bit_length()-1]+=v;bits-=bit
   if a:used_rows.add(j)
  for i,a,b in zs:
   v=a*(denominator//b);coeff[i]+=v
   if (ones|free)>>i&1:bound+=v
  for i,a,b in ws:
   v=a*(denominator//b);coeff[i]-=v
   if ones>>i&1:bound-=v
  assert min(coeff)>=denominator
  assert bound*claimed[1]==claimed[0]*denominator and bound<target*denominator
 assert len(initial_selected)==len(set(initial_selected)) and all(type(i)is int and 0<=i<n for i in initial_selected)
 ones=sum(1<<i for i in initial_selected)
 descend(tree,ones,full^ones)
 return dict(stats=dict(statistics),used_rows=sorted(used_rows),used_permutations=sorted(used_actions))
