#!/usr/bin/env python3
"""Auditoría física reproducible de cadenas de diálogo: nunca modifica ISO/DLC.

Uso: python auditar_manifiesto.py --manifiesto mapa.csv --extraidos DIR --salida DIR
DIR: ISO_SCRIPT/, ISO_START/, DLC_00/..DLC_03/ con archivos extraídos.
"""
import argparse,csv,json,sys,unicodedata
from pathlib import Path
from collections import Counter,defaultdict
from relocador import TablaTalk


def origen_equivalente(raw:bytes,original:str):
    try:return unicodedata.normalize('NFKC',raw.decode('cp932'))==unicodedata.normalize('NFKC',original)
    except UnicodeError:return False


def analizar(manifiesto,extraidos,destino):
    rows=list(csv.DictReader(Path(manifiesto).open('r',encoding='utf-8-sig',newline='')))
    files={};tabs={};bygroup=defaultdict(list);r_byfile=defaultdict(dict);c=Counter()
    for x in rows:
        res=x['recurso']
        if '/talk' not in res:continue
        if res.startswith('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'):
            p=Path(extraidos,'ISO_SCRIPT',res.split('/')[-1])
        else:
            area,name=res.split('/');p=Path(extraidos,area,name)
        if res not in files:
            b=p.read_bytes();files[res]=b;tabs[res]=TablaTalk(b)
        r_byfile[res][int(x['offset'])]=x
        bygroup[x['grupo_id']].append(x)
    links={};orphans=set()
    for res,rmap in r_byfile.items():
        b=files[res]
        for pos,x in rmap.items():
            if 0<pos<len(b) and b[pos-1]==1:
                end=b.find(b'\0',pos,min(len(b),pos+2048))
                if end!=-1 and end+2<len(b) and b[end+1]==1:
                    nxt=end+2
                    if nxt in rmap:links[(res,pos)]=(res,nxt)
                    else:orphans.add(x['unit_id'])
    incoming=set(links.values());chains=[];chain_units=set();closed_units=set()
    for first in links:
        if first in incoming:continue
        line=[first];seen={first}
        while line[-1] in links:
            cur=links[line[-1]]
            if cur in seen:raise ValueError('Bucle de intervención')
            line.append(cur);seen.add(cur)
        if len(line)>=2:
            ch=[r_byfile[r][o] for r,o in line]
            chains.append(ch)
            groupids=set(x['grupo_id'] for x in ch)
            unitids={x['unit_id'] for x in ch}
            chain_units.update(unitids)
            if all({x['unit_id'] for x in bygroup[g]}.issubset(unitids) for g in groupids):closed_units.update(unitids)
    out=[]
    for res,rmap in r_byfile.items():
        b=files[res];tab=tabs[res]
        for pos,x in rmap.items():
            end=b.find(b'\0',pos,min(len(b),pos+2048))
            src=b[pos:end] if end>=0 else b''
            status='CANDIDATO_CON_CAJA_VERIFICADA'
            if pos<=tab.base or pos>=len(b):status='FUERA_DE_BYTECODE'
            elif end<0:status='SIN_TERMINADOR'
            elif b[pos-1]!=1:status='OPCODE_NO_ES_01'
            elif not origen_equivalente(src,x['original']):status='FUENTE_NO_COINCIDE'
            elif x['unit_id'] in orphans:status='CONTINUACION_SIN_MAPEAR'
            elif x['unit_id'] in chain_units and x['unit_id'] not in closed_units:status='INTERVENCION_MULTIGRUPO_NO_CERRADA'
            elif x['unit_id'] not in chain_units and len(bygroup[x['grupo_id']])>1:status='GRUPO_SIN_CADENA_CONFIRMADA'
            c[status]+=1
            out.append({'unit_id':x['unit_id'],'grupo_id':x['grupo_id'],'recurso':res,
                        'offset':pos,'bytes_original':len(src),'estado':status})
    destino=Path(destino);destino.mkdir(parents=True,exist_ok=True)
    with (destino/'auditoria_talk.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    summary={'total_unidades_talk':len(out),'archivos_talk':len(tabs),
             'tablas_validadas':sum(1 for t in tabs.values() if t.punteros[0]==0),
             'intervenciones_encadenadas':len(chains),'continuaciones_sin_mapear':len(orphans),
             'estados':dict(c),
             'advertencia':'Elegibilidad estructural, NO inserción final ni prueba visual PPSSPP.'}
    (destino/'auditoria_talk.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifiesto',type=Path,required=True)
    p.add_argument('--extraidos',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();print(json.dumps(analizar(a.manifiesto,a.extraidos,a.salida),ensure_ascii=False,indent=2))
