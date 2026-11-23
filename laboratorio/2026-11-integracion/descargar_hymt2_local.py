"""Instala versiones fijadas, comprueba SHA256 y no altera el sistema."""
from pathlib import Path
import hashlib,json,urllib.request,zipfile,time,sys
B=Path(__file__).resolve().parent/'herramientas/hymt2'
release=json.loads((B/'release.json').read_text())
large='--7b' in sys.argv
model=json.loads((B/('modelo_7b.json' if large else 'modelo.json')).read_text())
asset=next(a for a in release['assets'] if a['name']=='llama-b12359-bin-win-cpu-x64.zip')
weight=next(a for a in model['siblings'] if a['rfilename']==('Hy-MT2-7B-Q4_K_M.gguf' if large else 'Hy-MT2-1.8B-Q8_0.gguf'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
def download(url,path,size,digest):
 if path.exists() and path.stat().st_size==size and sha(path)==digest:
  print('Verificado existente:',path.name,flush=True);return
 part=path.with_suffix(path.suffix+'.part')
 req=urllib.request.Request(url,headers={'User-Agent':'LaPucelle-localizacion'})
 with urllib.request.urlopen(req,timeout=120) as r,part.open('wb') as f:
  count=0;last=time.monotonic()
  while block:=r.read(4*1024*1024):
   f.write(block);count+=len(block)
   if time.monotonic()-last>15:
    print(path.name,round(100*count/size,1),'%',flush=True);last=time.monotonic()
 if part.stat().st_size!=size or sha(part)!=digest:raise RuntimeError('Integridad incorrecta: '+path.name)
 part.replace(path);print('Descarga verificada:',path.name,flush=True)
download(asset['browser_download_url'],B/asset['name'],asset['size'],asset['digest'].split(':')[1])
target=(B/'bin').resolve();target.mkdir(exist_ok=True)
with zipfile.ZipFile(B/asset['name']) as z:
 for member in z.infolist():
  p=(target/member.filename).resolve()
  if not p.is_relative_to(target):raise RuntimeError('Ruta ZIP fuera del destino')
 z.extractall(target)
url=f"https://huggingface.co/{model['id']}/resolve/{model['sha']}/{weight['rfilename']}"
download(url,B/weight['rfilename'],weight['size'],weight['lfs']['sha256'])
(B/'instalacion.json').write_text(json.dumps(dict(modelo=weight['rfilename'],revision=model['sha'],sha256=weight['lfs']['sha256'],motor=release['tag_name'],motor_sha256=asset['digest'],fecha='2026-11-17'),indent=2),encoding='utf8')
print('Instalación local completa',flush=True)
