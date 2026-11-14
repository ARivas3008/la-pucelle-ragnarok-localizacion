import json
from collections import Counter
from util import load
result=[]
for i in range(1,16):
 code=f'{i:02}';rows=load(f'corpus/{code}/revision.csv'); counts=Counter(x['estado'] for x in rows)
 result.append({'corpus':code,'total':len(rows),'revisados':counts['revisado'],'en_revision':counts['en_revision'],'investigacion':counts['requiere_investigacion'],'pendientes':counts['pendiente']})
print(json.dumps({'corpus':result,'revisados_total':sum(x['revisados'] for x in result),'universo':15016},ensure_ascii=False,indent=2))
