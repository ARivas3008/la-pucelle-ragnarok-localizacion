from pathlib import Path
import sys,json,struct,csv,hashlib
B=Path(__file__).resolve().parent;R=B.parent
sys.path[:0]=[str(B/'fuente/parcheador/app/scripts'),str(B/'fuente/parcheador/investigacion/v0.10')]
import construir_parche as c
from nis_formats import nispack,lzs_decompress
from contenedores import reconstruir_dat,reconstruir_nispack
from iso_reubicar import anexar_recurso
from menus_adicionales import aplicar as adicionales
from fuentes_es import add_spanish_fonts
from correcciones_tablas_qa import aplicar as corregir_tablas
source=R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso'
iso=c.Image(source);rec={p:(o,n) for p,o,n,_ in iso.records()}
start=(B/'recursos_base/START_JP.LZS').read_bytes();raw=lzs_decompress(start)
manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')));reviews,_,_=c.read_reviews(B/'fuente',False)
original_members=c.members_from_dat(lzs_decompress(iso.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])))
members=c.members_from_dat(raw);font_report=add_spanish_fonts(members)
table_report=corregir_tablas('ISO_START',original_members,members,manifest,reviews)
folder=B/'dialogos_compilados'
members['talk00.dat']=(folder/'ISO_START__talk00.dat').read_bytes()
for path in (B/'scripts_compilados').glob('ISO_START__*.dat'):members[path.name.split('__')[-1]]=path.read_bytes()
start_new=reconstruir_dat(raw,{n:bytes(b) for n,b in members.items()})
start_packed=c.cpack(start_new,start,'ISO_START')
sp=(B/'recursos_base/SCRIPTPACK.DAT').read_bytes()
talks={it['name']:(folder/('ISO__PSP_GAME__USRDIR__SCRIPTPACK.DAT__'+it['name'])).read_bytes() for it in nispack(sp) if it['name'].startswith('talk')}
scripts={p.name.split('__')[-1]:p.read_bytes() for p in (B/'scripts_compilados').glob('ISO__*.dat')}
assert max(map(len,scripts.values()))<59000
sp_new=reconstruir_nispack(sp,{**talks,**scripts})
outdir=B/'prueba_correcciones';outdir.mkdir(exist_ok=True)
stage=outdir/'etapa_start.iso';dest=outdir/'La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'
audit=[anexar_recurso(source,stage,'/PSP_GAME/USRDIR/START_JP.LZS',start_packed)]
audit.append(anexar_recurso(stage,dest,'/PSP_GAME/USRDIR/SCRIPTPACK.DAT',sp_new))
orig=c.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');orec={p:(o,n) for p,o,n,_ in orig.records()}
eboot=orig.read(*orec['/PSP_GAME/SYSDIR/EBOOT.BIN']);new=bytearray(eboot)
manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')));reviews,_,_=c.read_reviews(B/'fuente',False)
menus,rejected=c.sustituir_eboot_ascii(new,manifest,reviews,{},c.cargar_menus_centrales(),True)
assert not rejected
new,extras=adicionales(eboot,new)
# Nueve cargas/asignaciones del búfer talk; solo LUI $v0,2 -> LUI $v0,4.
# Capacidad pasa de 155000 a 286072 bytes. El lector usa el tamaño real
# para fread y esta capacidad para malloc/memset. No se toca otro código.
sites=[0x088422d8,0x08844c8c,0x08846440,0x088464b8,0x08846658,0x08846698,0x08847394,0x088478f4,0x08853604]
bias=142622720-84;patches=[]
for addr in sites:
 off=addr-bias;before=struct.unpack_from('<I',eboot,off)[0]
 assert before==0x3c020002 and new[off:off+4]==eboot[off:off+4]
 struct.pack_into('<I',new,off,0x3c020004)
 patches.append(dict(direccion=hex(addr),offset=off,antes=hex(before),despues='0x3c020004'))
assert max(map(len,talks.values()))<286072
check=c.Image(dest);newrec={p:(o,n) for p,o,n,_ in check.records()}
with dest.open('r+b') as f:f.seek(newrec['/PSP_GAME/SYSDIR/EBOOT.BIN'][0]);f.write(new)
for name,(off,size) in rec.items():
 if name in ('/PSP_GAME/USRDIR/START_JP.LZS','/PSP_GAME/USRDIR/SCRIPTPACK.DAT','/PSP_GAME/SYSDIR/EBOOT.BIN'):continue
 assert newrec[name]==(off,size)
assert lzs_decompress(check.read(*newrec['/PSP_GAME/USRDIR/START_JP.LZS']),allow_overlap=False)==start_new
assert check.read(*newrec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])==sp_new
dlc_reports=[];dlcdir=outdir/'ULJS00244';dlcdir.mkdir(exist_ok=True)
for num in range(4):
 key=f'DLC_{num:02d}'
 original_dlc=(R/f'ULJS00244/ULJS00244/DL_JP_{num:02d}.EDAT').read_bytes()
 original_inner=c.members_from_dat(lzs_decompress(nispack(original_dlc)[0]['content']))
 base_lzs=(B/f'recursos_base/{key}.lzs').read_bytes();base_raw=lzs_decompress(base_lzs)
 inner=c.members_from_dat(base_raw);font=add_spanish_fonts(inner)
 labels=corregir_tablas(key,original_inner,inner,manifest,reviews)
 for path in folder.glob(key+'__*.dat'):inner[path.name.split('__')[-1]]=path.read_bytes()
 for path in (B/'scripts_compilados').glob(key+'__*.dat'):inner[path.name.split('__')[-1]]=path.read_bytes()
 decoded=reconstruir_dat(base_raw,{n:bytes(b) for n,b in inner.items()})
 compressed=c.cpack(decoded,base_lzs,key)
 header=bytearray(original_dlc[:2048]);struct.pack_into('<I',header,0x34,len(compressed))
 target=dlcdir/f'DL_JP_{num:02d}.EDAT';target.write_bytes(bytes(header)+compressed)
 assert lzs_decompress(nispack(target.read_bytes())[0]['content'],allow_overlap=False)==decoded
 dlc_reports.append(dict(recurso=key,sha256=c.sha_file(target),fuentes=font,etiquetas=labels))
result=dict(iso=str(dest),recursos_reubicados=audit,menus=len(menus),menus_adicionales=len(extras),
 fuentes=font_report,etiquetas_tablas=table_report,dlc=dlc_reports,
 capacidad_talk=286072,max_talk=max(map(len,talks.values())),parches_eboot=patches,
 iso_sha256=c.sha_file(dest),eboot_sha256=hashlib.sha256(new).hexdigest())
(B/'informes/prueba_dialogos.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ('iso','menus','menus_adicionales','max_talk','iso_sha256')},indent=2))
print('DLC verificados:',len(dlc_reports))
