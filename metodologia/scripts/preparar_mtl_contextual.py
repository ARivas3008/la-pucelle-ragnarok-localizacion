#!/usr/bin/env python3
"""Prepara peticiones de MTL con contexto e importa borradores sin aprobarlos.

No contacta servicios externos; admite respuestas JSONL de cualquier sistema.
Los originales permanecen inmutables y las variables se verifican por unidad.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

TOKENS = re.compile(r"\{[^{}]*\}|%[0-9$.*+-]*[sdifuxX]|<[^<>]+>|\\[nr]")
CAMPOS = ("unit_id", "grupo_id", "recurso", "original")

def leer_lotes(directorio):
    paths = sorted(Path(directorio).glob("*/entrada.csv"))
    if not paths:
        raise ValueError("No se encontraron entradas de lotes (NNN/entrada.csv)")
    rows = []
    ids = set()
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            read = csv.DictReader(f)
            if not set(CAMPOS).issubset(read.fieldnames or []):
                raise ValueError("Faltan columnas de origen en " + str(path))
            for row in read:
                uid = row["unit_id"]
                if not uid or uid in ids:
                    raise ValueError("unit_id vacío o duplicado: " + uid)
                ids.add(uid)
                rows.append({**row, "lote": path.parent.name})
    return rows

def solicitudes(rows):
    buckets = {}
    for row in rows:
        key = (row["lote"], row["recurso"], row.get("escena", ""),
               row["grupo_id"])
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(row)
    for (lot, recurso, escena, gid), group in buckets.items():
        yield {
            "lote": lot, "grupo_id": gid, "recurso": recurso, "escena": escena,
            "contexto_previo": group[0].get("contexto_previo", ""),
            "contexto_siguiente": group[-1].get("contexto_siguiente", ""),
            "instruccion": (
                "Traducir como borrador al español, respetando orden, etiquetas, "
                "variables y nombres propios. No agregar oraciones. Devolver "
                "una línea JSON por unit_id con campos unit_id y mtl_es."
            ),
            "unidades": [
                {"unit_id": r["unit_id"], "original": r["original"],
                 "hablante": r.get("hablante", ""),
                 "marcadores": TOKENS.findall(r["original"])}
                for r in group
            ]
        }

def exportar(lotes, salida):
    rows = leer_lotes(lotes)
    path = Path(salida)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for req in solicitudes(rows):
            f.write(json.dumps(req, ensure_ascii=False) + "\n")
            count += 1
    return {"unidades": len(rows), "solicitudes_grupos": count,
            "estado": "PENDIENTE_MTL_EXTERNA"}

def importar(lotes, respuestas, salida):
    rows = leer_lotes(lotes)
    ids = {r["unit_id"] for r in rows}
    supplied = {}
    with Path(respuestas).open(encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                uid = str(obj["unit_id"])
                raw = obj["mtl_es"]
            except (ValueError, KeyError, TypeError) as e:
                raise ValueError(f"Respuesta JSONL inválida en línea {line_no}") from e
            if not isinstance(raw, str):
                raise ValueError("mtl_es debe ser texto: " + uid)
            if uid not in ids:
                raise ValueError("Respuesta para unit_id no solicitado: " + uid)
            if uid in supplied:
                raise ValueError("Respuesta duplicada para unit_id: " + uid)
            supplied[uid] = raw
    reports = []
    for row in rows:
        uid = row["unit_id"]
        candidate = supplied.get(uid, "")
        original = row["original"]
        if not candidate.strip():
            status = "SIN_BORRADOR"
        elif TOKENS.findall(original) != TOKENS.findall(candidate):
            status = "MTL_MARCADORES_ALTERADOS"
        elif candidate == original:
            status = "MTL_IDENTICA_AL_ORIGINAL"
        else:
            status = "BORRADOR_PENDIENTE_REVISION"
        reports.append({
            "unit_id": uid, "grupo_id": row["grupo_id"], "lote": row["lote"],
            "recurso": row["recurso"], "original": original,
            "mtl_es": candidate, "estado_mtl": status,
            "marcadores_originales": "|".join(TOKENS.findall(original)),
            "marcadores_borrador": "|".join(TOKENS.findall(candidate))
        })
    out = Path(salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=reports[0].keys())
        wr.writeheader()
        wr.writerows(reports)
    counts = {}
    for r in reports:
        counts[r["estado_mtl"]] = counts.get(r["estado_mtl"], 0) + 1
    return {"unidades": len(rows), "recibidas": len(supplied),
            "estados": counts, "revisadas": 0,
            "advertencia": "No modificar revision.csv automáticamente"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lotes", type=Path, required=True)
    ap.add_argument("--solicitudes", type=Path,
                    help="Ruta para exportar peticiones JSONL")
    ap.add_argument("--respuestas", type=Path,
                    help="Respuestas unit_id/mtl_es en JSONL")
    ap.add_argument("--salida-borradores", type=Path)
    a = ap.parse_args()
    if bool(a.solicitudes) == bool(a.respuestas):
        ap.error("Indica --solicitudes O --respuestas")
    if a.respuestas and not a.salida_borradores:
        ap.error("Se exige --salida-borradores al importar")
    result = (exportar(a.lotes, a.solicitudes) if a.solicitudes
              else importar(a.lotes, a.respuestas, a.salida_borradores))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
