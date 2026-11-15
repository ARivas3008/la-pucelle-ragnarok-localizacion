#!/usr/bin/env python3
"""Preflight reproducible para fuentes y continuaciones talk de La Pucelle.
No aplica traducciones ni modifica datos del juego. Solo carga originales del usuario.
"""
import argparse
import csv
import json
import struct
import sys
import unicodedata
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path

from relocador import Edicion, RelocacionError, TablaTalk


def nfk_norm(s: str) -> str:
    return unicodedata.normalize('NFKC', s).strip()


def resolve_path(recurso: str, extraidos: Path) -> Path:
    if recurso.startswith('ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'):
        return extraidos / 'ISO_SCRIPT' / recurso.split('/')[-1]
    area, archivo = recurso.split('/', 1)
    return extraidos / area / archivo


def iter_rows(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as fp:
        yield from csv.DictReader(fp)


def decode_bytes(source: bytes) -> tuple[str, str]:
    try:
        return source.decode('cp932', 'strict'), 'DECODIFICABLE'
    except UnicodeError:
        return source.decode('cp932', 'replace'), 'NO_CP932'


def audit(manifiesto: Path, extraidos: Path, output: Path, stress: bool = False):
    output.mkdir(parents=True, exist_ok=True)
    rows = [r for r in iter_rows(manifiesto) if '/talk' in r['recurso']]
    groups = defaultdict(set)
    by_resource = defaultdict(dict)
    for row in rows:
        groups[row['grupo_id']].add((row['recurso'], int(row['offset'])))
        k = int(row['offset'])
        if k in by_resource[row['recurso']]:
            raise ValueError(f'Offset repetido {row["recurso"]} {k}')
        by_resource[row['recurso']][k] = row

    files = {}
    indexes = {}
    for res in by_resource:
        p = resolve_path(res, extraidos)
        files[res] = p.read_bytes()
        indexes[res] = TablaTalk(files[res])

    statuses = []
    normalized_padding = []
    untranslated = []
    orphan_keys = set()
    reported = set()
    chains = []
    annotated = Counter()
    max_unmapped_chain = 0

    for res, m in by_resource.items():
        raw = files[res]
        table = indexes[res]
        for offset, row in sorted(m.items()):
            status = 'FUENTE_COINCIDE'
            end = raw.find(b'\x00', offset, min(len(raw), offset + 2048))
            if not(table.base < offset < len(raw)):
                status = 'FUERA_DEL_BYTECODE'
            elif raw[offset-1] != 1:
                status = 'OPCODE_INESPERADO'
            elif end < 0:
                status = 'SIN_TERMINADOR'
            else:
                decoded, decode_status = decode_bytes(raw[offset:end])
                original = row['original']
                if decode_status != 'DECODIFICABLE':
                    status = 'ERROR_DECODIFICACION'
                elif unicodedata.normalize('NFKC', decoded) == unicodedata.normalize('NFKC', original):
                    status = 'FUENTE_COINCIDE'
                elif nfk_norm(decoded) == nfk_norm(original):
                    status = 'COINCIDE_SOLO_CON_RELLENO'
                    pad_left = len(decoded) - len(decoded.lstrip())
                    pad_right = len(decoded) - len(decoded.rstrip())
                    normalized_padding.append({
                        'unit_id': row['unit_id'], 'grupo_id': row['grupo_id'],
                        'recurso': res, 'offset': offset,
                        'espacios_delante': pad_left, 'espacios_detras': pad_right,
                        'bytes_raw': len(raw[offset:end]),
                        'nota': 'La fuente coincide con el manifiesto tras NFKC y trim. Preservar disposición.'
                    })
                else:
                    status = 'FUENTE_DIFERENTE_REAL'
                if end >= 0 and end + 1 < len(raw) and raw[end+1] == 1:
                    next_offset = end+2
                    if next_offset not in m:
                        orphan_keys.add((res, next_offset))
                        # Recorrer todas las continuaciones consecutivas no mapeadas.
                        cur = next_offset
                        depth = 0
                        while (cur not in m and (res,cur) not in reported
                               and 0 < cur < len(raw) and raw[cur-1] == 1 and depth < 200):
                            stop = raw.find(b'\x00', cur, min(cur + 2048, len(raw)))
                            if stop < 0 or stop <= cur:
                                break
                            data = raw[cur:stop]
                            txt, enc = decode_bytes(data)
                            # NUL y opcode legítimos: NO implica que la cadena sea diálogo jugable.
                            untranslated.append({
                                'recurso': res, 'offset': cur, 'bytes':len(data),
                                'texto_original': txt,
                                'cp932':enc, 'unidad_previa': row['unit_id'],
                                'grupo_previo': row['grupo_id'],
                                'candidato_nueva_unidad': 'SI' if enc=='DECODIFICABLE' else 'REVISAR'
                            })
                            reported.add((res,cur))
                            depth += 1
                            if stop+1 >= len(raw) or raw[stop+1] != 1:break
                            cur=stop+2
                        max_unmapped_chain=max(max_unmapped_chain,depth)
            statuses.append({'unit_id':row['unit_id'],'grupo_id':row['grupo_id'],
                             'recurso':res,'offset':offset,'estado_fuente':status})
            annotated[status]+=1

    for res, m in by_resource.items():
        raw=files[res]
        edges={}
        for off,row in m.items():
            end=raw.find(b'\x00',off,min(len(raw),off+2048))
            if end > off and end+1 < len(raw) and raw[end+1]==1:
                to=end+2
                if to in m:edges[off]=to
        incoming=set(edges.values())
        for off in sorted(edges):
            if off in incoming:continue
            chain=[off];seen={off}
            while chain[-1] in edges:
                to=edges[chain[-1]]
                if to in seen:raise ValueError(f'Ciclo en {res}:{off}')
                chain.append(to);seen.add(to)
            if len(chain)<2:continue
            chain_groups={m[o]['grupo_id'] for o in chain}
            covered={(res,o) for o in chain}
            complete=all(groups[g].issubset(covered) for g in chain_groups)
            chains.append({'recurso':res,'offset_inicio':off,'lineas':len(chain),
                           'grupos':','.join(sorted(chain_groups,key=int)),
                           'intervencion_cerrada':int(complete),
                           'offsets':','.join(map(str,chain))})

    stress_results=[]
    if stress:
        for res,m in sorted(by_resource.items()):
            t=indexes[res]
            edits=[]
            raw=files[res]
            for off in sorted(m):
                stop=raw.find(b'\x00',off,min(len(raw),off+2048))
                if stop > off and off>t.base and raw[off-1]==1:
                    # Añade 2 bytes ASCII dentro de cada cadena reconocida; no es español editorial.
                    edits.append(Edicion(off,raw[off:stop],raw[off:stop]+b'!?'))
            try:
                new, offsets=t.aplicar(edits)
                stress_results.append({'recurso':res,'ediciones':len(edits),
                            'delta_total':len(new)-len(raw), 'estado':'EXITO'} )
            except (RelocacionError, ValueError) as e:
                stress_results.append({'recurso':res,'ediciones':len(edits),
                            'delta_total':'','estado':'ERROR: '+str(e)})

    def save_csv(name,data,keys=None):
        path=output/name
        if keys is None:keys=list(data[0]) if data else []
        with path.open('w',encoding='utf-8-sig',newline='') as f:
            if not keys:return
            wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(data)
    save_csv('validacion_fuentes.csv', statuses)
    save_csv('normalizacion_espacios.csv',normalized_padding)
    save_csv('continuaciones_sin_unidad.csv',untranslated)
    save_csv('cadenas_multigrupo.csv', chains)
    save_csv('pruebas_expansion_masiva.csv',stress_results)
    keys=[(r['recurso'],r['texto_original']) for r in untranslated]
    unique_count=len(set(keys))
    unique_texts=len(set(r['texto_original'] for r in untranslated))
    summary={
        'unidades_talk':len(rows),'archivos_talk':len(files),
        'fuentes_normalizadas':dict(annotated),
        'equivalencias_seguras_detectadas_por_relleno':len(normalized_padding),
        'continuaciones_cabecera_sin_mapa':len(orphan_keys),
        'cadenas_consecutivas_extraidas_sin_unidad':len(untranslated),
        'continuaciones_unicas_por_recurso_y_texto':unique_count,
        'continuaciones_unicas_por_texto':unique_texts,
        'cadenas_cp932_descodificables':sum(1 for r in untranslated if r['cp932']=='DECODIFICABLE'),
        'intervenciones_encadenadas_mapeadas':len(chains),
        'intervenciones_cerradas':sum(int(x['intervencion_cerrada']) for x in chains),
        'intervenciones_multigrupo_no_cerradas':sum(x['intervencion_cerrada']==0 for x in chains),
        'pruebas_expansion_masiva':stress_results,
        'advertencia':'Los tests validan reconstruccion de bytes, NO bytecode, PPSSPP ni cobertura editorial.',
    }
    (output/'resumen_v010.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--manifiesto',type=Path,required=True)
    p.add_argument('--extraidos',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True)
    p.add_argument('--stress',action='store_true')
    a=p.parse_args();print(json.dumps(audit(a.manifiesto,a.extraidos,a.salida,a.stress),indent=2,ensure_ascii=False))
