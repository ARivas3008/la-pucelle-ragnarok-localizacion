#!/usr/bin/env python3
"""Cuantifica lo que queda fuera del experimento talk. No confunde prueba con traduccion."""
import argparse,csv,json
from collections import Counter
from pathlib import Path

def run(manifest,output):
    with manifest.open('r',encoding='utf-8-sig',newline='') as f:
        data=list(csv.DictReader(f))
    talk=[x for x in data if '/talk' in x['recurso']]
    other=[x for x in data if '/talk' not in x['recurso']]
    counts=Counter(x['recurso'] for x in other)
    result={'unidades_manifestadas':len(data),'talk_mapeadas':len(talk),
            'no_talk_mapeadas':len(other),'recursos_no_talk':len(counts),
            'pendientes_no_talk':[{'recurso':k,'unidades':v} for k,v in counts.most_common()],
            'advertencia':'Inventario físico. No equivale a texto traducido, integrado o jugable.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifiesto',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();r=run(a.manifiesto,a.salida)
    print({k:v for k,v in r.items() if k!='pendientes_no_talk'})
