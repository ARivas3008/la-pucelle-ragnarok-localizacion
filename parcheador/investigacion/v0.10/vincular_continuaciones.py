#!/usr/bin/env python3
"""Cruza continuaciones omitidas con otras apariciones de la MISMA fuente.
No aplica traducciones automáticamente: la equivalencia literal no asegura contexto.
"""
import argparse,csv,json,unicodedata
from pathlib import Path
from collections import defaultdict,Counter


def norm(text):return unicodedata.normalize('NFKC',text).strip()

def parse(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)

def vincular(continuaciones:Path,manifiesto:Path,salida:Path):
    db=defaultdict(list)
    for item in parse(manifiesto):
        db[norm(item['original'])].append(item)
    rows=[];c=Counter()
    for item in parse(continuaciones):
        options=db.get(norm(item['texto_original']),[])
        own=[x for x in options if x['recurso']==item['recurso']]
        prefer=own or options
        best=next((x for x in prefer if x.get('es_unidad_candidata','').strip()),prefer[0] if prefer else None)
        classification='SIN_EQUIVALENCIA'
        if options:classification='MISMO_RECURSO' if own else 'OTRO_RECURSO'
        c[classification]+=1
        candidate=best.get('es_unidad_candidata','') if best else ''
        if candidate.strip():c['CANDIDATAS_DE_OTRAS_UNIDADES']+=1
        rows.append({'recurso':item['recurso'],'offset':item['offset'],
           'texto_original_no_mapeado':item['texto_original'],
           'estado_coincidencia':classification,'cantidad_coincidencias':len(options),
           'unidad_referencia':best['unit_id'] if best else '',
           'recurso_referencia':best['recurso'] if best else '',
           'es_propuesta_sin_validar':candidate,
           'requiere_cotejo':'SI'})
    salida.mkdir(parents=True,exist_ok=True)
    with (salida/'vinculaciones_continuaciones.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (salida/'continuaciones_sin_equivalencia.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(x for x in rows if x['estado_coincidencia']=='SIN_EQUIVALENCIA')
    (salida/'resumen_vinculaciones.json').write_text(json.dumps(dict(c),indent=2,ensure_ascii=False),encoding='utf-8')
    return dict(c)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--continuaciones',type=Path,required=True);p.add_argument('--manifiesto',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();print(json.dumps(vincular(a.continuaciones,a.manifiesto,a.salida),indent=2,ensure_ascii=False))
