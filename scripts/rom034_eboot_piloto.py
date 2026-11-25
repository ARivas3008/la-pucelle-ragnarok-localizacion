#!/usr/bin/env python3
"""ROM-034: reproducir piloto EBOOT 2/2, sin publicar binarios."""
import argparse, hashlib, json, shutil
from pathlib import Path

ISO_SHA = "4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5"
EBOOT_SHA = "2b9a1a9864f3b236e83a2848f839023e92dcb7a5272bcb430cef527eafb563f6"
PILOT_SHA = "4c07a141106b39b8e10368833dc93b3dad94d260c548091d665024865a2ceebc"
PILOT_EBOOT_SHA = "58697f60562cadf0f3ae77e5ca4a5d277e7cbc7d9f90f844b9839e9e900811ae"
OFFSET, SIZE = 65536, 895108
TARGETS = [(3774,792108,"Move Speed  Blitz","Paso máximo"),
           (3778,792204,"Text Speed  Blitz","Texto máximo")]

def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def require(value, message):
    if not value:
        raise ValueError(message)

def patch_eboot(raw):
    require(hashlib.sha256(raw).hexdigest()==EBOOT_SHA,"EBOOT original desconocido")
    out = bytearray(raw)
    changes = []
    for uid,off,source,target in TARGETS:
        old = source.encode("ascii")
        require(raw[off:off+len(old)+1]==old+b"\0","Ancla original distinta")
        # F040 es el gaiji para á del codec fontB versionado.
        enc = b"".join(b"\xf0\x40" if c=="á" else c.encode("ascii") for c in target)
        require(len(enc)<=len(old),"Campo insuficiente")
        new = enc.ljust(len(old),b" ")
        out[off:off+len(old)] = new
        changes.append(dict(unit_id=uid,offset=off,original=source,traduccion=target,
                            antes_hex=old.hex(),despues_hex=new.hex(),terminador_conservado=True))
    require(hashlib.sha256(out).hexdigest()==PILOT_EBOOT_SHA,"Hash EBOOT piloto distinto")
    return bytes(out),changes

def run(original, output):
    require(original.resolve()!=output.resolve() and not output.exists(),"Salida debe ser nueva")
    require(sha(original)==ISO_SHA,"ISO original desconocida")
    with original.open("rb") as f:
        f.seek(OFFSET); raw=f.read(SIZE)
    patched, changes=patch_eboot(raw)
    shutil.copyfile(original,output)
    try:
        with output.open("r+b") as f:
            f.seek(OFFSET); f.write(patched)
        with output.open("rb") as f:
            f.seek(OFFSET); require(f.read(SIZE)==patched,"Relectura incorrecta")
        require(sha(output)==PILOT_SHA,"Hash ISO piloto distinto")
        # Hash exacto de la ISO piloto previamente cotejada byte a byte.
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return dict(iso_original_sha256=ISO_SHA,iso_piloto_sha256=PILOT_SHA,
                eboot_original_sha256=EBOOT_SHA,eboot_piloto_sha256=PILOT_EBOOT_SHA,
                cambios=changes,ppsspp=False,candidata_integral=False,
                advertencia="Piloto de dos rótulos: requiere fontB y fusión desde originales.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original",type=Path);p.add_argument("salida",type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.original,a.salida),ensure_ascii=False,indent=2))
