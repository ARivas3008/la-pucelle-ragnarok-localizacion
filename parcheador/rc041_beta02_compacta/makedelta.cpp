// Lossless source-copy/literal patch generator, Linux build tool (not required by installer).
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <stdexcept>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
struct Map { int fd; size_t n; const uint8_t* p; Map(const char* s){fd=open(s,O_RDONLY);struct stat st{};if(fd<0||fstat(fd,&st)||st.st_size<8)throw std::runtime_error(s);n=st.st_size;p=(const uint8_t*)mmap(nullptr,n,PROT_READ,MAP_PRIVATE,fd,0);if(p==MAP_FAILED)throw std::runtime_error("mmap");}~Map(){munmap((void*)p,n);close(fd);} };
uint64_t word(const uint8_t*p){uint64_t v;memcpy(&v,p,8);return v;}
uint64_t hash(uint64_t x){x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;x*=0x94d049bb133111ebULL;return x^(x>>31);}
size_t match(const Map&a,const Map&b,size_t x,size_t y){if(x>=a.n||y>=b.n)return 0;size_t max=std::min(a.n-x,b.n-y),i=0;while(max-i>=4096&&!memcmp(a.p+x+i,b.p+y+i,4096))i+=4096;while(max-i>=64&&!memcmp(a.p+x+i,b.p+y+i,64))i+=64;while(i<max&&a.p[x+i]==b.p[y+i])++i;return i;}
void put(FILE*f,uint64_t n,int len){for(int j=0;j<len;j++)fputc((n>>(8*j))&255,f);}
int main(int argc,char**argv){if(argc!=5)return 2;Map a(argv[1]),b(argv[2]);size_t stride=strtoull(argv[4],nullptr,10);if(!stride||a.n>=UINT32_MAX||b.n>=UINT32_MAX)return 2;size_t cap=1;while(cap<2*(a.n/stride+1))cap*=2;std::vector<uint32_t> tab(cap);size_t mask=cap-1;
for(size_t x=0;x+8<=a.n;x+=stride){auto w=word(a.p+x);size_t h=hash(w)&mask;while(tab[h]&&word(a.p+tab[h]-1)!=w)h=(h+1)&mask;if(!tab[h])tab[h]=x+1;}
FILE*f=fopen(argv[3],"wb");if(!f)return 3;fwrite("LPCOPY01",1,8,f);size_t t=0,literal=0,copied=0,lit=0,commands=0;int64_t shift=0;
auto emitlit=[&](size_t from,size_t to){if(to==from)return;fputc(2,f);put(f,to-from,4);fwrite(b.p+from,1,to-from,f);lit+=to-from;commands++;};
while(t<b.n){size_t best=0,src=0;auto test=[&](int64_t off){if(off<0||(uint64_t)off>=a.n)return;size_t v=match(a,b,off,t);if(v>best){best=v;src=off;}};test((int64_t)t+shift);if(shift!=0)test(t);
if(best<4096&&t+8<=b.n){auto w=word(b.p+t);size_t h=hash(w)&mask;while(tab[h]&&word(a.p+tab[h]-1)!=w)h=(h+1)&mask;if(tab[h])test(tab[h]-1);}
if(best>=24){while(t>literal&&src>0&&a.p[src-1]==b.p[t-1]){--src;--t;++best;}emitlit(literal,t);fputc(1,f);put(f,src,8);put(f,best,4);copied+=best;commands++;shift=(int64_t)src-(int64_t)t;t+=best;literal=t;}else ++t;}
emitlit(literal,b.n);fputc(0,f);if(fclose(f))return 4;fprintf(stderr,"%s copied=%zu literal=%zu commands=%zu\n",argv[3],copied,lit,commands);return 0;}
