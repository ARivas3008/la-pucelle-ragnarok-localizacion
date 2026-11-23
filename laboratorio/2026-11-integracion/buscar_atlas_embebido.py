from pathlib import Path
import zlib,io,tarfile,json
B=Path(__file__).resolve().parent
p=next((B.parent/'07_Herramientas_Windows').glob('*.exe')); data=p.read_bytes()
pos=0;found=[]
while True:
 pos=data.find(b'\x1f\x8b\x08',pos)
 if pos<0:break
 try:
  dec=zlib.decompressobj(31);raw=dec.decompress(data[pos:],80_000_000)
  if not dec.eof:raise ValueError('no termina o demasiado grande')
  with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
   names=[n for n in tf.getnames() if 'atlas' in n.lower()]
   found.append(dict(offset=pos,miembros=len(tf.getnames()),atlas=names))
   for name in names:
    if name.endswith('atlas_deltas.json.z'):
     payload=tf.extractfile(name).read()
     target=B/'fuente/parcheador/app/datos/atlas_deltas.json.z'
     assert not target.exists()
     target.write_bytes(payload)
 except (zlib.error,tarfile.TarError,ValueError):pass
 pos+=3
(B/'informes/recuperacion_atlas.json').write_text(json.dumps(found,indent=2),encoding='utf-8')
print(found)
