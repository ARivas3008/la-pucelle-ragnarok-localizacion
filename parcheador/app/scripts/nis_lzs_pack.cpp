#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <algorithm>
#include <string>
#include <cstring>
using namespace std;
static uint32_t hash3(const uint8_t *p){
 uint32_t n=uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16);
 n^=n>>9; n*=0x9E3779B1; return (n>>16)&0xFFFF;
}
int main(int argc,char **argv){
 if(argc!=5){cerr<<"Usage: nis_lzs_pack input-raw output.lzs extension(3 ASCII) marker(0-255)\n";return 2;}
 string ip=argv[1],op=argv[2],ext=argv[3];if(ext.size()>4){cerr<<"extension too long\n";return 2;}
 int marker=atoi(argv[4]);if(marker<=0||marker>255){cerr<<"marker out of range\n";return 2;}
 ifstream in(ip,ios::binary|ios::ate); if(!in){cerr<<"input missing\n";return 3;}
 size_t n=in.tellg();in.seekg(0);vector<uint8_t> src(n);in.read((char*)src.data(),n);
 vector<int32_t> prev(n,-1);array<int32_t,65536> last;last.fill(-1);
 vector<uint8_t> out;out.reserve(n/2); out.resize(16,0);
 ext.resize(4,'\0'); memcpy(out.data(),ext.data(),4);
 uint32_t unc=n;memcpy(out.data()+4,&unc,4);
 out[12]=(uint8_t)marker;
 auto appendpos=[&](size_t pos){if(pos+2<n){auto h=hash3(src.data()+pos);prev[pos]=last[h];last[h]=pos;}};
 size_t i=0;size_t matches=0;
 while(i<n){
  size_t best=0,dist=0;
  if(i+2<n){
   int32_t cand=last[hash3(src.data()+i)];
   for(int checks=0;cand>=0 && i-(size_t)cand<=254 && checks<260; cand=prev[cand],++checks){
    size_t length=0;
    // El decodificador del juego requiere que la fuente ya esté completa.
    // No emitir referencias solapadas (longitud > distancia): el decoder
    // Python byte a byte las toleraba, ocultando corrupción en ejecución.
    while(length<255 && length<i-(size_t)cand && i+length<n && src[cand+length]==src[i+length])++length;
    if(length>best && length>=3){best=length;dist=i-cand;if(best==255)break;}
   }
  }
  if(best>=3){
   out.push_back((uint8_t)marker);
   out.push_back((uint8_t)(dist>=marker?dist+1:dist));
   out.push_back((uint8_t)best);matches++;
   for(size_t p=i;p<i+best;++p)appendpos(p);
   i+=best;
  }else{
   out.push_back(src[i]);if(src[i]==marker)out.push_back((uint8_t)marker);
   appendpos(i);++i;
  }
 }
 uint32_t compressed=(uint32_t)(out.size()-4);memcpy(out.data()+8,&compressed,4);
 ofstream f(op,ios::binary);f.write((char*)out.data(),out.size());
 cout<<"raw="<<n<<" packed="<<out.size()<<" marker="<<marker<<" matches="<<matches<<" ratio="<<double(out.size())/n<<"\n";
}
