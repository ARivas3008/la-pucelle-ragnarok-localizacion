from pathlib import Path
import csv,sys,json,collections
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
# Reutiliza exclusivamente la carga de originales, antes de compilar.
scope={'__file__':str(B/'planificar_todos_dialogos.py')}
exec((B/'planificar_todos_dialogos.py').read_text(encoding='utf-8').split('trie,rejected=')[0],scope)
from recompilar_talk import runs,canon
groups=collections.defaultdict(list)
for row in scope['manifest']:groups[row['grupo_id']].append(row)
bad=json.loads((B/'informes/grupos_no_catalogados.json').read_text(encoding='utf-8'))
targets={'14685','14901','5091','3907','5106','15184'}
for gid in targets:bad.setdefault(gid,'Caso de captura del usuario')
report=[]
for gid,reason in bad.items():
 if 'control' not in reason and gid not in targets:continue
 units=groups[gid];res=units[0]['recurso'];raw=scope['buffers'][res];meta=scope['metas'][res]
 wanted={int(u['offset']) for u in units}
 affected=[run for run in runs(raw,meta) if any(t['offset'] in wanted for t in run)]
 report.append(dict(gid=gid,recurso=res,es=scope['reviews'].get(gid,{}).get('es_revisado',''),
  runs=[[dict(offset=t['offset'],original=t['raw'].decode('cp932'),en_grupo=t['offset'] in wanted,choice=t.get('choice',False)) for t in run] for run in affected]))
(B/'informes/huecos_corpus.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Grupos',len(report),'en un bloque',sum(len(r['runs'])==1 for r in report))
for r in report:
 if r['gid'] in {'5263','5284','5324','3806','5513'}:
  print(r['gid'],r['es'])
  for run in r['runs']:print([(t['offset'],canon(t['original']),t['en_grupo']) for t in run])
  raw=scope['buffers'][r['recurso']]
  for left,right in zip(r['runs'],r['runs'][1:]):
   end=raw.find(b'\0',left[-1]['offset'])
   print('ENTRE',raw[end:right[0]['offset']].hex())
