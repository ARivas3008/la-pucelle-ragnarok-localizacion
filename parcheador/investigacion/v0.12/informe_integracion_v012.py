#!/usr/bin/env python3
"""Consolida la auditoría de 843 unidades no resueltas en v0.11.

La clasificación corresponde a pruebas de estructura de archivos; nunca a QA visual.
"""
from pathlib import Path
import csv, json
from collections import Counter
import argparse

def filas(p):
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def hacer(estado, propuestas, scripts, especiales, destino):
    estado=filas(estado)
    propos={r['unit_id']:r for r in filas(propuestas)}
    script={r['unit_id']:r for r in filas(scripts)}
    especial={r['unit_id']:r for r in filas(especiales)}
    out=[]
    for r in estado:
        orig=r['estado_tecnico']
        if orig in ('CANDIDATO_DAT','CANDIDATO_EBOOT'):
            continue
        uid=r['unit_id']
        typ='SIN_CAMBIO'
        nota=''
        propuesta=''
        if orig in ('EXCEDE_CAMPO','EBOOT_EXCEDE_CAMPO'):
            p=propos.get(uid)
            if p:
                propuesta=p['propuesta']
                typ={'CABE_ESTRUCTURAL':'COMPATIBLE_ESTRUCTURAL_ENSAYADO',
                    'PROPUESTA_POR_REVISAR':'ALTERNATIVA_NO_APROBADA',
                    'SIN_ALTERNATIVA':'NECESITA_NUEVA_ESTRATEGIA'}[p['estado_propuesta']]
                nota='Reducir/abreviar el nombre o texto de HUD; no dividir campos fijos'
            else:
                typ='SIN_PROPUESTA'
        elif orig=='PUNTERO_INTERNO_AMBIGUO':
            if script.get(uid,{}).get('estado')=='REUBICACION_ESTRUCTURAL_OK':
                typ='SCRIPT_REUBICABLE_ENSAYADO'
                nota='Ancla alineada al principio de un carácter; comprobar temporización en PPSSPP'
            else:
                typ='SCRIPT_ANCLA_SUBCARACTER_EXPERIMENTAL'
                nota='Nunca activar por defecto: ancla dentro de un carácter CP932'
        elif orig=='ESQUEMA_NO_VERIFICADO' and uid in especial:
            typ='CAMPO_ESPECIAL_ENSAYADO'
            propuesta=especial[uid]['traduccion']
            nota='Campo reconocido por reversión binaria; revisión de traducción pendiente'
        elif orig=='FUERA_DE_ALCANCE':
            typ='TEXTURA_PENDIENTE'
            nota='Requiere edición gráfica con atlas, paleta y UV documentados'
        elif orig=='EBOOT_NO_APTO_ASCII':
            typ='EBOOT_CODIFICACION_PENDIENTE'
            nota='No reemplazar por gaiji sin comprobar renderer EBOOT'
        elif orig=='NO_APROBADO':
            typ='PENDIENTE_EDITORIAL'
            nota='Revisar texto fuente y aprobar traducción antes de insertar'
        elif orig=='OMITIDO_NOW_LOADING':
            typ='OMITIDO_SOLICITADO'
            nota='No modificar Now Loading por petición del usuario'
        elif orig=='EBOOT_SIN_CAMBIO':
            typ='SIN_CAMBIO_NECESARIO'
        else:
            typ='CASO_ESPECIAL_PENDIENTE'
        out.append({'unit_id':uid,'grupo_id':r['grupo_id'],'recurso':r['recurso'],'estado_anterior':orig,
                    'estado_v012':typ,'texto_es_actual':r['es_revisado'],'propuesta_v012':propuesta,
                    'observacion':nota})
    assert len(out)==843,len(out)
    counts=Counter(r['estado_v012'] for r in out)
    accepted={'COMPATIBLE_ESTRUCTURAL_ENSAYADO','SCRIPT_REUBICABLE_ENSAYADO','CAMPO_ESPECIAL_ENSAYADO'}
    n=sum(counts[s] for s in accepted)
    assert n==296,(n,counts)
    destino=Path(destino);destino.mkdir(parents=True,exist_ok=True)
    with (destino/'estado_843_v012.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    summary={'total_originalmente_no_resuelto':843,
             'nuevas_simulaciones_estructurales_satisfactorias':n,
             'pendientes_sin_validacion_estructural_conservadora':843-n,
             'estados':dict(counts),
             'verificacion_ppsspp':'NO REALIZADA',
             'advertencia':'Las propuestas acortadas necesitan cotejo editorial, los scripts necesitan QA temporal y el juego necesita QA visual.'}
    (destino/'resumen_843_v012.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ('estado','propuestas','scripts','especiales','destino'):
        ap.add_argument('--'+name,required=True,type=Path)
    a=ap.parse_args()
    print(json.dumps(hacer(a.estado,a.propuestas,a.scripts,a.especiales,a.destino),ensure_ascii=False,indent=2))
