import sys,hashlib,json,csv,re,zlib,zipfile,struct
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/rc41qa');T=P/'RC041_rev2.iso';D=P/'ULJS00244';out=Path('/mnt/data');exe=out/'LaPucelle_Parcheador_RC041_REV2_GUI_Nativo.exe'
def hs(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
def write(name,rows):
 with (P/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Re-audit approved sub-blocks, not full ANM members.
a=nis(read(T,'/PSP_GAME/USRDIR/ANMPACK.DAT'));cfg=json.loads(zipfile.ZipFile(out/'LaPucelle_RC030_Codigo_y_QA.zip').read('corrections.json'));checks=[]
for r in cfg['banners']:
 v=a[r['member']][r['block_offset']:r['block_offset']+r['size']];sha=h.sha256(v).hexdigest();assert sha==r['compact_sha'];checks.append(dict(id=r['id'],resource=r['member'],offset=r['block_offset'],size=r['size'],expected_sha256=r['compact_sha'],actual_sha256=sha,match=True))
intro=json.load(open(out/'QA_RC036_Sombras.json'))['shadow_correction'];sha=h.sha256(a['anm3000.dat']).hexdigest();assert sha==intro['rc036_sha256'];checks.append(dict(id='INTRO_RC036',resource='anm3000.dat',offset=0,size=len(a['anm3000.dat']),expected_sha256=intro['rc036_sha256'],actual_sha256=sha,match=True))
b=nis(read(T,'/PSP_GAME/USRDIR/BGPACK.DAT'));sha=h.sha256(b['wmap_03.txp']).hexdigest();assert sha==hs(out/'wmap_03_Mapa_pulido.txp');checks.append(dict(id='MAPA_RC032',resource='wmap_03.txp',offset=0,size=len(b['wmap_03.txp']),expected_sha256=sha,actual_sha256=sha,match=True));write('graficos_aprobados_verificados.csv',checks)
# Historical ROM039 closure offsets from data/control/ROM039_intervalos_consolidacion.json, 574d15750ef2128d0294dd5ea55cbf8f8020ebfd.
cl='''9442 anm3210.dat 653642432 5472
9445 anm3510.dat 656773456 5456
9455 anm4507.dat 665277408 5472
9450 anm4009.dat 668811216 5472
9449 anm3904.dat 671821072 5472
9445 anm3509.dat 683068960 5456
9442 anm3211.dat 692430288 5472
9443 anm3313.dat 695099328 5472
9441 anm3110.dat 698173296 5472
9443 anm3310.dat 704990624 5472
9441 anm3105.dat 708525136 5472
9446 anm3611.dat 710250000 5456
9443 anm3314.dat 712860432 5472
9445 anm3511.dat 714290768 5456
9456 anm4608.dat 723631104 5472
9444 anm3404.dat 724130752 5472
9457 anm4709.dat 727239680 5472
9441 anm3107.dat 732457920 5472
9448 anm3805.dat 735890880 5472
9444 anm3412.dat 737602512 5472
9447 anm3704.dat 740671648 5472
9451 anm4107.dat 747201856 5456'''
closures=[]
with SRC.open('rb') as orig,T.open('rb') as final:
 for row in cl.splitlines():
  gid,member,off,n=row.split();off=int(off);n=int(n);orig.seek(off);final.seek(off);x,y=orig.read(n),final.read(n);closures.append(dict(group=gid,member=member,offset=off,size=n,original_sha256=h.sha256(x).hexdigest(),actual_sha256=h.sha256(y).hexdigest(),identical_to_original=x==y,status='Edición histórica no presente' if x==y else 'Comparar contra payload histórico'))
write('cierres_ROM039.csv',closures)
# 62 historical inventory units: resource-level coverage, not individual region certification.
_,origp=inventory(SRC,Path('/tmp/rc38/orig'));_,newp=inventory(T,D);origb=nis(read(SRC,'/PSP_GAME/USRDIR/BGPACK.DAT'));hist=[]
def add(ids,resource):
 if resource.startswith('BGPACK.DAT/'):
  n=resource.split('/')[-1];x,y=origb[n],b[n]
 else:
  n=resource.split('/')[-1];x,y=origp['ISO_START'][n],newp['ISO_START'][n]
 for i in ids:hist.append(dict(unit_id=i,resource=resource,resource_modified=x!=y,status='Mapa exacto aprobado' if n=='wmap_03.txp' else 'Contenedor modificado: cotejo de región pendiente' if x!=y else 'Recurso idéntico al original'))
for i,j in enumerate(list(range(1,13))+list(range(15,19))):add([26197+i],f'BGPACK.DAT/at{j:02}.txp')
for i,n in [(26213,'title_mj.txp'),(26214,'wmap_03.txp'),(26215,'title2.txp')]:add([i],'BGPACK.DAT/'+n)
for lo,hi,n in [(26216,26225,'sys3.txp'),(26226,26231,'sys4.txp'),(26232,26247,'sys6.txp'),(26248,26253,'item.txp'),(26254,26255,'sys2.txp'),(26256,26257,'sys5.txp'),(26258,26258,'sys7.txp')]:add(range(lo,hi+1),'ISO_START/'+n)
assert len(hist)==62;write('inventario_historico_62.csv',hist)
# Prove embedded streams in Windows build equal the tested Linux worker streams.
raw=exe.read_bytes();found={};expected={hs(P/'gui/patches'/x['patch']):x['name'] for x in json.load(open(P/'gui/patches/manifest.json'))['specs']}
for m in re.finditer(b'\x1f\x8b\x08',raw):
 i=m.start()
 try:
  obj=zlib.decompressobj(31)
  if obj.decompress(raw[i:i+65536],8)!=b'LPGUI001':continue
  obj=zlib.decompressobj(31);data=obj.decompress(raw[i:]);assert obj.eof;length=len(raw)-i-len(obj.unused_data);sha=h.sha256(raw[i:i+length]).hexdigest()
  if sha in expected:found[expected[sha]]=sha
 except (ValueError,AssertionError,zlib.error):continue
assert len(found)==5,found
r=json.load(open(P/'QA_RC041_rev2.json'));s0=json.load(open(P/'summary.json'));r.update(talk_audit=s0['talk'],long_lines=s0['long_lines'],decode_error_candidates=s0['decode_candidates'],known_approved_graphics_exact=len(checks),carteles_exact=19,intro_shadow_exact=True,map_exact=True,historical_units=62,historical_units_in_unmodified_resources=sum(not x['resource_modified'] for x in hist),historical_units_in_modified_resources=sum(x['resource_modified'] for x in hist),historical_closures_checked=len(closures),historical_closures_identical_to_original=sum(x['identical_to_original'] for x in closures),resource_inventory_graphics=s0['graphics_total'],modified_graphic_resources=s0['graphics_changed'],windows_exe_sha256=hs(exe),embedded_streams_verified=found,linux_replay_passes=5,limitations=['No PPSSPP ni GUI Windows disponibles; no pruebas en ejecución.','No se ha recuperado RC024 ni el BPS privado de ROM039; los cierres y las ediciones gráficas históricas faltantes requieren payload aprobado o una nueva edición.','Auditoría TALK estructural y coincidencias exactas; no certifica revisión semántica de todo el juego.','Correcciones de tablas nuevas se basan en localización inglesa y anclas japonesas equivalentes; revisión contextual pendiente.','Los campos reutilizados de DLC00 mantienen traducción previa; no son traducciones nuevas.','Espaciado: no modificado sin confirmar el comportamiento del renderizador; no se puede validar por longitud de bytes.','No se han subido cambios al repositorio.'])
(out/'QA_RC041_REV2.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items() if k in ('changes','historical_units_in_unmodified_resources','historical_units_in_modified_resources','historical_closures_checked','historical_closures_identical_to_original','known_approved_graphics_exact','linux_replay_passes')},ensure_ascii=False));print('exe embedded',len(found))
