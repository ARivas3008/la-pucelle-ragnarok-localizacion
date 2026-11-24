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
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def run(args):
 out=args.salida.resolve();out.mkdir(parents=True,exist_ok=True)
 final=out/'JUEGO_PARA_PPSSPP'
 if final.exists():raise ValueError('La salida ya contiene una entrega; elige una carpeta vacía')
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
 p=argparse.ArgumentParser();p.add_argument('--iso',type=Path);p.add_argument('--dlc-directorio',type=Path);p.add_argument('--repo-directorio',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
 a=p.parse_args()
 if not(a.iso or a.dlc_directorio):p.error('Selecciona ISO, DLC o ambos')
 run(a)
if __name__=='__main__':main()
