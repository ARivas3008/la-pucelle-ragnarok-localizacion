from pathlib import Path
import sys,json,csv,collections
B=Path(__file__).resolve().parent
exec((B/'planificar_todos_dialogos.py').read_text(encoding='utf8').split('manifest=')[0])
from campos_fijos import capacidad_verificada
from fuentes_es import encode_script_text,missing_render_glyphs
rows=list(csv.DictReader((B/'informes/cobertura_insercion_real.csv').open(encoding='utf-8-sig',newline='')))
reviews,_,_=core.read_reviews(B/'fuente',False)
results=[]
for r in rows:
 if r['estado'] not in ('CAMPO_SIN_TRADUCIR','CAMPO_MODIFICADO_COTEJO_PENDIENTE'):continue
 if r['recurso'].startswith('ISO/'):continue
 key,name=r['recurso'].split('/');raw=fonts[key][name];off=int(r['offset']);end=raw.find(b'\0',off)
 capacity=capacidad_verificada(name,raw,off,end-off)
 rev=reviews.get(r['grupo_id'],{});es=rev.get('es_revisado','')
 try:
  encoded=encode_script_text(es);missing=missing_render_glyphs(es,fonts[key])
 except (ValueError,UnicodeError):encoded=b'';missing=['codificacion']
 state='SIN_TRADUCCION' if not es else 'SIN_CAPACIDAD_VERIFICADA' if capacity is None else 'REVISION_PENDIENTE' if rev.get('estado')!='revisado' else 'NO_CABE' if len(encoded)>=capacity else 'GLIFOS_AUSENTES' if missing else 'CABE'
 results.append(dict(**r,capacidad_bytes=capacity,bytes_es=len(encoded),estado_plan=state,estado_editorial=rev.get('estado'),glifos_ausentes=missing))
(B/'informes/campos_pendientes_plan.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print(dict(collections.Counter(r['estado_plan'] for r in results)))
print('Entre campos originales:',dict(collections.Counter(r['estado_plan'] for r in results if r['estado']=='CAMPO_SIN_TRADUCIR')))
