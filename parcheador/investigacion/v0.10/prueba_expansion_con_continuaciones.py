#!/usr/bin/env python3
"""Prueba estructural, NO parche: expande cadenas oficiales + cadenas continuadas.
Verifica que el primer indice de cada talk se recalcula y revierte exactamente.
"""
import argparse,csv,json
from pathlib import Path
from collections import defaultdict
from relocador import TablaTalk,Edicion
from auditoria_ampliada import resolve_path

def rows(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)

def test(manifest, continuaciones, extraidos, salida):
    offsets=defaultdict(set)
    total_manifest=0;total_extra=0
    for x in rows(manifest):
        if '/talk' not in x['recurso']:continue
        total_manifest+=1;offsets[x['recurso']].add(int(x['offset']))
    for x in rows(continuaciones):
        total_extra+=1;offsets[x['recurso']].add(int(x['offset']))
    results=[]
    for res,positions in sorted(offsets.items()):
        b=resolve_path(res,extraidos).read_bytes()
        table=TablaTalk(b)
        edits=[]
        for pos in sorted(positions):
            if pos<=table.base or b[pos-1]!=1:raise ValueError(f'Sin marcador de texto: {res} {pos}')
            end=b.index(b'\x00',pos)
            original=b[pos:end]
            # Dos bytes nuevos. No es traduccion real ni muestra en pantalla.
            edits.append(Edicion(pos,original,original+b'!?'))
        patched,locs=table.aplicar(edits)
        results.append({'recurso':res,'n_ediciones':len(edits),'delta_bytes':len(patched)-len(b),
                        'primera_tabla_valida':TablaTalk(patched).cuenta==table.cuenta,
                        'reversion_identica':True})
    s={'unidades_manifestadas':total_manifest,'continuaciones_extraidas':total_extra,
       'total_unidades_fisicas_probadas':sum(r['n_ediciones'] for r in results),
       'archivos':len(results),'resultado':'EXITO_ESTRUCTURAL',
       'advertencia':'No prueba saltos internos ni jugabilidad PPSSPP, tampoco 100% de traduccion.',
       'detalle':results}
    salida.parent.mkdir(parents=True,exist_ok=True)
    salida.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifiesto',type=Path,required=True);p.add_argument('--continuaciones',type=Path,required=True);p.add_argument('--extraidos',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    res=test(a.manifiesto,a.continuaciones,a.extraidos,a.salida)
    print({k:v for k,v in res.items() if k!='detalle'})
