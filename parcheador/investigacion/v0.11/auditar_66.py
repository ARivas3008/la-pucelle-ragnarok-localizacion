#!/usr/bin/env python3
"""Deterministic 66-resource audit; no file changes.

Uses an existing 26,258-unit physical manifest and a matching translation report.
The report is only a snapshot: it is NOT authorization to insert uncertain text.
"""
from __future__ import annotations
import argparse,csv,json,sys,hashlib,struct,unicodedata
from pathlib import Path
from collections import Counter,defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from script_relocator import ScriptTable
from campos_v011 import locate,PERFILES
from txp_verify import inspect as inspect_txp, TXPError
from nis_formats import nispack
from iso_inspect import ISO
from fuentes_es import encode_es,FontError

PROFILES=set(PERFILES)

def classify(resource):
 name=resource.rsplit('/',1)[-1].lower()
 if name in PROFILES:return 'TABLA_FIJA'
 if name.startswith('script') and name.endswith('.dat'):return 'SCRIPT'
 if name=='eboot.bin':return 'EBOOT'
 if name.endswith('.txp'):return 'TEXTURA'
 return 'OTRO'

def physical_file(root:Path,resource:str):
 if resource.startswith('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'):
  return root/'ISO_SCRIPT'/resource.rsplit('/',1)[-1]
 if resource.startswith('ISO/PSP_GAME/SYSDIR/EBOOT.BIN'):
  return root/'PSP_EBOOT.BIN'
 if resource.split('/')[0] in ['ISO_START','DLC_00','DLC_01','DLC_02','DLC_03']:
  return root/resource
 return None

def exact_match(raw:bytes,off:int,expected:str):
 if off<0 or off>=len(raw) or not expected:return None,None
 end=raw.find(b'\0',off,min(len(raw),off+1024))
 if end<off:return None,None
 stored=raw[off:end]
 try:found=stored.decode('cp932')
 except UnicodeError:return None,None
 def norm(x):return unicodedata.normalize('NFKC',x)
 if norm(found)!=norm(expected):
  if norm(found).strip()!=norm(expected).strip():return None,None
  return 'ESPACIOS_EXTERIORES',stored
 return 'COINCIDENCIA',stored

def check(args):
 with args.manifest.open(encoding='utf-8-sig',newline='') as f:
  manifest=[r for r in csv.DictReader(f) if '/talk' not in r['recurso'].lower()]
 text={}
 if args.report.is_file():
  with args.report.open(encoding='utf-8-sig',newline='') as f:
   for r in csv.DictReader(f):text[r['unit_id']]=r
 if len(manifest)!=4507 or len({r['recurso'] for r in manifest})!=66:
  raise ValueError('Expected exactly 4507 units / 66 resources, got '+str((len(manifest),len({r['recurso'] for r in manifest}))))
 paths={r['recurso']:physical_file(args.source,r['recurso']) for r in manifest}
 contents={res:path.read_bytes() if path and path.is_file() else None for res,path in paths.items()}
 if args.iso and args.iso.is_file():
  # Original BGPACK is in ISO; no binary asset is copied to the result archive.
  iso=ISO(str(args.iso))
  try:
   found=[(size,off) for path,size,off,isdir in iso.walk() if path.upper()=='/PSP_GAME/USRDIR/BGPACK.DAT']
   if len(found)!=1:raise ValueError('BGPACK.DAT missing/duplicate in ISO')
   size,offset=found[0]
   byname={x['name']:x['content'] for x in nispack(iso.read(offset,size))}
  finally:
   iso.fp.close()
  for res in contents:
   if '/BGPACK.DAT/' in res:
    contents[res]=byname.get(res.rsplit('/',1)[-1])
 scripts={res:ScriptTable(b) for res,b in contents.items() if b and classify(res)=='SCRIPT'}
 rows=[]
 for row in manifest:
  uid=row['unit_id'];res=row['recurso'];gid=row['grupo_id'];kind=classify(res)
  r=text.get(uid,{});spanish=r.get('es_revisado','') or ''
  state=r.get('estado_editorial','sin_reporte')
  off=int(row['offset']);original=row['original'];buf=contents[res]
  raw_source=None;byte_len=None;cap=None;size_es=None;status='';detail=''
  if buf is None:status='RECURSO_NO_EXTRAIDO'
  elif kind=='TEXTURA':
   try:
    tex=inspect_txp(buf)
    status='TEXTURA_FORMATO_VERIFICADO'
    detail=f"{tex['width']}×{tex['height']} px; {tex['bpp']}bpp; {tex['palette_banks']} paleta(s). Traducción gráfica pendiente."
   except TXPError as exc:
    status='TEXTURA_FORMATO_DESCONOCIDO';detail=str(exc)
  else:
   quality,raw_source=exact_match(buf,off,original)
   if raw_source is None:
    status='FUENTE_NO_COINCIDE'
    detail='Los bytes descodificados no corresponden al original del manifiesto'
   else:
    byte_len=len(raw_source)
    if kind=='TABLA_FIJA':
     campo=locate(res,buf,off,raw_source)
     cap=campo.longitud if campo else None
     if cap is None:status='CAMPO_NO_VERIFICADO'
     else:status='CAMPO_FIJO_VERIFICADO'
    elif kind=='SCRIPT':
     tab=scripts[res]
     if off>=2 and buf[off-2]==0x32 and buf[off-1]==len(raw_source)+1:
      status='SCRIPT_32_VERIFICADO';cap=254
     else:status='SCRIPT_CONTROL_DIFERENTE'
    elif kind=='EBOOT':
     if all(32<=c<127 for c in raw_source):status='EBOOT_ASCII_VERIFICADO';cap=len(raw_source)
     else:status='EBOOT_REQUIERE_RELOCALIZACION'
  if spanish.strip():
   try:size_es=len(encode_es(spanish))
   except (FontError,UnicodeError) as exc:
    detail=(detail+' | ' if detail else '')+'Español con códigos no cubiertos: '+str(exc)[:140]
  fit=''
  if cap is not None and size_es is not None:
   fit='DENTRO_DE_CAPACIDAD' if size_es+(1 if kind=='TABLA_FIJA' else 0)<=cap else 'EXCEDE_CAPACIDAD'
  rows.append(dict(unit_id=uid,grupo_id=gid,recurso=res,tipo=kind,offset=off,
    situacion=status,calidad_fuente=quality if buf is not None and kind!='TEXTURA' else '',
    bytes_original=byte_len,capacidad_total=cap,bytes_espanol=size_es,encaje=fit,
    estado_editorial=state,estado_reporte_anterior=r.get('estado',''),
    original=original,es_revisado=spanish,detalle=detail))
 args.output.mkdir(parents=True,exist_ok=True)
 dest=args.output/'auditoria_66_unidades.csv'
 with dest.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 byres=defaultdict(list)
 for r in rows:byres[r['recurso']].append(r)
 per=[]
 for name,rs in sorted(byres.items()):
  file=contents[name]
  per.append(dict(recurso=name,tipo=classify(name),unidades=len(rs),bytes_archivo=len(file) if file else None,
    sha256_original=hashlib.sha256(file).hexdigest() if file else '',
    verificados=sum(r['situacion'] in {'CAMPO_FIJO_VERIFICADO','SCRIPT_32_VERIFICADO','EBOOT_ASCII_VERIFICADO'} for r in rs),
    fuente_no_coincide=sum(r['situacion']=='FUENTE_NO_COINCIDE' for r in rs),
    con_espanol=sum(bool(r['es_revisado'].strip()) for r in rs),
    cabe=sum(r['encaje']=='DENTRO_DE_CAPACIDAD' for r in rs),
    excede=sum(r['encaje']=='EXCEDE_CAPACIDAD' for r in rs)))
 with (args.output/'66_recursos.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(per[0]));w.writeheader();w.writerows(per)
 report={'auditoria':'ESTRUCTURAL, NO APROBACIÓN DE JUGABILIDAD NI DE TRADUCCIÓN',
  'total_unidades':len(rows),'total_recursos':len(per),
  'por_tipo':dict(Counter(r['tipo'] for r in rows)),
  'por_estado':dict(Counter(r['situacion'] for r in rows)),
  'por_encaje':dict(Counter(r['encaje'] for r in rows)),
  'status_editorial':dict(Counter(r['estado_editorial'] for r in rows)),
  'es_revisado_disponible':sum(bool(r['es_revisado'].strip()) for r in rows),
  'nota':'Verificado significa formato fuente coherente, no libre de referencias MIPS, metadata, glyphs ni clips de UI'}
 (args.output/'resumen_66.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--manifest',type=Path,required=True)
 p.add_argument('--report',type=Path,required=True)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--iso',type=Path,required=True)
 p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'informes')
 print(json.dumps(check(p.parse_args()),ensure_ascii=False,indent=2))
