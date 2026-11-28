import struct as s, json, numpy as np, hashlib as h
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
P=Path('/tmp/lp_reintegracion'); orig=(P/'orig.anm').read_bytes(); old=(P/'beta.anm').read_bytes(); qa=json.load(open('/mnt/data/QA_RC035.json'))['intro']['pairs']; pairs=json.load(open('/mnt/data/QA_RC036_Sombras.json'))['shadow_correction']['pairs']; out=bytearray(orig); assert orig[:0xc50]==old[:0xc50]
# The 16-byte pixel-data prefix is not swizzled pixel storage; verified against intact Japanese glyphs.
OFF=0xc60; S=65536

def decode(b,i):
 d=np.frombuffer(b[OFF+i*S:OFF+(i+1)*S],dtype='u1').reshape(32,16,8,16).transpose(0,2,1,3).reshape(256,256);return np.stack([d&15,d>>4],axis=-1).reshape(256,512).copy()
def encode(a):
 d=a[:,::2]|(a[:,1::2]<<4);return d.reshape(32,8,16,16).transpose(0,2,1,3).tobytes()
A=[decode(orig,i) for i in range(4)]; base=[x.copy() for x in A]; mask=[np.zeros_like(x,dtype=bool) for x in A]
def cut(i):return list(s.unpack_from('<8H',orig,0x55c+i*16))
def tr(i):return list(s.unpack_from('<8h',orig,0x6dc+i*16))
for i in range(1,23):
 t,_,_,_,x,y,w,hh=cut(i);A[t][y:y+hh,x:x+w]=0;mask[t][y:y+hh,x:x+w]=True
# Repack into the same four 512x256 atlases; preserve the gradient (cut 23) and all unrelated data.
font='/usr/share/fonts/truetype/noto/NotoSerif-CondensedBold.ttf';factor=4;used=[0,0];records=[]
for q in qa:
 i,j=q['main'],q['shadow'];t=cut(i)[0]; assert t in (0,1) and cut(j)[0]==t+2
 text=q['text'];
 for size in range(16,10,-1):
  f=ImageFont.truetype(font,size*factor);bb=f.getbbox(text);im=Image.new('L',(bb[2]-bb[0]+8,bb[3]-bb[1]+8));ImageDraw.Draw(im).text((4-bb[0],4-bb[1]),text,font=f,fill=255);im=im.crop(im.getbbox());im=im.resize(((im.width+factor-1)//factor,(im.height+factor-1)//factor),Image.Resampling.LANCZOS)
  if im.width<=432 and im.height<=19:break
 else:raise ValueError(text)
 w=im.width+10;hh=26;x=(512-w)//2;y=2+30*used[t];used[t]+=1;assert y+hh<=190
 img=Image.new('L',(w,hh));img.paste(im,(5,(hh-im.height)//2)); arr=np.array(img);shadow=Image.new('L',(w,hh));shadow.paste(im,(5,(hh-im.height)//2+2));shadow=shadow.filter(ImageFilter.GaussianBlur(1.3)); sa=np.minimum(np.array(shadow).astype(float)*1.8,255).astype('u1')
 for k,plane,idx in [(i,t,arr),(j,t+2,sa)]:
  # Assert no unrelated image data overwritten.
  region=A[plane][y:y+hh,x:x+w];assert not region.any(),(k,plane,x,y,w,hh,np.count_nonzero(region))
  region[:]=np.rint(idx.astype(float)*15/255).astype('u1');mask[plane][y:y+hh,x:x+w]=True
  oldcut=cut(k);s.pack_into('<8H',out,0x55c+k*16,*oldcut[:4],x,y,w,hh)
 pair=next(p for p in pairs if p['main']==i);mi,si=pair['transform_main_id'],pair['transform_shadow_id'];m=tr(mi);m[2:6]=[w//2,hh//2,100,100];s.pack_into('<8h',out,0x6dc+mi*16,*m)
 if si!=mi:s.pack_into('<8h',out,0x6dc+si*16,*m)
 records.append(dict(main=i,shadow=j,text=text,size=size,width=im.width,height=im.height,cut=[x,y,w,hh],transform_main=mi,transform_shadow=si))
for i,a in enumerate(A):
 assert np.array_equal(a[~mask[i]],base[i][~mask[i]])
 out[OFF+i*S:OFF+(i+1)*S]=encode(a);assert np.array_equal(decode(out,i),a)
 assert encode(base[i])==orig[OFF+i*S:OFF+(i+1)*S]
assert out[:0x55c]==orig[:0x55c] and out[0x85c:OFF]==orig[0x85c:OFF] and out[OFF+4*S:]==orig[OFF+4*S:]
assert out[0x55c+23*16:0x55c+24*16]==orig[0x55c+23*16:0x55c+24*16]
assert out[0x6dc+22*16:0x6dc+24*16]==orig[0x6dc+22*16:0x6dc+24*16]
(P/'new.anm').write_bytes(out);(P/'intro_records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));
for i,a in enumerate(A):Image.fromarray(a*17).save(P/f'new_atlas{i}.png')
print('corrected',len(records),'pairs',used,'sha',h.sha256(out).hexdigest())
