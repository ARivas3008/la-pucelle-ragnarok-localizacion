"""Experimento GFX-007 local: no distribuye texturas originales ni reconstruidas.

Dependencias del laboratorio: numpy, Pillow, opencv-python.
La salida es un piloto estático, no certificado en PPSSPP.
"""
import struct,hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

TITLES={1:'Aprender el oficio',2:'La promesa de un niño',3:'Prier y Alouette',4:'Un problema gigantesco',5:'Un asunto peliagudo',6:'El viaje',7:'Un baile en el cielo',8:'Hacia una tierra inexplorada',9:'Recuerdos de Fátima',10:'El príncipe de las tinieblas',11:'La Doncella de la Luz',12:'Nace una leyenda',15:'Nace una Señora Demonio',16:'La Señora Demonio',17:'El emperador de la desesperación',18:'El espíritu de las tinieblas'}
LIMITS=(50,35,430,116)
def unpack(raw):
 w,h,colors,_,decl,banks,_,_=struct.unpack_from('<8H',raw)
 if (w,h,colors,decl,banks)!=(480,170,256,256,1) or len(raw)!=82640:raise ValueError('unexpected chapter format')
 palette=np.frombuffer(raw[16:1040],np.uint8).reshape(256,4)
 indices=np.empty((h,w),np.uint8);pos=1040
 for y in range(0,h,8):
  n=min(8,h-y)
  for x in range(0,w,16):
   indices[y:y+n,x:x+16]=np.frombuffer(raw[pos:pos+n*16],np.uint8).reshape(n,16);pos+=n*16
 assert pos==len(raw)
 return indices,palette

def pack(original,indices):
 out=bytearray(original[:1040])
 for y in range(0,170,8):
  for x in range(0,480,16):out.extend(indices[y:y+8,x:x+16].tobytes())
 assert len(out)==len(original);return bytes(out)

def quantize(rgb,palette):
 out=np.empty(len(rgb),np.uint8)
 for i in range(0,len(rgb),512):
  c=rgb[i:i+512].astype(np.int32);out[i:i+len(c)]=np.argmin(((c[:,None,:]-palette[None,:,:3].astype(np.int32))**2).sum(2),axis=1)
 return out

def edit(raw,num,fontpath):
 ind,pal=unpack(raw);assert pack(raw,ind)==raw
 rgb=pal[ind,:3].copy();ink=pal[1,:3].astype(np.float32)
 engw={1:246,2:264,3:213,4:252,5:217,6:132,7:230,8:304,9:244,10:225,11:182,12:207,15:184,16:187,17:274,18:229}[num]
 box=np.zeros((170,480),np.uint8)
 box[40:67,168:312]=1
 box[78:110,240-engw//2-6:240+engw//2+6]=1
 dist=np.sqrt(((rgb.astype(np.float32)-ink)**2).sum(2))
 mask=((dist<42)&(box>0)).astype(np.uint8)
 mask=cv2.dilate(mask,np.ones((3,3),np.uint8));mask&=box
 # Restauración aproximada del área de tinta, no recuperación exacta del arte oculto.
 cleaned=cv2.inpaint(rgb,mask*255,3,cv2.INPAINT_TELEA)
 alpha=Image.new('L',(480,170));draw=ImageDraw.Draw(alpha)
 for line,cy,maxw in [(f'Capítulo {num if num<15 else num-14}',53,190),(TITLES[num],93,360)]:
  size=27
  while True:
   f=ImageFont.truetype(fontpath,size);b=draw.textbbox((0,0),line,font=f)
   if b[2]-b[0]<=maxw or size<=16:break
   size-=1
  draw.text((240-(b[2]-b[0])/2-b[0],cy-(b[3]-b[1])/2-b[1]),line,font=f,fill=255)
 a=np.array(alpha,dtype=np.float32)/255
 active=(mask>0)|(a>0);out=ind.copy();target=cleaned.astype(np.float32)*(1-a[:,:,None])+ink*a[:,:,None]
 out[active]=quantize(np.rint(target[active]).astype(np.uint8),pal)
 assert not np.any(out[:35]!=ind[:35]) and not np.any(out[116:]!=ind[116:])
 assert not np.any(out[:,:50]!=ind[:,:50]) and not np.any(out[:,430:]!=ind[:,430:])
 data=pack(raw,out);assert data[:1040]==raw[:1040] and np.array_equal(unpack(data)[0],out)
 return data, {'original_sha256':hashlib.sha256(raw).hexdigest(),'nuevo_sha256':hashlib.sha256(data).hexdigest(),'pixeles_modificados':int((out!=ind).sum()),'rectangulo_autorizado':LIMITS,'titulo':f'Capítulo {num if num<15 else num-14} / {TITLES[num]}'}

def main():
 import argparse,json,sys,shutil
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--iso-original',type=Path,required=True)
 p.add_argument('--salida',type=Path,required=True)
 p.add_argument('--fuente',type=Path,required=True,help='LiberationSerif-Bold.ttf local')
 p.add_argument('--informe',type=Path,required=True)
 args=p.parse_args()
 if args.salida.resolve()==args.iso_original.resolve() or args.salida.exists():raise ValueError('Elegir otra ruta de salida nueva')
 root=Path(__file__).resolve().parent
 sys.path.insert(0,str(root))
 from verificar_iso_aislamiento import inventory
 ref=json.loads((root.parent/'docs/seguimiento/informes/GFX-007_capitulos_piloto.json').read_text(encoding='utf8'))
 with args.iso_original.open('rb') as f: original_sha=hashlib.file_digest(f,'sha256').hexdigest()
 if original_sha!=ref['iso_original_sha256']:raise ValueError('ISO original no autenticada')
 files,_=inventory(str(args.iso_original));off,size=files['PSP_GAME/USRDIR/BGPACK.DAT']
 with args.iso_original.open('rb') as f:f.seek(off);original=f.read(size)
 if hashlib.sha256(original).hexdigest()!=ref['BGPACK_original_sha256']:raise ValueError('BGPACK distinto')
 patched=bytearray(original);result={}
 for i in range(struct.unpack_from('<I',original,12)[0]):
  n,o,sz,u=struct.unpack_from('<32sIII',original,16+44*i);n=n.partition(bytes(1))[0].decode('cp932')
  if n not in ref['assets']:continue
  raw=original[o:o+sz]
  if hashlib.sha256(raw).hexdigest()!=ref['assets'][n]['original_sha256']:raise ValueError('TXP original distinto: '+n)
  new,proof=edit(raw,int(n[2:4]),args.fuente)
  if proof['nuevo_sha256']!=ref['assets'][n]['nuevo_sha256']:raise ValueError('Salida no reproducible: '+n+'; comprobar dependencias y fuente')
  patched[o:o+sz]=new;result[n]=proof
 if set(result)!=set(ref['assets']) or hashlib.sha256(patched).hexdigest()!=ref['BGPACK_piloto_sha256']:raise ValueError('BGPACK final no reproducible')
 shutil.copyfile(args.iso_original,args.salida)
 try:
  with args.salida.open('r+b') as f:f.seek(off);f.write(patched)
  with args.salida.open('rb') as f: output_sha=hashlib.file_digest(f,'sha256').hexdigest()
  if output_sha!=ref['iso_piloto_sha256']:raise ValueError('ISO final no reproducible')
 except Exception:
  args.salida.unlink(missing_ok=True);raise
 args.informe.write_text(json.dumps({'iso_original_sha256':original_sha,'iso_piloto_sha256':output_sha,'assets':result,'ppsspp':False},ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
