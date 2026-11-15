#!/usr/bin/env python3
"""Auditoría reproducible de las 14 anclas CP932 en script*.dat.

NO modifica ISO, EDAT ni scripts: genera observaciones y candidatos de fase.
Los desplazamientos se leen del manifiesto original, NO se calculan por
tamaño del texto traducido. La hipótesis de fase NO equivale a semántica probada.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REPORT = REPO / "parcheador/informes/estado_unificado_66.csv"
MANIFEST = REPO / "data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv"
IDS = (1758,1759,3883,3897,3898,3924,3969,3989,4007,4083,4095,4098,4170,4220)

sys.path.insert(0, str(HERE.parent / "v0.14"))
from integrar_scripts_v014 import originals, match
from reubicador_anclas_v012 import Reubicador, limites_cp932
from fuentes_es import encode_es


def leer_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def proponer_fase(antes: bytes, despues: bytes, byte_rel: int, tolerancia=2):
    """Retorna un destino de la MISMA fase 0/1 del carácter.

    Si la fuente apunta al segundo byte de un carácter de dos bytes,
    solo propone un segundo byte de un carácter de dos bytes en destino.
    A diferencia de v0.12, nunca fuerza el puntero al inicio del carácter.
    NO asegura que el índice sea un cursor de texto; no parchea datos.
    """
    x = limites_cp932(antes)
    y = limites_cp932(despues)
    if not 0 <= byte_rel <= len(antes):
        raise ValueError("referencia fuera de la cadena")
    if byte_rel == len(antes):
        return {"estado":"TERMINADOR","byte_destino":len(despues),"fase":0}
    ix = bisect.bisect_right(x, byte_rel)-1
    phase = byte_rel-x[ix]
    if phase not in (0,1):
        raise ValueError("fase fuera de un carácter CP932")
    ideal = round(ix * (len(y)-2) / max(1,len(x)-2))
    candidates = [(abs(i-ideal),i,y[i]+phase)
                  for i in range(len(y)-1) if y[i+1]-y[i]>phase]
    if not candidates:
        return {"estado":"SIN_CARACTER_DE_LA_MISMA_FASE",
                "fase":phase,"indice_origen":ix,"indice_ideal":ideal}
    distancia,i,newpos = min(candidates)
    state = "PROPUESTA_FASE_CERCANA" if distancia<=tolerancia else "FUERA_DE_TOLERANCIA"
    return {"estado":state,"byte_destino":newpos,"fase":phase,
            "indice_origen":ix,"indice_destino":i,"indice_ideal":ideal,
            "distancia_en_caracteres":distancia}


def observar(rows, manifest, sources):
    manifest_by_id={r["unit_id"]:r for r in manifest}
    result=[]
    for row in rows:
        uid=row["unit_id"]
        base={"unit_id":uid,"grupo_id":row["grupo_id"],
              "recurso":row["recurso"],"original":row["original"],
              "es_revisado":row["es_revisado"]}
        m=manifest_by_id.get(uid)
        if not m or m["recurso"]!=row["recurso"] or m["original"]!=row["original"]:
            result.append({**base,"estado":"MANIFIESTO_NO_COINCIDE"});continue
        raw=sources.get(row["recurso"])
        if raw is None:
            result.append({**base,"estado":"SIN_BINARIO_ORIGINAL"});continue
        off=int(m["offset"])
        source_bytes=match(raw,off,row["original"])
        if not source_bytes:
            result.append({**base,"offset":off,"estado":"FUENTE_NO_COINCIDE"});continue
        try:
            new=encode_es(row["es_revisado"])
            t=Reubicador(raw)
            bounds=limites_cp932(source_bytes)
        except Exception as exc:
            result.append({**base,"offset":off,"estado":"FORMATO_NO_VALIDADO",
                           "detalle":str(exc)});continue
        rel=off-t.body
        inside=[(i,p) for i,p in enumerate(t.pointers)
                if rel<=p<rel+len(source_bytes)+1]
        sub=[(i,p) for i,p in inside if p-rel not in bounds]
        if not sub:
            result.append({**base,"offset":off,
                           "estado":"NO_SE_REPRODUJO_ANCLA_SUBCARACTER",
                           "referencias_en_cadena":len(inside)})
            continue
        for idx,p in sub:
            byte_rel=p-rel
            candidate=proponer_fase(source_bytes,new,byte_rel)
            result.append({**base, "estado":"OBSERVADO_NO_APLICADO",
                           "offset":off,"sha256_script":hashlib.sha256(raw).hexdigest(),
                           "puntero_indice":idx,"puntero_relativo_tabla":p,
                           "puntero_absoluto_script":t.body+p,
                           "byte_relativo_cadena":byte_rel,
                           "byte_origen_hex":source_bytes[byte_rel:byte_rel+1].hex(),
                           "par_original_hex":source_bytes[byte_rel-1:byte_rel+1].hex(),
                           "bytes_origen":len(source_bytes),"bytes_propuesta":len(new),
                           "referencias_en_cadena":len(inside),
                           **{("mapeo_"+k):v for k,v in candidate.items()}})
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--iso",type=Path,help="ISO original, nunca modificada")
    ap.add_argument("--dlc-directorio",type=Path,help="Directorio de EDAT originales")
    ap.add_argument("--salida",type=Path,required=True)
    ap.add_argument("--manifiesto",type=Path,default=MANIFEST)
    ap.add_argument("--informe",type=Path,default=REPORT)
    args=ap.parse_args()
    args.salida.mkdir(parents=True,exist_ok=True)
    rows=[r for r in leer_csv(args.informe) if int(r["unit_id"]) in IDS]
    if len(rows)!=len(IDS) or len({r["unit_id"] for r in rows})!=len(IDS):
        ap.error("El informe no contiene exactamente las 14 unidades esperadas")
    sources={}
    if args.iso or args.dlc_directorio:
        sources,_=originals(args.iso,args.dlc_directorio)
    output=observar(rows,leer_csv(args.manifiesto),sources)
    fields=list(dict.fromkeys(k for r in output for k in r.keys()))
    with (args.salida/"anclas_14_observadas.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(output)
    summary={"unidades":len(rows),"registros_observados":len(output),
             "referencias_subcaracter_observadas":sum(r["estado"]=="OBSERVADO_NO_APLICADO" for r in output),
             "fuentes_provistas":bool(sources),
             "estados":{s:sum(r["estado"]==s for r in output) for s in sorted({r["estado"] for r in output})},
             "garantias":"SOLO LECTURA. No afirma sincronía, jugabilidad ni interpretación de opcode."}
    (args.salida/"resumen_anclas.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
