import sys, numpy as np,struct as s
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/rc41rev5');B=Path('/tmp/rc41text/RC041_rev4.iso');D=Path('/tmp/rc41text/ULJS00244')
def txp(b):
 w,h,n=s.unpack_from('<HHH',b); banks=s.unpack_from('<H',b,10)[0]; assert n in (16,256) and banks>=1,(w,h,n,banks);off=16+n*4*banks; d=np.frombuffer(b[off:],dtype='u1');bw=w if n==256 else w//2; hh=len(d)//bw; assert bw%16==0,(w,h,n,hh,len(d));d=np.concatenate([d[:(hh//8)*8*bw].reshape(hh//8,bw//16,8,16).transpose(0,2,1,3).reshape((hh//8)*8,bw),d[(hh//8)*8*bw:].reshape(bw//16,hh%8,16).transpose(1,0,2).reshape(hh%8,bw)],axis=0); a=d if n==256 else np.stack([d&15,d>>4],axis=-1).reshape(hh,w); pal=np.frombuffer(b[16:16+n*4],dtype='u1').reshape(n,4);return a.copy(),pal.copy(),off,w,h
def enc(b,a):
 _,pal,off,w,h=txp(b); d=a if len(pal)==256 else (a[:,::2]|(a[:,1::2]<<4));hh,bw=d.shape;return b[:off]+d[:(hh//8)*8].reshape(hh//8,8,bw//16,16).transpose(0,2,1,3).tobytes()+d[(hh//8)*8:].reshape(hh%8,bw//16,16).transpose(1,0,2).tobytes()
def image(b):
 a,p,_,w,h=txp(b);assert enc(b,a)==b;return Image.fromarray(p[a[:h]])
if __name__=='__main__':
 bg=nis(read(B,'/PSP_GAME/USRDIR/BGPACK.DAT'));_,packs=inventory(B,D)
 items={**{k:v for k,v in bg.items() if re.match(r'at\d+|title_mj|title2',k)},**{k:v for k,v in packs['ISO_START'].items() if re.match(r'(sys[2-7]|item)\.txp',k)}}
 for k,v in items.items():
  im=image(v);im.save(P/(k+'.png'))
 sheet=Image.new('RGB',(1000,4*210),(45,45,48));dr=ImageDraw.Draw(sheet)
 for i,k in enumerate([x for x in items if x.startswith('at')]):
  im=image(items[k]);im.thumbnail((240,175));x=(i%4)*250;y=(i//4)*210;dr.text((x+4,y+4),k,fill='white');sheet.paste(im,(x+4,y+25),im)
 sheet.save(P/'chapters.png')
 sheet=Image.new('RGB',(1100,900),(45,45,48));dr=ImageDraw.Draw(sheet)
 for i,k in enumerate([x for x in items if x.startswith(('sys','item','title'))]):
  im=image(items[k]);im.thumbnail((350,275));x=i%3*366;y=i//3*300;dr.text((x+4,y+4),k,fill='white');sheet.paste(im,(x+4,y+25),im)
 sheet.save(P/'ui.png')
