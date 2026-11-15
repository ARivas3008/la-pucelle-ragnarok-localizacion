#!/usr/bin/env python3
"""Inserción *experimental* de scripts La Pucelle Ragnarok, ISO + DLC.

No toca binarios originales. Cadenas 0x32 reciben la longitud real; las tablas
se reubican con verificación inversa. El modo conservador RECHAZA punteros que
caigan en medio de caracteres CP932. La inspección binaria no prueba PPSSPP.

Proyecto del usuario. Código fuente propio, no incluye contenidos comerciales.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,re,shutil,struct,subprocess,sys,tempfile,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[1]                       # parcheador/
for name in ('app/scripts','investigacion/v0.10','investigacion/v0.12'):
 p=ROOT/name
 if not p.is_dir():
  raise RuntimeError('Dependencia no publicada en el repositorio: '+str(p))
 sys.path.insert(0,str(p))
from nis_formats import lzs_decompress, lzs_header, nispack
from contenedores import reconstruir_dat, reconstruir_nispack
from iso_reubicar import recorrer, IsoError
from reubicador_anclas_v012 import Reubicador, Edicion, ReubicacionInsegura, limites_cp932
from fuentes_es import encode_es, FontError, add_spanish_fonts, missing_render_glyphs, CODIGOS

class Peligro(ValueError):pass

def sha(raw):return hashlib.sha256(raw).hexdigest()

def match(raw,offset,expected):
 """Equivalencia NFKC+espacios externos; nunca busca otra posición parecida."""
 if not (0<=offset<len(raw)) or not expected:return None
 end=raw.find(b'\0',offset,min(len(raw),offset+2048))
 if end<=offset:return None
 b=raw[offset:end]
 try:got=b.decode('cp932')
 except UnicodeError:return None
 canon=lambda s:unicodedata.normalize('NFKC',s).strip()
 return b if canon(got)==canon(expected) else None

def load_rows(manifest,report):
 with Path(manifest).open(encoding='utf-8-sig',newline='') as f:
  idx={row['unit_id']:row for row in csv.DictReader(f)}
 with Path(report).open(encoding='utf-8-sig',newline='') as f:
  report_rows=list(csv.DictReader(f))
 byres=defaultdict(list)
 for row in report_rows:
  res=row.get('recurso','')
  if not re.search(r'(?:^|/)script\d+\.dat$',res):continue
  uid=row['unit_id'];m=idx.get(uid)
  if not m or m['recurso']!=res or m['original']!=row.get('original'):
   raise Peligro(f'Manifiesto incoherente: {uid} {res}')
  r=dict(row);r['offset']=int(m['offset']);byres[res].append(r)
 return byres

def originals(iso,dlc):
 """Carga exclusivamente los recursos necesarios, sin cargar toda la ISO."""
 all_sources={};contexts={}
 if iso:
  from construir_parche import Image,members_from_dat
  disc=Image(iso);records={p:(off,size,record) for p,off,size,record in disc.records()}
  for file in ('/PSP_GAME/USRDIR/START_JP.LZS','/PSP_GAME/USRDIR/SCRIPTPACK.DAT'):
   if file not in records:raise Peligro('ISO sin '+file)
  start_lzs=disc.read(*records['/PSP_GAME/USRDIR/START_JP.LZS'][:2])
  start_raw=lzs_decompress(start_lzs)
  start=members_from_dat(start_raw)
  for name,body in start.items():
   if name.startswith('script') and name.endswith('.dat'):
    all_sources['ISO_START/'+name]=bytes(body)
  scriptpack=disc.read(*records['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'][:2])
  for item in nispack(scriptpack):
   if item['name'].startswith('script') and item['name'].endswith('.dat'):
    all_sources['ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+item['name']]=item['content']
  contexts['ISO']={'start_lzs':start_lzs,'start_raw':start_raw,'scriptpack':scriptpack,'records':records}
 if dlc:
  for n in range(4):
   path=Path(dlc)/f'DL_JP_{n:02d}.EDAT'
   if not path.is_file():raise Peligro('Falta '+str(path))
   b=path.read_bytes();parts=nispack(b)
   if len(parts)!=1 or parts[0]['name'].lower()!='start_jp.lzs':raise Peligro('DLC desconocido '+str(path))
   lzs=parts[0]['content'];raw=lzs_decompress(lzs)
   from construir_parche import members_from_dat
   members=members_from_dat(raw)
   for name,body in members.items():
    if name.startswith('script') and name.endswith('.dat'):
     all_sources[f'DLC_{n:02d}/'+name]=bytes(body)
   contexts[f'DLC_{n:02d}']={'source':b,'path':path,'lzs':lzs,'raw':raw,'member_name':parts[0]['name']}
 return all_sources,contexts

def contains_unsafe_reference(raw,offset,old):
 table=Reubicador(raw)
 begin=offset-table.body
 lim=set(limites_cp932(old))
 return any((begin<=ptr<begin+len(old)) and (ptr-begin not in lim) for ptr in table.pointers)

def plan(byres,sources,mode='conservador',allow_unapproved=False):
 """Planifica por unidad. Un ancla mala nunca invalida otras 489 ediciones.

 En modo fase, cada referencia de riesgo se ensaya *adicionalmente* sobre el
 lote conservador ya validado. Solo se acepta si el archivo completo se puede
 reconstruir e invertir byte a byte. Aun así no certifica PPSSPP.
 """
 results=[];changed={};stats=Counter()
 for res,rows in sorted(byres.items()):
  if res not in sources:
   for r in rows:
    results.append(dict(unit_id=r['unit_id'],recurso=res,estado='OBJETIVO_NO_SELECCIONADO',motivo='ISO/DLC no seleccionado'))
    stats['OBJETIVO_NO_SELECCIONADO']+=1
   continue
  raw=sources[res];editions=[];special=[];local_rows=[]
  for r in sorted(rows,key=lambda x:x['offset']):
   uid=r['unit_id'];status='';reason='';new=None
   original=r['original'];spanish=r.get('es_revisado','');state=r.get('estado_editorial','')
   if '読み込み中' in original or 'Now Loading' in original or 'Now Loading' in spanish:
    status='EXCLUIDO_NOW_LOADING';reason='Conservado a solicitud del usuario'
   elif state!='revisado' and not allow_unapproved:
    status='PENDIENTE_EDITORIAL';reason=state or 'Sin revisión'
   elif not spanish.strip():
    status='SIN_TRADUCCION';reason='Falta texto español'
   else:
    off=r['offset'];old=match(raw,off,original)
    if old is None:status='NO_COINCIDE_ORIGINAL';reason='Bytes fuente o offset distintos'
    elif raw[off-2:off]!=bytes([0x32,len(old)+1]):
     status='OPCODE_NO_VERIFICADO';reason='No se reconoce 0x32 + longitud'
    elif re.findall(r'%[ds]|\{[^}]*\}|\\[rn]|<[^>]+>',original)!=re.findall(r'%[ds]|\{[^}]*\}|\\[rn]|<[^>]+>',spanish):
     status='CONTROLES_DIFERENTES';reason='Control o variable no preservado'
    else:
     try:new=encode_es(spanish)
     except (FontError,UnicodeError) as e:status='FUENTE_NO_CODIFICA';reason=str(e)
     if new is not None:
      if len(new)>=255:status='OPCODE_LONGITUD_255';reason='No cabe en u8 de script'
      elif new==old:status='SIN_CAMBIO';reason='Coincide byte por byte'
      else:
       edition=Edicion(off,old,new,uid)
       is_special=(mode in ('fase','conservador') and contains_unsafe_reference(raw,off,old))
       if is_special and mode=='conservador':
        status='REFERENCIA_SUBCARACTER';reason='Ancla dentro de carácter CP932; no modificar'
       elif is_special and mode=='fase':
        status='ANCLA_FASE_PENDIENTE';reason='Pendiente de prueba de lote completo'
        special.append((edition,uid))
       else:
        editions.append(edition);status='CANDIDATO_REUBICACION';reason='Pendiente de reversión del archivo completo'
   entry=dict(unit_id=uid,recurso=res,estado=status,motivo=reason,offset=r['offset'])
   results.append(entry);local_rows.append(entry)
  if not editions and not special:continue
  byid={r['unit_id']:r for r in local_rows}
  def compile_batch(chosen):
   return Reubicador(raw,permitir_subcaracter=(mode=='experimental'),
                     preservar_fase=(mode=='fase')).aplicar(chosen)
  try:
   # Primera puerta: el lote que ya debía funcionar en modo conservador.
   compiled=compile_batch(editions) if editions else (raw,{'ediciones':[], 'anclas':[]})
  except (ReubicacionInsegura,ValueError,IndexError) as exc:
   for row in local_rows:
    if row['estado'] in ('CANDIDATO_REUBICACION','ANCLA_FASE_PENDIENTE'):
     row['estado']='REUBICACION_RECHAZADA';row['motivo']=str(exc)
   continue
  if mode=='fase':
   for edit,uid in special:
    try:
     proposal=compile_batch(editions+[edit])
    except (ReubicacionInsegura,ValueError,IndexError) as exc:
     byid[uid]['estado']='ANCLA_FASE_BLOQUEADA'
     byid[uid]['motivo']=str(exc)
    else:
     editions.append(edit);compiled=proposal
     byid[uid]['estado']='CANDIDATO_REUBICACION_FASE'
     byid[uid]['motivo']='Lote reversible, PENDIENTE de traza PPSSPP'
  if not editions:continue
  result,journal=compiled
  changed[res]={'original_sha256':sha(raw),'nuevo_sha256':sha(result),'raw':result,
                'journal':journal,'cadenas':len(editions)}
  for row in local_rows:
   if row['estado']=='CANDIDATO_REUBICACION':
    row['estado']='REUBICACION_ESTRUCTURAL';row['motivo']='Probada ida/vuelta, NO verificada en PPSSPP'
   elif row['estado']=='CANDIDATO_REUBICACION_FASE':
    row['estado']='REUBICACION_FASE_EXPERIMENTAL';row['motivo']='Fase conservada, NO verificada en PPSSPP'
 for r in results:stats[r['estado']]+=1
 return changed,results,stats

def compress(raw,original,packer):
 h=lzs_header(original)
 if not Path(packer).is_file():raise Peligro('Falta compresor LZS compilado')
 with tempfile.TemporaryDirectory(prefix='lapucelle_v014_') as tmp:
  t=Path(tmp);(t/'src.bin').write_bytes(raw)
  cmd=[str(Path(packer).resolve()),str(t/'src.bin'),str(t/'out.lzs'),h['ext'].rstrip(b'\0').decode('ascii'),str(h['marker'])]
  p=subprocess.run(cmd,check=False,capture_output=True,text=True,errors='replace')
  if p.returncode:raise Peligro('Compresor falló: '+(p.stderr or p.stdout)[:1000])
  result=(t/'out.lzs').read_bytes()
  if lzs_decompress(result)!=raw:raise Peligro('LZS no reversible')
 return result

def append_multiple_iso(input_iso,out_iso,replacements):
 """Adjunta archivos a una ISO copiada y actualiza entradas ISO9660 y volumen.

 Solo modificar entradas cuyo recurso se reconstruyó. Usar transacción .tmp.
 """
 target=Path(out_iso);origin=Path(input_iso)
 if origin.resolve()==target.resolve():raise Peligro('No sobrescribir ISO original')
 target.parent.mkdir(parents=True,exist_ok=True)
 temp=target.with_name(target.name+'.tmp')
 if temp.exists():temp.unlink()
 try:
  shutil.copyfile(origin,temp)
  with temp.open('r+b') as fp:
   records={x.ruta:x for x in recorrer(fp)}
   for path in replacements:
    if path not in records:raise Peligro('No hay entrada ISO '+path)
   fp.seek(0,os.SEEK_END)
   for name,blob in sorted(replacements.items()):
    if not isinstance(blob,bytes) or not blob:raise Peligro('Blob vacío')
    pos=fp.tell();start=(pos+2047)//2048*2048
    if start>pos:fp.write(b'\x00'*(start-pos))
    fp.write(blob)
    if fp.tell()%2048:fp.write(b'\x00'*(2048-fp.tell()%2048))
    entry=records[name].entrada
    fp.seek(entry+2)
    fp.write(struct.pack('<I',start//2048)+struct.pack('>I',start//2048))
    fp.write(struct.pack('<I',len(blob))+struct.pack('>I',len(blob)))
    fp.seek(0,os.SEEK_END)
   total=(fp.tell()+2047)//2048
   fp.seek(16*2048+80);fp.write(struct.pack('<I',total)+struct.pack('>I',total))
   fp.flush();os.fsync(fp.fileno())
  with temp.open('rb') as fp:
   indexes={x.ruta:x for x in recorrer(fp)}
   for name,expected in replacements.items():
    ent=indexes[name]
    if ent.size!=len(expected):raise Peligro('ISO tamaño incorrecto '+name)
    fp.seek(ent.offset)
    if sha(fp.read(ent.size))!=sha(expected):raise Peligro('ISO contenido incorrecto '+name)
  os.replace(temp,target)
 finally:
  if temp.exists():temp.unlink()

def compile_replacements(changed,contexts,packer,auto_fonts=True):
 """Reconstrucción reversible de script + fuentes; cero cambio fuera de miembros.

 add_spanish_fonts modifica únicamente cuatro miembros de fuente y es idempotente.
 Sin fuentes nuevas, los códigos españoles F040-F081 pueden verse invisibles.
 """
 from construir_parche import members_from_dat
 replacements={};dlcs={};glyphs={}
 def font_changes(raw,key):
  if not auto_fonts:return {}
  m=members_from_dat(raw)
  before={name:bytes(m[name]) for name in ('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')}
  try:report=add_spanish_fonts(m)
  except FontError as e:raise Peligro(f'No se puede preservar fontB de {key}: {e}') from e
  glyphs[key]=dict(glifos_agregados=report['glifos_agregados'],alias_ascii=report['alias_ascii'])
  return {name:bytes(m[name]) for name in before if bytes(m[name])!=before[name]}

 start_changes={k.split('/',1)[1]:v['raw'] for k,v in changed.items() if k.startswith('ISO_START/')}
 sp_changes={k.rsplit('/',1)[-1]:v['raw'] for k,v in changed.items() if k.startswith('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/')}
 if 'ISO' in contexts:
  ctx=contexts['ISO'];start_changes.update(font_changes(ctx['start_raw'],'ISO_START'))
 if start_changes:
  ctx=contexts['ISO'];raw=reconstruir_dat(ctx['start_raw'],start_changes)
  replacements['/PSP_GAME/USRDIR/START_JP.LZS']=compress(raw,ctx['start_lzs'],packer)
 if sp_changes:
  ctx=contexts['ISO'];repacked=reconstruir_nispack(ctx['scriptpack'],sp_changes)
  replacements['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']=repacked
 for n in range(4):
  prefix=f'DLC_{n:02d}/'
  changes={k[len(prefix):]:v['raw'] for k,v in changed.items() if k.startswith(prefix)}
  key=f'DLC_{n:02d}'
  if key not in contexts:continue
  ctx=contexts[key]
  changes.update(font_changes(ctx['raw'],key))
  if not changes:continue
  raw=reconstruir_dat(ctx['raw'],changes)
  lzs=compress(raw,ctx['lzs'],packer)
  repacked=reconstruir_nispack(ctx['source'],{ctx['member_name']:lzs})
  if lzs_decompress(nispack(repacked)[0]['content'])!=raw:raise Peligro('DLC no reversible '+key)
  dlcs[key]=repacked
 return replacements,dlcs,glyphs

def cli(args):
 if not args.iso and not args.dlc_directorio:raise Peligro('Se requiere ISO o DLC')
 if args.modo in ('experimental','fase') and not args.acepto_riesgo_referencias:
  raise Peligro('Modo experimental requiere --acepto-riesgo-referencias')
 if args.construir and not args.acepto_riesgo_ppsspp:
  raise Peligro('La reconstrucción no se ha probado en PPSSPP; confirma --acepto-riesgo-ppsspp')
 source,ctx=originals(args.iso,args.dlc_directorio)
 byres=load_rows(args.manifiesto,args.auditoria)
 changed,rows,counts=plan(byres,source,args.modo,args.incluir_investigacion)
 args.salida.mkdir(parents=True,exist_ok=True)
 rpath=args.salida/'informe_script_v014.csv'
 with rpath.open('w',newline='',encoding='utf-8-sig') as f:
  wr=csv.DictWriter(f,fieldnames=['unit_id','recurso','estado','motivo','offset']);wr.writeheader();wr.writerows(rows)
 result={'version_reubicacion':'0.16-fase-candidata' if args.modo=='fase' else '0.14',
         'modo':args.modo,'script_unidades':len(rows),'estados':dict(counts),
         'recursos_modificados':{k:{q:v[q] for q in ('original_sha256','nuevo_sha256','cadenas')} for k,v in changed.items()},
         'resultado':'SOLO VERIFICACION ESTRUCTURAL; no certifica visualización en PPSSPP',
         'now_loading':'sin modificar',
         'control_seguridad':'fase: interpretación desconocida; NO equivale a QA PPSSPP'}
 if args.construir and changed:
  replacements,dlcs,glyphs=compile_replacements(changed,ctx,args.packer,auto_fonts=not args.sin_fuentes_automaticas)
  result['fuentes_es']=glyphs
  if replacements:
   name=args.salida/'La_Pucelle_Ragnarok_ES_SCRIPT_V014_EXPERIMENTAL.iso'
   append_multiple_iso(args.iso,name,replacements)
   result['iso']=str(name)
  for key,blob in dlcs.items():
   name=args.salida/f'{key}_SCRIPT_V014_EXPERIMENTAL.EDAT';name.write_bytes(blob)
   result[key]=str(name)
  result['binarios_escritos']=True
 else:result['binarios_escritos']=False
 (args.salida/'resumen_script_v014.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result

def main():
 p=argparse.ArgumentParser(description='Inserción experimental de scripts 0x32 con índices reubicados')
 p.add_argument('--iso',type=Path)
 p.add_argument('--dlc-directorio',type=Path)
 p.add_argument('--manifiesto',type=Path,default=ROOT.parent/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv')
 p.add_argument('--auditoria',type=Path,default=ROOT/'informes/estado_unificado_66.csv',help='CSV de estado de 4507 recursos, con texto español y estado editorial')
 p.add_argument('--salida',type=Path,required=True)
 p.add_argument('--modo',choices=('conservador','experimental','fase'),default='conservador')
 p.add_argument('--incluir-investigacion',action='store_true')
 p.add_argument('--construir',action='store_true')
 p.add_argument('--sin-fuentes-automaticas',action='store_true',help='Desactivar fuentes españolas (riesgo de glifos invisibles)')
 p.add_argument('--packer',type=Path,help='Compresor NIS LZS para crear ISO/DLC')
 p.add_argument('--acepto-riesgo-ppsspp',action='store_true')
 p.add_argument('--acepto-riesgo-referencias',action='store_true')
 args=p.parse_args()
 try:
  if args.construir and not args.packer:raise Peligro('Falta --packer')
  r=cli(args);print(json.dumps(r,ensure_ascii=False,indent=2));return 0
 except (ValueError,RuntimeError,OSError) as e:
  print('BLOQUEADO:',e,file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())