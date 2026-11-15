#!/usr/bin/env python3
"""Divide unidades extraídas en lotes editoriales sin cortar grupos ni escenas.

Solo usa la biblioteca estándar y archivos CSV del proyecto. No necesita ISO.
La fuente original y sus IDs son inmutables. Los lotes son propuestas de revisión.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

def get(r,*keys,default=""):
    for key in keys:
        if key in r and r[key] is not None:return str(r[key])
    return default

def normalizar(rows):
    seen=set();order=set();units=[]
    for number,row in enumerate(rows,1):
        uid=get(row,"unit_id","unidad_id")
        original=get(row,"original")
        res=get(row,"recurso","resource")
        grupo=get(row,"grupo_id","group_id",default=uid) or uid
        if not uid or not res or not original:raise ValueError(f"Fila {number} sin unidad, recurso u original")
        if uid in seen:raise ValueError("ID de unidad duplicado "+uid)
        seen.add(uid)
        units.append(dict(unit_id=uid,grupo_id=grupo,recurso=res,
                          escena=get(row,"escena","scene",default="SIN_ESCENA"),
                          hablante=get(row,"hablante","speaker",default=""),
                          offset=get(row,"offset"),
                          original=original,capacidad_bytes=get(row,"capacidad_bytes"),
                          tipo=get(row,"tipo",default="DESCONOCIDO"),
                          hash_original=hashlib.sha256(original.encode("utf-8")).hexdigest()))
    return units

def agrupar(units):
    """Conserva el orden físico; rechaza grupos no contiguos en la misma escena."""
    grouped=[];closed=set()
    for x in units:
        key=(x["recurso"],x["escena"],x["grupo_id"])
        if grouped and grouped[-1][0]==key:
            grouped[-1][1].append(x)
        else:
            if key in closed:raise ValueError("Grupo no contiguo: "+repr(key))
            if grouped:closed.add(grouped[-1][0])
            grouped.append((key,[x]))
    return grouped

def lotear(units,grupos_por_lote=50):
    if grupos_por_lote<1:raise ValueError("Límite de lotes inválido")
    out=[];batch=[];area=None
    for key,members in agrupar(units):
        current=key[:2]
        if batch and (len(batch)>=grupos_por_lote or current!=area):
            out.append(batch);batch=[]
        batch.append((key,members));area=current
    if batch:out.append(batch)
    return out

def procesar(archivo,salida,max_grupos):
    with Path(archivo).open(encoding="utf-8-sig",newline="") as f:
        units=normalizar(list(csv.DictReader(f)))
    lots=lotear(units,max_grupos)
    salida=Path(salida);salida.mkdir(parents=True,exist_ok=True)
    fields=["unit_id","grupo_id","recurso","escena","hablante","offset","original",
            "hash_original","capacidad_bytes","tipo","contexto_previo",
            "contexto_siguiente","mtl_es","es_revisado","estado"]
    summary=[]
    for i,lot in enumerate(lots,1):
        name=f"{i:03d}";path=salida/name;path.mkdir(exist_ok=True)
        flat=[r.copy() for key,grp in lot for r in grp]
        for j,r in enumerate(flat):
            def ctx(k):
                if 0<=k<len(flat) and flat[k]["recurso"]==r["recurso"] and flat[k]["escena"]==r["escena"]:
                    return flat[k]["original"]
                return ""
            r.update(contexto_previo=ctx(j-1),contexto_siguiente=ctx(j+1),
                     mtl_es="",es_revisado="",estado="pendiente")
        with (path/"entrada.csv").open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
        (path/"INSTRUCCIONES.md").write_text(
            "# Revisión del lote "+name+"\n\n"
            "No cambiar IDs, originales, hash, orden ni contexto. MTL es solo un borrador.\n"
            "Revisar japonés/inglés, nombres y controles; marcar revisado únicamente tras QA.\n"
            "No repartir una intervención entre escenas por límite de caracteres.\n",
            encoding="utf-8")
        summary.append({"lote":name,"recurso":lot[0][0][0],"escena":lot[0][0][1],
                        "grupos":len(lot),"unidades":len(flat),
                        "primer_id":flat[0]["unit_id"],"ultimo_id":flat[-1]["unit_id"]})
    with (salida/"lotes.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]) if summary else ["lote","unidades"])
        w.writeheader();w.writerows(summary)
    result={"unidades":len(units),"grupos":len(agrupar(units)),
            "lotes":len(lots),"max_grupos_por_lote":max_grupos,
            "conservar_fuente":True}
    (salida/"resumen.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--unidades",type=Path,required=True)
    a.add_argument("--salida",type=Path,required=True)
    a.add_argument("--grupos-por-lote",type=int,default=50)
    x=a.parse_args();print(json.dumps(procesar(x.unidades,x.salida,x.grupos_por_lote),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
