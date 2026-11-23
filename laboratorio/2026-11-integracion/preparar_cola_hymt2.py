from pathlib import Path
import json,csv,collections,hashlib,unicodedata,re,sys
B=Path(__file__).resolve().parent
exec((B/'planificar_todos_dialogos.py').read_text(encoding='utf8').split('trie,rejected=')[0])
from recompilar_talk import runs,canon
pending=json.loads((B/'informes/dialogos_pendientes.json').read_text(encoding='utf8'))
groups=collections.defaultdict(list)
for row in manifest:groups[row['grupo_id']].append(row)
lookup=collections.defaultdict(list)
for gid,rows in groups.items():
 rev=reviews.get(gid,{})
 if rev.get('estado')=='revisado' and rev.get('es_revisado'):
  key=canon(''.join(r['original'] for r in sorted(rows,key=lambda r:int(r['offset']))))
  lookup[key].append(dict(grupo_id=gid,es=rev['es_revisado'],recurso=rows[0]['recurso']))
runmap={};neighbors={}
for res,meta in metas.items():
 rr=runs(buffers[res],meta)
 for i,run in enumerate(rr):
  key=(res,run[0]['offset']);runmap[key]=run
  near=[r for r in rr[max(0,i-2):i+3] if r[0]['entry']==run[0]['entry'] and r is not run]
  neighbors[key]=[unicodedata.normalize('NFKC',' '.join(t['raw'].decode('cp932') for t in r)) for r in near]
queue={};punct=[];reuse=[]
for row in pending:
 res=row['recurso'];off=row['offset'];run=runmap[(res,off)]
 source=unicodedata.normalize('NFKC',' '.join(row['original']))
 segment=dict(recurso=res,offset=off,entry_id=row['entry_id'],original_hex=[t['raw'].hex() for t in run],opcion=bool(run[0].get('choice')),contexto=neighbors[(res,off)])
 if not any(ch.isalnum() for ch in source):punct.append(dict(**segment,original=source));continue
 candidates=lookup.get(canon(''.join(row['original'])),[])
 local=[r for r in candidates if r['recurso']==res]
 if local:candidates=local
 if candidates and len({r['es'] for r in candidates})==1:
  reuse.append(dict(**segment,original=source,es=candidates[0]['es'],grupo_id=candidates[0]['grupo_id']));continue
 # Una misma frase puede variar con el contexto: agrupamos únicamente cuando
 # comparten fuente, tipo de menú y vecinos de la misma escena.
 key=hashlib.sha256(json.dumps([source,segment['opcion'],segment['contexto']],ensure_ascii=False).encode()).hexdigest()[:20]
 if key not in queue:queue[key]=dict(id=key,original=source,contexto=segment['contexto'],opcion=segment['opcion'],apariciones=[])
 queue[key]['apariciones'].append(segment)
for name,value in [('cola_hymt2',list(queue.values())),('reutilizables_corpus',reuse),('signos_originales_conservar',punct)]:
 (B/f'informes/{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
print(dict(pendientes=len(pending),reutilizables=len(reuse),signos_sin_traduccion=len(punct),solicitudes_hymt2=len(queue),apariciones_hymt2=sum(len(r['apariciones']) for r in queue.values())),flush=True)
