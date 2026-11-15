"""Explicit, hash-pinned byte diffs for known START_JP sys3/sys4 text atlases.

No third-party image library required in the distributed program. Fail closed on
unknown versions. Only documented byte offsets, no palette/texture header changes.
"""
import json,zlib,hashlib
from pathlib import Path

DATA=Path(__file__).resolve().parents[1]/'datos/atlas_deltas.json.z'

class AtlasError(ValueError):pass

def all_patches():
 return json.loads(zlib.decompress(DATA.read_bytes()))

def expected_patch(name,source):
 sha=hashlib.sha256(source).hexdigest()
 desc=all_patches().get(name,{}).get(sha)
 if not desc:raise AtlasError(f'No hay atlas validado para {name} SHA256 {sha}')
 if len(source)!=desc['size']:raise AtlasError('Longitud de textura inesperada')
 b=bytearray(source)
 for offset,val in desc['changes']:
  if offset<1040 or offset>=len(b) or not 0<=val<=255:raise AtlasError('Cambio fuera de región de píxeles')
  b[offset]=val
 if b[:1040]!=source[:1040]:raise AtlasError('Se alteró la paleta/cabecera')
 return bytes(b),desc

def apply(members):
 info={}
 for name in ('sys3.txp','sys4.txp'):
  if name not in members:raise AtlasError(f'Falta {name} en paquete')
  original=bytes(members[name]);new,meta=expected_patch(name,original)
  members[name]=bytearray(new)
  info[name]={'original_sha256':hashlib.sha256(original).hexdigest(),
              'nuevo_sha256':hashlib.sha256(new).hexdigest(),
              'bytes_modificados':len(meta['changes']),
              'elementos_traducidos':meta['labels']}
 return info

def validate(original_members,new_members):
 out={}
 for name in ('sys3.txp','sys4.txp'):
  expected,_=expected_patch(name,bytes(original_members[name]))
  if bytes(new_members[name])!=expected:
   raise AtlasError(f'{name} no coincide con el parche aprobado')
  out[name]=hashlib.sha256(expected).hexdigest()
 return out
