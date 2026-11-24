"""Construcción reproducible desde ISO/DLC originales, sin recursos base del laboratorio."""
from pathlib import Path
import argparse,csv,json,struct,sys,zlib,hashlib,shutil
import construir_parche as c
ROOT=c.ROOT if (c.ROOT/'investigacion').is_dir() else c.ROOT.parent
for sub in ('investigacion/v0.10','investigacion/v0.14'):sys.path.insert(0,str(ROOT/sub))
from nis_formats import nispack,lzs_decompress
from contenedores import reconstruir_dat,reconstruir_nispack
from iso_reubicar import anexar_recurso
from integrar_scripts_v014 import load_rows,plan
from fuentes_es import add_spanish_fonts
from atlas_ui_es import apply as atlas
from formato_talk import inspect
from recompilar_talk import catalog,compile_one
from menus_adicionales import aplicar as menus_extra
from correcciones_tablas_qa import aplicar as etiquetas
from campos_revisados import aplicar as campos
from revisiones_coordinadas import merge_central
VERSION='0.19.0-integracion'
# ISO base auténtica, comprobada en la auditoría de recursos originales.
ISO_BASE_SHA256='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
def verificar_iso_base(ruta):
 if not ruta.is_file():raise ValueError('No existe la ISO original: '+str(ruta))
 digest=c.sha_file(ruta)
 if digest.lower()!=ISO_BASE_SHA256:raise ValueError('SHA-256 de ISO original no reconocido: '+digest)
 return digest

def verificar_destinos(iso,dlc_directorio,salida):
 """Rechaza salidas peligrosas antes de crear cualquier fichero."""
 out=salida.resolve()
 entradas=[]
 if iso:entradas.append(iso.resolve())
 if dlc_directorio:
  carpeta=dlc_directorio.resolve()
  if not carpeta.is_dir():raise ValueError('No existe la carpeta DLC original')
  entradas.append(carpeta)
  for n in range(4):
   archivo=carpeta/f'DL_JP_{n:02d}.EDAT'
   if not archivo.is_file():raise ValueError('Falta DLC original: '+archivo.name)
   entradas.append(archivo.resolve())
 for src in entradas:
  if out==src or src.is_relative_to(out) or out.is_relative_to(src):
   raise ValueError('La salida no puede contener ni sobrescribir recursos originales: '+str(src))
 if out.exists():
  if not out.is_dir():raise ValueError('La salida existe y no es un directorio')
  if any(out.iterdir()):raise ValueError('La salida debe estar vacía para evitar mezclas y sobrescrituras')
 return out

def aplicar_capitulos_gfx008(iso_original,iso_destino,fuente):
 """Aplica 16 deltas TXP autenticados sobre candidata textual, sin reubicar BGPACK."""
 import importlib.util
 ruta=c.ROOT.parents[1]/'scripts/gfx007_editar_capitulos.py'
 if not ruta.is_file():raise ValueError('GFX-008: falta el editor TXP del repositorio')
 spec=importlib.util.spec_from_file_location('gfx007_editar_capitulos',ruta)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 ref=json.loads((c.ROOT.parents[1]/'docs/seguimiento/informes/GFX-007_capitulos_piloto.json').read_text(encoding='utf8'))
 if c.sha_file(iso_original)!=ref['iso_original_sha256']:
  raise ValueError('GFX-008: ISO original no autenticada')
 original=c.Image(iso_original)
 destino=c.Image(iso_destino)
 a={p:(o,n) for p,o,n,_ in original.records()}
 b={p:(o,n) for p,o,n,_ in destino.records()}
 key='/PSP_GAME/USRDIR/BGPACK.DAT'
 if key not in a or key not in b or a[key]!=b[key]:
  raise ValueError('GFX-008: BGPACK reubicado; no se permite escritura directa')
 bg=original.read(*a[key])
 if c.sh(bg)!=ref['BGPACK_original_sha256']:
  raise ValueError('GFX-008: BGPACK original distinto')
 patched=bytearray(bg);report={}
 for i in range(struct.unpack_from('<I',bg,12)[0]):
  name,offset,size,_=struct.unpack_from('<32sIII',bg,16+44*i)
  name=name.partition(bytes([0]))[0].decode('cp932')
  if name not in ref['assets']:continue
  old=bg[offset:offset+size]
  if c.sh(old)!=ref['assets'][name]['original_sha256']:
   raise ValueError('GFX-008: TXP original distinto: '+name)
  new,proof=mod.edit(old,int(name[2:4]),fuente)
  if proof['nuevo_sha256']!=ref['assets'][name]['nuevo_sha256']:
   raise ValueError('GFX-008: edición no reproducible: '+name)
  patched[offset:offset+size]=new;report[name]=proof
 if set(report)!=set(ref['assets']) or c.sh(patched)!=ref['BGPACK_piloto_sha256']:
  raise ValueError('GFX-008: BGPACK reconstruido no reproducible')
 if destino.read(*b[key])!=bg:
  raise ValueError('GFX-008: candidata textual ya alteró BGPACK')
 with iso_destino.open('r+b') as stream:
  stream.seek(b[key][0]);stream.write(patched)
 reread=c.Image(iso_destino)
 if reread.read(*b[key])!=patched:raise ValueError('GFX-008: escritura no verificable')
 return dict(assets=report,BGPACK_original_sha256=c.sh(bg),
             BGPACK_piloto_sha256=c.sh(patched),ppsspp=False)

def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def run(args):
 # Preflight de originales y rutas antes de crear directorios o escribir una candidata.
 if args.iso:verificar_iso_base(args.iso)
 out=verificar_destinos(args.iso,args.dlc_directorio,args.salida)
 out.mkdir(parents=True,exist_ok=True)
 final=out/'JUEGO_PARA_PPSSPP'
 stage=out/'construccion';stage.mkdir(exist_ok=False)
 reports=out/'informes';reports.mkdir(exist_ok=True)
 manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')))
 reviews,checks,states=c.read_reviews(args.repo_directorio,False)
 reviews,checks,states=merge_central(args.repo_directorio,reviews,manifest,checks,states)
 packs={};sources={};buffers={};rec={};iso=None;sp=None
 if args.iso:
  iso=c.Image(args.iso);rec={p:(o,n) for p,o,n,_ in iso.records()}
  blob=iso.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])
  if c.sh(blob)!=c.SHA_ISO_START:raise ValueError('START original desconocido')
  packs['ISO_START']=dict(lzs=blob)
  sp=iso.read(*rec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])
  for it in nispack(sp):
   res='ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+it['name']
   if it['name'].startswith('talk'):buffers[res]=it['content']
   if it['name'].startswith('script'):sources[res]=it['content']
 if args.dlc_directorio:
  for n in range(4):
   blob=(args.dlc_directorio/f'DL_JP_{n:02d}.EDAT').read_bytes()
   parts=nispack(blob)
   if len(parts)!=1 or parts[0]['name'].lower()!='start_jp.lzs':raise ValueError('DLC desconocido')
   packs[f'DLC_{n:02d}']=dict(lzs=parts[0]['content'],header=blob[:2048])
 deltas=json.loads(zlib.decompress((c.ROOT/'datos/tablas_base_deltas.json.z').read_bytes()))
 proof={}
 for key,obj in packs.items():
  raw=lzs_decompress(obj['lzs'],allow_overlap=False);original=c.members_from_dat(raw)
  members={n:bytearray(v) for n,v in original.items()};obj.update(raw=raw,members=members)
  for name,body in original.items():
   res=key+'/'+name
   if name.startswith('talk'):buffers[res]=bytes(body)
   if name.startswith('script'):sources[res]=bytes(body)
   if res in deltas:
    d=deltas[res]
    if c.sh(body)!=d['original_sha256'] or len(body)!=d['size']:raise ValueError('Tabla original distinta: '+res)
    for off,h in d['changes']:members[name][off:off+len(bytes.fromhex(h))]=bytes.fromhex(h)
    if c.sh(members[name])!=d['nuevo_sha256']:raise ValueError('Delta de tabla incorrecto')
  proof[key]=dict(fuentes=add_spanish_fonts(members),atlas=atlas(members),etiquetas=etiquetas(key,original,members,manifest,reviews))
  proof[key]['campos']=campos(key,original,members,manifest,reviews)
 metas={res:inspect(raw) for res,raw in buffers.items()}
 segments=json.loads((c.ROOT/'datos/segmentos_talk_revisados.json').read_text(encoding='utf8'))
 extra=c.ROOT/'datos/segmentos_hymt2_aprobados.json'
 if extra.is_file():segments+=json.loads(extra.read_text(encoding='utf8'))
 segments=[s for s in segments if s['recurso'] in buffers]
 scopes=json.loads((c.ROOT/'datos/segmentos_centrales_anclados.json').read_text(encoding='utf8'))
 trie,rejected=catalog(manifest,reviews,buffers,metas,segments=segments,scoped=scopes)
 talks={};applied=[];pending=[];preserved=[]
 for res,raw in buffers.items():
  font=packs['ISO_START' if res.startswith('ISO/') else res.split('/')[0]]['members']
  data,ok,bad,journal=compile_one(res,raw,metas[res],trie,font)
  if res.startswith('ISO/') and len(data)>286072:raise ValueError('Talk excede búfer ampliado: '+res)
  talks[res]=data;applied+=ok
  preserved += [r for r in bad if r['motivo']=='SIGNOS_ORIGINALES_CONSERVADOS']
  pending += [r for r in bad if r['motivo']!='SIGNOS_ORIGINALES_CONSERVADOS']
  dump(reports/(res.replace('/','__')+'.talk.json'),journal)
  print(res,len(ok),'bloques insertados;',len(bad),'pendientes',flush=True)
 index=c.ROOT/'datos/estado_unificado_66.csv'
 if not index.exists():index=ROOT/'informes/estado_unificado_66.csv'
 rows=load_rows(c.DATA,index,reviews=reviews)
 rows={k:v for k,v in rows.items() if k in sources}
 scripts,script_report,script_stats=plan(rows,sources,'conservador')
 for res,obj in scripts.items():
  if res.startswith('ISO/') and len(obj['raw'])>=59000:raise ValueError('Script excede búfer: '+res)
  dump(reports/(res.replace('/','__')+'.script.json'),obj['journal'])
 replacements={**talks,**{r:o['raw'] for r,o in scripts.items()}}
 rebuilt={}
 for key,obj in packs.items():
  for res,blob in replacements.items():
   if res.startswith(key+'/'):obj['members'][res.split('/')[-1]]=bytearray(blob)
  raw=reconstruir_dat(obj['raw'],{n:bytes(v) for n,v in obj['members'].items()})
  packed=c.cpack(raw,obj['lzs'],key)
  assert lzs_decompress(packed,allow_overlap=False)==raw
  rebuilt[key]=packed
  print('Contenedor verificado:',key,flush=True)
 if iso:
  changes={res.split('/')[-1]:blob for res,blob in replacements.items() if res.startswith('ISO/')}
  spnew=reconstruir_nispack(sp,changes)
  first=stage/'etapa_start.iso';dest=stage/'La_Pucelle_Ragnarok_ES.iso'
  anexar_recurso(args.iso,first,'/PSP_GAME/USRDIR/START_JP.LZS',rebuilt['ISO_START'])
  anexar_recurso(first,dest,'/PSP_GAME/USRDIR/SCRIPTPACK.DAT',spnew)
  eboot=iso.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN']);new=bytearray(eboot)
  labels,bad=c.sustituir_eboot_ascii(new,manifest,reviews,{},c.cargar_menus_centrales(),True)
  if bad:raise ValueError('Menús rechazados: '+repr(bad))
  new,extras=menus_extra(eboot,new)
  for address in (0x088422d8,0x08844c8c,0x08846440,0x088464b8,0x08846658,0x08846698,0x08847394,0x088478f4,0x08853604):
   off=address-(142622720-84)
   if struct.unpack_from('<I',new,off)[0]!=0x3c020002:raise ValueError('Instrucción EBOOT distinta')
   struct.pack_into('<I',new,off,0x3c020004)
  reread=c.Image(dest);rr={p:(o,n) for p,o,n,_ in reread.records()}
  with dest.open('r+b') as f:f.seek(rr['/PSP_GAME/SYSDIR/EBOOT.BIN'][0]);f.write(new)
  assert reread.read(*rr['/PSP_GAME/SYSDIR/EBOOT.BIN'])==new
  assert reread.read(*rr['/PSP_GAME/USRDIR/START_JP.LZS'])==rebuilt['ISO_START']
  assert reread.read(*rr['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])==spnew
  if args.fuente_capitulos:
   proof['GFX_008']=aplicar_capitulos_gfx008(args.iso,dest,args.fuente_capitulos)
   dump(reports/'GFX-008_capitulos_integrados.json',proof['GFX_008'])
  for path,pair in rec.items():
   if path not in ('/PSP_GAME/SYSDIR/EBOOT.BIN','/PSP_GAME/USRDIR/START_JP.LZS','/PSP_GAME/USRDIR/SCRIPTPACK.DAT'):assert rr[path]==pair
  first.unlink()
 if args.dlc_directorio:
  d=stage/'ULJS00244';d.mkdir()
  for n in range(4):
   key=f'DLC_{n:02d}';header=bytearray(packs[key]['header']);struct.pack_into('<I',header,0x34,len(rebuilt[key]))
   p=d/f'DL_JP_{n:02d}.EDAT';p.write_bytes(header+rebuilt[key]);assert nispack(p.read_bytes())[0]['content']==rebuilt[key]
 dump(reports/'dialogos_aplicados.json',applied);dump(reports/'dialogos_pendientes.json',pending)
 dump(reports/'signos_originales_conservados.json',preserved)
 dump(reports/'scripts.json',script_report);dump(reports/'grupos_no_catalogados.json',rejected)
 hashes={str(p.relative_to(stage)):c.sha_file(p) for p in stage.rglob('*') if p.is_file()}
 summary=dict(version=VERSION,bloques_talk_insertados=len(applied),bloques_talk_pendientes=len(pending),bloques_signos_originales=len(preserved),scripts=dict(script_stats),hashes=hashes,componentes=proof,corpus_sha256=checks,estado_editorial=dict(states),validacion_visual='PENDIENTE: no certifica PPSSPP ni traducción completa')
 dump(reports/'construccion.json',summary)
 stage.rename(final)
 print('Entrega generada:',final,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--iso',type=Path);p.add_argument('--dlc-directorio',type=Path);p.add_argument('--repo-directorio',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--fuente-capitulos',type=Path,help='Fuente local para integrar los 16 TXP de GFX-007 en la candidata textual')
 a=p.parse_args()
 if not(a.iso or a.dlc_directorio):p.error('Selecciona ISO, DLC o ambos')
 if a.fuente_capitulos and not a.iso:p.error('--fuente-capitulos requiere --iso')
 if a.fuente_capitulos and not a.fuente_capitulos.is_file():p.error('No existe la fuente de capítulos')
 run(a)
if __name__=='__main__':main()
