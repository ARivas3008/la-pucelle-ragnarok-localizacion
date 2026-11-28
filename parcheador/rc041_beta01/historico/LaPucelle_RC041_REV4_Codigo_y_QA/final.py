import json,hashlib as h,struct as s,sys,re,zlib,csv,zipfile,shutil,collections
from pathlib import Path
p=Path('/tmp/rc41text');out=Path('/mnt/data');sys.path.insert(0,'/tmp/rc38');from audit import *
base=Path('/tmp/rc41closures/RC041_rev3.iso');target=p/'RC041_rev4.iso';exe=out/'LaPucelle_Parcheador_RC041_REV4_GUI_Nativo.exe';r=json.loads((p/'report.json').read_text())
def sha(x):
 with x.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
replay=p/'replay_final/JUEGO_PARA_PPSSPP_RC041_REV4';assert sha(replay/'La_Pucelle_Ragnarok_ES_RC041_REV4.iso')==sha(target)==r['outputs'][0]['target_sha256']
for v in r['outputs'][1:]:assert sha(replay/'ULJS00244'/v['name'])==v['target_sha256']==sha(p/'ULJS00244'/v['name'])
a,b=iso(base),iso(target);assert a.keys()==b.keys();different=[]
for k in a:
 if '.' in k.split('/')[-1] and read(base,k)!=read(target,k):different.append(k)
assert set(different)=={SP,ST},different
oldtalk,old=inventory(base,Path('/tmp/rc41qa/ULJS00244'));newtalk,new=inventory(target,p/'ULJS00244');assert oldtalk==newtalk
allowed={'kis.dat','magic.dat','skill.dat','mapinfo.dat','char.dat','ritem.dat','name.dat','com.dat','script00.dat'}
for k in old:assert old[k].keys()==new[k].keys() and all(old[k][f]==new[k][f] for f in old[k] if f not in allowed)
fields=json.loads((p/'fields.json').read_text());exec((p/'scan.py').read_text().split('layouts=')[1].split('rows=[]')[0].join(['layouts=','']))
changes=list(csv.DictReader((p/'RC041_REV4_Correcciones.csv').open(encoding='utf-8-sig')));by={(q['package'],q['table'],int(q['offset'])):q for q in changes};assert len(by)==2037
jp_left=[];invalid_left=[];unmodified=0
for f in fields:
 k,n,o,cap,rel=f['package'],f['table'],f['offset'],f['cap'],f['rel'];x=new[k][n][o:o+cap];v=parse(x,n,rel);assert v is not None
 q=by.get((k,n,o))
 if q:assert x.hex()==q['hex_after'] and v[2]==q['after']
 else:assert x==old[k][n][o:o+cap];unmodified+=1
 if jp.search(v[2]):jp_left.append(dict(f,final=v[2]))
 if '\ufffd' in v[2]:invalid_left.append(dict(f,final=v[2]))
assert not jp_left and not invalid_left,(len(jp_left),len(invalid_left))
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
r.update(windows_exe_sha256=sha(exe),embedded_streams_verified=found,linux_replay_verified=5,table_fields_reread=len(fields),table_fields_with_japanese=0,table_fields_with_invalid_encoding=0,unchanged_fields=unmodified,iso_changed_members=different,nontext_START_members_unchanged=True,ANMPACK_unchanged=True,BGPACK_unchanged=True,closures_preserved=22,qa_status='Verificación binaria; no ejecución PPSSPP ni GUI Windows')
(out/'QA_RC041_REV4.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
for n in ['RC041_REV4_Correcciones.csv','RC041_REV4_Scripts.csv']:shutil.copyfile(p/n,out/n)
with zipfile.ZipFile(out/'LaPucelle_RC041_REV4_Codigo_y_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in [p/n for n in ['scan.py','plan.py','extend.py','apply.py','script_plan.py','patch_sp.py','scripts_scan.py','check_sp.py','final.py','plan.json','script_plan.json','fields.json','residual.json','scriptpack_residual.json','replay_final.log']]+[out/n for n in ['QA_RC041_REV4.json','RC041_REV4_Correcciones.csv','RC041_REV4_Scripts.csv']]:z.write(f,f.name)
 z.write('/tmp/rc38/audit.py','dependencias/audit.py');z.write('/tmp/rc41/implement.py','dependencias/implement.py')
 for f in (p/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 z.write(p/'gui/patches/manifest.json','gui/patches/manifest.json')
 z.writestr('LEEME.txt','Código de auditoría de laboratorio, dependiente de rutas locales /tmp y de las versiones anteriores del proyecto. No es un proyecto autónomo de compilación. El ejecutable distribuido aparte sí contiene los cinco parches. No contiene ISO ni DLC originales.')
print(json.dumps(r,ensure_ascii=False,indent=2));print([(x.name,x.stat().st_size) for x in out.glob('*REV4*')])
