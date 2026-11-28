import gzip, hashlib, json, pathlib, subprocess, shutil, sys, tempfile
# Usage: build_deltas.py ORIGINAL_DIR TARGET_DIR OUTPUT_PATCH_DIR MATCHER
orig,target,out,matcher=map(pathlib.Path,sys.argv[1:]); manifest=json.loads((out/'manifest.json').read_text()); stats=[]
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for s in manifest['specs']:
 name=s['name']; a=orig/('La_Pucelle_Ragnarok_v1.1.2.iso' if name=='ISO' else name); b=target/('La_Pucelle_Ragnarok_ES_RC041_REV6_BETA02.iso' if name=='ISO' else 'ULJS00244/'+name)
 assert a.stat().st_size==s['source_size'] and digest(a)==s['source_sha256']; assert b.stat().st_size==s['target_size'] and digest(b)==s['target_sha256']
 with tempfile.TemporaryDirectory() as td:
  raw=pathlib.Path(td)/'delta'; p=out/s['patch'].replace('.xor.gz','.copy.gz'); result=subprocess.run([str(matcher),str(a),str(b),str(raw),'64' if name=='ISO' else '8'],capture_output=True,text=True,check=True); print(result.stderr,flush=True)
  with raw.open('rb') as r,p.open('wb') as f,gzip.GzipFile(filename='',mode='wb',fileobj=f,compresslevel=9,mtime=0) as z:shutil.copyfileobj(r,z)
  s['patch']=p.name;stats.append(dict(name=name,compressed_bytes=p.stat().st_size,raw_bytes=raw.stat().st_size,sha256=digest(p),matcher=result.stderr.strip().split(' copied=')[-1]))
manifest['version']='RC041-REV6-BETA02-COMPACTA'; (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'); (out.parent.parent/'delta_stats.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
