"""Compiled backtracking traversal plus unchanged Python prerequisite checker.

Engine.check validates a CONDITIONAL local proof only. Verifier.verify closes
all dependencies in a fresh recursive ledger before accepting that parent.
"""
import ctypes as C,gzip,time,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import published_checker as pc

LIBRARY_PATH = None

class Engine:
    def __init__(self,records):
        if len(records)!=496:raise ValueError('catalog must contain496 records')
        for i,r in enumerate(records):
            if r['index']!=i or type(r['bound'])is not int or not 0<=r['bound']<=32:raise ValueError('invalid catalog index/bound')
            if len(r['constraints'])>9 or any(type(x)is not int or not 0<=x<512 for x in r['constraints']):raise ValueError('invalid catalog constraints')
            if tuple(r['constraints'])!=pc.canonical(r['constraints']):raise ValueError('noncanonical constraints')
        self.records=records;self.lib=C.CDLL(str(LIBRARY_PATH))
        self.lib.fast_init.argtypes=[C.POINTER(C.c_uint16),C.POINTER(C.c_uint8),C.POINTER(C.c_uint8),C.c_char_p,C.c_size_t]
        self.lib.fast_init.restype=C.c_int
        self.lib.fast_check.argtypes=[C.c_int,C.POINTER(C.c_uint8),C.c_size_t,C.c_uint64,C.c_uint64,C.POINTER(C.c_uint64),C.POINTER(C.c_uint8),C.c_char_p,C.c_size_t]
        self.lib.fast_check.restype=C.c_int
        self.lib.fast_tables.argtypes=[C.POINTER(C.c_uint16)]*3;self.lib.fast_tables.restype=None
        values=[x for r in records for x in list(r['constraints'])+[0]*(9-len(r['constraints']))]
        self.flat=(C.c_uint16*(496*9))(*values);self.counts=(C.c_uint8*496)(*[len(r['constraints'])for r in records]);self.bounds=(C.c_uint8*496)(*[r['bound']for r in records])
        self.activate()
    def activate(self):
        # Native storage is process-global. Restore this engine's catalog before
        # every check so successive mutation-test engines cannot contaminate it.
        # This bounded tool is single-threaded; concurrent engines are unsupported.
        error=C.create_string_buffer(1024)
        if self.lib.fast_init(self.flat,self.counts,self.bounds,error,len(error)):raise ValueError(error.value.decode())
    def check(self,index,raw,milliseconds=180000):
        self.activate()
        buffer=(C.c_uint8*len(raw)).from_buffer_copy(raw);stats=(C.c_uint64*3)();deps=(C.c_uint8*496)();error=C.create_string_buffer(1024)
        code=self.lib.fast_check(index,buffer,len(raw),self.records[index]['proof_size'],milliseconds,stats,deps,error,len(error))
        if code:raise ValueError(error.value.decode())
        return {'leaves':stats[0],'nodes':stats[1],'maximum_depth':stats[2],'dependencies':[i for i,x in enumerate(deps)if x]}

class Verifier(pc.Verifier):
    def __init__(self,records,blobs,total_seconds=600):
        super().__init__(records,blobs);self.engine=Engine(records)
        self.deadline=time.perf_counter()+total_seconds;self.native_timings=[]
    def verify(self,index):
        if index in self.verified:return self.verified[index]
        if time.perf_counter()>=self.deadline:raise TimeoutError('whole cone deadline')
        r=self.records[index]
        if r['kind']!='backtracking':return super().verify(index)
        assert index not in self.active;self.active.add(index)
        raw=gzip.decompress(self.blobs[index]);limit=min(180000,int(1000*(self.deadline-time.perf_counter())))
        if limit<=0:raise TimeoutError('whole cone deadline before native call')
        started=time.perf_counter();local=self.engine.check(index,raw,milliseconds=limit);del raw
        self.native_timings.append({'index':index,'seconds':time.perf_counter()-started,'leaves':local['leaves']})
        for child in local['dependencies']:
            self.verify(child)
            assert self.verified[child]['bound']==self.records[child]['bound']
        out={'index':index,'bound':r['bound'],'method':r['kind'],**local}
        self.active.remove(index);self.verified[index]=out;return out
