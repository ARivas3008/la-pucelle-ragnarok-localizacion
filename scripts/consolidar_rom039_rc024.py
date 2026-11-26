#!/usr/bin/env python3
"""Merge the 41 authenticated ROM039 animation groups into RC024.
No commercial bytes are embedded. The original, RC024 ISO and ROM039 BPS
(or already reconstructed ROM039 pilot ISO) must be supplied by their owner.
Do not apply the ROM039 BPS directly to RC024.
"""
import argparse
import hashlib
import json
import mmap
import os
from pathlib import Path
import shutil
import struct
import tempfile
import zlib

MANIFEST = Path(__file__).resolve().parents[1] / "data/control/ROM039_intervalos_consolidacion.json"
CHUNK = 4 * 1024 * 1024

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    with Path(path).open("rb") as f:
        h = hashlib.sha256()
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
        return h.hexdigest()

def bps_replay(original, patch_path, target, manifest):
    p = Path(patch_path).read_bytes()
    require(len(p) == manifest["patch"]["size"], "Longitud BPS incorrecta")
    require(sha(p) == manifest["patch"]["sha256"], "SHA256 BPS incorrecto")
    require(p[:4] == b"BPS1", "Cabecera BPS no válida")
    require(len(p) >= 16, "BPS truncado")
    end = len(p) - 12
    src_crc, dst_crc, patch_crc = struct.unpack_from("<III", p, end)
    require(zlib.crc32(p[:-4]) == patch_crc, "CRC BPS incorrecto")
    pos = 4
    def num():
        nonlocal pos
        value, shift = 0, 1
        while True:
            require(pos < end, "Varint BPS truncado")
            b = p[pos]
            pos += 1
            value += (b & 127) * shift
            if b & 128:
                return value
            shift <<= 7
            require(shift <= 1 << 63, "Varint BPS desmesurado")
            value += shift
    def signed():
        n = num()
        return -(n >> 1) if n & 1 else n >> 1
    source_size, target_size, meta_size = num(), num(), num()
    require(source_size == Path(original).stat().st_size, "Tamaño origen BPS incorrecto")
    require(target_size == source_size, "ROM039 debe conservar tamaño ISO")
    pos += meta_size
    require(pos <= end, "Metadatos BPS fuera de límites")
    with Path(original).open("rb") as sf, Path(target).open("w+b") as tf:
        with mmap.mmap(sf.fileno(), 0, access=mmap.ACCESS_READ) as src:
            require(zlib.crc32(src) == src_crc, "CRC origen BPS incorrecto")
            tf.truncate(target_size)
            with mmap.mmap(tf.fileno(), 0) as dst:
                off = source_rel = target_rel = 0
                while pos < end:
                    command = num()
                    mode, length = command & 3, (command >> 2) + 1
                    require(off + length <= target_size, "BPS excede salida")
                    if mode == 0:
                        require(off + length <= source_size, "SourceRead fuera de origen")
                        for i in range(0, length, CHUNK):
                            n = min(CHUNK, length-i)
                            dst[off+i:off+i+n] = src[off+i:off+i+n]
                    elif mode == 1:
                        require(pos + length <= end, "Literal BPS truncado")
                        dst[off:off+length] = p[pos:pos+length]
                        pos += length
                    elif mode == 2:
                        source_rel += signed()
                        require(0 <= source_rel and source_rel + length <= source_size,
                                "SourceCopy fuera de origen")
                        for i in range(0, length, CHUNK):
                            n = min(CHUNK, length-i)
                            dst[off+i:off+i+n] = src[source_rel+i:source_rel+i+n]
                        source_rel += length
                    else:
                        target_rel += signed()
                        require(0 <= target_rel < off, "TargetCopy aún no escrito")
                        # Copy from the already written prefix; BPS permits overlap.
                        done = 0
                        while done < length:
                            n = min(length-done, off-target_rel, CHUNK)
                            dst[off+done:off+done+n] = dst[target_rel+done:target_rel+done+n]
                            done += n
                        target_rel += length
                    off += length
                require(pos == end and off == target_size, "Salida BPS incompleta")
                require(zlib.crc32(dst) == dst_crc, "CRC destino BPS incorrecto")
                dst.flush()
    require(file_sha(target) == manifest["pilot_sha256"], "SHA piloto incorrecto")

def read_at(file, offset, size):
    file.seek(offset)
    data = file.read(size)
    require(len(data) == size, "Lectura truncada")
    return data

def members(pack):
    require(pack[:8] == b"NISPACK\0", "ANMPACK no es NISPACK")
    n = struct.unpack_from("<I", pack, 12)[0]
    require(0 < n < 20000 and 16 + n*44 <= len(pack), "Directorio NISPACK inválido")
    out = {}
    for i in range(n):
        name, off, size, extra = struct.unpack_from("<32sIII", pack, 16+i*44)
        name = name.split(b"\0", 1)[0].decode("ascii")
        require(name not in out and off+size <= len(pack), "Miembro NISPACK inválido")
        out[name] = (off, size, extra)
    return out

def merge(original, base, pilot, output, manifest):
    for path, key in [(original,"source_sha256"), (base,"base_rc024_sha256"),
                      (pilot,"pilot_sha256")]:
        require(file_sha(path) == manifest[key], "SHA incorrecto: "+str(path))
    require(not Path(output).exists(), "La salida ya existe")
    require(len({Path(p).resolve() for p in (original,base,pilot,output)}) == 4,
            "No se permite sobrescribir entradas")
    start, size = manifest["pack_offset"], manifest["pack_size"]
    with Path(original).open("rb") as a, Path(base).open("rb") as b, Path(pilot).open("rb") as c:
        orig, old, new = (read_at(f,start,size) for f in (a,b,c))
    for raw,key in [(orig,"original_anm_sha256"),(old,"base_anm_sha256"),(new,"anm_sha256")]:
        require(sha(raw) == manifest[key], "ANMPACK no autenticado: "+key)
    directory = members(orig)
    require(directory == members(old) == members(new), "Directorio ANMPACK distinto")
    records = sorted(manifest["records"], key=lambda r:r["offset"])
    require(len(records)==41, "Inventario incompleto")
    result, cursor = bytearray(old), 0
    journal=[]
    for r in records:
        lo, length = r["offset"]-start,r["size"]
        hi=lo+length
        require(cursor<=lo<hi<=size, "Intervalo solapado/fuera de ANMPACK")
        mo, ms, _ = directory[r["member"]]
        require(mo<=lo<hi<=mo+ms, "Intervalo no pertenece al miembro registrado")
        a,b,c = orig[lo:hi],old[lo:hi],new[lo:hi]
        require(sha(a)==r["sha_before"] and sha(c)==r["sha_after"],
                "Ancla ROM039 no coincide: "+r["member"])
        require(a != c, "Edición sin diferencia")
        require(b==a or b==c, "Conflicto con RC024: "+r["member"])
        result[lo:hi]=c
        journal.append({"id":r["id"],"member":r["member"],"text":r["text"],
                        "offset":r["offset"],"size":length,"sha256":sha(c),
                        "already_present":b==c})
        cursor=hi
    # Preserve canonical introduction and all other bytes of RC024.
    cursor=0
    for r in records:
        lo=r["offset"]-start
        require(result[cursor:lo]==old[cursor:lo],"Regresión fuera de intervalos")
        cursor=lo+r["size"]
    require(result[cursor:]==old[cursor:],"Regresión al final de ANMPACK")
    opening_off, opening_size, _ = directory["anm3000.dat"]
    require(result[opening_off:opening_off+opening_size] ==
            old[opening_off:opening_off+opening_size],"Regresión en apertura ROM038")
    output=Path(output)
    tmp=output.with_name(output.name+".part")
    require(not tmp.exists(), "Existe una salida temporal; no sobrescribir")
    try:
        shutil.copyfile(base,tmp)
        with tmp.open("r+b") as out:
            out.seek(start)
            out.write(result)
        require(tmp.stat().st_size==Path(base).stat().st_size,"Tamaño ISO alterado")
        with tmp.open("rb") as out, Path(base).open("rb") as before:
            require(read_at(out,start,size)==result,"Relectura ANMPACK incorrecta")
            for lo,hi in ((0,start),(start+size,tmp.stat().st_size)):
                for i in range(lo,hi,CHUNK):
                    n=min(CHUNK,hi-i)
                    require(read_at(out,i,n)==read_at(before,i,n),"Regresión externa ANMPACK")
        report={"source_sha256":manifest["source_sha256"],
                "base_sha256":manifest["base_rc024_sha256"],
                "pilot_sha256":manifest["pilot_sha256"],
                "output_sha256":file_sha(tmp),"anm_sha256":sha(result),
                "records":journal,"verified":len(journal),
                "outside_intervals_preserved":True,"opening_preserved":True,
                "ppsspp":False,"dlc_merged":False,
                "provisional_names":manifest["provisional_names"]}
        os.replace(tmp,output)
        return report
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original",type=Path,required=True)
    ap.add_argument("--rc024",type=Path,required=True)
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--bps",type=Path)
    src.add_argument("--piloto",type=Path)
    ap.add_argument("--salida",type=Path,required=True)
    ap.add_argument("--informe",type=Path,required=True)
    args=ap.parse_args()
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(not args.informe.exists(),"No sobrescribir informe")
    require(args.informe.resolve() not in {args.original.resolve(),args.rc024.resolve(),
            args.salida.resolve(),*(p.resolve() for p in (args.bps,args.piloto) if p)},
            "Ruta de informe coincide con entrada/salida")
    require(file_sha(args.original)==m["source_sha256"],"ISO original incompatible")
    if args.bps:
        with tempfile.TemporaryDirectory(dir=args.salida.parent) as folder:
            pilot=Path(folder)/"pilot.iso"
            bps_replay(args.original,args.bps,pilot,m)
            report=merge(args.original,args.rc024,pilot,args.salida,m)
    else:
        report=merge(args.original,args.rc024,args.piloto,args.salida,m)
    args.informe.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Relectura:",report["verified"],"/41; SHA256:",report["output_sha256"])

if __name__=="__main__":
    main()
