import csv,struct as s, numpy as np, hashlib as h, json, shutil
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path('/tmp/rc41closures'); base=Path('/tmp/rc41qa/RC041_rev2.iso');target=p/'RC041_rev3.iso'; original=Path('/tmp/rc38/orig/La_Pucelle_Ragnarok_v1.1.2.iso')
rows=list(csv.DictReader(open('/tmp/rc41qa/cierres_ROM039.csv',encoding='utf-8-sig')))
texts={9441:(1,'Aprender el oficio'),9442:(2,'La promesa de un niño'),9443:(3,'Prier y Alouette'),9444:(4,'Un problema gigantesco'),9445:(5,'Un asunto peliagudo'),9446:(6,'El viaje'),9447:(7,'Un baile en el cielo'),9448:(8,'Hacia una tierra inexplorada'),9449:(9,'Recuerdos de Fátima'),9450:(10,'El príncipe de las tinieblas'),9451:(11,'La Doncella de la Luz'),9455:(1,'Nace una Señora Demonio'),9456:(2,'Fragmentos del corazón'),9457:(3,'La aparición de la desesperación')}
FONT='/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf'; S=4

def sha(b):return h.sha256(b).hexdigest()
def decode(b):
 pal,=s.unpack_from('<I',b,56); desc,=s.unpack_from('<I',b,40);po,=s.unpack_from('<I',b,desc);w,hh=s.unpack_from('<HH',b,desc+4);cut,=s.unpack_from('<I',b,48);cx,cy,cw,ch=s.unpack_from('<4H',b,cut-8)
 assert w==128 and hh==64 and po+4096==len(b) and pal+1024==po
 a=np.zeros((hh,w),dtype='u1');raw=b[po:]
 for y in range(hh):
  for x in range(w):
   j=((y//8)*(w//32)+x//32)*128+(y%8)*16+(x%32)//2;a[y,x]=(raw[j]>>(4*(x%2)))&15
 return a,pal,po,(cx,cy,cw,ch)
def encode(a):
 raw=bytearray(4096)
 for y in range(64):
  for x in range(128):
   j=((y//8)*4+x//32)*128+(y%8)*16+(x%32)//2;raw[j]|=int(a[y,x])<<(4*(x%2))
 return raw

def glyph(txt,size):
 font=ImageFont.truetype(FONT,size*S);bb=font.getbbox(txt);im=Image.new('L',(bb[2]-bb[0]+4,bb[3]-bb[1]+4));ImageDraw.Draw(im).text((2-bb[0],2-bb[1]),txt,font=font,fill=255);im=im.crop(im.getbbox());return im.resize(((im.width+S-1)//S,(im.height+S-1)//S),Image.Resampling.LANCZOS)
def fit(txt,maxw,maxh,start=13):
 for size in range(start,7,-1):
  im=glyph(txt,size)
  if im.width<=maxw and im.height<=maxh:return im,size
 return None,0

def render(b,g):
 a,pal,po,rect=decode(b);x,y,w,hh=rect;n,title=texts[g];cl=np.frombuffer(b[pal:pal+64],dtype='u1').reshape(16,4);alpha=cl[:,3].astype(int);assert alpha[0]==0 and (alpha[1:]>0).all()
 # Original has 3 separate text bands and final ornamental underline at y+45..49.
 # Preserve the underline and all pixels outside this rectangle exactly.
 a0=a.copy();a[y:y+45,x:x+w]=0
 def place(im,cy):
  xx=x+(w-im.width)//2; yy=y+cy-im.height//2; assert xx>=x and xx+im.width<=x+w and yy>=y and yy+im.height<=y+45
  v=np.array(im).astype(int);q=np.abs(v[:,:,None]-alpha[None,None,:]).argmin(2);assert not a[yy:yy+im.height,xx:xx+im.width].any();a[yy:yy+im.height,xx:xx+im.width]=q
 chapter,cs=fit(f'Capítulo {n}',w-4,12,14);assert chapter is not None;place(chapter,6)
 t,ts=fit(title,w-4,13,14)
 if ts>=11:parts=[title];place(t,20)
 else:
  words=title.split();options=[]
  for i in range(1,len(words)):
   parts2=[' '.join(words[:i]),' '.join(words[i:])];v1,s1=fit(parts2[0],w-4,10,13);v2,s2=fit(parts2[1],w-4,10,13)
   if v1 is not None and v2 is not None:options.append((min(s1,s2),-abs(v1.width-v2.width),parts2))
  assert options;ts,_,parts=max(options,key=lambda q:q[:2]);place(glyph(parts[0],ts),18);place(glyph(parts[1],ts),28)
 fin,fs=fit('Fin',w-4,11,14);assert fin is not None;place(fin,39)
 mask=np.zeros_like(a,dtype=bool);mask[y:y+45,x:x+w]=True;assert np.array_equal(a[~mask],a0[~mask]);assert np.array_equal(a[y+45:y+hh],a0[y+45:y+hh]);assert bytes(encode(a0))==b[po:]
 new=b[:po]+bytes(encode(a));assert len(new)==len(b) and new[:po]==b[:po];assert np.array_equal(decode(new)[0],a)
 return new,dict(group=g,chapter=n,title=title,lines=parts,rect=list(rect),pixel_start=po,changed_pixels=int((a!=a0).sum()),chapter_font_size=cs,title_font_size=ts,fin_font_size=fs),Image.fromarray(cl[a0]),Image.fromarray(cl[a])

def main():
 shutil.copyfile(base,target);reports=[];ims={};patches={}
 with base.open('rb') as f,original.open('rb') as o,target.open('r+b') as dst:
  for r in rows:
   off,n,g=int(r['offset']),int(r['size']),int(r['group']);f.seek(off);b=f.read(n);o.seek(off);assert b==o.read(n) and sha(b)==r['original_sha256'];assert s.unpack_from('<H',b,4)[0]==g
   new,j,im0,im1=render(b,g);j.update(member=r['member'],offset=off,size=n,original_sha256=sha(b),new_sha256=sha(new));assert new!=b;dst.seek(off);dst.write(new);dst.seek(off);assert dst.read(n)==new
   if g in patches:assert patches[g]==new
   else:patches[g]=new;ims[g]=(im0,im1)
   reports.append(j)
 # Verify all bytes of whole ISO outside the edited blocks.
 with base.open('rb') as a,target.open('rb') as b:
  cur=0
  for off,n in sorted([(j['offset'],j['size']) for j in reports])+[(base.stat().st_size,0)]:
   for pos in range(cur,off,4*1024*1024):
    m=min(4*1024*1024,off-pos);a.seek(pos);b.seek(pos);assert a.read(m)==b.read(m)
   cur=off+n
 assert target.stat().st_size==base.stat().st_size
 # Actual texture comparison, no simulated emulator.
 sheet=Image.new('RGB',(2*300,14*160),(22,22,26));d=ImageDraw.Draw(sheet)
 for i,g in enumerate(sorted(ims)):
  for k,im in enumerate(ims[g]):
   x=k*300;y=i*160;d.text((x+8,y+4),f'{g}  '+('Original' if k==0 else 'Nueva edición ES'),fill='white');im=im.resize((256,128),Image.Resampling.NEAREST);sheet.paste(im,(x+20,y+24),im)
 sheet.save('/mnt/data/RC041_REV3_Cierres_comparacion.png')
 (p/'closures.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));(p/'assets').mkdir(exist_ok=True)
 for g,b in patches.items():(p/'assets'/f'{g}.bin').write_bytes(b)
 print('verified',len(reports),'physical;',len(ims),'unique')
if __name__=='__main__':main()
