#!/usr/bin/env python3
"""Verificador independiente: compara cada recurso de los cinco START.

No analiza la jugabilidad del motor PSP. Solo valida estructura de contenedores,
conservación de tamaños de miembros y cobertura de fuentes españolas.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from construir_parche import Image,members_from_dat
from nis_formats import nispack,lzs_decompress
from fuentes_es import CODIGOS,index_sjis,missing_render_glyphs
import struct

def members_iso(path):
    a=Image(path)
    paths={p:(o,l) for p,o,l,_ in a.records()}
    if '/PSP_GAME/USRDIR/START_JP.LZS' not in paths:raise ValueError('START no localizado en ISO')
    off,n=paths['/PSP_GAME/USRDIR/START_JP.LZS']
    return members_from_dat(lzs_decompress(a.read(off,n))),paths

def members_edat(path):
    l=nispack(Path(path).read_bytes())
    if len(l)!=1 or l[0]['name'].lower()!='start_jp.lzs':raise ValueError('DLC sin START')
    return members_from_dat(lzs_decompress(l[0]['content']))

def verify(a,b,only_fonts):
    if a.keys()!=b.keys():raise ValueError('Lista de miembros distinta')
    changed=[k for k in a if a[k]!=b[k]]
    if any(len(a[k])!=len(b[k]) for k in a):raise ValueError('Un miembro cambió de tamaño')
    allowed={'fontB.fnt','fontB.ftd','FontB0001.txp','FontB0000.txp'}
    if only_fonts and any(k not in allowed for k in changed):raise ValueError('Se modificó un recurso no fuente')
    fnt=struct.unpack('<11616H',b['fontB.fnt'])
    missing=[char for char,pair in CODIGOS.items() if fnt[index_sjis(pair)]==0]
    if missing:raise ValueError(f'Glifos ausentes: {missing}')
    return {'cambios':changed,'miembros':len(a),'glifos':len(CODIGOS),'longitudes_estables':True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--iso-generada',required=True,type=Path)
    ap.add_argument('--dlc-original',required=True,type=Path)
    ap.add_argument('--salida',required=True,type=Path)
    ap.add_argument('--solo-fuentes',action='store_true',help='Asegura que nada fuera de fontB ha cambiado')
    a=ap.parse_args()
    output={}
    iso_a,files_a=members_iso(a.iso_original)
    iso_b,files_b=members_iso(a.iso_generada)
    if sorted(files_a)!=sorted(files_b):raise ValueError('Árbol ISO cambiado')
    if a.iso_original.stat().st_size!=a.iso_generada.stat().st_size:raise ValueError('Longitud ISO cambió')
    output['ISO_START']=verify(iso_a,iso_b,a.solo_fuentes)
    for i in range(4):
        original=a.dlc_original/f'DL_JP_{i:02d}.EDAT'
        generated=a.salida/f'DL_JP_{i:02d}_ES_PRELIMINAR.EDAT'
        output[f'DLC_{i:02d}']=verify(members_edat(original),members_edat(generated),a.solo_fuentes)
    print(json.dumps({'valido':True,'recursos':output},ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,IndexError,OSError,struct.error) as e:
        print('VERIFICACIÓN FALLIDA:',e,file=sys.stderr);sys.exit(2)
