import json,hashlib as h,struct as s,sys,re,zlib,csv,zipfile
from pathlib import Path
p=Path('/tmp/rc41closures');out=Path('/mnt/data');sys.path.insert(0,'/tmp/rc38');from audit import iso,read,nis
base=Path('/tmp/rc41qa/RC041_rev2.iso');target=p/'RC041_rev3.iso';exe=out/'LaPucelle_Parcheador_RC041_REV3_GUI_Nativo.exe';r=json.loads((p/'report.json').read_text());rows=json.loads((p/'closures.json').read_text());
def sha(x):
 with x.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
replay=p/'replay/JUEGO_PARA_PPSSPP_RC041_REV3';assert sha(replay/'La_Pucelle_Ragnarok_ES_RC041_REV3.iso')==sha(target)
for v in r['outputs'][1:]:assert sha(replay/'ULJS00244'/v['name'])==v['target_sha256']
key='/PSP_GAME/USRDIR/ANMPACK.DAT';off,n,_=iso(target)[key];a=read(base,key);b=read(target,key);aa,bb=nis(a),nis(b);assert set(aa)==set(bb);expected={x['member'] for x in rows};assert {k for k in aa if aa[k]!=bb[k]}==expected
for row in rows:
 i=row['offset']-off;n=row['size'];assert h.sha256(b[i:i+n]).hexdigest()==row['new_sha256'];assert h.sha256(a[i:i+n]).hexdigest()==row['original_sha256']
raw=exe.read_bytes();found={};expected_streams={sha(p/'gui/patches'/x['patch']):x['name'] for x in r['outputs']}
for m in re.finditer(b'\x1f\x8b\x08',raw):
 i=m.start()
 try:
  o=zlib.decompressobj(31)
  if o.decompress(raw[i:i+65536],8)!=b'LPGUI001':continue
  o=zlib.decompressobj(31);o.decompress(raw[i:]);assert o.eof;size=len(raw)-i-len(o.unused_data);digest=h.sha256(raw[i:i+size]).hexdigest()
  if digest in expected_streams:found[expected_streams[digest]]=digest
 except (ValueError,AssertionError,zlib.error):continue
assert len(found)==5
r.update(iso_sha256=sha(target),windows_exe_sha256=sha(exe),embedded_streams_verified=found,linux_replay_verified=5,ANMPACK_members_modified=len(expected),all_other_ANMPACK_members_unchanged=True,ppsspp=False,windows_gui=False)
(out/'QA_RC041_REV3.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));
with (out/'RC041_REV3_Cierres.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with zipfile.ZipFile(out/'LaPucelle_RC041_REV3_Cierres_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in [p/'rebuild_closures.py',p/'build.py',p/'final.py',p/'closures.json',p/'replay.log',out/'QA_RC041_REV3.json',out/'RC041_REV3_Cierres.csv',out/'RC041_REV3_Cierres_comparacion.png',Path('/tmp/rc41qa/cierres_ROM039.csv')]:z.write(f,f.name)
 for f in (p/'assets').glob('*.bin'):z.write(f,'assets/'+f.name)
 for f in (p/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 z.write(p/'gui/patches/manifest.json','gui/patches/manifest.json')
print(json.dumps(r,ensure_ascii=False,indent=2));print('OUTPUTS',[(x.name,x.stat().st_size) for x in out.glob('*REV3*')])
