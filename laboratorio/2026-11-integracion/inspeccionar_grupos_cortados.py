from pathlib import Path
import json,csv,sys,collections
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as c
bad=json.loads((B/'informes/grupos_no_catalogados.json').read_text(encoding='utf-8'))
rows=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')));groups=collections.defaultdict(list)
for r in rows:groups[r['grupo_id']].append(r)
reviews,_,_=c.read_reviews(B/'fuente',False)
for gid,reason in list((g,m) for g,m in bad.items() if 'control' in m)[:25]:
 print(gid,groups[gid][0]['recurso'],[(u['offset'],u['original']) for u in groups[gid]],'ES:',reviews[gid]['es_revisado'])
