#!/usr/bin/env python3
"""Validación de límites físicos de texto y marcadores inmutables.

NUNCA auto-divide ni escribe binarios del videojuego. No usar longitud Unicode
como proxy de bytes. Sin parser de controles, la medición se declara pendiente.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

TOKEN=re.compile(r"\{[^{}]*\}|%[sd]|<[^<>]+>|\\[nr]")
class PresupuestoError(ValueError):pass

def tokens(text):return TOKEN.findall(text)

def codificar(text,codec="cp932",gaiji=None):
    gaiji=gaiji or {}
    buf=bytearray()
    for ch in text:
        if ch in gaiji:
            chunk=bytes.fromhex(gaiji[ch])
            if not chunk:raise PresupuestoError("Gaiji vacío")
            buf+=chunk
        else:
            try:buf+=ch.encode(codec)
            except UnicodeError:raise PresupuestoError("No codificable: "+ch)
    return bytes(buf)

def evaluar(source,revision,codec="cp932",gaiji=None,terminador=1):
    uid=source["unit_id"]
    result={"unit_id":uid,"recurso":source.get("recurso",""),
            "tipo":source.get("tipo",""),"capacidad_bytes":source.get("capacidad_bytes","")}
    original=source.get("original","")
    es=revision.get("es_revisado","")
    if not es or revision.get("estado")!="revisado":
        return {**result,"estado":"PENDIENTE_EDITORIAL"}
    if sorted(tokens(original))!=sorted(tokens(es)):
        return {**result,"estado":"CONTROLES_MODIFICADOS"}
    if tokens(es):
        return {**result,"estado":"REQUIERE_PARSER_DE_CONTROL"}
    try:encoded=codificar(es,codec,gaiji)
    except PresupuestoError as exc:
        return {**result,"estado":"NO_CODIFICABLE","motivo":str(exc)}
    total=len(encoded)+terminador
    result.update(bytes_texto=len(encoded),bytes_con_terminador=total,bits_con_terminador=8*total)
    tipo=source.get("tipo","").lower()
    if tipo in ("script","script_dinamico","script*.dat") and total>255:
        return {**result,"estado":"LIMITE_U8_LONGITUD"}
    capacidad=source.get("capacidad_bytes","")
    if capacidad in ("",None):
        return {**result,"estado":"CAPACIDAD_FISICA_NO_DOCUMENTADA"}
    try:n=int(capacidad)
    except (ValueError,TypeError):
        return {**result,"estado":"CAPACIDAD_NO_NUMERICA"}
    if n<1:return {**result,"estado":"CAPACIDAD_INVALIDA"}
    if total>n:
        return {**result,"estado":"EXCEDE_CAMPO_FIJO" if tipo in ("fijo","hud","nombre","descripcion") else "REUBICACION_O_REFORMULACION_REQUERIDA",
                "exceso_bytes":total-n}
    return {**result,"estado":"CABE_EN_BYTES_PENDIENTE_QA_VISUAL",
            "espacio_libre":n-total}

def procesar(unidades,revisiones,salida,codec="cp932",gaiji=None):
    with Path(unidades).open(encoding="utf-8-sig",newline="") as f:
        src=list(csv.DictReader(f))
    with Path(revisiones).open(encoding="utf-8-sig",newline="") as f:
        trs=list(csv.DictReader(f))
    mapping={x["unit_id"]:x for x in trs}
    if len(mapping)!=len(trs):raise PresupuestoError("Revisión con IDs duplicados")
    if len({x["unit_id"] for x in src})!=len(src):raise PresupuestoError("Fuente con IDs duplicados")
    reports=[]
    for u in src:
        if u["unit_id"] not in mapping:
            reports.append({"unit_id":u["unit_id"],"recurso":u.get("recurso",""),
                            "estado":"FALTA_REVISION"})
        else:reports.append(evaluar(u,mapping[u["unit_id"]],codec,gaiji))
    salida=Path(salida);salida.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for r in reports for k in r))
    with salida.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(reports)
    return reports

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--unidades",type=Path,required=True)
    a.add_argument("--revisiones",type=Path,required=True)
    a.add_argument("--salida",type=Path,required=True)
    a.add_argument("--codec",default="cp932")
    a.add_argument("--gaiji-json",type=Path)
    x=a.parse_args()
    gaiji=json.loads(x.gaiji_json.read_text(encoding="utf-8")) if x.gaiji_json else {}
    rows=procesar(x.unidades,x.revisiones,x.salida,x.codec,gaiji)
    from collections import Counter
    print(json.dumps(dict(Counter(r["estado"] for r in rows)),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
