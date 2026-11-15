#!/usr/bin/env python3
"""Cambia únicamente cadenas ASCII de tamaño fijo de EBOOT.BIN.

Sin mover instrucciones, direcciones, secciones ELF o terminadores.
Los cambios NO certifican que el texto quede visible en PSP ni que los menús
quepan gráficamente: existen abreviaciones editoriales aprobadas en un CSV.
Now Loading permanece en inglés por petición del titular.
"""
import argparse,csv,hashlib,json,sys,re
from pathlib import Path
from collections import Counter

def entries(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def apply(raw,manifest,report,menus):
 report_by_id={r['unit_id']:r for r in report}
 curated={r['original']:r['es'] for r in menus}
 selected=[r for r in manifest if r['recurso']=='ISO/PSP_GAME/SYSDIR/EBOOT.BIN']
 if len(selected)!=259:raise ValueError('Manifiesto no corresponde a los 259 EBOOT esperados')
 output=bytearray(raw); rows=[];changes=[]
 for row in selected:
  uid=row['unit_id'];off=int(row['offset']);source=row['original'];r=report_by_id.get(uid,{})
  target=curated.get(source)
  if target is None and r.get('estado_editorial')=='revisado':target=r.get('es_revisado')
  if source.lower().strip()=='now loading' or (target or '').lower().strip()=='now loading':
   rows.append({'unit_id':uid,'original':source,'traduccion':'','offset':off,'estado':'OMITIDO_NOW_LOADING','motivo':'Exclusión solicitada'});continue
  if target is None:
   rows.append({'unit_id':uid,'original':source,'traduccion':'','offset':off,'estado':'SIN_TRADUCCION_APROBADA','motivo':'No hay ajuste editorial o estado revisado'});continue
  if not source.isascii() or not target.isascii() or not target.strip() or re.search(r'[%{}<>\\\r\n]',target+source):
   rows.append({'unit_id':uid,'original':source,'traduccion':target,'offset':off,'estado':'NO_APTO_ASCII','motivo':'Caracteres especiales o control'});continue
  if off<0 or off>=len(raw):raise ValueError('Offset EBOOT fuera de rango')
  end=raw.find(b'\0',off,min(len(raw),off+256))
  if end==-1:
   rows.append({'unit_id':uid,'original':source,'traduccion':target,'offset':off,'estado':'SIN_TERMINADOR','motivo':'Campo NUL no localizado'});continue
  orig=raw[off:end]
  if orig.rstrip(b' ')!=source.encode('ascii'):
   rows.append({'unit_id':uid,'original':source,'traduccion':target,'offset':off,'estado':'ORIGINAL_NO_COINCIDE','motivo':'Fuente o padding no coincidente'});continue
  if len(target)>len(orig):
   rows.append({'unit_id':uid,'original':source,'traduccion':target,'offset':off,'estado':'EXCEDE_CAMPO','motivo':f'{len(target)} > {len(orig)} bytes'});continue
  blob=target.encode('ascii').ljust(len(orig),b' ')
  for a,b in changes:
   if off<b and a<end:raise ValueError('Dos campos EBOOT se solapan')
  changes.append((off,end))
  output[off:end]=blob
  rows.append({'unit_id':uid,'original':source,'traduccion':target,'offset':off,'estado':'ASCII_TAMANO_FIJO' if blob!=orig else 'SIN_CAMBIO','motivo':'Tamaño y terminador conservados'})
 # Reconstruct exact modifications (no other bytes changed)
 expected=bytearray(raw)
 for r in rows:
  if r['estado'] not in ('ASCII_TAMANO_FIJO','SIN_CAMBIO'):continue
  off=int(r['offset']);end=raw.index(0,off)
  expected[off:end]=r['traduccion'].encode('ascii').ljust(end-off,b' ')
 if bytes(output)!=bytes(expected):raise ValueError('Se alteraron bytes fuera de cadenas EBOOT autorizadas')
 return bytes(output),rows

def run(eboot,manifest,report,menus,output,guardar=False):
 original=eboot.read_bytes();new,rows=apply(original,entries(manifest),entries(report),entries(menus))
 output.mkdir(parents=True,exist_ok=True)
 with (output/'eboot_66.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 stats={'resource':'EBOOT.BIN','estados':dict(Counter(r['estado'] for r in rows)),
  'antes_sha256':hashlib.sha256(original).hexdigest(),'despues_sha256':hashlib.sha256(new).hexdigest(),
  'mismo_tamano':len(original)==len(new),'now_loading_intacto':True,
  'advertencia':'Candidatos ASCII de tamaño fijo, no se ha probado PPSSPP'}
 (output/'resumen_eboot_66.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
 if guardar:
  folder=output/'borradores';folder.mkdir(exist_ok=True)
  (folder/'PSP_EBOOT.BIN').write_bytes(new)
 return stats

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ('eboot','manifest','report','menus','output'):
  p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--guardar-borrador',action='store_true')
 a=p.parse_args()
 print(json.dumps(run(a.eboot,a.manifest,a.report,a.menus,a.output,a.guardar_borrador),ensure_ascii=False,indent=2))
