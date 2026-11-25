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


# ROM-031: variables reales del intérprete, no las letras A1 de texto normal.
VARIABLE=re.compile(r'(?<![A-Za-z0-9])A[0-9](?![A-Za-z0-9])')
def variables(raw):
 if len(raw)%2:raise TalkError('Cadena TALK de ancho impar')
 result=[]
 for i in range(0,len(raw),2):
  pair=raw[i:i+2]
  if pair[0]>=0x80:continue
  if pair[0]==0x41 and 0x30<=pair[1]<=0x39:result.append(pair.decode('ascii'))
  else:raise TalkError('Control de texto TALK no reconocido')
 return tuple(result)

def source_variables(run):
 return tuple(v for item in run for v in variables(item['raw']))

def variable_encoder(source):
 """Conservar A0..A9 solo si aparecen como controles reales en la fuente."""
 expected=source_variables(source)
 def enc(text):
  if not expected:return encode(text)
  out=bytearray();pos=0
  for match in VARIABLE.finditer(text):
   out+=encode(text[pos:match.start()]);out+=match.group().encode('ascii');pos=match.end()
  out+=encode(text[pos:])
  return bytes(out)
 return expected,enc

def glyph_text(text,expected):
 return to_full(VARIABLE.sub('',text) if expected else text)

def fit_slots(text,run,limit=28):
 """Repartir sin perder palabras ni cambiar el número de líneas y páginas."""
 if any(c in text for c in '\0\n\r\t'):raise TalkError('Control editorial pendiente')
 words=text.split(' ')
 if not words or any(not w for w in words):raise TalkError('Espaciado estructurado')
 expected,enc=variable_encoder(run)
 if variables(enc(text))!=expected:raise TalkError('Variables TALK distintas')
 by_line=[variables(t['raw']) for t in run]
 if len(words)<len(run) or len(words)>len(run)*limit:raise TalkError('Número de palabras incompatible con slots')
 @lru_cache(None)
 def solve(slot,start):
  if slot==len(run):return () if start==len(words) else None
  if len(words)-start<len(run)-slot:return None
  stop=min(start+limit,len(words)-(len(run)-slot-1))
  for end in range(stop,start,-1):
   line=' '.join(words[start:end]);data=enc(line)
   if len(data)>2*limit or variables(data)!=by_line[slot]:continue
   rest=solve(slot+1,end)
   if rest is not None:return (line,)+rest
  return None
 lines=solve(0,0)
 if lines is None:raise TalkError('Subgrupo no cabe en sus líneas originales')
 if ' '.join(lines)!=text:raise TalkError('Reflujo perdió contenido')
 return lines,enc,expected

def wrap(text,limit=28,encoder=encode):
 if any(c in text for c in '\0\n\r\t'):raise TalkError('Control editorial pendiente de interpretar')
 words=text.split(' ')
 if not words or any(not w for w in words):raise TalkError('Espaciado estructurado')
 lines=[];line=''
 for word in words:
  if len(encoder(word))>2*limit:raise TalkError('Palabra mayor que la línea')
  candidate=(line+' '+word) if line else word
  if len(encoder(candidate))>2*limit:lines.append(line);line=word
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
  if any(a['entry']!=b['entry'] or a.get('choice') or b.get('choice') or bytes(raw[a['end']:b['offset']]) not in (b'\0\1',b'\0\2\1') for a,b in zip(physical,physical[1:])):
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

def _partial_singletons(res,raw,run,trie,font):
 """Subgrupos exactos revisados, cada token conserva su slot.
 Sin reutilización de variantes ajenas, ni grupos cortados por controles.
 """
 edits=[];applied=[];i=0
 while i<len(run):
  item=run[i];node=trie;options=[]
  for end in range(i,len(run)):
   node=node.get(canon(run[end]['raw'].decode('cp932')))
   if node is None:break
   count=end-i+1
   exact=[p for p in node.get(None,[]) if p['res']==res
          and p['offset']==item['offset'] and p['estado']=='revisado'
          and len(p['unit_ids'])==count and len(set(p['unit_ids']))==count]
   if exact and len({p['es'] for p in exact})==1 and len({tuple(p['unit_ids']) for p in exact})==1:
    options.append((end+1,exact[0]))
  matched=False
  for end,candidate in reversed(options):
   seq=run[i:end];phrase=candidate['es']
   if not any(c.isalnum() for t in seq for c in t['raw'].decode('cp932')):continue
   try:
    lines,enc,expected=fit_slots(phrase,seq)
    if missing_render_glyphs(glyph_text(phrase,expected),font):continue
    changes=[]
    for t,line in zip(seq,lines):
     a=t['offset']-1;b=t['end']+1;new=b'\1'+enc(line)+b'\0'
     if a<0:raise TalkError('Ancla negativa')
     changes.append((a,b,new))
    if all(bytes(raw[a:b])==new for a,b,new in changes):continue
    edits.extend(changes)
    applied.append(dict(recurso=res,offset=changes[0][0],
      entry_id=struct.unpack_from('<I',raw,12+32*item['entry'])[0],
      grupos=list(candidate.get('grupos',[candidate['gid']])),
      unidades_origen=list(candidate['unit_ids']),lineas_originales=len(seq),
      lineas_nuevas=len(lines),original=[t['raw'].decode('cp932') for t in seq],
      es=phrase,modo='SUBBLOQUE_EXACTO_SIN_CAMBIAR_CONTROLES'))
    i=end;matched=True;break
   except (TalkError,ValueError,UnicodeError):
    continue
  if not matched:i+=1
 return edits,applied

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
   expected,encoder=variable_encoder(run)
   if variables(encoder(phrase))!=expected:raise TalkError('Variables TALK distintas')
   lines=wrap(phrase,encoder=encoder)
   if run[0].get('choice') and len(lines)!=1:raise TalkError('Opción de menú necesita abreviación de una línea')
   if (missing:=missing_render_glyphs(glyph_text(phrase,expected),font)):raise TalkError('Glifos ausentes: '+repr(missing))
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
    new+=b'\1'+encoder(line)+b'\0'
   a=run[0]['offset']-1;b=run[-1]['end']+1
   edits.append((a,b,bytes(new)))
   applied.append(dict(recurso=res,offset=a,entry_id=entry_id,grupos=list(dict.fromkeys(g for c in selected for g in c.get('grupos',[c['gid']]))),
    unidades_origen=[u for c in selected for u in c['unit_ids']],lineas_originales=len(run),
    lineas_nuevas=len(lines),original=source,es=phrase))
  except (TalkError,ValueError,UnicodeError) as exc:
   # Cuando una sola línea no aprobada bloquea todo un run, permitir
   # únicamente subgrupos completos, inequívocos y en sus slots originales.
   # Las unidades restantes siguen pendientes; no se cuenta el run completo.
   if selected is None and str(exc)=='Falta traducción completa o hay variantes ambiguas':
    extra,items=_partial_singletons(res,raw,run,trie,font)
    edits.extend(extra);applied.extend(items)
    motivo=('Inserción parcial: '+str(len(items))+' cadena(s) exactas; resto pendiente'
             if items else str(exc))
   else:motivo=str(exc)
   pending.append(dict(recurso=res,offset=run[0]['offset'],entry_id=entry_id,original=source,motivo=motivo))
 out,journal=replace(raw,edits)
 return out,applied,pending,journal
