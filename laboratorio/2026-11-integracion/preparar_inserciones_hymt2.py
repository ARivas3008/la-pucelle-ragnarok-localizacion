from pathlib import Path
import json,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from recompilar_talk import wrap
out={}
def add(r,es,gid,origin):
 if r.get('opcion') and len(wrap(es))!=1:raise ValueError('Opción excesiva: '+es)
 key=(r['recurso'],r['offset'])
 value=dict(grupo_id=gid,recurso=r['recurso'],offset=r['offset'],original_hex=r['original_hex'],es=es,procedencia=origin)
 if key in out and out[key]['es']!=es:raise ValueError('Conflicto de revisión: '+str(key))
 out[key]=value
for r in json.loads((B/'informes/reutilizables_corpus.json').read_text(encoding='utf8')):
 es='Catedral Santa Doncella' if r['opcion'] and r['grupo_id']=='1130' else r['es']
 add(r,es,r['grupo_id'],'Corpus revisado, bloque completo cotejado; opción 1130 abreviada para una línea')
for p in sorted((B/'hymt2_revisados').glob('lote*.json')):
 for r in json.loads(p.read_text(encoding='utf8')):
  if r['estado']!='revisado':raise ValueError('Borrador no aprobado')
  for a in r['apariciones']:add(a,r['es'],'HYMT2:'+r['id'],r['procedencia'])
target=B/'fuente/parcheador/app/datos/segmentos_hymt2_aprobados.json'
target.write_text(json.dumps(list(out.values()),ensure_ascii=False,indent=2),encoding='utf8')
print('Segmentos físicos listos:',len(out))
