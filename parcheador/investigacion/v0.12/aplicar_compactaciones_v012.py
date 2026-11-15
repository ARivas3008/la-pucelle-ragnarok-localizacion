#!/usr/bin/env python3
"""Aplica traducciones breves SOLO a copias de registros verificados.

El parche de prueba no toca game images ni cambia punteros. No considera las
propuestas equivalentes a validación editorial o de PPSSPP.
"""
import argparse, csv, json, hashlib, sys, re
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1]/'v0.11'
sys.path.insert(0,str(ROOT))
from campos_v011 import locate, replace, CampoError
from auditar_66 import exact_match,physical_file
from fuentes_es import encode_es

def sha(b):return hashlib.sha256(b).hexdigest()
def load(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def run(proposals, audit, source, output, apply=False, include_review=False):
 proposals=load(proposals)
 source=Path(source);output=Path(output);output.mkdir(parents=True,exist_ok=True)
 metad={r['unit_id']:r for r in load(audit)}
 byres=defaultdict(list)
 for row in proposals:
  if row['estado_propuesta']=='SIN_ALTERNATIVA':continue
  if row['estado_propuesta']=='PROPUESTA_POR_REVISAR' and not include_review:continue
  byres[row['recurso']].append(row)
 results=[];manifest=[]
 for resource,rows in sorted(byres.items()):
  src=physical_file(source,resource)
  if src is None or not src.exists():
   for x in rows:results.append(dict(unit_id=x['unit_id'],estado='SIN_ARCHIVO',razon=resource))
   continue
  base=src.read_bytes();current=base;blocked=[];applied=[];changed_intervals=[]
  for row in sorted(rows,key=lambda x:int(metad[x['unit_id']]['offset'])):
   uid=row['unit_id'];a=metad[uid];off=int(a['offset'])
   expected=a['original'];new_text=row['propuesta'];kind=row['tipo']
   if not new_text or new_text==a['es_revisado'] or 'Now Loading' in expected or '読み込み中' in expected:
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='No hay sustitución de texto o es Now Loading'));continue
   if re.search(r'%[sd]|\{\d+\}|<[^>]*>|\\[rn]',expected+new_text):
    # Do not alter symbols/control on a fixed field without a format parser.
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Marcador no validado'));continue
   qual,old=exact_match(base,off,expected)
   if old is None:
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Original no coincide'));continue
   try:new=encode_es(new_text) if kind=='TABLA_FIJA' else new_text.encode('ascii')
   except UnicodeError:
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Codificación no certificada en EBOOT'));continue
   if kind=='TABLA_FIJA':
    field=locate(resource,base,off,old)
    if field is None or len(new)+1>field.longitud:
     results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Perfil/capacidad incompatibles'));continue
    try:changed=replace(current,off,old,new,resource)
    except CampoError as e:
     results.append(dict(unit_id=uid,estado='RECHAZADO',razon=str(e)));continue
    upper=off+field.longitud
   elif kind=='EBOOT':
    # Old original terminator MUST remain at its verified offset. This is an
    # ASCII-only proposal to avoid untested private glyph decoding in EBOOT.
    if not old.isascii() or len(new)>len(old) or current[off:off+len(old)+1]!=old+b'\0':
     results.append(dict(unit_id=uid,estado='RECHAZADO',razon='EBOOT límite/terminador'));continue
    buf=bytearray(current)
    buf[off:off+len(old)]=new.ljust(len(old),b'\0')
    changed=bytes(buf);upper=off+len(old)
   else:
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Tipo incompatible'));continue
   if any(not (upper<=lo or hi<=off) for lo,hi in changed_intervals):
    results.append(dict(unit_id=uid,estado='RECHAZADO',razon='Intervalo solapado'));continue
   current=changed;changed_intervals.append((off,upper));applied.append(uid)
   results.append(dict(unit_id=uid,estado='SIMULACION_BINARIA_OK',razon=f'{len(new)} bytes; rango {off}:{upper}; {row["estado_propuesta"]}'))
  if applied:
   # Byte differences must be contained within every approved field.
   changed_positions=[i for i,(a,b) in enumerate(zip(base,current)) if a!=b]
   if len(current)!=len(base) or any(not any(lo<=i<hi for lo,hi in changed_intervals) for i in changed_positions):
    raise AssertionError('Cambios fuera de campo')
   name=resource.replace('/','__').replace('.','_')
   if apply:
    dest=output/'borradores'/name
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(current)
   manifest.append({'recurso':resource,'sha256_fuente':sha(base),'sha256_salida':sha(current),
                    'cantidad':len(applied),'bytes_archivo':len(base),'ids':applied})
 st=Counter(r['estado'] for r in results)
 with (output/'simulacion.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['unit_id','estado','razon']);w.writeheader();w.writerows(results)
 result={'estados':dict(st),'recursos_que_cambian':len(manifest),'total_aprobacion_ppsspp':0,'advertencia':'ENSAYO LOCAL; NO PARCHE CERTIFICADO; COTEJO EDITORIAL Y VISUAL PENDIENTE','archivos':manifest}
 (output/'resultado.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
 return result

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--propuestas',type=Path,required=True);a.add_argument('--auditoria',type=Path,required=True)
 a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
 a.add_argument('--guardar-borradores',action='store_true');a.add_argument('--incluir-por-revisar',action='store_true');x=a.parse_args()
 print(json.dumps(run(x.propuestas,x.auditoria,x.source,x.output,x.guardar_borradores,x.incluir_por_revisar),ensure_ascii=False,indent=2)[:1200])
