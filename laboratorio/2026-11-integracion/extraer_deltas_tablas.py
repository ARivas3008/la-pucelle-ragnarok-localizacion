"""Migra las tablas ya insertadas a diferencias reproducibles desde originales."""
from pathlib import Path
import sys,json,hashlib,zlib
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as c
from nis_formats import lzs_decompress,nispack
im=c.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in im.records()}
sources={'ISO_START':im.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])}
for n in range(4):sources[f'DLC_{n:02d}']=nispack((R/f'ULJS00244/ULJS00244/DL_JP_{n:02d}.EDAT').read_bytes())[0]['content']
patches={}
for key,lzs in sources.items():
 original=c.members_from_dat(lzs_decompress(lzs));cached=c.members_from_dat(lzs_decompress((B/'recursos_base'/('START_JP.LZS' if key=='ISO_START' else key+'.lzs')).read_bytes()))
 for name,before in original.items():
  after=cached[name]
  if before==after:continue
  if name.startswith(('talk','script','fontB','FontB')) or name in ('sys3.txp','sys4.txp'):continue
  if name not in ('char.dat','com.dat','kis.dat','magic.dat','mapinfo.dat','name.dat','ritem.dat','skill.dat'):
   raise ValueError('Recurso modificado inesperado: '+key+'/'+name)
  assert len(before)==len(after)
  changes=[];i=0
  while i<len(before):
   if before[i]==after[i]:i+=1;continue
   start=i
   while i<len(before) and before[i]!=after[i]:i+=1
   changes.append([start,bytes(after[start:i]).hex()])
  patches[key+'/'+name]=dict(original_sha256=c.sh(before),nuevo_sha256=c.sh(after),size=len(before),changes=changes)
target=B/'fuente/parcheador/app/datos/tablas_base_deltas.json.z'
target.write_bytes(zlib.compress(json.dumps(patches,separators=(',',':')).encode(),9))
print('Tablas',len(patches),'bytes de diferencias comprimidas',target.stat().st_size)
print('\n'.join(patches))
