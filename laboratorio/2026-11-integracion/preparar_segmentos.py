from pathlib import Path
import json,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from recompilar_talk import wrap
review=json.loads((B/'segmentos_revisados.json').read_text(encoding='utf-8'))
sources={r['gid']:r for r in json.loads((B/'informes/huecos_corpus.json').read_text(encoding='utf-8'))}
result={}
for gid,translations in review.items():
 source=sources[gid]
 assert len(translations)==len(source['runs']),(gid,len(translations),len(source['runs']))
 for run,es in zip(source['runs'],translations):
  if run[0]['choice']:assert len(wrap(es))==1,(gid,es)
  row=dict(grupo_id=gid,recurso=source['recurso'],offset=run[0]['offset'],
   original_hex=[t['original'].encode('cp932').hex() for t in run],es=es)
  key=(row['recurso'],row['offset'])
  if key in result:assert result[key]['es']==es,('Revisiones incompatibles',gid,key)
  else:result[key]=row
target=B/'fuente/parcheador/app/datos/segmentos_talk_revisados.json'
target.write_text(json.dumps(list(result.values()),ensure_ascii=False,indent=2),encoding='utf-8')
print('Grupos revisados:',len(review),'segmentos físicos:',len(result))
