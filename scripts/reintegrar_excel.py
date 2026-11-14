#!/usr/bin/env python3
"""Reintegra los diálogos revisados en una COPIA del Excel original, por grupo_id y fila verificada.
Requiere artifact_tool. No reescribe la ISO ni altera originales.
"""
from pathlib import Path
import csv,argparse
from util import ROOT,load,esc_excel
from compilar import compile_all

def go(strict):
    compile_all(strict)
    from artifact_tool import Blob, SpreadsheetFile
    source=ROOT/'data/referencias/08_DIALOGOS_PARA_CORRECCION_POR_RECURSO.xlsx'
    workbook=SpreadsheetFile.import_xlsx(Blob.load(str(source)))
    revisions={r['grupo_id']:r for r in load('salidas/grupos_consolidados.csv') if r['estado_final']=='revisado'}
    index=load('data/maestros/mapa_excel_grupo.csv')
    sheetmap={}
    for r in index:
        if r['grupo_id'] in revisions and r['excel_dialogos_hoja']:
            sheetmap.setdefault(r['excel_dialogos_hoja'],[]).append((int(r['excel_dialogos_fila']),r['grupo_id']))
    written=0
    for name,rows in sheetmap.items():
        ws=workbook.worksheets.get_item(name)
        # El Excel original guarda «Español para revisión» en H (octava columna).
        for row,gid in rows:
            # Verificación previa: la celda A de esa fila DEBE contener grupo_id.
            found=ws.get_range(f'A{row}').values[0][0]
            if str(found)!=gid:raise ValueError(f'Desalineación Excel {name}!A{row}: {found} != {gid}')
            value=revisions[gid]['espanol_revisado']
            ws.get_range(f'H{row}').values=[[esc_excel(value)]]
            written+=1
    target=ROOT/'salidas/08_DIALOGOS_REVISION_REINTEGRADA.xlsx';target.parent.mkdir(exist_ok=True)
    SpreadsheetFile.export_xlsx(workbook).save(str(target))
    print(f'Escrito {target} con {written} revisiones; se conservan otras celdas y hojas.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--estricto',action='store_true');a=p.parse_args();go(a.estricto)
