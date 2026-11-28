from pathlib import Path
import hashlib as H,json,re,zlib,shutil,zipfile,csv
from PIL import Image,ImageDraw
p=Path('/tmp/rc41rev5');o=Path('/mnt/data');exe=o/'LaPucelle_Parcheador_RC041_REV5_GUI_Nativo.exe';r=json.loads((p/'report.json').read_text());rp=p/'replay/JUEGO_PARA_PPSSPP_RC041_REV5'
def sha(x):
 with x.open('rb') as f:return H.file_digest(f,'sha256').hexdigest()
for q in r['outputs']:
 path=rp/'La_Pucelle_Ragnarok_ES_RC041_REV5.iso' if q['name']=='ISO' else rp/'ULJS00244'/q['name'];assert sha(path)==q['target_sha256']
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
r.update(windows_exe_sha256=sha(exe),embedded_streams_verified=found,linux_replay_verified=5,qa_status='Verificación binaria de ISO y cuatro DLC, sin ejecutar PPSSPP ni GUI Windows')
qa=o/'QA_RC041_REV5.json';qa.write_text(json.dumps(r,ensure_ascii=False,indent=2));shutil.copyfile(p/'comparacion_titulos.png',o/'RC041_REV5_Titulos_comparacion.png')
# Atlas captures with true indexed textures, 2x nearest-neighbor.
sets=[('sys3.txp.png','sys3.txp.new.png','Anuncios'),('sys5.txp.png','sys5.txp.new.png','Bonificaciones'),('sys6.txp.png','sys6.txp.new.png','HUD base'),('item.txp.png','item.txp.new.png','Estadísticas'),('DLC_sys6.txp.png','DLC_sys6.new.png','HUD DLC')];sheet=Image.new('RGB',(1060,len(sets)*550),(34,34,38));d=ImageDraw.Draw(sheet)
for i,(a,b,t) in enumerate(sets):
 for j,f in enumerate((a,b)):
  im=Image.open(p/f).convert('RGBA');im=im.resize((512,512),Image.Resampling.NEAREST);x=j*530+8;y=i*550+26;d.text((x,y-20),t+' | '+('Antes' if j==0 else 'Después'),fill='white');sheet.paste(im,(x,y),im)
sheet.save(o/'RC041_REV5_Interfaz_comparacion.png')
rows=json.loads((p/'text_changes.json').read_text());rows2=json.loads((p/'table_changes.json').read_text());f=o/'RC041_REV5_Correcciones.csv'
with f.open('w',encoding='utf-8-sig',newline='') as out:
 w=csv.DictWriter(out,fieldnames=['resource','source_offset','current_offset','offset','original','before','after']);w.writeheader();w.writerows(rows+rows2)
with zipfile.ZipFile(o/'LaPucelle_RC041_REV5_Codigo_y_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['view.py','graphics.py','dlc_graphics.py','textscan.py','normalize.py','build.py','final.py','graphics.json','text_candidates.json','text_skips.json','text_changes.json','table_changes.json','build.log','replay.log']:z.write(p/n,n)
 for n in ['QA_RC041_REV5.json','RC041_REV5_Correcciones.csv']:z.write(o/n,n)
 for name in ['audit.py','fix.py']:z.write('/tmp/rc38/'+name,'dependencias/'+name)
 z.write('/tmp/rc41/implement.py','dependencias/implement.py')
 for f in (p/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 z.write(p/'gui/patches/manifest.json','gui/patches/manifest.json');z.writestr('LEEME.txt','Auditoría de laboratorio RC041 REV5. Los scripts dependen de rutas /tmp y de REV4. El EXE distribuido aparte contiene los cinco parches. No contiene ISO ni DLC originales. No certifica visualización en PPSSPP.')
print(json.dumps(r,ensure_ascii=False,indent=2));print([(x.name,x.stat().st_size) for x in o.glob('*REV5*')])
