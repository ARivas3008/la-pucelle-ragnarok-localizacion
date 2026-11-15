#!/usr/bin/env python3
"""Ensayo de reconstruccion 21 talk en los 6 contenedores NIS, sin distribuir juegos.
Alarga 2 bytes cada cadena mapeada y continuada, recompone y compara contenidos.
No modifica el original y no prueba interpretacion PSP de bytecode.
"""
import argparse,csv,json,sys,subprocess,tempfile,hashlib
from collections import defaultdict
from pathlib import Path
from relocador import TablaTalk, Edicion
from contenedores import reconstruir_nispack,entradas_nispack,reconstruir_dat,entradas_dat


def ls(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)

def sha(b):return hashlib.sha256(b).hexdigest()

def expand(b,offsets):
    t=TablaTalk(b);ed=[]
    for off in sorted(offsets):
        stop=b.index(0,off)
        ed.append(Edicion(off,b[off:stop],b[off:stop]+b'!?'))
    new,_=t.aplicar(ed)
    return new

def get_dict_nis(pack):
    endian,ent=entradas_nispack(pack)
    return {n:pack[o:o+sz] for n,o,sz,*_ in ent}

def get_dict_dat(pack):
    return {n:pack[s:e] for n,s,e,*_ in entradas_dat(pack)}

def run(manifest, continuaciones, extraidos, iso_path, start_lzs, dlc_dir, packer, output):
    from nis_formats import lzs_decompress,nispack
    from iso_reubicar import recorrer
    # Get offsets by their actual physical resource
    offsets=defaultdict(set)
    for path in (manifest,continuaciones):
        for row in ls(path):
            if '/talk' in row['recurso']:
                offsets[row['recurso']].add(int(row['offset']))
    results=[]
    with iso_path.open('rb') as fp:
        record={r.ruta:r for r in recorrer(fp)}['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']
        fp.seek(record.offset)
        b=fp.read(record.size)
    old=get_dict_nis(b);changes={}
    for res,poses in offsets.items():
        if not res.startswith('ISO/'):continue
        name=res.split('/')[-1]
        changes[name]=expand(old[name],poses)
    rebuilt=reconstruir_nispack(b,changes)
    actual=get_dict_nis(rebuilt)
    assert all(actual[n]==changes.get(n,old[n]) for n in old)
    assert len(actual)==len(old)
    results.append({'contenedor':'ISO/SCRIPTPACK.DAT','unidades_ampliadas':sum(len(offsets[x]) for x in offsets if x.startswith('ISO/')),
       'miembros_sin_cambio_verificados':sum(actual[n]==old[n] for n in old if n not in changes),
       'bytes_original':len(b),'bytes_ensayo':len(rebuilt),'estado':'EXITO'})
    # Raw START + DLC; recompile inner index, LZS re-compress and compare decompression
    with tempfile.TemporaryDirectory() as temp:
        for area in ['ISO_START','DLC_00','DLC_01','DLC_02','DLC_03']:
            if area=='ISO_START':
                lz=start_lzs.read_bytes()
            else:
                edat=(dlc_dir/('DL_JP_'+area[-2:]+'.EDAT')).read_bytes()
                entries=nispack(edat)
                assert len(entries)==1 and entries[0]['name'].lower()=='start_jp.lzs'
                lz=entries[0]['content']
            raw=lzs_decompress(lz)
            old=get_dict_dat(raw)
            edits={}
            for res, poses in offsets.items():
                if res.startswith(area+'/'):
                    edits[res.split('/')[-1]]=expand(old[res.split('/')[-1]],poses)
            newraw=reconstruir_dat(raw,edits)
            after=get_dict_dat(newraw)
            assert all(after[n]==edits.get(n,old[n]) for n in old)
            inf=Path(temp)/(area+'.dat');outf=Path(temp)/(area+'.lzs')
            inf.write_bytes(newraw)
            subprocess.run([str(packer),str(inf),str(outf),'dat','213'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            re=lzs_decompress(outf.read_bytes())
            assert re==newraw, f'LZS corrupto {area}'
            results.append({'contenedor':area,'unidades_ampliadas':sum(len(offsets[x]) for x in offsets if x.startswith(area+'/')),
                'miembros_sin_cambio_verificados':sum(after[n]==old[n] for n in old if n not in edits),
                'bytes_original':len(raw),'bytes_ensayo':len(newraw),'estado':'EXITO'})
    summary={'estado':'EXITO_ESTRUCTURAL','contenedores':len(results),
     'textos_ampliados':sum(x['unidades_ampliadas'] for x in results),
     'advertencia':'Prueba estructural reversible, NO uso jugable PSP y NO traduccion real; no se entregan archivos comerciales.',
     'detalles':results}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifiesto',type=Path,required=True)
    p.add_argument('--continuaciones',type=Path,required=True);p.add_argument('--extraidos',type=Path,required=True)
    p.add_argument('--iso',type=Path,required=True);p.add_argument('--start',type=Path,required=True)
    p.add_argument('--dlc',type=Path,required=True);p.add_argument('--packer',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.manifiesto,a.continuaciones,a.extraidos,a.iso,a.start,a.dlc,a.packer,a.salida),ensure_ascii=False,indent=2))
