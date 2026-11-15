#!/usr/bin/env python3
"""Inventario forense (solo lectura) de contenedores PSP La Pucelle.

No guarda bytes de recursos comerciales: solo hashes y metadatos.
La identificación de formatos es heurística y falla cerrada.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
PATCHER=HERE.parents[1]
sys.path.insert(0,str(PATCHER/"app/scripts"))
sys.path.insert(0,str(HERE.parent/"v0.10"))
from nis_formats import nispack,lzs_header,lzs_decompress
from contenedores import entradas_dat
from iso_reubicar import recorrer

def sha(b):
    return hashlib.sha256(b).hexdigest()

def fichar(nodes, nombre, data, padre, profundidad=0, offset=None, limit=64*1024*1024):
    """Inventaria capas conocidas; no interpreta tipos no confirmados."""
    name=nombre.split("/")[-1].split("::")[-1]
    label="DESCONOCIDO";parts=[]
    if data.startswith(b"NISPACK\0"):
        try:
            parts=[(e["name"],e["content"],e["offset"]) for e in nispack(data)]
            label="NISPACK"
        except Exception as exc:label="NISPACK_INVALIDO:"+str(exc)[:100]
    elif name.upper().endswith(".LZS"):
        try:
            meta=lzs_header(data)
            if meta["raw_size"]>limit:label="LZS_SUPERA_LIMITE"
            else:
                raw=lzs_decompress(data)
                label="NIS_LZS"
                parts=[(nombre+"::DAT_DESCOMPRIMIDO",raw,None)]
        except Exception as exc:label="LZS_INVALIDO:"+str(exc)[:100]
    elif name=="DAT_DESCOMPRIMIDO":
        try:
            members=entradas_dat(data)
            label="DAT_INDEXADO"
            parts=[(n,data[s:e],s) for n,s,e,_ in members]
        except Exception as exc:label="DAT_NO_RECONOCIDO:"+str(exc)[:100]
    elif name.lower().endswith(".txp"):
        label="TXP_GRAFICO_FORMATO_PENDIENTE"
    elif name.lower().startswith("script") and name.lower().endswith(".dat"):
        label="SCRIPT_EVENTOS_PRESUNTO"
    elif name.lower().startswith("talk") and name.lower().endswith(".dat"):
        label="TALK_DIALOGOS_PRESUNTO"
    elif name.upper()=="EBOOT.BIN":
        label="EBOOT_PSP"
    node={"ruta":nombre,"padre":padre,"profundidad":profundidad,
          "clase":label,"offset_en_padre":offset if offset is not None else "",
          "tamano_bytes":len(data),"sha256":sha(data)}
    nodes.append(node)
    if profundidad<5:
        for child,raw,off in parts:
            # Cada submiembro conserva ruta única; no guarda contenido.
            childname=child if "::DAT_DESCOMPRIMIDO" in child else nombre+"::"+child
            fichar(nodes,childname,raw,nombre,profundidad+1,off,limit)


def inventariar(iso=None,dlc_dir=None,limit=64*1024*1024):
    nodes=[];warnings=[]
    if iso:
        with Path(iso).open("rb") as fd:
            records=recorrer(fd)
            for rec in records:
                last=rec.ruta.rsplit("/",1)[-1]
                if "." not in last or rec.size<=0:
                    continue  # directorios o registros vacíos
                if rec.size>limit:
                    nodes.append({"ruta":rec.ruta,"padre":"ISO9660","profundidad":0,
                                  "clase":"OMITIDO_LIMITE_LECTURA","offset_en_padre":rec.offset,
                                  "tamano_bytes":rec.size,"sha256":""})
                    continue
                fd.seek(rec.offset)
                b=fd.read(rec.size)
                if len(b)!=rec.size:
                    warnings.append("Truncamiento ISO: "+rec.ruta);continue
                fichar(nodes,rec.ruta,b,"ISO9660",offset=rec.offset,limit=limit)
    if dlc_dir:
        for i in range(4):
            path=Path(dlc_dir)/f"DL_JP_{i:02d}.EDAT"
            if not path.is_file():
                warnings.append("DLC no disponible: "+str(path));continue
            if path.stat().st_size>limit:
                warnings.append("DLC supera límite de lectura: "+str(path));continue
            fichar(nodes,str(path.name),path.read_bytes(),"PSP/GAME/ULJS00244",limit=limit)
    return nodes,warnings


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso",type=Path)
    ap.add_argument("--dlc-directorio",type=Path)
    ap.add_argument("--salida",type=Path,required=True)
    ap.add_argument("--limite-mib",type=int,default=64)
    a=ap.parse_args()
    if not (a.iso or a.dlc_directorio):ap.error("Se necesita ISO y/o DLC")
    if not 1<=a.limite_mib<=256:ap.error("Límite fuera de rango")
    nodes,warnings=inventariar(a.iso,a.dlc_directorio,a.limite_mib*1024*1024)
    a.salida.mkdir(parents=True,exist_ok=True)
    fields=["ruta","padre","profundidad","clase","offset_en_padre","tamano_bytes","sha256"]
    with (a.salida/"inventario_forense.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(nodes)
    summary={"nodos":len(nodes),"clases":dict(Counter(x["clase"] for x in nodes)),
             "advertencias":warnings,"estado":"Inventario estructural de solo lectura; no certifica formatos no reconocidos"}
    (a.salida/"inventario_resumen.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
