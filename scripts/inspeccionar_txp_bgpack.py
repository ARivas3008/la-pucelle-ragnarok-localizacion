"""Analiza TXP paletizados de BGPACK original sin modificar ni publicar texturas.

Formato comprobado en ISO original: cabecera 16 bytes, CLUT RGBA8888,
píxeles de 4/8 bpp en bloques PSP swizzled de 16 bytes x 8 líneas.
Una imagen decodificada del original NO certifica su aspecto en PPSSPP parcheado.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from auditar_bgpack_original import read_bgpack,parse_bgpack

CANDIDATOS=("title1.txp","wbg00.txp","wbg02.txp","wbg04.txp",
            "wbg05.txp","wbg06.txp","wmap.txp","wmap_04.txp")
class TXPError(ValueError):pass

def metadata(raw):
    if len(raw)<16:raise TXPError("TXP truncado")
    w,h,colors,reserved,pal_size,banks,one,two=struct.unpack_from("<8H",raw,0)
    if not 0<w<=4096 or not 0<h<=4096 or colors not in (16,256):
        raise TXPError("Dimensiones o número de colores no soportados")
    if reserved!=0 or pal_size!=colors or banks!=1 or one!=1 or two!=1:
        raise TXPError("CLUT/bancos o banderas TXP desconocidos")
    bpp=4 if colors==16 else 8
    if (w*bpp)%8:raise TXPError("Ancho no alineado a bytes")
    stride=w*bpp//8
    if stride%16 or h%8:raise TXPError("TXP fuera de bloques swizzle 16x8")
    plen=colors*4
    total=16+plen+stride*h
    if total!=len(raw):raise TXPError(f"Tamaño TXP inválido: {len(raw)} frente a {total}")
    palette=raw[16:16+plen]
    data=raw[16+plen:]
    return {"ancho":w,"alto":h,"bpp":bpp,"colores":colors,"bytes":len(raw),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "sha256_paleta":hashlib.sha256(palette).hexdigest(),
            "sha256_indices_swizzled":hashlib.sha256(data).hexdigest()},palette,data

def swizzle(index_bytes,w,h,bpp):
    stride=w*bpp//8
    if len(index_bytes)!=stride*h or stride%16 or h%8:
        raise TXPError("Dimensiones o índices fuera de bloques 16x8")
    out=bytearray(len(index_bytes));position=0
    for by in range(h//8):
        for bx in range(stride//16):
            for yy in range(8):
                offset=(by*8+yy)*stride+bx*16
                out[position:position+16]=index_bytes[offset:offset+16]
                position+=16
    return bytes(out)

def unswizzle(data,w,h,bpp):
    stride=w*bpp//8
    if len(data)!=stride*h or stride%16 or h%8:
        raise TXPError("Dimensiones o swizzle inválidos")
    out=bytearray(len(data));position=0
    for by in range(h//8):
        for bx in range(stride//16):
            for yy in range(8):
                offset=(by*8+yy)*stride+bx*16
                out[offset:offset+16]=data[position:position+16]
                position+=16
    return bytes(out)

def rgba_bytes(linear,palette,bpp):
    colors=16 if bpp==4 else 256
    if bpp not in (4,8) or len(palette)!=colors*4:
        raise TXPError("CLUT RGBA8888 incorrecta")
    out=bytearray()
    if bpp==8:
        for index in linear:out+=palette[index*4:index*4+4]
    else:
        for packed in linear:
            for index in (packed&15,packed>>4):
                out+=palette[index*4:index*4+4]
    return bytes(out)

def analizar_iso(iso,expected_sha256,preview_dir=None):
    path=Path(iso)
    with path.open("rb") as f:
        iso_sha=hashlib.file_digest(f,"sha256").hexdigest()
    if iso_sha.lower()!=expected_sha256.lower():
        raise TXPError("ISO distinta a la autenticada; cancelando análisis")
    bgpack,locator=read_bgpack(path)
    members={item["name"]:item for item in parse_bgpack(bgpack)}
    previews=Path(preview_dir) if preview_dir else None
    if previews:
        previews.mkdir(parents=True,exist_ok=True)
        from PIL import Image
    report=[]
    for name in CANDIDATOS:
        if name not in members:raise TXPError(f"Falta TXP esperado: {name}")
        member=members[name]
        a,b=member["offset"],member["offset"]+member["size"]
        raw=bgpack[a:b]
        info,palette,packed=metadata(raw)
        linear=unswizzle(packed,info["ancho"],info["alto"],info["bpp"])
        assert swizzle(linear,info["ancho"],info["alto"],info["bpp"])==packed
        rgba=rgba_bytes(linear,palette,info["bpp"])
        info.update(nombre=name,offset_bgpack=a,sha256_rgba=hashlib.sha256(rgba).hexdigest(),
                    verificacion_reversible=True,certificado_ppsspp=False)
        report.append(info)
        if previews:
            # Solo copias locales del usuario: NO subir PNG comerciales al repositorio.
            Image.frombytes("RGBA",(info["ancho"],info["alto"]),rgba).save(previews/(name+".png"))
    return dict(fuente="A: ISO original autentica",iso_sha256=iso_sha,
                bgpack_sha256=hashlib.sha256(bgpack).hexdigest(),
                recurso=locator["path"],candidatos=report,
                nota="La detección visual de texto y el resultado en PPSSPP son cuestiones distintas.")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso",required=True,type=Path)
    p.add_argument("--expect-iso-sha256",required=True)
    p.add_argument("--out",type=Path)
    p.add_argument("--preview-dir",type=Path,
                   help="Opcional: imágenes PRIVADAS del original. No publicar PNG comerciales.")
    args=p.parse_args()
    result=analizar_iso(args.iso,args.expect_iso_sha256,args.preview_dir)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: {len(result['candidatos'])} TXP originales; sin validación PPSSPP")

if __name__=="__main__":main()
