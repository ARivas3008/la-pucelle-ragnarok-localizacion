"""Comprobación BGPACK 'fail closed': solo píxeles TXP explícitamente autorizados.

Aun cuando pase, requiere ejecutar la candidata en PPSSPP. No distribuye ISO.
"""
import argparse, hashlib, json
from pathlib import Path
from auditar_bgpack_original import read_bgpack, parse_bgpack
from inspeccionar_txp_bgpack import metadata

class BGPACKIntegrityError(ValueError):
    pass

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def verify(original, candidate, allowed=None):
    """allowed: nombre de TXP -> sha256 del blob original de la textura."""
    if allowed is None:
        allowed={}
    if not isinstance(allowed,dict) or not all(isinstance(k,str) and isinstance(v,str) and len(v)==64 for k,v in allowed.items()):
        raise BGPACKIntegrityError("Autorizaciones deben ser {nombre:SHA256_original}")
    if len(original)!=len(candidate):
        raise BGPACKIntegrityError("Tamaño BGPACK modificado")
    try:
        old=parse_bgpack(original)
        new=parse_bgpack(candidate)
    except (ValueError,UnicodeError) as exc:
        raise BGPACKIntegrityError("Contenedor inválido: "+str(exc)) from exc
    layout=lambda entries:[(x["name"],x["offset"],x["size"],x["metadata_u32"]) for x in entries]
    if layout(old)!=layout(new):
        raise BGPACKIntegrityError("Orden, metadata u offsets NISPACK cambiados")
    byname={item["name"]:item for item in old}
    if not set(allowed).issubset(byname):
        raise BGPACKIntegrityError("Se autoriza un TXP inexistente")
    intervals=[]
    for name,expected_sha in allowed.items():
        if not name.lower().endswith(".txp"):
            raise BGPACKIntegrityError("Solo pueden autorizarse TXP")
        member=byname[name]
        a,b=member["offset"],member["offset"]+member["size"]
        oldblob=bytes(original[a:b]);newblob=bytes(candidate[a:b])
        if sha256(oldblob)!=expected_sha.lower():
            raise BGPACKIntegrityError("Hash fuente incorrecto para "+name)
        try:
            meta_o,palette_o,_=metadata(oldblob)
            meta_n,palette_n,_=metadata(newblob)
        except (ValueError,KeyError) as exc:
            raise BGPACKIntegrityError("TXP inválida: "+name+" "+str(exc)) from exc
        if meta_o["ancho"]!=meta_n["ancho"] or meta_o["alto"]!=meta_n["alto"] or meta_o["bpp"]!=meta_n["bpp"]:
            raise BGPACKIntegrityError("Geometría o bpp TXP cambiado: "+name)
        start=16+len(palette_o)
        if oldblob[:start]!=newblob[:start] or palette_o!=palette_n:
            raise BGPACKIntegrityError("Cabecera o CLUT alterados: "+name)
        intervals.append((a+start,b))
    intervals.sort()
    prev=0
    for a,b in intervals:
        if original[prev:a]!=candidate[prev:a]:
            raise BGPACKIntegrityError("Región fuera de píxeles autorizados cambiada")
        prev=b
    if original[prev:]!=candidate[prev:]:
        raise BGPACKIntegrityError("Recurso, relleno o cabecera no autorizados modificados")
    return {"estado":"SEGURIDAD_BINARIA_SUPERADA_NO_PPSSPP",
            "sha256_bgpack_original":sha256(original),
            "sha256_bgpack_candidato":sha256(candidate),
            "miembros":len(old),
            "texturas_autorizadas":sorted(allowed),
            "integridad_fuera_de_pixeles":True,
            "certificacion_visual":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path,required=True)
    p.add_argument("--iso-candidata",type=Path,required=True)
    p.add_argument("--hash-original-iso",required=True,help="SHA256 de ISO autenticada")
    p.add_argument("--allow-json",type=Path,help="JSON {nombre_txp: sha256_original}; ausente equivale a política cero cambios")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    with args.iso_original.open("rb") as fp:
        if hashlib.file_digest(fp,"sha256").hexdigest()!=args.hash_original_iso.lower():
            raise BGPACKIntegrityError("ISO original no coincide con hash autenticado")
    original,_=read_bgpack(args.iso_original)
    candidate,_=read_bgpack(args.iso_candidata)
    allowed=json.loads(args.allow_json.read_text(encoding="utf-8")) if args.allow_json else {}
    result=verify(original,candidate,allowed)
    output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:print(output)

if __name__=="__main__":
    main()
