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


def variante_tabla_rom020(row,text,raw,cap,variants):
 """Reservas exactas del piloto ROM-020; no se generalizan offsets atípicos."""
 v=variants.get(row['unit_id'])
 if not v or text!=v['revision']:return None
 if any(str(row[k])!=str(v[k]) for k in ('unit_id','grupo_id','recurso','offset','original')):return None
 resource=row['recurso']
 hashes={
  'ISO_START/com.dat':'817f8759328aa448aa9124a33a6c4dbe4ca16d6327028ed0fe6793707760b7be',
  'ISO_START/skill.dat':'8df0acaff462429663138dc75773a709e1548d5d751ad0649a5283a9c8fc8944',
 }
 expected=hashes.get(resource)
 if not expected or v['sha256_recurso']!=expected or hashlib.sha256(raw).hexdigest()!=expected:return None
 if v['tipo']=='reserva_original':
  special={
   '24106':(3219,'4d616769632042617272696572000000000000000000'),
   '24111':(3689,'2848656176656e204261727269657200000000000000'),
  }.get(row['unit_id'])
  if resource!='ISO_START/skill.dat' or cap is not None or v['capacidad']!=22 or not special:return None
  off,source_hex=special
  if int(row['offset'])!=off or v['fuente_hex']!=source_hex or bytes(raw[off:off+22])!=bytes.fromhex(source_hex):return None
  cap=22
  if v['compacto']!=text:return None
 elif v['tipo']=='compacto':
  if cap not in ((23,49) if resource=='ISO_START/com.dat' else (21,57)) or v['capacidad']!=cap:return None
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


def variante_tabla_rom021(row,text,raw,cap,variants):
 """Compacidad de objetos/modificadores con anclas, reserva y SHA exactos."""
 v=variants.get(row['unit_id'])
 if not v or v['tipo']!='compacto' or text!=v['revision']:return None
 if any(str(row[k])!=str(v[k]) for k in ('unit_id','grupo_id','recurso','offset','original')):return None
 resource=row['recurso']
 profiles={
  'ISO_START/kis.dat':('4bfbd0175f7d8a8feb7bbe8b94379b3cbe10c893c0768430ef9fd80731a135d3',(21,57)),
  'ISO_START/ritem.dat':('3abb44d07f3e07f39626536f0320147776b6913108c6190aca186c108642abbb',(13,43)),
 }
 profile=profiles.get(resource)
 if not profile:return None
 expected,caps=profile
 if cap not in caps or v['capacidad']!=cap or v['sha256_recurso']!=expected or hashlib.sha256(raw).hexdigest()!=expected:return None
 try:
  if len(encode_script_text(text))<cap:return None
 except FontError:return None
 compact=v['compacto']
 if not compact or any(unicodedata.category(c).startswith('C') for c in compact):return None
 # El botón cuadrado es un símbolo funcional, no puntuación decorativa.
 if text.count('□')!=compact.count('□'):return None
 try:data=encode_script_text(compact)
 except FontError:return None
 if not data or b'\0' in data or len(data)>=cap:return None
 return compact,data,cap


def variante_tabla_rom022(row,text,raw,cap,variants):
 """Solo magic.dat ISO auténtica; conservar prefijos funcionales y metadatos."""
 v=variants.get(row['unit_id'])
 if not v or text!=v['revision'] or row['recurso']!='ISO_START/magic.dat':return None
 if any(str(row[k])!=str(v[k]) for k in ('unit_id','grupo_id','recurso','offset','original')):return None
 expected='9018e9c5ea277ad1acd5f9a2a9d10120c3d5864a1ee45d8fe789166b8a138fe3'
 if v['sha256_recurso']!=expected or hashlib.sha256(raw).hexdigest()!=expected:return None
 typ=v['tipo']
 if typ in ('reserva_original','reserva_original_compacta'):
  special={
   '23133':(14178,13,'427574742041747461636b2000',b'\x09','reserva_original_compacta'),
   '23302':(24964,25,'426f7865732047616c6f726500000000000000000000000000',b'\x87\x41','reserva_original'),
  }.get(row['unit_id'])
  if cap is not None or not special:return None
  off,c,source_hex,tail,expected_typ=special
  if int(row['offset'])!=off or v['capacidad']!=c or typ!=expected_typ or v['fuente_hex']!=source_hex:return None
  if bytes(raw[off:off+c])!=bytes.fromhex(source_hex) or bytes(raw[off+c:off+c+len(tail)])!=tail:return None
  cap=c
  if typ=='reserva_original' and v['compacto']!=text:return None
 elif typ=='compacto':
  if cap not in (23,57) or v['capacidad']!=cap:return None
 else:return None
 try:
  if typ!='reserva_original' and len(encode_script_text(text))<cap:return None
 except FontError:return None
 compact=v['compacto']
 if not compact or any(unicodedata.category(c).startswith('C') for c in compact):return None
 icons='①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
 if [c for c in compact if c in icons]!=[c for c in text if c in icons]:return None
 if text[0] in icons and compact[0]!=text[0]:return None
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
 rom020_path=ROOT/'datos/campos_compactos_rom020.json'
 rom020_variants={r['unit_id']:r for r in json.loads(rom020_path.read_text(encoding='utf8'))} if rom020_path.exists() else {}
 rom021_path=ROOT/'datos/campos_compactos_rom021.json'
 rom021_variants={r['unit_id']:r for r in json.loads(rom021_path.read_text(encoding='utf8'))} if rom021_path.exists() else {}
 rom022_path=ROOT/'datos/campos_compactos_rom022.json'
 rom022_variants={r['unit_id']:r for r in json.loads(rom022_path.read_text(encoding='utf8'))} if rom022_path.exists() else {}
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
   fallback20=variante_tabla_rom020(row,text,raw,cap,rom020_variants)
   if fallback20 is not None:text,data,cap=fallback20
  if cap is None or len(data)>=cap:
   fallback21=variante_tabla_rom021(row,text,raw,cap,rom021_variants)
   if fallback21 is not None:text,data,cap=fallback21
  if cap is None or len(data)>=cap:
   fallback22=variante_tabla_rom022(row,text,raw,cap,rom022_variants)
   if fallback22 is not None:text,data,cap=fallback22
  if cap is None or len(data)>=cap:
   pending.append(dict(unit_id=uid,motivo='No cabe en reserva verificada',capacidad=cap,bytes=len(data),es=text));continue
  missing=missing_render_glyphs(decode_es(data),current)
  if missing:pending.append(dict(unit_id=uid,motivo='Glifos ausentes',glifos=missing));continue
  after=data.ljust(cap,b'\0');current[name][off:off+cap]=after
  journal.append(dict(unit_id=uid,grupo_id=row['grupo_id'],recurso=res,offset=off,capacidad=cap,es=text,revision_completa=full_text,adaptacion_compacta=(text!=full_text),antes_hex=bytes(raw[off:off+cap]).hex(),despues_hex=after.hex()))
 return dict(aplicados=journal,pendientes=pending)
