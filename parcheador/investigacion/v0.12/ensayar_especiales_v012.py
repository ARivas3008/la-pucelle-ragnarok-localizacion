#!/usr/bin/env python3
"""Cinco sustituciones de campos excepcionales: no tocar los bytes vecinos."""
import csv,sys,json,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]/'v0.11'
sys.path.insert(0,str(ROOT))
from campos_v011 import reemplazar_en_hueco_original,CampoError
from auditar_66 import physical_file,exact_match
from fuentes_es import encode_es
SPECIAL={
 '1804':('(Bloq. giro','Abreviación de bloqueo circular; exige cotejo editorial'),
 '23133':('Culazo','Nombre de técnica Butt Attack; humor coloquial; cotejar'),
 '23302':('Mil cajas','Boxes Galore; título condensado'),
 '24106':('Muro mágico','Magic Barrier; sin cambio de función'),
 '24111':('(Muro celeste','Heaven Barrier; fragmento con prefijo de control conservado'),
}

def run(audit,source,out,save=False):
 rows={r['unit_id']:r for r in csv.DictReader(Path(audit).open(encoding='utf-8-sig'))}
 grouped=defaultdict(list)
 for uid,(text,note) in SPECIAL.items():grouped[rows[uid]['recurso']].append((uid,text,note))
 out=Path(out);out.mkdir(parents=True,exist_ok=True);records=[];sha=[]
 for res,ls in grouped.items():
  path=physical_file(Path(source),res);raw=path.read_bytes();patch=raw
  for uid,text,note in ls:
   r=rows[uid];off=int(r['offset']);match,old=exact_match(raw,off,r['original']);new=encode_es(text)
   if not old:raise ValueError(f'Fuente no coincide unidad {uid}')
   patch=reemplazar_en_hueco_original(patch,off,old,new)
   records.append({'unit_id':uid,'recurso':res,'original':r['original'],'traduccion':text,
                   'bytes_fuente':len(old),'bytes_es':len(new),'nota':note,'estado':'BINARIO_REVERSIBLE_COTEJO_PENDIENTE'})
  assert len(patch)==len(raw)
  sha.append({'recurso':res,'sha_original':hashlib.sha256(raw).hexdigest(),
              'sha_modificado':hashlib.sha256(patch).hexdigest()})
  if save:
   d=out/'borradores'/res.replace('/','__').replace('.','_');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(patch)
 with (out/'casos_especiales.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 (out/'resumen_especiales.json').write_text(json.dumps({'cantidad':len(records),'recursos':sha,'advertencia':'Sin cotejo editorial ni PPSSPP'},ensure_ascii=False,indent=2),encoding='utf-8')
 return records
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--auditoria',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--guardar-borradores',action='store_true');args=p.parse_args()
 print(len(run(args.auditoria,args.source,args.output,args.guardar_borradores)))
