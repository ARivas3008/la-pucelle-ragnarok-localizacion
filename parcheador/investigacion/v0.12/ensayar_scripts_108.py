#!/usr/bin/env python3
"""Prueba sobre scripts propios, sin generar ISO ni EDAT de distribución."""
from __future__ import annotations
import csv,json,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'v0.11'))
from reubicador_anclas_v012 import Reubicador,Edicion,ReubicacionInsegura,limites_cp932
from script_relocator import ScriptTable
from fuentes_es import encode_es
from auditar_66 import physical_file,exact_match

def main(audit,source,dest,save=False,experimental=False):
 source=Path(source);dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
 with Path(audit).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 items=defaultdict(list);ledger=[]
 for r in rows:
  if r['tipo']!='SCRIPT':continue
  if 'Now Loading' in r['original'] or '読み込み中' in r['original']:continue
  if r['estado_editorial'] not in ('revisado','requiere_investigacion') or not r['es_revisado']:
   ledger.append({'unit_id':r['unit_id'],'estado':'SIN_ES_APROBADO'});continue
  res=r['recurso'];p=physical_file(source,res)
  if not p or not p.is_file():ledger.append({'unit_id':r['unit_id'],'estado':'FALTA_RECURSO'});continue
  raw=p.read_bytes();off=int(r['offset']);_,old=exact_match(raw,off,r['original'])
  if old is None:ledger.append({'unit_id':r['unit_id'],'estado':'FUENTE_DIFERENTE'});continue
  try:new=encode_es(r['es_revisado'])
  except Exception as e:ledger.append({'unit_id':r['unit_id'],'estado':'NO_CODIFICABLE','motivo':str(e)});continue
  # Los punteros en la cola de un byte Shift-JIS no pueden reubicarse
  # con una correspondencia segura de caracteres.
  tab=ScriptTable(raw); rel=off-tab.body;boundaries=set(limites_cp932(old))
  anchors=[(i,p-rel) for i,p in enumerate(tab.pointers) if rel<=p<rel+len(old)+1]
  unaligned=[(i,p) for i,p in anchors if p not in boundaries]
  if unaligned and not experimental:
   ledger.append({'unit_id':r['unit_id'],'estado':'ANCLA_SUBCARACTER_NO_RESUELTA',
                  'motivo':f'{len(unaligned)} referencia(s) en mitad de carácter Shift-JIS'})
   continue
  items[res].append(Edicion(off,old,new,r['unit_id']))
 output=[];files=[]
 for res,edits in sorted(items.items()):
  p=physical_file(source,res);raw=p.read_bytes()
  try:patched,journal=Reubicador(raw,permitir_subcaracter=experimental).aplicar(edits)
  except (ReubicacionInsegura,ValueError) as e:
   for x in edits:output.append({'unit_id':x.unit_id,'estado':'SCRIPT_NO_REUBICADO','motivo':str(e)})
   continue
  if save:
   target=dest/'copias'/res.replace('/','__');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(patched)
  for e in edits:output.append({'unit_id':e.unit_id,'estado':'REUBICACION_ESTRUCTURAL_OK','motivo':'Sin prueba PPSSPP'})
  files.append({'recurso':res,'sha256_fuente':hashlib.sha256(raw).hexdigest(),
                'sha256_ensayo':hashlib.sha256(patched).hexdigest(),
                'cadenas':len(edits),'anclas':journal['anclas_reubicadas'],
                'correcciones_subcaracter_experimentales':len(journal['anclas_subcaracter_corregidas_experimentalmente'])})
  if save:(dest/f'diario_{p.name}.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2),encoding='utf-8')
 ledger+=output
 with (dest/'auditoria_scripts.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['unit_id','estado','motivo'],extrasaction='ignore');w.writeheader();w.writerows(ledger)
 result={'estados':dict(Counter(r['estado'] for r in ledger)),'archivos':files,'total_anclas':sum(r['anclas'] for r in files),
         'correcciones_subcaracter':sum(r['correcciones_subcaracter_experimentales'] for r in files),
         'modo_experimental':experimental,
         'aviso':'Solo prueba estructural reversible, NO aprobado para ejecución en PPSSPP.'}
 (dest/'resumen_scripts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--auditoria',type=Path,required=True);a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--guardar-borradores',action='store_true');a.add_argument('--anclas-subcaracter-experimentales',action='store_true');x=a.parse_args()
 print(json.dumps(main(x.auditoria,x.source,x.output,x.guardar_borradores,x.anclas_subcaracter_experimentales),ensure_ascii=False,indent=2)[:1600])
