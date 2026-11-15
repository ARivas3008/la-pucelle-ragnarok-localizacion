#!/usr/bin/env python3
"""Prueba de repaquetado de seis contenedores del juego proporcionado.

No distribuye la ISO, EDAT ni los recursos comerciales reconstruidos.
"""
import sys,hashlib,json,tempfile,subprocess
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'v0.11'))
from contenedores import reconstruir_nispack,reconstruir_dat,entradas_nispack,entradas_dat
from nis_formats import lzs_decompress,lzs_header,nispack

def h(b):return hashlib.sha256(b).hexdigest()
def comp(raw,original,exe):
 header=lzs_header(original)
 with tempfile.TemporaryDirectory() as d:
  x=Path(d);(x/'plain.bin').write_bytes(raw)
  z=subprocess.run([str(exe),str(x/'plain.bin'),str(x/'out.lzs'),header['ext'].rstrip(b'\x00').decode('ascii'),str(header['marker'])],capture_output=True,text=True)
  if z.returncode:raise RuntimeError('Error packer: '+z.stderr[:300])
  result=(x/'out.lzs').read_bytes()
  assert lzs_decompress(result)==raw
  return result

def test(input_path, dat_patches, script_patches, output, packer):
 inp=Path(input_path);dat_patches=Path(dat_patches);script_patches=Path(script_patches);out=Path(output);out.mkdir(exist_ok=True)
 summary={}
 def getpatch(resource):
  d=dat_patches/resource.replace('/','__').replace('.','_')
  s=script_patches/resource.replace('/','__')
  if d.is_file():return d.read_bytes()
  if s.is_file():return s.read_bytes()
  return None
 def audit(typ,old_members,new_members,changes):
  assert old_members.keys()==new_members.keys()
  assert all(new_members[k]==changes.get(k,old_members[k]) for k in old_members)
  return {'total_miembros':len(old_members),'modificados':len(changes),'otros_intactos':sum(new_members[k]==old_members[k] for k in old_members if k not in changes)}
 # SCRIPTPACK.DAT is NISPACK
 raw=(inp/'scriptpack.dat').read_bytes();entries=nispack(raw)
 before={r['name']:r['content'] for r in entries}
 changes={n:pat for n in before if (pat:=getpatch('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+n)) is not None}
 changed=reconstruir_nispack(raw,changes)
 after={r['name']:r['content'] for r in nispack(changed)}
 summary['ISO_SCRIPT']=audit('NISPACK',before,after,changes);summary['ISO_SCRIPT']['sha256_reconstruido']=h(changed)
 # start_jp.lzs from ISO, and four EDAT one-member NISPACK
 for label in ['ISO_START','DLC_00','DLC_01','DLC_02','DLC_03']:
  if label=='ISO_START':raw_lzs=(inp/'start_jp.lzs').read_bytes();outer=None
  else:
   edat=(inp/f'DL_JP_0{label[-1]}.EDAT').read_bytes();xs=nispack(edat)
   assert len(xs)==1 and xs[0]['name'].lower()=='start_jp.lzs';outer=edat
   raw_lzs=xs[0]['content']
  dat=lzs_decompress(raw_lzs)
  oldrows=entradas_dat(dat);before={n:dat[s:e] for n,s,e,_ in oldrows}
  changes={n:pat for n in before if (pat:=getpatch(label+'/'+n)) is not None}
  dat_new=reconstruir_dat(dat,changes)
  rows=entradas_dat(dat_new);after={n:dat_new[s:e] for n,s,e,_ in rows}
  summary[label]=audit('DAT',before,after,changes)
  if changes:
   lzs_new=comp(dat_new,raw_lzs,packer)
   if outer is not None:
    outer_new=reconstruir_nispack(outer,{'start_jp.lzs':lzs_new})
    assert nispack(outer_new)[0]['content']==lzs_new
   else:outer_new=lzs_new
  else:outer_new=outer if outer is not None else raw_lzs
  summary[label]['sha256_contenedor']=h(outer_new)
  summary[label]['recompresion_verificada']=True
 (out/'resultado_contenedores.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
 return summary
if __name__=='__main__':
 import argparse
 x=argparse.ArgumentParser()
 for name in ['source','fijos','scripts','output','packer']:x.add_argument('--'+name,type=Path,required=True)
 v=x.parse_args();print(json.dumps(test(v.source,v.fijos,v.scripts,v.output,v.packer),indent=2,ensure_ascii=False))
