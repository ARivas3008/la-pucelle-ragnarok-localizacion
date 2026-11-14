#!/usr/bin/env python3
"""Solo crea un manifiesto: no modifica ISO, EBOOT, LZS o EDAT."""
import argparse,csv
from util import ROOT,load
from compilar import compile_all

def go(strict):
    compile_all(strict)
    groups={r['grupo_id']:r for r in load('salidas/grupos_consolidados.csv')}
    central={r['grupo_id']:r for r in load('data/preexistentes/509_revision_central.csv')}
    manifest=load('data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv')
    root=ROOT/'salidas';root.mkdir(exist_ok=True)
    dst=root/'candidatos_preinsercion.csv'
    with dst.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['unit_id','grupo_id','recurso','offset','original','grupo_es_revisado','candidato_unidad','estado_seguridad','motivo']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for u in manifest:
            g=groups[u['grupo_id']];approved=g['estado_final']=='revisado'
            if g['estado_final']=='CONTROL_CENTRAL_509':
                c=central[g['grupo_id']]
                approved=(c['estado']=='revisado' and bool(c['es_revisado'].strip()))
                if approved:g={**g,'espanol_revisado':c['es_revisado']}
            # Peligro: solo hay correspondencia inequívoca para grupos de una unidad.
            alone=len([z for z in g['unit_ids'].split(',') if z.strip()])==1
            safe=approved and alone and g['original']!='ェD' and '????' not in g['original'] and '？？？？' not in g['original']
            w.writerow({'unit_id':u['unit_id'],'grupo_id':u['grupo_id'],'recurso':u['recurso'],'offset':u['offset'],'original':u['original'],
                        'grupo_es_revisado':g['espanol_revisado'],
                        'candidato_unidad':g['espanol_revisado'] if safe else '',
                        'estado_seguridad':'LISTO_SOLO_PARA_QA_BINARIO' if safe else 'NO_INSERTAR',
                        'motivo':'Debe verificarse fuente, codificación, ancho y bytes' if safe else 'Requiere aprobación, resegmentación o protección de marcador'})
    print('Generado',dst,'; NO se ha modificado ninguna ISO.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--estricto',action='store_true');a=ap.parse_args();go(a.estricto)
