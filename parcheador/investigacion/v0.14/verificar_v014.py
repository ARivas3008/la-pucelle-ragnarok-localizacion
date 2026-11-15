#!/usr/bin/env python3
"""Validación binaria repetible después de generar salida con v0.14.

Se invoca con las ISO y el directorio de EDAT originales y reconstruidos. No
confunde reversibilidad de contenedor con jugabilidad en PPSSPP.
"""
import sys,json,hashlib,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'app/scripts'))
from construir_parche import Image,members_from_dat
from nis_formats import lzs_decompress,nispack
from fuentes_es import CODIGOS,index_sjis

def hash(x):return hashlib.sha256(x).hexdigest()

def get(iso,path):
 disc=Image(iso)
 recs={p:(o,n,r) for p,o,n,r in disc.records()}
 if path not in recs:raise ValueError('Falta '+path)
 return disc.read(*recs[path][:2])

def members(iso):
 return {k:bytes(v) for k,v in members_from_dat(lzs_decompress(get(iso,'/PSP_GAME/USRDIR/START_JP.LZS'))).items()}

def inspect(original,modified,old_dlc,new_dlc):
 original=Path(original);modified=Path(modified);old_dlc=Path(old_dlc);new_dlc=Path(new_dlc)
 old=members(original);new=members(modified)
 if old.keys()!=new.keys():raise ValueError('Miembros ISO_START inconsistentes')
 protected=[k for k in old if k not in ('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp','script00.dat')]
 textures=[k for k in protected if k.lower().endswith('.txp')]
 assert all(old[k]==new[k] for k in protected),'Recurso ISO_START ajeno alterado'
 assert get(original,'/PSP_GAME/SYSDIR/EBOOT.BIN')==get(modified,'/PSP_GAME/SYSDIR/EBOOT.BIN'),'EBOOT alterado'
 orig_script={r['name']:r['content'] for r in nispack(get(original,'/PSP_GAME/USRDIR/SCRIPTPACK.DAT'))}
 mod_script={r['name']:r['content'] for r in nispack(get(modified,'/PSP_GAME/USRDIR/SCRIPTPACK.DAT'))}
 assert orig_script.keys()==mod_script.keys(),'SCRIPTPACK miembros perdidos'
 assert all(orig_script[k]==mod_script[k] for k in orig_script if not k.startswith('script')),'Talks u otros recursos cambiaron'
 # Now Loading fue excluido y se encuentra exactamente en el mismo miembro.
 oldnow='現在読み込み中……'.encode('cp932')
 assert old['script00.dat'].count(oldnow)==new['script00.dat'].count(oldnow)
 res={'iso_no_script_miembros_preservados':len(protected),'iso_texturas_intactas':len(textures),
      'eboot_preservado':True,'talk_members_preservados':sum(k.startswith('talk') for k in orig_script),
      'now_loading_iso_conservado':True,'iso_total_bytes':modified.stat().st_size}
 for i in range(4):
  key=f'DLC_{i:02d}';a=old_dlc/f'DL_JP_{i:02d}.EDAT';b=new_dlc/f'{key}_SCRIPT_V014_EXPERIMENTAL.EDAT'
  olddat=members_from_dat(lzs_decompress(nispack(a.read_bytes())[0]['content']))
  newdat=members_from_dat(lzs_decompress(nispack(b.read_bytes())[0]['content']))
  assert set(olddat)==set(newdat),'Miembros del DLC cambiaron'
  expected={'fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp'}
  if i==0:expected.add('script00.dat')
  assert all(bytes(olddat[k])==bytes(newdat[k]) for k in olddat if k not in expected),'Otros miembros DLC alterados'
  if i==0:
   assert bytes(olddat['script00.dat']).count(oldnow)>0, 'No se detectó texto de carga en DLC 00'
   assert bytes(olddat['script00.dat']).count(oldnow)==bytes(newdat['script00.dat']).count(oldnow)
  fnt=struct.unpack('<11616H',newdat['fontB.fnt'])
  assert all(fnt[index_sjis(code)]!=0 for code in CODIGOS.values()),'Hay glifos españoles ausentes'
  res[key]={'otros_miembros_preservados':len(olddat)-len(expected),'glifos_es_presentes':len(CODIGOS)}
 res['resultado']='Valida miembros y empaquetado; NO certifica PPSSPP'
 return res

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser()
 for name in ('original_iso','iso','original_dlc','dlc'):p.add_argument('--'+name.replace('_','-'),type=Path,required=True)
 p.add_argument('--salida',type=Path,required=True)
 a=p.parse_args();qa=inspect(a.original_iso,a.iso,a.original_dlc,a.dlc);a.salida.parent.mkdir(parents=True,exist_ok=True)
 a.salida.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(qa,ensure_ascii=False,indent=2))