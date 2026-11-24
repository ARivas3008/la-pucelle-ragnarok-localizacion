"""Revisión coordinada central y segmentos completos anclados al original.

La revisión editorial no es evidencia de inserción. Los segmentos recuperan
líneas omitidas por el manifiesto sin alterar sus IDs ni sus offsets.
"""
import csv,hashlib,io,struct
from collections import Counter
from pathlib import Path

CENTRAL="data/preexistentes/509_revision_central.csv"

class RevisionError(ValueError):pass

def merge_central(repo_dir,reviews,manifest,checks,states,expected=509):
    path=Path(repo_dir)/CENTRAL
    if not path.is_file():raise RevisionError("Falta CSV central: "+CENTRAL)
    payload=path.read_bytes()
    rows=csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not {"grupo_id","es_revisado","estado"}.issubset(rows.fieldnames or []):
        raise RevisionError("Cabecera central inválida")
    master={r["grupo_id"] for r in manifest}
    central={}
    for row in rows:
        gid=row["grupo_id"];status=row["estado"];text=row["es_revisado"]
        if gid in reviews or gid in central or gid not in master:
            raise RevisionError("ID central duplicado o desconocido: "+gid)
        if status not in ("revisado","pendiente") or (status=="revisado")!=bool(text.strip()):
            raise RevisionError("Estado/texto central incoherente: "+gid)
        central[gid]=row
    if len(central)!=expected or set(reviews)|set(central)!=master:
        raise RevisionError("Catálogo central/distribuido no coincide con maestro")
    counter=Counter(states);counter.update(row["estado"] for row in central.values())
    proof=list(checks)+[{"corpus":"central","ruta":CENTRAL,"sha256":hashlib.sha256(payload).hexdigest(),"filas":len(central)}]
    return {**reviews,**central},proof,counter

def lines_sha(run):
    """Hash inequívoco de las cadenas CP932 crudas, con longitud de cada una."""
    h=hashlib.sha256()
    for line in run:
        raw=line["raw"]
        h.update(struct.pack("<I",len(raw)));h.update(raw)
    return h.hexdigest()

def scoped_segments(doc,manifest,reviews,buffers,metas,runs,legacy=()):
    if not doc:return [],set()
    if doc.get("schema")!=1:raise RevisionError("Esquema de segmentos anclados inválido")
    sources=doc["recursos"];selected=[];blocked=set();seen=set()
    existing={(s["recurso"],s["offset"]) for s in legacy}
    index={(r["recurso"],int(r["offset"])):r for r in manifest if r["recurso"] in buffers}
    byres={}
    for row in doc["segmentos"]:
        res=row["recurso"];off=row["offset"]
        if res not in buffers:continue
        if res not in byres:
            if hashlib.sha256(buffers[res]).hexdigest()!=sources.get(res):
                raise RevisionError("SHA de recurso original distinto: "+res)
            byres[res]={r[0]["offset"]:r for r in runs(buffers[res],metas[res])}
        key=(res,off)
        if key in seen or key in existing:raise RevisionError("Segmento duplicado o solapado con aprobación previa: "+str(key))
        seen.add(key);run=byres[res].get(off)
        if not run or lines_sha(run)!=row["sha256_lineas"]:
            raise RevisionError("Cadenas originales no coinciden: "+str(key))
        units=[index[(res,t["offset"])] for t in run if (res,t["offset"]) in index]
        gids=list(dict.fromkeys(u["grupo_id"] for u in units))
        targets=list(row["grupos_objetivo"])
        if not targets or len(set(targets))!=len(targets) or gids!=row["grupos"] or not set(targets).issubset(gids):
            raise RevisionError("Relación grupo/unidad no coincide: "+str(key))
        if any(reviews.get(g,{}).get("estado")!="revisado" for g in gids):
            raise RevisionError("Segmento con grupo sin revisión: "+str(key))
        if not isinstance(row["es"],str) or not row["es"].strip():
            raise RevisionError("Segmento vacío: "+str(key))
        blocked.update(targets)
        selected.append(dict(recurso=res,offset=off,grupo_id=targets[0],
                             grupos=gids,es=row["es"],original_hex=[t["raw"].hex() for t in run],
                             solo_origen=True))
    return selected,blocked
