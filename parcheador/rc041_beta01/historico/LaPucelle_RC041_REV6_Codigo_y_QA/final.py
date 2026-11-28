from pathlib import Path
import hashlib as H,json,re,zlib,zipfile,csv
p=Path('/tmp/rc41rev6');o=Path('/mnt/data');exe=o/'LaPucelle_Parcheador_RC041_REV6_GUI_Nativo.exe';r=json.loads((p/'report.json').read_text());rp=p/'replay/JUEGO_PARA_PPSSPP_RC041_REV6'
def sha(x):
 with x.open('rb') as f:return H.file_digest(f,'sha256').hexdigest()
for q in r['outputs']:
 path=rp/'La_Pucelle_Ragnarok_ES_RC041_REV6.iso' if q['name']=='ISO' else rp/'ULJS00244'/q['name'];assert sha(path)==q['target_sha256']
raw=exe.read_bytes();found={};expected={sha(p/'gui/patches'/x['patch']):x['name'] for x in r['outputs']}
for m in re.finditer(b'\x1f\x8b\x08',raw):
 i=m.start()
 try:
  z=zlib.decompressobj(31)
  if z.decompress(raw[i:i+65536],8)!=b'LPGUI001':continue
  z=zlib.decompressobj(31);z.decompress(raw[i:]);assert z.eof;size=len(raw)-i-len(z.unused_data);digest=H.sha256(raw[i:i+size]).hexdigest()
  if digest in expected:found[expected[digest]]=digest
 except (ValueError,AssertionError,zlib.error):continue
assert len(found)==5
inv=json.loads((p/'texture_inventory.json').read_text());r.update(windows_exe_sha256=sha(exe),embedded_streams_verified=found,linux_replay_verified=5,texture_inventory_physical=len(inv),texture_inventory_unique=sum(not x['duplicate_of'] for x in inv),qa_status='Verificación binaria; no ejecución PPSSPP ni GUI Windows')
qa=o/'QA_RC041_REV6.json';qa.write_text(json.dumps(r,ensure_ascii=False,indent=2));f=o/'RC041_REV6_Inventario_texturas.csv'
with f.open('w',encoding='utf-8-sig',newline='') as out:
 w=csv.DictWriter(out,fieldnames=['resource','sha256','size','duplicate_of']);w.writeheader();w.writerows(inv)
with zipfile.ZipFile(o/'LaPucelle_RC041_REV6_Codigo_y_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['edit.py','skip.py','build.py','final.py','texture_inventory.json','build.log','replay.log']:z.write(p/n,n)
 for n in ['QA_RC041_REV6.json','RC041_REV6_Inventario_texturas.csv']:z.write(o/n,n)
 for f in (p/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 for name in ['view.py','graphics.py']:z.write('/tmp/rc41rev5/'+name,'dependencias/'+name)
 z.write('/tmp/rc38/audit.py','dependencias/audit.py');z.write('/tmp/rc41/implement.py','dependencias/implement.py');z.write(p/'gui/patches/manifest.json','gui/patches/manifest.json');z.writestr('LEEME.txt','Auditoría de laboratorio RC041 REV6. Los scripts dependen de rutas /tmp y de REV5. No contiene ISO, DLC ni parches incrustados (el EXE se distribuye por separado). No certifica visualización en PPSSPP.')
print('OK',len(found),len(inv),r['texture_inventory_unique']);print(exe.stat().st_size)
