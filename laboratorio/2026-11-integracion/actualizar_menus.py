from pathlib import Path
import csv,json,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from fuentes_es import encode_es
updates=json.loads((B/'menus_contextuales.json').read_text(encoding='utf-8'))
path=B/'fuente/parcheador/app/datos/menu_eboot_contextual.csv'
with path.open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
indexed={r['original']:r for r in old}
for source,text in updates.items():
 indexed[source]=dict(original=source,es=text,contexto='Adaptación contextual de integración total; comprobar en HUD')
 if len(encode_es(text))>len(source.encode('ascii')):print('EXCEDE',source,len(source),repr(text),len(encode_es(text)))
with path.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['original','es','contexto']);w.writeheader();w.writerows(indexed.values())
print('Menús',len(indexed))
