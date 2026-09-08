#include <array>
#include <vector>
#include <map>
#include <stdexcept>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <chrono>
#include <string>

namespace {
using Space=std::array<uint16_t,9>;
uint16_t mul[512][512], tr[512], inv[512];
Space catalog[496]; int dimensions[496], bounds[496];
std::map<Space,int> lookup; bool initialized=false;
void need(bool b,const char* message){if(!b)throw std::runtime_error(message);}
Space canonical(const std::vector<uint16_t>& rows){
    Space p{};
    for(unsigned x:rows){
        need(x<512,"matrix outside F2^9");
        while(x){int j=31-__builtin_clz(x);if(!p[j]){p[j]=x;break;}x^=p[j];}
    }
    for(int j=0;j<9;j++)if(p[j])for(int k=j+1;k<9;k++)if((p[k]>>j)&1)p[k]^=p[j];
    return p;
}
int dim(const Space& s){int n=0;for(auto x:s)n+=x!=0;return n;}
std::vector<uint16_t> rows(const Space& s){std::vector<uint16_t> v;for(auto x:s)if(x)v.push_back(x);return v;}
uint32_t u32(const uint8_t* p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
uint64_t u64(const uint8_t* p){return uint64_t(u32(p))|(uint64_t(u32(p+4))<<32);}
void error_out(char* out,size_t cap,const char* message){if(cap){std::strncpy(out,message,cap-1);out[cap-1]=0;}}

struct Walk {
    int parent;const uint8_t* raw;uint64_t n,pos=0,nodes=0;int maximum=0;
    std::vector<uint16_t> forms,path;std::array<uint8_t,496> dependencies{};
    std::chrono::steady_clock::time_point deadline;
    Walk(int p,const uint8_t* bytes,size_t size,uint64_t expected,uint64_t milliseconds):parent(p),raw(bytes){
        need(initialized,"uninitialized catalog");need(0<=p&&p<496,"bad parent");
        need(size>=8,"truncated header");n=u64(raw);need(n>0&&n==expected,"proof leaf count mismatch");
        need(n<=(SIZE_MAX-8)/13&&size==8+13*n,"proof byte length mismatch");
        need(bounds[p]>0&&bounds[p]<=32,"rank bound exceeds mask width");
        need(milliseconds>0,"invalid time limit");
        deadline=std::chrono::steady_clock::now()+std::chrono::milliseconds(milliseconds);
        for(int x=1;x<512;x++){
            bool good=true;for(int j=0;j<9;j++)if(catalog[p][j]&&((x>>j)&1))good=false;
            if(good)forms.push_back(x);
        }
        need(forms.size()==(size_t(1)<<(9-dimensions[p]))-1,"incomplete quotient forms");
    }
    void visit(int max_index){
        ++nodes;maximum=std::max(maximum,int(path.size()));
        if((nodes&16383)==1)need(std::chrono::steady_clock::now()<deadline,"native time limit");
        need(pos<n,"premature end of proof");unsigned depth=raw[8+pos];
        need(path.size()<=depth&&depth<unsigned(bounds[parent])&&depth<32,"invalid leaf depth");
        if(path.size()!=depth){
            need(path.size()<unsigned(bounds[parent]-1),"branch exceeds target depth");
            for(int k=0;k<=max_index;k++){path.push_back(forms[k]);visit(k);path.pop_back();}
            return;
        }
        uint32_t mask=u32(raw+8+n+4*pos),q=u32(raw+8+5*n+4*pos),s=u32(raw+8+9*n+4*pos);
        need(mask>0&&uint64_t(mask)<(uint64_t(1)<<depth),"invalid nonempty leaf mask");
        need((mask>>(depth-1))&1,"leaf mask omits newest path form");
        uint32_t left=q&65535,trans=q>>16;
        need(trans<=1&&left<512&&s<512&&inv[left]&&inv[s],"invalid invertible normalization");
        std::vector<uint16_t> extended=rows(catalog[parent]);
        for(unsigned j=0;j<depth;j++)if((mask>>j)&1)extended.push_back(path[j]);
        Space restricted=canonical(extended);need(dim(restricted)>dimensions[parent],"restriction is not strict");
        std::vector<uint16_t> image;
        for(auto h:rows(restricted))image.push_back(mul[mul[left][trans?tr[h]:h]][inv[s]]);
        auto found=lookup.find(canonical(image));need(found!=lookup.end(),"child orbit missing");int child=found->second;
        need(child<parent&&dimensions[child]>dimensions[parent],"invalid child ordering or dimension");
        need(__builtin_popcount(mask)+bounds[child]>=bounds[parent],"leaf rank inequality fails");
        dependencies[child]=1;++pos;
    }
};
}

extern "C" int fast_init(const uint16_t* flat,const uint8_t* counts,const uint8_t* lbs,char* error,size_t capacity){
    try{
        initialized=false;lookup.clear();
        for(int a=0;a<512;a++){
            tr[a]=0;inv[a]=0;
            for(int i=0;i<3;i++)for(int j=0;j<3;j++)tr[a]|=((a>>(3*i+j))&1)<<(3*j+i);
            for(int b=0;b<512;b++){
                unsigned x=0;
                for(int i=0;i<3;i++)for(int j=0;j<3;j++)for(int k=0;k<3;k++)x^=(((a>>(3*i+k))&(b>>(3*k+j)))&1)<<(3*i+j);
                mul[a][b]=x;
            }
        }
        for(int a=1;a<512;a++)for(int b=1;b<512;b++)if(mul[a][b]==273&&mul[b][a]==273){need(!inv[a],"duplicate inverse");inv[a]=b;}
        for(int i=0;i<496;i++){
            need(counts[i]<=9&&lbs[i]<=32,"bad catalog dimension or bound");
            std::vector<uint16_t> v;for(int j=0;j<counts[i];j++)v.push_back(flat[9*i+j]);
            catalog[i]=canonical(v);need(rows(catalog[i])==v,"noncanonical catalog constraints");
            dimensions[i]=counts[i];bounds[i]=lbs[i];need(lookup.emplace(catalog[i],i).second,"duplicate catalog orbit");
        }
        initialized=true;return 0;
    }catch(const std::exception& e){error_out(error,capacity,e.what());return 1;}
}

extern "C" int fast_check(int parent,const uint8_t* raw,size_t size,uint64_t expected,uint64_t milliseconds,uint64_t* stats,uint8_t* dependencies,char* error,size_t capacity){
    try{
        Walk w(parent,raw,size,expected,milliseconds);w.visit(int(w.forms.size())-1);
        need(w.pos==w.n,"unconsumed proof leaves");stats[0]=w.pos;stats[1]=w.nodes;stats[2]=w.maximum;
        std::copy(w.dependencies.begin(),w.dependencies.end(),dependencies);return 0;
    }catch(const std::exception& e){error_out(error,capacity,e.what());return 1;}
}

extern "C" void fast_tables(uint16_t* products,uint16_t* transposes,uint16_t* inverses){
    std::copy(&mul[0][0],&mul[0][0]+512*512,products);std::copy(tr,tr+512,transposes);std::copy(inv,inv+512,inverses);
}

extern "C" int fast_canonical(const uint16_t* input,size_t n,uint16_t* output){
    try{need(n<=64,"too many test rows");auto c=canonical(std::vector<uint16_t>(input,input+n));std::copy(c.begin(),c.end(),output);return 0;}
    catch(const std::exception&){return 1;}
}
