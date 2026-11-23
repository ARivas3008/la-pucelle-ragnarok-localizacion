from pathlib import Path
import sys,struct,zlib,json,hashlib
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from construir_parche import Image,members_from_dat
from nis_formats import nispack,lzs_decompress
def png(path,w,h,rgba):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
 raw=b''.join(b'\0'+rgba[y*w*4:(y+1)*w*4] for y in range(h))
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
def decode(raw,swizzle=False):
 w,h,col,unused,pal,banks,_,_=struct.unpack_from('<8H',raw)
 start=16+4*col*banks; palette=[raw[16+i*4:20+i*4] for i in range(col)]
 data=raw[start:];line=w if col==256 else w//2
 out=bytearray()
 for y in range(h):
  for x in range(w):
   xb=x if col==256 else x//2
   off=((y//8)*(line//16)+xb//16)*128+(y%8)*16+xb%16 if swizzle else y*line+xb
   if off>=len(data):out+=b'\xff\0\xff\xff';continue
   val=data[off] if col==256 else (data[off]>>(4*(x%2)))&15
   out+=palette[val]
 return w,h,out
def main():
 iso=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in iso.records()}
 bg={i['name']:i for i in nispack(iso.read(*rec['/PSP_GAME/USRDIR/BGPACK.DAT']))}
 out=B/'texturas';out.mkdir(exist_ok=True)
 for name in ['at01.txp','wmap_03.txp','title_mj.txp']:
  raw=bg[name]['content'];print(name,len(raw),struct.unpack_from('<8H',raw),hashlib.sha256(raw).hexdigest())
  (out/name).write_bytes(raw)
  for swizzle in [False,True]:
   w,h,rgba=decode(raw,swizzle);png(out/(name+('_swizzle' if swizzle else '_lineal')+'.png'),w,h,rgba)
 members=members_from_dat(lzs_decompress(iso.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])))
 from atlas_ui_es import apply
 for name in ('sys3.txp','sys4.txp'):
  raw=members[name];print(name,len(raw),struct.unpack_from('<8H',raw))
  w,h,rgba=decode(raw,True);png(out/(name+'_original.png'),w,h,rgba)
 apply(members)
 for name in ('sys3.txp','sys4.txp'):
  w,h,rgba=decode(members[name],True);png(out/(name+'_es.png'),w,h,rgba)
if __name__=='__main__':main()
