from pathlib import Path
import urllib.request,json,hashlib,zipfile,sys
B=Path(__file__).resolve().parent;D=B/'herramientas/hymt2';D.mkdir(parents=True,exist_ok=True)
def read(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'LaPucelle-localizacion'}),timeout=60) as r:return r.read()
def get(url):return json.loads(read(url))
release=json.loads((B/'referencias_web/llama_release.json').read_text())
if len(release['assets'])==1 and release['assets'][0]['name']=='nightly-tag.txt':
 tag=read(release['assets'][0]['browser_download_url']).decode().strip()
 release=get('https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/'+tag)
(D/'release.json').write_text(json.dumps(release,indent=2),encoding='utf-8')
model=get('https://huggingface.co/api/models/tencent/Hy-MT2-1.8B-GGUF?blobs=true')
(D/'modelo.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
print('Release',release['tag_name'],flush=True)
for a in release['assets']:
 if 'win' in a['name'].lower():print(a['name'],a['size'],a['browser_download_url'],flush=True)
print('Modelo',model['sha'],[x for x in model['siblings'] if 'Q8' in x['rfilename']],flush=True)
