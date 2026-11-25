"""Aplica revisiones completas en las reservas verificadas de tablas fijas."""
from pathlib import Path
import json,unicodedata,hashlib
from campos_fijos import capacidad_verificada,PERFILES
from fuentes_es import encode_script_text,decode_es,missing_render_glyphs,FontError
from construir_parche import match_source,ROOT
def conservar_icono(source,text):
 decoded=source.decode('cp932')
 if decoded and decoded[0] in '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳':
  marker=decoded[0];number=unicodedata.normalize('NFKC',marker)
  if text.startswith(marker):return text
  if text.startswith(number):text=text[len(number):].lstrip()
  return marker+text
 return text
def variante_nominal(row,text,raw,cap,variants):
 """Fallback técnico, únicamente para la reserva y la revisión cotejadas."""
 v=variants.get(row['unit_id'])
 if not v or cap!=12 or row['recurso']!='ISO_START/name.dat':return None
 if any(str(row[k])!=str(v[k]) for k in ('unit_id','grupo_id','recurso','offset','original')) or text!=v['revision']:return None
 if hashlib.sha256(raw).hexdigest()!='6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c':return None
 compact=v['compacto']
 if not compact or any(unicodedata.category(x).startswith('C') for x in compact):return None
 try:data=encode_script_text(compact)
 except FontError:return None
 if not data or b'\0' in data or len(data)>=cap:return None
 return compact,data


def variante_tabla_rom019(row,text,raw,cap,variants):
 """Devuelve (texto, bytes, capacidad) solo para anclas ROM-019 exactas.

 Las variantes no sustituyen la revisión editorial. El caso Cafeteria
 limita la escritura al C-string original: el byte 03 posterior se conserva.
 """
 v=variants.get(row['unit_id'])
 if not v or text!=v['revision']:return None
 if any(str(row[k])!=str(v[k]) for k in ('unit_id','grupo_id','recurso','offset','original')):return None
 resource=row['recurso']
 hashes={
  'ISO_START/char.dat':'58c85a8ccec6d3346518e7de9319185cf1f5216bff3e1e067be5638b5653d976',
  'ISO_START/mapinfo.dat':'48a008418abd429ec5408d8de8b6f8c092afebb07db3b35096d308658dd431c6',
 }
 expected=hashes.get(resource)
 if not expected or v['sha256_recurso']!=expected or hashlib.sha256(raw).hexdigest()!=expected:return None
 if v['tipo']=='reserva_original':
  if row['unit_id']!='23493' or resource!='ISO_START/mapinfo.dat' or cap is not None or v['capacidad']!=10:return None
  off=int(row['offset'])
  if off!=3476 or bytes(raw[off:off+12])!=b'Cafeteria\x00\x00\x03':return None
  cap=10
  if v['compacto']!=text:return None
 elif v['tipo']=='compacto':
  expected_cap=24 if resource=='ISO_START/char.dat' else 28
  if cap!=expected_cap or v['capacidad']!=cap:return None
  try:
   if len(encode_script_text(text))<cap:return None
  except FontError:return None
 else:return None
 compact=v['compacto']
 if not compact or any(unicodedata.category(c).startswith('C') for c in compact):return None
 try:data=encode_script_text(compact)
 except FontError:return None
 if not data or b'\0' in data or len(data)>=cap:return None
 return compact,data,cap

def aplicar(key,original,current,manifest,reviews):
 extra=ROOT/'datos/campos_revisados_adicionales.json'
 overrides={r['unit_id']:r for r in json.loads(extra.read_text(encoding='utf8'))} if extra.exists() else {}
 compact_path=ROOT/'datos/nombres_compactos_rom017.json'
 variants={r['unit_id']:r for r in json.loads(compact_path.read_text(encoding='utf8'))} if compact_path.exists() else {}
 table_path=ROOT/'datos/campos_compactos_rom019.json'
 table_variants={r['unit_id']:r for r in json.loads(table_path.read_text(encoding='utf8'))} if table_path.exists() else {}
 journal=[];pending=[]
 for row in manifest:
  res=row['recurso'];name=res.split('/')[-1]
  if not res.startswith(key+'/') or name not in PERFILES:continue
  uid=row['unit_id'];rev=reviews.get(row['grupo_id'],{})
  text=rev.get('es_revisado','');state=rev.get('estado')
  if uid in overrides:
   r=overrides[uid]
   if r['original']!=row['original'] or r['estado']!='revisado':raise ValueError('Revisión adicional no cotejada: '+uid)
   text=r['es'];state='revisado'
  if state!='revisado' or not text:pending.append(dict(unit_id=uid,motivo='Revisión pendiente'));continue
  raw=original[name];off=int(row['offset'])
  style,before=match_source(raw,off,row['original'])
  if not before:raise ValueError('Fuente de tabla distinta: '+uid)
  text=conservar_icono(before,text)
  cap=capacidad_verificada(name,raw,off,len(before))
  full_text=text
  try:data=encode_script_text(text)
  except FontError as e:
   pending.append(dict(unit_id=uid,motivo='Codificación no admitida',detalle=str(e),es=text));continue
  if cap is not None and len(data)>=cap:
   fallback=variante_nominal(row,text,raw,cap,variants)
   if fallback is not None:text,data=fallback
  if cap is None or len(data)>=cap:
   table_fallback=variante_tabla_rom019(row,text,raw,cap,table_variants)
   if table_fallback is not None:text,data,cap=table_fallback
  if cap is None or len(data)>=cap:
   pending.append(dict(unit_id=uid,motivo='No cabe en reserva verificada',capacidad=cap,bytes=len(data),es=text));continue
  missing=missing_render_glyphs(decode_es(data),current)
  if missing:pending.append(dict(unit_id=uid,motivo='Glifos ausentes',glifos=missing));continue
  after=data.ljust(cap,b'\0');current[name][off:off+cap]=after
  journal.append(dict(unit_id=uid,grupo_id=row['grupo_id'],recurso=res,offset=off,capacidad=cap,es=text,revision_completa=full_text,adaptacion_compacta=(text!=full_text),antes_hex=bytes(raw[off:off+cap]).hex(),despues_hex=after.hex()))
 return dict(aplicados=journal,pendientes=pending)
