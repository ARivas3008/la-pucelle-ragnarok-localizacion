from pathlib import Path
import urllib.request,json
B=Path(__file__).resolve().parent
out=B/'referencias_web';out.mkdir(exist_ok=True)
urls={
 'neoseeker.html':'https://www.neoseeker.com/la-pucelle/faqs/78770-a.html',
 'hymt2_modelo.json':'https://huggingface.co/api/models/tencent/Hy-MT2-1.8B-GGUF',
 'llama_release.json':'https://api.github.com/repos/ggml-org/llama.cpp/releases/latest'}
for name,url in urls.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/json'})
  with urllib.request.urlopen(req,timeout=30) as response:data=response.read()
  (out/name).write_bytes(data);print(name,len(data))
 except Exception as exc:print(name,type(exc).__name__,str(exc))
