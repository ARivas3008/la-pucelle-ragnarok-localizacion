"""Etiquetas fuera del manifiesto: intervalos exactos, sin mover el EBOOT."""
from pathlib import Path
import json,hashlib,re
from construir_parche import ROOT
DATA=ROOT/'datos/menus_fuera_corpus.json'

def aplicar(original,current):
 spec=json.loads(DATA.read_text(encoding='utf-8'))
 if len(original)!=spec['size'] or hashlib.sha256(original).hexdigest()!=spec['original_sha256']:
  raise ValueError('EBOOT desconocido para las etiquetas adicionales')
 out=bytearray(current);used=set();journal=[]
 for r in spec['patches']:
  off=r['offset'];old=bytes.fromhex(r['antes_hex']);new=bytes.fromhex(r['despues_hex']);end=off+len(old)
  if len(old)!=len(new) or original[off:end]!=old or original[end]!=0 or current[off:end]!=old:
   raise ValueError('Etiqueta adicional no coincide o ya fue modificada: '+r['id'])
  if b'\0' in new or used.intersection(range(off,end)):raise ValueError('Colisión o NUL interior')
  used.update(range(off,end));out[off:end]=new;journal.append(r)
 assert len(out)==len(current)
 assert all(i in used for i,(a,b) in enumerate(zip(current,out)) if a!=b)
 return out,journal
