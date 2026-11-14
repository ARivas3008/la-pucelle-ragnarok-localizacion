#!/usr/bin/env python3
"""Revisión reproducible: preserva fuente, orden, claves, relación Excel y controles."""
import argparse, collections, csv, json, sys
from util import ROOT, load, fingerprint, marker_list, STATES

CAMPOS_FUENTE=('seccion','recurso','offset_inicio','unidades','unit_ids','idioma',
               'original','es_previa','es_correccion_trabajo','fuente_correccion',
               'estado_revision','estado_insercion','alertas','comentario',
               'contexto_previo','contexto_siguiente')
REV_HEADER=['grupo_id','es_revisado','estado','notas_editoriales','referencias_consultadas']

def validate(number=None,strict=False):
    failures=[]; counts=collections.Counter();ids=[]
    selected=[str(number).zfill(2)] if number else [f'{n:02}' for n in range(1,16)]
    master=load('data/maestros/03_TODOS_LOS_GRUPOS_15525.csv')
    original={g['grupo_id']:g for g in master}
    excel={g['grupo_id']:g for g in load('data/maestros/mapa_excel_grupo.csv')}
    for code in selected:
        input_path=ROOT/f'corpus/{code}/entrada.csv'
        review_path=ROOT/f'corpus/{code}/revision.csv'
        with review_path.open(encoding='utf-8-sig',newline='') as f:
            headers=csv.DictReader(f).fieldnames
        if headers!=REV_HEADER:failures.append(f'{code}: columnas de revision.csv modificadas: {headers!r}')
        e=load(f'corpus/{code}/entrada.csv')
        r=load(f'corpus/{code}/revision.csv')
        if len(e)!=len(r):failures.append(f'{code}: número de filas distinto: fuente={len(e)} revision={len(r)}')
        for index,(a,b) in enumerate(zip(e,r),2):
            gid=a['grupo_id'];ids.append(gid)
            if gid!=b['grupo_id']: failures.append(f'{code}: fila {index} ID alterado {gid} -> {b["grupo_id"]}')
            source=original.get(gid)
            if not source or source['estado_revision']!='borrador_pendiente_cotejo':
                failures.append(f'{code}: grupo {gid} fuera del inventario pendiente')
            else:
                for key in CAMPOS_FUENTE:
                    if a.get(key)!=source[key]:failures.append(f'{code}: grupo {gid} campo {key} alterado')
            exp=excel.get(gid)
            if exp:
                if a['sha256_original']!=exp['hash_original'] or fingerprint(a['original'])!=exp['hash_original']:
                    failures.append(f'{code}: grupo {gid} SHA256 alterado')
                for k in ('excel_dialogos_hoja','excel_dialogos_fila','excel_unidades_referencias'):
                    val=exp['excel_dialogos_hoja' if k=='excel_dialogos_hoja' else 'excel_dialogos_fila' if k=='excel_dialogos_fila' else 'excel_unidades_referencias']
                    if a.get(k)!=val:failures.append(f'{code}: grupo {gid} referencia Excel {k} alterada')
            state=b['estado'];counts[state]+=1
            if state not in STATES:failures.append(f'{code}: grupo {gid} estado desconocido: {state}')
            if state=='revisado':
                if not b['es_revisado'].strip():failures.append(f'{code}: grupo {gid} revisado sin español')
                elif marker_list(a['original'])!=marker_list(b['es_revisado']):
                    failures.append(f'{code}: grupo {gid} controles alterados: {marker_list(a["original"])} != {marker_list(b["es_revisado"])}')
            elif state=='requiere_investigacion' and not b['notas_editoriales'].strip():
                failures.append(f'{code}: grupo {gid} requiere investigación sin nota')
            if strict and state!='revisado':failures.append(f'{code}: grupo {gid} sigue en {state}')
        if len(e)!=sum(1 for rr in r):failures.append(f'{code}: revisión incompleta')
    if len(ids)!=len(set(ids)):failures.append('IDs duplicados dentro de los corpus examinados')
    if not number:
        need={g['grupo_id'] for g in master if g['estado_revision']=='borrador_pendiente_cotejo'}
        if set(ids)!=need:failures.append(f'Inventario distinto: faltan {len(need-set(ids))}, sobran {len(set(ids)-need)}')
        if len(ids)!=15016:failures.append(f'Cobertura incorrecta: {len(ids)} de 15016')
    for x in failures[:35]:print('ERROR:',x)
    print(json.dumps({'corpus':selected,'grupos':len(ids),'estados':dict(counts),'errores':len(failures),'estricto':strict},ensure_ascii=False,indent=2))
    if len(failures)>35:print('... otros',len(failures)-35,'errores')
    return int(bool(failures))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=int,choices=range(1,16));p.add_argument('--estricto',action='store_true')
    args=p.parse_args();sys.exit(validate(args.corpus,args.estricto))
