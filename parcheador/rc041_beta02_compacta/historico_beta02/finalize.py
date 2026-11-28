from pathlib import Path
import json,hashlib as H, re,zlib,zipfile,shutil
P=Path('/tmp/lp_reintegracion');M=Path('/mnt/data');r=json.loads((P/'report.json').read_text());exe=M/'LaPucelle_Parcheador_RC041_REV6_BETA02_GUI_Nativo.exe';replay=P/'replay/JUEGO_PARA_PPSSPP_RC041_REV6_BETA02'
def sha(p):
 with p.open('rb') as f:return H.file_digest(f,'sha256').hexdigest()
for q in r['outputs']:
 p=replay/'La_Pucelle_Ragnarok_ES_RC041_REV6_BETA02.iso' if q['name']=='ISO' else replay/'ULJS00244'/q['name'];assert sha(p)==q['target_sha256']
assert sha(replay/'ULJS00244/PARAM.PBP')==sha(Path('/tmp/lapucelle_beta1/inputs/PARAM.PBP'))
raw=exe.read_bytes();expected={sha(P/'gui/patches'/q['patch']):q['name'] for q in r['outputs']};found={}
for m in re.finditer(b'\x1f\x8b\x08',raw):
 i=m.start()
 try:
  z=zlib.decompressobj(31)
  if z.decompress(raw[i:i+65536],8)!=b'LPGUI001':continue
  z=zlib.decompressobj(31);z.decompress(raw[i:]);assert z.eof;size=len(raw)-i-len(z.unused_data);digest=H.sha256(raw[i:i+size]).hexdigest()
  if digest in expected:found[expected[digest]]=digest
 except (ValueError,AssertionError,zlib.error):continue
assert len(found)==5
r.update(windows_exe_sha256=sha(exe),windows_exe_bytes=exe.stat().st_size,embedded_streams_verified=found,linux_replay_verified=5,ppsspp_version='1.20.4',runtime_intro_candidate_sha256=sha(P/'replay_intro_only/JUEGO_PARA_PPSSPP_RC041_REV6_BETA02/La_Pucelle_Ragnarok_ES_RC041_REV6_BETA02.iso'),runtime_intro_candidate='Captura real antes de añadir 11 cadenas de EBOOT; anm3000.dat idéntico al final.',runtime_intro_first_line_capture='RC041_BETA02_Introduccion_PPSSPP.png',runtime_intro_second_line_capture='RC041_BETA02_Introduccion_segunda_PPSSPP.png',runtime_full_intro_verified=False,windows_gui_executed=False)
if (M/'RC041_BETA02_Arranque_PPSSPP.png').exists():r['runtime_final_boot_capture']='RC041_BETA02_Arranque_PPSSPP.png';r['runtime_final_boot_verified']=True;r['runtime_final_boot_observed']='Leyendo Memory Stick / Un momento'
(M/'QA_RC041_REV6_BETA02.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));
with zipfile.ZipFile(M/'LaPucelle_RC041_REV6_BETA02_Codigo_y_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['intro.py','bootmenus.py','check.py','build.py','finalize.py','intro_records.json','tutorial.json','bootmenus.json','replay.log','ppsspp.log','ppsspp_final.log']:
  z.write(P/n,n)
 for n in ['QA_RC041_REV6_BETA02.json']:z.write(M/n,n)
 for f in (P/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 for n in ['manifest.json','informe.json']:z.write(P/'gui/patches'/n,'gui/patches/'+n)
 for n in ['audit.py','fix.py']:z.write('/tmp/rc38/'+n,'dependencias/'+n)
 z.write('/tmp/rc41/implement.py','dependencias/implement.py');z.writestr('LEEME.txt','BETA02 acumulativa: ISO y cuatro DLC se verificaron desde originales. El código de laboratorio depende de rutas de trabajo y no incluye las ISO, DLC, texturas extraídas ni flujos XOR. PPSSPP 1.20.4 arrancó y se observó la primera línea de la introducción en la candidata con idéntico recurso ANM; no certifica las restantes escenas ni la GUI Windows.')
print('EXE streams:',len(found),'verified replay:',len(r['outputs']), 'sha',r['windows_exe_sha256'])
