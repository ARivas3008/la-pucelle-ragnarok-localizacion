#!/usr/bin/env python3
"""Une el ensayo y la auditoría para crear una cola verificable de unidades no resueltas."""
import csv, argparse, json
from collections import Counter
from pathlib import Path

def rows(path):
 with path.open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))

def run(audit_path, trial_path, out):
 audit={r['unit_id']:r for r in rows(audit_path)}
 trials=rows(trial_path)
 if len(trials)!=4507 or len(audit)!=4507:raise ValueError('Faltan unidades o hay identificadores repetidos')
 blockers=[]
 for r in trials:
  if r['estado']=='INSERTADO_ESTRUCTURAL':continue
  x=audit[r['unit_id']]
  blockers.append({**r,'grupo_id':x['grupo_id'],'tipo':x['tipo'],'offset':x['offset'],
   'capacidad_total':x['capacidad_total'],'bytes_espanol':x['bytes_espanol'],
   'estado_editorial':x['estado_editorial'],'original':x['original'],'es_revisado':x['es_revisado']})
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(blockers[0]));writer.writeheader();writer.writerows(blockers)
 stats={'total_pendiente':len(blockers),'por_estado':dict(Counter(x['estado'] for x in blockers))}
 (out.parent/'pendientes_66_resumen.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
 return stats

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--auditoria',required=True,type=Path);p.add_argument('--ensayo',required=True,type=Path);p.add_argument('--salida',required=True,type=Path)
 a=p.parse_args()
 print(json.dumps(run(a.auditoria,a.ensayo,a.salida),ensure_ascii=False,indent=2))
