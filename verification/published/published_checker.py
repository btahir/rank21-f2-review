"""Independent standard-library checker for a small published proof cone."""
from pathlib import Path
from itertools import product
from functools import lru_cache
import ast,gzip,hashlib,json,re,struct,time

ROOT=Path(__file__).resolve().parent

def canonical(vectors):
    piv={}
    for x in vectors:
        assert 0<=x<512
        while x:
            j=x.bit_length()-1
            if j not in piv:piv[j]=x;break
            x^=piv[j]
    for j in sorted(piv):
        for k in sorted(piv):
            if k>j and piv[k]>>j&1:piv[k]^=piv[j]
    return tuple(piv[j] for j in sorted(piv))

def rank(rows):
    # Opposite pivot convention from constraint canonicalization.
    piv={}
    for x in rows:
        while x:
            j=(x&-x).bit_length()-1
            if j not in piv:piv[j]=x;break
            x^=piv[j]
    return len(piv)

def mm(a,b):
    return sum((sum((a>>(3*i+k)&1)*(b>>(3*k+j)&1) for k in range(3))%2)<<(3*i+j)
               for i,j in product(range(3),repeat=2))

def transpose(a):return sum((a>>(3*i+j)&1)<<(3*j+i) for i,j in product(range(3),repeat=2))

@lru_cache(None)
def inverse(a):
    assert 0<a<512 and rank([a&7,(a>>3)&7,(a>>6)&7])==3
    return next(b for b in range(512) if mm(a,b)==273 and mm(b,a)==273)

def read_catalog():
    data=[]
    for block in (ROOT/'upstream-certificate.pb.txt').read_text().split('constrained_tensors {')[1:]:
        def integer(name,default=0):
            hit=re.search(r'\b'+name+r': (\d+)\b',block)
            return int(hit[1]) if hit else default
        quoted=re.search(r'^  constraints: ("(?:\\.|[^"\\])*")$',block,re.M)
        raw=ast.literal_eval('b'+quoted[1]) if quoted else b''
        assert len(raw)%2==0
        constraints=tuple(struct.unpack('<'+'H'*(len(raw)//2),raw))
        assert canonical(constraints)==constraints
        kind=next(k for k in ('flatten_matrix','forced_product','degenerate','backtracking') if k+'_proof {' in block)
        data.append(dict(index=integer('index'),constraints=constraints,bound=integer('rank_lower_bound'),kind=kind,
                         extra=integer('extra_constraint'),query=integer('query_elem'),store=integer('store_elem'),
                         projection=integer('projection_type'),proof_size=integer('proof_size')))
    assert [r['index'] for r in data]==list(range(496))
    return data

def read_archive():
    raw=(ROOT/'upstream-certificate.btp').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='4e824eb13c235e69045881d173d8ababe622421055a238005afce413aabe3289'
    assert raw[:8]==b'BTPARCH\0' and struct.unpack_from('<IQ',raw,8)==(2,496)
    pos=20;blobs=[]
    for _ in range(496):
        n,=struct.unpack_from('<Q',raw,pos);pos+=8;blobs.append(raw[pos:pos+n]);pos+=n
    assert pos==len(raw)
    return blobs

def body(blob):
    raw=gzip.decompress(blob);n,=struct.unpack_from('<Q',raw)
    assert len(raw)==8+13*n and n>0
    depth=list(raw[8:8+n]);mask=struct.unpack_from('<'+'I'*n,raw,8+n)
    query=struct.unpack_from('<'+'I'*n,raw,8+5*n);store=struct.unpack_from('<'+'I'*n,raw,8+9*n)
    return list(zip(depth,mask,query,store))

def tensor(constraints):
    basis=[]
    for x in range(512):
        if all((x&h).bit_count()%2==0 for h in constraints) and rank(basis+[x])>len(basis):basis.append(x)
    assert len(basis)+len(constraints)==9
    entries=[(a,3*j+k,3*k+i) for a,x in enumerate(basis) for i,j,k in product(range(3),repeat=3) if x>>(3*i+j)&1]
    return (len(basis),9,9),entries

def flatten(dims,entries,axis):
    other=[i for i in range(3) if i!=axis];rows=[0]*dims[axis]
    for xyz in entries:rows[xyz[axis]]^=1<<(xyz[other[0]]*dims[other[1]]+xyz[other[1]])
    return rank(rows)

def forced(dims,entries,axis,claimed):
    axes=[axis,(axis+1)%3,(axis+2)%3];a,b,c=[dims[j] for j in axes]
    slices=[0]*a
    for xyz in entries:slices[xyz[axes[0]]]^=1<<(xyz[axes[1]]*c+xyz[axes[2]])
    pure=[];rest=[]
    for s in slices:
        if not s:continue
        rowrank=rank([(s>>(j*c))&((1<<c)-1) for j in range(b)])
        if rowrank==1 and rank(pure+[s])>len(pure):pure.append(s)
        else:rest.append(s)
    n=len(pure);t=len(rest);assert n>0
    assert n*t<=24,('completion budget',n,t)
    additions=[0]
    for s in pure:additions += [x^s for x in additions]
    options=[[s^x for x in additions] for s in rest]
    br=[[[(s>>(j*c))&((1<<c)-1) for j in range(b)] for s in opts] for opts in options]
    cr=[[[sum((s>>(j*c+k)&1)<<j for j in range(b)) for k in range(c)] for s in opts] for opts in options]
    need=claimed-n;count=0
    for choice in product(range(1<<n),repeat=t):
        count+=1
        if rank([options[i][x] for i,x in enumerate(choice)])>=need:continue
        rows=[sum(br[i][x][j]<<(i*c) for i,x in enumerate(choice)) for j in range(b)]
        if rank(rows)>=need:continue
        rows=[sum(cr[i][x][j]<<(i*b) for i,x in enumerate(choice)) for j in range(c)]
        assert rank(rows)>=need,('forced-product completion violates claim',choice,claimed)
    assert count==1<<(n*t)
    return dict(pure_slices=n,remaining_slices=t,all_completions_checked=count,residual_lower_bound=need)

class Verifier:
    def __init__(self,records,blobs):
        self.records=records;self.blobs=blobs;self.lookup={r['constraints']:r['index'] for r in records}
        self.verified={};self.active=set();self.overrides={}
    def child(self,index,extended,query,store):
        rows=canonical(extended);assert len(rows)>len(self.records[index]['constraints'])
        left=query&65535;trans=query>>16;assert trans in (0,1)
        inverse(left);right_inverse=inverse(store)
        image=canonical(mm(mm(left,transpose(h) if trans else h),right_inverse) for h in rows)
        child=self.lookup[image];assert child<index and len(self.records[child]['constraints'])>len(self.records[index]['constraints'])
        self.verify(child);return child
    def verify(self,index):
        if index in self.verified:return self.verified[index]
        assert index not in self.active;self.active.add(index)
        r=self.records[index];constraints=r['constraints'];bound=r['bound'];kind=r['kind'];deps=set();details={}
        if kind=='flatten_matrix':
            dims,entries=tensor(constraints);values=[flatten(dims,entries,a) for a in range(3)]
            assert max(values)>=bound;details['mode_ranks']=values
        elif kind=='forced_product':
            dims,entries=tensor(constraints);details=forced(dims,entries,r['projection'],bound)
        elif kind=='degenerate':
            j=self.child(index,(*constraints,r['extra']),r['query'],r['store']);deps.add(j)
            assert self.records[j]['bound']>=bound
        else:
            proof=self.overrides.get(index)
            if proof is None:proof=body(self.blobs[index])
            assert len(proof)==r['proof_size']
            pivots=[h.bit_length()-1 for h in constraints]
            forms=[x for x in range(1,512) if all(not(x>>j&1) for j in pivots)]
            assert len(forms)==(1<<(9-len(constraints)))-1
            pos=0;nodes=0;maximum_depth=0
            def walk(path,max_index):
                nonlocal pos,nodes,maximum_depth
                nodes+=1;maximum_depth=max(maximum_depth,len(path));assert pos<len(proof)
                depth,mask,q,s=proof[pos];assert len(path)<=depth<=bound-1
                if len(path)==depth:
                    assert 0<mask<1<<depth
                    chosen=[f for k,f in enumerate(path) if mask>>k&1]
                    j=self.child(index,(*constraints,*chosen),q,s);deps.add(j)
                    assert len(chosen)+self.records[j]['bound']>=bound
                    pos+=1;return
                assert len(path)<bound-1
                for k in range(max_index+1):walk(path+[forms[k]],k)
            walk([],len(forms)-1);assert pos==len(proof)
            details=dict(leaves=pos,nodes=nodes,maximum_depth=maximum_depth)
        out=dict(index=index,bound=bound,method=kind,dependencies=sorted(deps),**details)
        self.active.remove(index);self.verified[index]=out;return out

# Imported by the portable published replay front door.
