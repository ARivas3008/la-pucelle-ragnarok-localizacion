"""Localiza todas las apariciones físicas de grupos, con bytecode talk real."""
import re,unicodedata,struct
from collections import defaultdict,Counter
from functools import lru_cache
from formato_talk import inspect,replace,TalkError
from fuentes_es import encode_es,missing_render_glyphs
from construir_parche import to_full
from revisiones_coordinadas import scoped_segments

def canon(text):
 text=unicodedata.normalize('NFKC',text).replace('、',',').replace('。','.')
 return re.sub(r'\s+','',text)

def encode(text):
 # No emitir ASCII: 0x41 ('A') es una variable del intérprete talk.
 raw=encode_es(to_full(text))
 if len(raw)%2 or any(raw[i]<0x80 for i in range(0,len(raw),2)):
  raise TalkError('Talk requiere caracteres de dos bytes')
 return raw

def wrap(text,limit=28):
 if any(c in text for c in '\0\n\r\t'):raise TalkError('Control editorial pendiente de interpretar')
 words=text.split(' ')
 if not words or any(not w for w in words):raise TalkError('Espaciado estructurado')
 lines=[];line=''
 for word in words:
  if len(encode(word))>2*limit:raise TalkError('Palabra mayor que la línea')
  candidate=(line+' '+word) if line else word
  if len(encode(candidate))>2*limit:lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 if ' '.join(lines)!=text:raise TalkError('Reflujo perdió contenido')
 return lines

def runs(raw,meta):
 result=[]
 for item in sorted(meta['strings'],key=lambda x:x['offset']):
  if not item['raw']:continue
  if result:
   prev=result[-1][-1]
   if not item.get('choice') and not prev.get('choice') and item['entry']==prev['entry'] and bytes(raw[prev['end']:item['offset']]) in (b'\0\1',b'\0\2\1'):
    result[-1].append(item);continue
  result.append([item])
 return result

def catalog(manifest,reviews,buffers,metas,include_pending=False,segments=(),scoped=None):
 exact,scoped_gids=scoped_segments(scoped,manifest,reviews,buffers,metas,runs,segments)
 segments=list(segments)+exact
 groups=defaultdict(list)
 for row in manifest:
  if row['recurso'] in buffers:groups[row['grupo_id']].append(row)
 patterns=defaultdict(list);rejected={}
 for gid,items in groups.items():
  if gid in scoped_gids:continue # no reutilizar fragmentos reconstruidos fuera de su ancla
  rev=reviews.get(gid)
  if not rev or not rev.get('es_revisado','').strip():rejected[gid]='Sin traducción';continue
  if rev['estado']!='revisado' and not include_pending:rejected[gid]='Revisión pendiente';continue
  ordered=sorted(items,key=lambda r:(r['recurso'],int(r['offset'])))
  res=ordered[0]['recurso'];raw=buffers[res];texts={t['offset']:t for t in metas[res]['strings']}
  if any(u['recurso']!=res or int(u['offset']) not in texts for u in ordered):rejected[gid]='Correspondencia física incompleta';continue
  physical=[texts[int(u['offset'])] for u in ordered]
  if any(canon(u['original'])!=canon(t['raw'].decode('cp932')) for u,t in zip(ordered,physical)):
   rejected[gid]='Fuente literal distinta';continue
  if any(bytes(raw[a['end']:b['offset']]) not in (b'\0\1',b'\0\2\1') for a,b in zip(physical,physical[1:])):
   rejected[gid]='Grupo atraviesa un control u omite una continuación';continue
  key=tuple(canon(t['raw'].decode('cp932')) for t in physical)
  entry=physical[0]['entry'];entry_id=struct.unpack_from('<I',raw,12+32*entry)[0]
  patterns[key].append(dict(gid=gid,es=rev['es_revisado'],estado=rev['estado'],res=res,
   offset=physical[0]['offset'],entry_id=entry_id,unit_ids=[u['unit_id'] for u in ordered]))
 # Segmentos revisados contra bloques físicos completos. Cada segmento
 # conserva los controles de retrato, voz y evento situados entre bloques.
 unit_lookup={(u['recurso'],int(u['offset'])):u['unit_id'] for u in manifest if u['recurso'] in buffers}
 segment_runs={res:{r[0]['offset']:r for r in runs(buffers[res],metas[res])} for res in {s['recurso'] for s in segments}}
 for segment in segments:
  res=segment['recurso'];offset=segment['offset'];raw=buffers[res]
  run=segment_runs[res].get(offset)
  if run is None or [t['raw'].hex() for t in run]!=segment['original_hex']:
   raise TalkError('Segmento revisado no corresponde al original')
  entry_id=struct.unpack_from('<I',raw,12+32*run[0]['entry'])[0]
  key=tuple(canon(t['raw'].decode('cp932')) for t in run)
  patterns[key].append(dict(gid=segment['grupo_id'],es=segment['es'],estado='revisado',res=res,
   offset=offset,entry_id=entry_id,segmento=True,solo_origen=segment.get('solo_origen',False),
   grupos=segment.get('grupos',[segment['grupo_id']]),
   unit_ids=[unit_lookup[(res,t['offset'])] for t in run if (res,t['offset']) in unit_lookup]))
 trie={}
 for key,candidates in patterns.items():
  node=trie
  for part in key:node=node.setdefault(part,{})
  node[None]=candidates
 return trie,rejected

def compile_one(res,raw,meta,trie,font):
 edits=[];applied=[];pending=[]
 for run in runs(raw,meta):
  source=[t['raw'].decode('cp932') for t in run];keys=[canon(s) for s in source]
  entry_id=struct.unpack_from('<I',raw,12+32*run[0]['entry'])[0]
  @lru_cache(None)
  def solve(i):
   if i==len(run):return []
   node=trie;choices=[]
   for end in range(i,len(run)):
    node=node.get(keys[end])
    if node is None:break
    for c in node.get(None,[]):
     if c.get('solo_origen') and (c['res']!=res or c['offset']!=run[i]['offset']):continue
     score=1000 if c['res']==res and c['offset']==run[i]['offset'] else 100 if c['entry_id']==entry_id else 0
     if c.get('segmento'):score+=10
     if c.get('solo_origen'):score+=100
     choices.append((score,end+1,c))
   choices.sort(key=lambda x:(x[0],x[1]),reverse=True)
   for score,end,c in choices:
    peers=[z for s,e,z in choices if s==score and e==end]
    if len({p['es'] for p in peers})>1 and score<1000:continue
    tail=solve(end)
    if tail is not None:return [c]+tail
   return None
  selected=solve(0)
  try:
   if not any(ch.isalnum() for part in source for ch in part):raise TalkError('SIGNOS_ORIGINALES_CONSERVADOS')
   if selected is None:raise TalkError('Falta traducción completa o hay variantes ambiguas')
   phrase=' '.join(c['es'] for c in selected)
   lines=wrap(phrase)
   if run[0].get('choice') and len(lines)!=1:raise TalkError('Opción de menú necesita abreviación de una línea')
   if (missing:=missing_render_glyphs(to_full(phrase),font)):raise TalkError('Glifos ausentes: '+repr(missing))
   # La rutina cuenta pares y tiene tres filas de 65 bytes. Una página
   # adicional usa exactamente el opcode 02 que ya borra el cuadro.
   new=bytearray()
   # Un cambio de expresión 09 no limpia las tres filas. Una continuación
   # recompuesta podría desbordarlas: separarla en página sin quitar el 09.
   previous=[t for t in meta['strings'] if t['entry']==run[0]['entry'] and t['end']<run[0]['offset']]
   if previous and not run[0].get('choice'):
    last=max(previous,key=lambda t:t['end'])
    between=[op for a,b,op in meta['tokens'] if a>last['end'] and b<=run[0]['offset']-1]
    if 9 in between and not any(op in (2,3) for op in between):new+=b'\2'
   for j,line in enumerate(lines):
    if j and j%3==0:new+=b'\2'
    new+=b'\1'+encode(line)+b'\0'
   a=run[0]['offset']-1;b=run[-1]['end']+1
   edits.append((a,b,bytes(new)))
   applied.append(dict(recurso=res,offset=a,entry_id=entry_id,grupos=list(dict.fromkeys(g for c in selected for g in c.get('grupos',[c['gid']]))),
    unidades_origen=[u for c in selected for u in c['unit_ids']],lineas_originales=len(run),
    lineas_nuevas=len(lines),original=source,es=phrase))
  except (TalkError,ValueError,UnicodeError) as exc:
   pending.append(dict(recurso=res,offset=run[0]['offset'],entry_id=entry_id,original=source,motivo=str(exc)))
 out,journal=replace(raw,edits)
 return out,applied,pending,journal
