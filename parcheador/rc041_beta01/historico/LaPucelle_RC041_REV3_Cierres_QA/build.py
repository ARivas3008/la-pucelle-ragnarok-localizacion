import json,hashlib as h,shutil,gzip,struct as s,sys,csv
from pathlib import Path
import numpy as np
p=Path('/tmp/rc41closures');prev=Path('/tmp/rc41qa');base=prev/'RC041_rev2.iso';dest=p/'RC041_rev3.iso';src=Path('/tmp/rc38/orig/La_Pucelle_Ragnarok_v1.1.2.iso');out=Path('/mnt/data')
def sha(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
shutil.copytree(prev/'gui',p/'gui',dirs_exist_ok=True);app=p/'gui';patch=app/'patches';m=json.loads((patch/'manifest.json').read_text());m['version']='RC041-REV3-GUI-NATIVO';m['scope']='RC041 REV2 + 22 cierres de capítulo reconstruidos en español (14 diseños); prueba visual en PPSSPP pendiente'
spec=m['specs'][0];assert spec['name']=='ISO' and sha(src)==spec['source_sha256'] and sha(base)==spec['target_sha256']
# Change only the blocks of the original-to-REV2 XOR stream that overlap the new graphics. Reuse the other four compressed files byte for byte.
with src.open('rb') as f,dest.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as o:
 o.write(b'LPGUI001');off=0
 while True:
  x=f.read(65536);y=g.read(65536)
  if not y:break
  x=x[:len(y)].ljust(len(y),b'\0')
  if x!=y:o.write(s.pack('<QI',off,len(y)));o.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
  off+=len(y)
 o.write(s.pack('<Q',2**64-1))
spec.update(target_sha256=sha(dest),target_size=dest.stat().st_size)
for v in m['specs'][1:]:assert sha(patch/v['patch'])==sha(prev/'gui/patches'/v['patch']) and sha(prev/'ULJS00244'/v['name'])==v['target_sha256']
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
for f in app.glob('*.go'):f.write_text(f.read_text().replace('RC041_REV2','RC041_REV3'))
r=json.loads((p/'closures.json').read_text());report={'version':'RC041 REV3','base_sha256':sha(base),'closures_physical':len(r),'unique_designs':len({x['group'] for x in r}),'changed_pixels':sum(x['changed_pixels'] for x in r),'preserved_palettes_headers_animation_and_ornament':True,'all_other_iso_bytes_unchanged':True,'DLC_unchanged_from_REV2':True,'outputs':m['specs'],'limitations':['Nuevas ediciones tipográficas, no los originales históricos ROM039; fuente Noto Serif Bold adaptada a las texturas originales.','No se ha ejecutado PPSSPP ni la GUI Windows.','Otros gráficos fuera de los 22 cierres, espaciado y auditoría global siguen pendientes.','No publicado en GitHub.']};(patch/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(p/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('delta ready',flush=True)
