#!/usr/bin/env python3
"""Prueba temporal 18.786 cadenas de SCRIPTPACK reubicado en ISO.
No produce una traduccion, no modifica originales, borra ISO temporal.
"""
import argparse,csv,hashlib,json,tempfile
from pathlib import Path
from collections import defaultdict
from relocador import TablaTalk,Edicion
from contenedores import entradas_nispack,reconstruir_nispack
from iso_reubicar import anexar_recurso, recorrer


def rows(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)

def sha(b):return hashlib.sha256(b).hexdigest()

def test(iso,manifest,continuaciones,report):
    offsets=defaultdict(set)
    for p in (manifest,continuaciones):
        for row in rows(p):
            if row['recurso'].startswith('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk'):
                offsets[row['recurso'].split('/')[-1]].add(int(row['offset']))
    with iso.open('rb') as fp:
        recs={r.ruta:r for r in recorrer(fp)}
        def get(name):
            r=recs[name];fp.seek(r.offset);return fp.read(r.size)
        base=get('/PSP_GAME/USRDIR/SCRIPTPACK.DAT')
        protected={name:sha(get(name)) for name in ('/PSP_GAME/USRDIR/START_JP.LZS','/PSP_GAME/SYSDIR/EBOOT.BIN')}
    _,entries=entradas_nispack(base)
    files={n:base[o:o+sz] for n,o,sz,*_ in entries}
    updates={}
    for n,locs in offsets.items():
        b=files[n];t=TablaTalk(b)
        edits=[Edicion(off,b[off:b.index(b'\x00',off)],b[off:b.index(b'\x00',off)]+b'!?') for off in sorted(locs)]
        updates[n],_=t.aplicar(edits)
    pack=reconstruir_nispack(base,updates)
    with tempfile.TemporaryDirectory() as d:
        temporary=Path(d)/'temporal_test.iso'
        detail=anexar_recurso(iso,temporary,'/PSP_GAME/USRDIR/SCRIPTPACK.DAT',pack)
        with temporary.open('rb') as fp:
            recs_after={r.ruta:r for r in recorrer(fp)}
            def read(name):
                r=recs_after[name];fp.seek(r.offset);return fp.read(r.size)
            assert read('/PSP_GAME/USRDIR/SCRIPTPACK.DAT')==pack
            for name,digest in protected.items():assert sha(read(name))==digest
    result={'estado':'EXITO_ESTRUCTURAL','unidades_probadas':sum(map(len,offsets.values())),
      'archivos_talk':len(offsets),'contenido_no_modificado_comprobado':len(protected),
      'iso_reubicada_y_borrada':True,'detalle':detail,
      'advertencia':'La ISO temporal se borró; no se ejecutó PPSSPP; no son traducciones reales.'}
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--iso',type=Path,required=True);p.add_argument('--manifiesto',type=Path,required=True)
    p.add_argument('--continuaciones',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();print(json.dumps(test(a.iso,a.manifiesto,a.continuaciones,a.salida),indent=2,ensure_ascii=False))
