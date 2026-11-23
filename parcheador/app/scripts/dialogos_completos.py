"""Cierra grupos editoriales y líneas físicas sin desplazar bytecode.

Una traducción de grupo se consume exactamente una vez. Solo se permiten
separadores literales 00 01 y 00 02 01; no se atraviesan otros eventos.
"""
import re
from collections import defaultdict


def planificar(core,manifest,buffers,groups,reviews,investigacion,sin_fuentes,fuentes,refinamientos):
 units={r['unit_id']:r for r in manifest if re.search(r'/talk\d+(?:_jp)?\.dat$',r['recurso']) and r['recurso'] in buffers}
 parent={u:u for u in units}
 def root(u):
  while parent[u]!=u:
   parent[u]=parent[parent[u]];u=parent[u]
  return u
 def join(a,b):parent[root(a)]=root(b)
 for group in groups.values():
  ids=[u['unit_id'] for u in group if u['unit_id'] in units]
  for uid in ids[1:]:join(ids[0],uid)
 chains,_,orphans=core.cadenas_dialogo(list(units.values()),buffers)
 for chain in chains:
  for u in chain[1:]:join(chain[0]['unit_id'],u['unit_id'])
 components=defaultdict(list)
 for uid,u in units.items():components[root(uid)].append(u)
 solutions={};rejected={}
 for items in components.values():
  ordered=sorted(items,key=lambda u:(u['recurso'],int(u['offset'])))
  ids=tuple(u['unit_id'] for u in ordered)
  try:
   res=ordered[0]['recurso'];buf=buffers[res]
   if any(u['recurso']!=res for u in ordered):raise core.SegmentacionError('Grupo editorial cruza recursos')
   if set(ids)&orphans:raise core.SegmentacionError('Continuación ausente del manifiesto: cerrar antes de traducir')
   descriptors=[]
   for u in ordered:
    off=int(u['offset']);style,src=core.match_source(buf,off,u['original'])
    if src is None or off<1 or buf[off-1]!=1:raise core.SegmentacionError('Fuente/opcode no verificado')
    descriptors.append((res,off,style,len(src)))
   for a,b in zip(descriptors,descriptors[1:]):
    if bytes(buf[a[1]+a[3]:b[1]]) not in (b'\x00\x01',b'\x00\x02\x01'):
     raise core.SegmentacionError('El grupo atraviesa un control no autorizado')
   gids=list(dict.fromkeys(u['grupo_id'] for u in ordered))
   sequence=[u['grupo_id'] for i,u in enumerate(ordered) if i==0 or u['grupo_id']!=ordered[i-1]['grupo_id']]
   if sequence!=gids:raise core.SegmentacionError('Grupos editoriales intercalados')
   phrase=[]
   for gid in gids:
    if {u['unit_id'] for u in groups[gid]}-set(ids):raise core.SegmentacionError('Grupo editorial incompleto')
    rev=reviews.get(gid)
    if not rev or rev['estado'] not in ('revisado','requiere_investigacion'):raise core.SegmentacionError('Sin revisión editorial del grupo')
    if rev['estado']=='requiere_investigacion' and not investigacion:raise core.SegmentacionError('Requiere investigación editorial')
    text=core.es_revisado_para_parche(gid,rev,refinamientos)
    if not text.strip():raise core.SegmentacionError('Traducción vacía')
    phrase.append(text)
   # En esta ruta todos los destinos usan ASCII/gaiji; la fuente se cotejó
   # usando su codificación original, incluida la mezcla de anchos.
   encoder=core.encode_es if not sin_fuentes else lambda t:t.encode('cp932')
   chunks=core.repartir(' '.join(phrase),[m[3] for m in descriptors],encoder=encoder)
   pack='ISO_START' if res.startswith('ISO/') else res.split('/')[0]
   staged={}
   for u,meta,chunk in zip(ordered,descriptors,chunks):
    if not sin_fuentes and (missing:=core.missing_render_glyphs(chunk,fuentes[pack]['inner'])):
     raise core.SegmentacionError('Glifos ausentes: '+repr(missing))
    data=core.safe_encoding(chunk,'normal',meta[3],fuentes_es=not sin_fuentes)
    staged[u['unit_id']]=(meta,chunk,data,ids)
   solutions.update(staged)
  except (core.Fail,core.SegmentacionError,core.FontError,UnicodeError) as exc:
   rejected.update({uid:str(exc) for uid in ids})
 return solutions,rejected,set(units)
