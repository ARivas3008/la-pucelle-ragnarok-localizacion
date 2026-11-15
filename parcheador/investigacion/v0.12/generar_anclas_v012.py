#!/usr/bin/env python3
import csv,sys,json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]/'v0.11'
sys.path.insert(0,str(ROOT))
from auditar_66 import physical_file,exact_match
from script_relocator import ScriptTable
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reubicador_anclas_v012 import limites_cp932

def run(audit,source,out):
 with Path(audit).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 result=[];sources={}
 for r in rows:
  if r['tipo']!='SCRIPT':continue
  fn=physical_file(Path(source),r['recurso']);b=sources.setdefault(r['recurso'],fn.read_bytes());t=ScriptTable(b)
  off=int(r['offset']);_,old=exact_match(b,off,r['original']);rel=off-t.body
  positions=[(i,p-rel) for i,p in enumerate(t.pointers) if rel<=p<rel+len(old)+1]
  limits=set(limites_cp932(old));bad=[(i,p) for i,p in positions if p not in limits]
  if not positions:continue
  next_three=b[off+len(old)+1:off+len(old)+4]
  result.append({'unit_id':r['unit_id'],'recurso':r['recurso'],'offset_fuente':off,
   'anclas_interiores':len(positions),'anclas_subcaracter':len(bad),
   'offsets_relativos':';'.join(str(k) for i,k in positions),
   'offsets_subcaracter':';'.join(str(k) for i,k in bad),
   'hay_opcode_vacio_siguiente':next_three==b'\x32\x01\x00',
   'dividir_sin_nuevo_opcode':'CANDIDATO_SOLO_CON_PRUEBA_EN_ESCENA' if bad and next_three==b'\x32\x01\x00' else 'NO_VERIFICADO',
   'nota':'No insertar una segunda caja sin validar flujo/temporización',
   'original':r['original'],'es_revisado':r['es_revisado']})
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with (out/'auditoria_anclas.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
 res={'casos_con_anclas':len(result),'casos_subcaracter':sum(int(r['anclas_subcaracter'])>0 for r in result),
      'anclas_subcaracter':sum(int(r['anclas_subcaracter']) for r in result),
      'segundos_slots_vacios_en_casos_subcaracter':sum(int(r['anclas_subcaracter'])>0 and r['hay_opcode_vacio_siguiente'] for r in result),
      'nota':'Slot vacío no acredita que se pueda dibujar un segundo mensaje en la misma escena'}
 (out/'resumen_anclas.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf-8')
 return res
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--auditoria',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 x=p.parse_args();print(json.dumps(run(x.auditoria,x.source,x.output),ensure_ascii=False,indent=2))
