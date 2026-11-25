#!/usr/bin/env python3
"""ROM-033: audita la contabilidad y las revisiones; no ejecuta PPSSPP."""
import csv, json, hashlib, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=json.loads((ROOT/'docs/seguimiento/informes/ROM-033_iso_talk_cierre.json').read_text(encoding='utf8'))
    hist=rows(ROOT/'docs/informes/cobertura_v0.19.0.csv')
    scope=[r for r in hist if r['recurso'].startswith('ISO') and 'talk' in r['recurso']]
    # El CSV historico distingue fisicamente las unidades insertadas y pendientes.
    statekey='estado'
    assert statekey in scope[0],scope[0].keys()
    pending=[r for r in scope if r[statekey]=='TALK_PENDIENTE']
    old=[r for r in scope if r[statekey]=='TALK_BLOQUE_INSERTADO']
    assert len(scope)==20083 and len(old)==17077 and len(pending)==3006
    ids=sorted(int(r['unit_id']) for r in pending)
    assert len(set(ids))==len(ids) and not set(ids)&{int(r['unit_id']) for r in old}
    assert sha(''.join(f'{i}\n' for i in ids).encode())==p['ids_sha256']
    assert collections.Counter(r['recurso'] for r in pending)=={r['recurso']:r['unidades'] for r in p['recursos']}
    gids={int(r['grupo_id']) for r in pending}
    rev={}
    for path in [*(ROOT/f'corpus/{i:02d}/revision.csv' for i in range(9,14)),ROOT/'data/preexistentes/509_revision_central.csv']:
        for r in rows(path):
            gid=int(r['grupo_id'])
            if gid in gids:
                assert gid not in rev and r['estado']=='revisado'
                rev[gid]=r['es_revisado']
    assert set(rev)==gids and len(rev)==1110
    raw=''.join(f'{i}\t{rev[i]}\n' for i in sorted(rev)).encode()
    assert sha(raw)==p['revisiones_sha256']
    for key in ('intervalos','entradas','opciones'):assert sum(r[key] for r in p['recursos'])==p[key]
    prev=json.loads((ROOT/'docs/seguimiento/informes/ROM-032_consolidacion_conservadora.json').read_text(encoding='utf8'))['contabilidad']
    assert prev['agregada_con_190_eboot']+len(ids)==p['agregada']==26193
    assert p['validas']-p['agregada']==p['pendientes']==64
    assert p['iso_talk_historicos']+p['iso_talk_nuevos']==p['iso_talk_total']==20083
    assert not p['candidata_integral'] and not p['ppsspp']
    print(json.dumps({'ok':True,'iso_talk_agregada':20083,'nuevas':3006,'grupos':1110,'agregada_global':26193,'pendientes':64,'alcance':'contabilidad documental; piloto binario privado'},ensure_ascii=False))
if __name__=='__main__':main()
