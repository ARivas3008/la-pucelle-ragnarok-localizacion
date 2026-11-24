"""Auditoría reproducible del corazón codificado como ￥ en recursos originales PSP.

Solo lectura: no modifica ni publica ISO, DLC, atlas o cuadros. Evidencia A
requiere ISO comercial original auténtica; pruebas unitarias son evidencia B.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"parcheador/app/scripts"))
from nis_formats import lzs_decompress, nispack
from fuentes_es import index_sjis, unpack_pixels, get_tile
from auditar_bgpack_original import _directory, BLOCK

ISO_SHA="4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5"
MARKER="￥"
CODE=b"\x81\x8f"
TEXT_GROUP_4268="そのほうがキュートだからエリ￥"
OFFSET_GROUP_4268=66462

def get_iso_files(iso,requested):
    with Path(iso).open("rb") as f:
        f.seek(16*BLOCK)
        pvd=f.read(BLOCK)
        if pvd[:7]!=b"\x01CD001\x01":
            raise ValueError("PVD ISO9660 inválido")
        root=pvd[156:190]
        stack=[("",int.from_bytes(root[2:6],"little"),int.from_bytes(root[10:14],"little"))]
        found={}
        seen=set()
        while stack and len(found)<len(requested):
            prefix,lba,size=stack.pop()
            if (lba,size) in seen:continue
            seen.add((lba,size))
            for name,extent,sz,is_dir in _directory(f,lba,size):
                path="/".join(x for x in (prefix,name) if x)
                if is_dir:
                    stack.append((path,extent,sz))
                elif path in requested:
                    f.seek(extent*BLOCK)
                    payload=f.read(sz)
                    if len(payload)!=sz:raise ValueError("Recurso ISO truncado")
                    found[path]=payload
        if set(found)!=set(requested):
            raise ValueError("Faltan recursos: "+str(sorted(set(requested)-set(found))))
        return found

def dat_members(raw):
    if len(raw)<20:raise ValueError("DAT truncado")
    n=struct.unpack_from("<I",raw)[0]
    if not (1<=n<=300 and 16+32*n<=len(raw)):
        raise ValueError("Tabla DAT no reconocida")
    base=16+32*n
    pos=base
    result={}
    for i in range(n):
        off=16+32*i
        end=base+struct.unpack_from("<I",raw,off)[0]
        name=raw[off+4:off+32].split(b"\0",1)[0].decode("cp932")
        if name in result or not pos<=end<=len(raw):
            raise ValueError("DAT inválido")
        result[name]=bytes(raw[pos:end])
        pos=end
    if pos!=len(raw):raise ValueError("DAT no cubre todos los bytes")
    return result

def heart_tile_rows(fnt,atlas):
    if len(fnt)!=23232:raise ValueError("FontB fnt no reconocido")
    entries=struct.unpack("<11616H",fnt)
    if CODE.decode("cp932")!=MARKER or MARKER.encode("cp932")!=CODE:
        raise ValueError("Marcador CP932 no reversible")
    ix=index_sjis(CODE)
    gid=entries[ix]
    if not gid:raise ValueError("Símbolo ￥ sin glifo fontB")
    pixels=unpack_pixels(atlas)
    tile=get_tile([pixels],gid)
    rows=[sum(bool(x) for x in row) for row in tile]
    return {"font_index":ix,"gid":gid,"filas_no_transparentes":rows,
            "forma_corazon":[8,12,14,14,14,12,12,10,8,6,4,2,0,0]==rows}

def audit(iso):
    p=Path(iso)
    with p.open("rb") as f:
        sha=hashlib.file_digest(f,"sha256").hexdigest()
    if sha!=ISO_SHA:
        raise ValueError("ISO distinta del original autorizado")
    payloads=get_iso_files(p,{"PSP_GAME/USRDIR/SCRIPTPACK.DAT","PSP_GAME/USRDIR/START_JP.LZS"})
    pack=payloads["PSP_GAME/USRDIR/SCRIPTPACK.DAT"]
    data={x["name"]:x["content"] for x in nispack(pack)}
    talk=data["talk01_jp.dat"]
    expected=TEXT_GROUP_4268.encode("cp932")
    if talk[OFFSET_GROUP_4268:OFFSET_GROUP_4268+len(expected)]!=expected:
        raise ValueError("Grupo 4268 no coincide en talk auténtico")
    if talk[OFFSET_GROUP_4268+len(expected)]!=0:
        raise ValueError("String 4268 sin NUL posterior")
    original_lzs=payloads["PSP_GAME/USRDIR/START_JP.LZS"]
    inner=dat_members(lzs_decompress(original_lzs))
    fnt=inner["fontB.fnt"]
    tex=inner["FontB0000.txp"]
    info=heart_tile_rows(fnt,tex)
    if info["font_index"]!=175 or info["gid"]!=99 or not info["forma_corazon"]:
        raise ValueError("Mapa de corazones original desconocido")
    contexts={n:bytes(x).count(CODE) for n,x in data.items() if n.startswith("talk")}
    return {"clase":"A: archivos originales auténticos; no juego en emulador",
            "sha256_iso":sha,"grupo_id":4268,"recurso":"SCRIPTPACK.DAT/talk01_jp.dat",
            "offset_texto":OFFSET_GROUP_4268,
            "cp932":"818f","unicode":"U+FFE5","render_original":"corazón 14x14",
            "fuente":info,"fontB_fnt_sha256":hashlib.sha256(fnt).hexdigest(),
            "fontB_atlas_sha256":hashlib.sha256(tex).hexdigest(),
            "ocurrencias_por_talk":contexts,
            "certificado_ppsspp_v019":False}

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--iso",type=Path,required=True)
    a.add_argument("--out",type=Path)
    args=a.parse_args()
    result=audit(args.iso)
    content=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding="utf-8")
    else:print(content)

if __name__=="__main__":main()
