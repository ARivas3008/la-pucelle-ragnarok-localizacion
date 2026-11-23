"""Nombres cotejados con las capturas; campos completos sin cortar caracteres."""
from campos_fijos import capacidad_verificada
from fuentes_es import encode_script_text,missing_render_glyphs,decode_es

def aplicar(key,original,members,manifest,reviews):
 journal=[]
 for row in manifest:
  if row['recurso'].split('/')[0]!=key:continue
  name=row['recurso'].split('/')[-1]
  if name not in ('char.dat','mapinfo.dat'):continue
  gid=row['grupo_id'];text=reviews.get(gid,{}).get('es_revisado','')
  if text not in ('Cuarto de Salade','Enfermería','Panza del Diablo'):continue
  off=int(row['offset']);raw=original[name];end=raw.find(b'\0',off)
  capacity=capacidad_verificada(name,raw,off,end-off)
  data=encode_script_text(text)
  if capacity is None or len(data)>=capacity:raise ValueError('Etiqueta no cabe: '+text)
  if missing_render_glyphs(decode_es(data),members):raise ValueError('Glifo ausente en etiqueta')
  before=bytes(members[name][off:off+capacity])
  after=data.ljust(capacity,b'\0');members[name][off:off+capacity]=after
  journal.append(dict(grupo_id=gid,recurso=row['recurso'],offset=off,es=text,antes_hex=before.hex(),despues_hex=after.hex()))
 return journal
