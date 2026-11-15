#!/usr/bin/env python3
"""Recompone y verifica, en RAM/temporal, los 39 recursos modificados.

NO guarda ISO/EDAT/parches de juego, solo JSON QA. No valida ejecución PSP.
El usuario debe proporcionar sus originales y los recursos individuales editados.
"""
import argparse, hashlib, json, sys, subprocess, tempfile, struct
from pathlib import Path
from nis_formats import nispack,lzs_decompress,lzs_header
from iso_inspect import ISO

# El código de los contenedores es parte del paquete de pruebas de la etapa v0.10
from contenedores import reconstruir_nispack, entradas_nispack, reconstruir_dat, entradas_dat

def blobs_dat(raw):
 return {n:raw[a:b] for n,a,b,*_ in entradas_dat(raw)}

def blobs_pack(raw):
 return {n:raw[o:o+s] for n,o,s,*_ in entradas_nispack(raw)[1]}

def get_changes(root,base,old):
 result={}
 for path in sorted((root/base).glob('*.dat')):
  if path.name not in old: raise ValueError(f'Miembro inesperado: {path.name}')
  b=path.read_bytes()
  if b==old[path.name]:raise ValueError(f'Borrador sin modificar: {base}/{path.name}')
  result[path.name]=b
 return result

def verify(source,iso,dlc,packer,output):
 details=[]; changes_total=0
 image=ISO(str(iso))
 try:
  loc={n:(size,off) for n,size,off,isdir in image.walk()}
  script_size,script_off=loc['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']
  scriptpack=image.read(script_off,script_size)
  start_size,start_off=loc['/PSP_GAME/USRDIR/START_JP.LZS']
  iso_start=image.read(start_off,start_size)
 finally:image.fp.close()
 rawmembers=blobs_pack(scriptpack)
 changed=get_changes(source,'ISO_SCRIPT',rawmembers)
 assert changed,'No ISO_SCRIPT proposals'
 rebuilt=reconstruir_nispack(scriptpack,changed)
 reread=blobs_pack(rebuilt)
 if reread.keys()!=rawmembers.keys() or any(reread[n]!=changed.get(n,rawmembers[n]) for n in rawmembers):
  raise ValueError('SCRIPTPACK loss')
 details.append({'contenedor':'ISO/SCRIPTPACK.DAT','miembros_modificados':len(changed),
   'sin_cambios':len(rawmembers)-len(changed),'bytes_antes':len(scriptpack),'bytes_despues':len(rebuilt),'verificado':True})
 changes_total+=len(changed)
 with tempfile.TemporaryDirectory(prefix='lapucelle_66_') as td:
  td=Path(td)
  for area in ['ISO_START','DLC_00','DLC_01','DLC_02','DLC_03']:
   if area=='ISO_START': lz=iso_start
   else:
    edat=(dlc/('DL_JP_'+area[-2:]+'.EDAT')).read_bytes()
    contents=nispack(edat)
    if len(contents)!=1 or contents[0]['name'].lower()!='start_jp.lzs':raise ValueError('DLC no contiene un solo start_jp.lzs')
    lz=contents[0]['content']
   original=lzs_decompress(lz)
   old=blobs_dat(original)
   changes=get_changes(source,area,old)
   after=reconstruir_dat(original,changes)
   got=blobs_dat(after)
   if got.keys()!=old.keys() or any(got[n]!=changes.get(n,old[n]) for n in old):raise ValueError(f'DAT corrupto: {area}')
   h=lzs_header(lz)
   sourcefile=td/(area+'.dat'); compressed=td/(area+'.lzs')
   sourcefile.write_bytes(after)
   args=[str(packer),str(sourcefile),str(compressed),h['ext'].rstrip(b'\x00').decode('ascii'),str(h['marker'])]
   p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   if p.returncode:raise ValueError(f'Compresor {area}: {p.stderr[:500]}')
   if lzs_decompress(compressed.read_bytes())!=after:raise ValueError(f'LZS round trip {area}')
   changes_total+=len(changes)
   details.append({'contenedor':area,'miembros_modificados':len(changes),'sin_cambios':len(old)-len(changes),
     'bytes_antes':len(original),'bytes_despues':len(after),'lzs_comprimido':len(compressed.read_bytes()),'verificado':True})
 summary={'resultado':'EXITO_ESTRUCTURAL','contenedores_verificados':len(details),'recursos_modificados':changes_total,
  'validacion_ppsspp':False,'advertencia':'NO se certifican referencias de bytecode ni aspectos gráficos. No se genera ISO.',
  'detalles':details}
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
 return summary

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--borradores',type=Path,required=True)
 p.add_argument('--iso',type=Path,required=True)
 p.add_argument('--dlc',type=Path,required=True)
 p.add_argument('--packer',type=Path,required=True)
 p.add_argument('--salida',type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(verify(a.borradores,a.iso,a.dlc,a.packer,a.salida),ensure_ascii=False,indent=2))
