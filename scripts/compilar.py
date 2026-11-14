#!/usr/bin/env python3
"""Compila por IDs del catálogo original; NO abre ni modifica ISO o Excel."""
import argparse,csv,sys
from pathlib import Path
from util import ROOT, load, marker_list, esc_excel
from validar import validate

def compile_all(strict):
    if validate(strict=strict):raise SystemExit('QA falló; no es seguro compilar')
    reviews={}
    for i in range(1,16):
        for r in load(f'corpus/{i:02}/revision.csv'):
            if r['grupo_id'] in reviews:raise RuntimeError('revisión duplicada')
            reviews[r['grupo_id']]=r
    master=load('data/maestros/03_TODOS_LOS_GRUPOS_15525.csv')
    out=ROOT/'salidas';out.mkdir(exist_ok=True)
    columns=['grupo_id','seccion','recurso','offset_inicio','unit_ids','original','espanol_de_trabajo','espanol_revisado','estado_final','fuente']
    with (out/'grupos_consolidados.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for g in master:
            r=reviews.get(g['grupo_id'])
            w.writerow({'grupo_id':g['grupo_id'],'seccion':g['seccion'],'recurso':g['recurso'],'offset_inicio':g['offset_inicio'],
                        'unit_ids':g['unit_ids'],'original':g['original'],'espanol_de_trabajo':g['es_correccion_trabajo'],
                        'espanol_revisado':r['es_revisado'] if r and r['estado']=='revisado' else g['es_correccion_trabajo'],
                        'estado_final':r['estado'] if r else 'CONTROL_CENTRAL_509',
                        'fuente':'revision_corpus' if r else g['fuente_correccion']})
    print('Escrito salidas/grupos_consolidados.csv, 15525 filas; los 509 grupos centrales requieren revisión separada.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--estricto',action='store_true');a=ap.parse_args()
    compile_all(a.estricto)
