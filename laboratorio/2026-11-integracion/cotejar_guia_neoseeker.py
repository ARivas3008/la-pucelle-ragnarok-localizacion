"""Cotejo textual auxiliar; PS2 no constituye inventario de Ragnarok."""
from pathlib import Path
import json,csv,re,unicodedata,collections
B=Path(__file__).resolve().parent
guide=(B/'referencias_web/neoseeker_78770_visible.txt').read_text(encoding='utf8')
assert '- End of Frequently Asked Questions Document -' in guide
start=guide.index('2.20 Game Script',guide.index('2.20 Game Script')+1)
end=guide.index('3.00 Game Combat',start)
script=guide[start:end]
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKC',s).lower())
normalized=norm(script)
coverage=list(csv.DictReader((B/'informes/cobertura_insercion_real.csv').open(encoding='utf-8-sig',newline='')))
matches=[]
for r in coverage:
 text=unicodedata.normalize('NFKC',r['original'])
 if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',text):continue
 key=norm(text)
 if len(key)<25:continue
 if key in normalized:matches.append(r)
summary=dict(url='https://www.neoseeker.com/la-pucelle/faqs/78770-a.html',titulo='La Pucelle: Tactics FAQ/Walkthrough v1.10',autor='Crimson Phantom',fecha_fuente='2004-06-12',plataforma='PS2',caracteres_documento=len(guide),coincidencias_literales_unidades=len(matches),estados_coincidentes=dict(collections.Counter(r['estado'] for r in matches)),limites=['El autor excluye NPC de la ciudad y tutoriales de su transcripción.','No cubre los añadidos de Ragnarok ni los DLC PSP.','Las diferencias entre japonés original, localización inglesa y transcripción impiden usar ausencia de coincidencia como prueba de texto faltante.','Se cotejan coincidencias de al menos 25 letras/dígitos normalizados. Es evidencia auxiliar; el denominador de cobertura es el manifiesto y los recursos binarios.'])
(B/'informes/cotejo_neoseeker.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
with (B/'informes/coincidencias_neoseeker.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(matches)
print(json.dumps(summary,ensure_ascii=False,indent=2))
