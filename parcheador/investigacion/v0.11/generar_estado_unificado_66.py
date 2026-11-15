#!/usr/bin/env python3
"""Crea un estado único para los 66 recursos sin fingir compatibilidad PSP."""
import argparse,csv,json
from pathlib import Path
from collections import Counter

def read(f):
 with f.open(encoding='utf-8-sig',newline='') as x:return list(csv.DictReader(x))

def run(audit,dat,eboot,output):
 a=read(audit);p={x['unit_id']:x for x in read(dat)};e={x['unit_id']:x for x in read(eboot)}
 if len(a)!=4507 or len(p)!=4507 or len(e)!=259:raise ValueError('Faltan unidades')
 rows=[]
 for r in a:
  uid=r['unit_id'];pstatus=p[uid]['estado'];why=p[uid]['motivo']
  if r['tipo']=='EBOOT':
   q=e[uid];pstatus=('CANDIDATO_EBOOT' if q['estado']=='ASCII_TAMANO_FIJO' else 'EBOOT_'+q['estado']);why=q['motivo']
  elif pstatus=='INSERTADO_ESTRUCTURAL':pstatus='CANDIDATO_DAT'
  rows.append({'unit_id':uid,'grupo_id':r['grupo_id'],'recurso':r['recurso'],
   'tipo':r['tipo'],'estado_tecnico':pstatus,'motivo':why,'estado_editorial':r['estado_editorial'],
   'bytes_espanol':r['bytes_espanol'],'capacidad_total':r['capacidad_total'],
   'original':r['original'],'es_revisado':r['es_revisado']})
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 st=Counter(r['estado_tecnico'] for r in rows)
 result={'unidades_total':4507,'recursos_total':66,'estados':dict(st),
  'candidatos_estructurales':st['CANDIDATO_DAT']+st['CANDIDATO_EBOOT'],
  'candidatos_no_aprobados_ppsspp':st['CANDIDATO_DAT']+st['CANDIDATO_EBOOT'],
  'otras_unidades':4507-st['CANDIDATO_DAT']-st['CANDIDATO_EBOOT'],
  'aviso':'No hay 100 % de reinserción, solo candidatos. No se ha ejecutado el juego modificado.'}
 (output.parent/'estado_unificado_66.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for x in ('auditoria','ensayo','eboot','salida'):p.add_argument('--'+x,required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.auditoria,a.ensayo,a.eboot,a.salida),ensure_ascii=False,indent=2))
