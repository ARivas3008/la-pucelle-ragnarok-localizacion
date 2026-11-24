"""Compara recursos de dos ISO PSP sin depender de su sector físico.

Defensa complementaria a verificadores específicos (talk/BGPACK): NO certifica
que la ISO candidata arranque en PPSSPP. Solo lectura y hashes de los archivos.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

BLOCK=2048
class ISOIsolationError(ValueError):pass

def _entry(row:bytes):
    if len(row)<34 or row[0]!=len(row) or row[32]>len(row)-33:
        raise ISOIsolationError("Registro ISO9660 inválido")
    if int.from_bytes(row[2:6],"little")!=int.from_bytes(row[6:10],"big"):
        raise ISOIsolationError("LBA dual endian discordante")
    if int.from_bytes(row[10:14],"little")!=int.from_bytes(row[14:18],"big"):
        raise ISOIsolationError("Longitud dual endian discordante")
    rawname=row[33:33+row[32]]
    if rawname in (b"\x00",b"\x01"):
        name="." if rawname==b"\x00" else ".."
    else:
        try:name=rawname.decode("ascii").split(";")[0]
        except UnicodeError as exc:raise ISOIsolationError("Nombre ISO no ASCII") from exc
        if not name or name in (".","..") or "/" in name or "\\" in name:
            raise ISOIsolationError("Nombre ISO inválido")
    return name,int.from_bytes(row[2:6],"little"),int.from_bytes(row[10:14],"little"),bool(row[25]&2)

def inventory(path):
    """Devuelve ruta ISO -> (LBA,bytes) para todos los archivos autenticados estructuralmente."""
    path=Path(path);sz=path.stat().st_size
    if sz<BLOCK*19 or sz%BLOCK:raise ISOIsolationError("Longitud ISO inválida")
    with path.open("rb") as f:
        f.seek(16*BLOCK);pvd=f.read(BLOCK)
        if pvd[:7]!=b"\x01CD001\x01" or pvd[6]!=1:
            raise ISOIsolationError("PVD ISO9660 incorrecto")
        root=_entry(pvd[156:190]);stack=[("",root[1],root[2])]
        files={};directories=set();visited=set()
        while stack:
            prefix,lba,size=stack.pop()
            if not size or (lba*BLOCK+size)>sz or (lba,size) in visited:
                raise ISOIsolationError("Directorio inválido/duplicado")
            visited.add((lba,size))
            f.seek(lba*BLOCK);data=f.read(size)
            if len(data)!=size:raise ISOIsolationError("Directorio truncado")
            pos=0
            while pos<len(data):
                n=data[pos]
                if not n:
                    pos=((pos//BLOCK)+1)*BLOCK
                    continue
                if pos//BLOCK != (pos+n-1)//BLOCK or pos+n>len(data):
                    raise ISOIsolationError("Entrada cruza sector o directorio")
                name,extent,length,isdir=_entry(data[pos:pos+n]);pos+=n
                if name in (".",".."):continue
                namefull=(prefix+"/"+name).lstrip("/")
                if not length or (extent*BLOCK+length)>sz or namefull in files or namefull in directories:
                    raise ISOIsolationError("Archivo o subdirectorio inválido/duplicado")
                if isdir:
                    directories.add(namefull)
                    stack.append((namefull,extent,length))
                else:
                    files[namefull]=(extent*BLOCK,length)
        spans=sorted((s,s+size,name) for name,(s,size) in files.items())
        if any(end>other for (_,end,_),(other,_,_) in zip(spans,spans[1:])):
            raise ISOIsolationError("Archivos físicos superpuestos")
        return files,directories

def _hash_member(file,offset,size):
    digest=hashlib.sha256()
    file.seek(offset)
    remaining=size
    while remaining:
        part=file.read(min(1024*1024,remaining))
        if not part:raise ISOIsolationError("Recurso ISO incompleto")
        digest.update(part);remaining-=len(part)
    return digest.hexdigest()

def verify(original,candidate,allowed=None,expected_source_iso_sha256=None):
    """allowed: nombres exactos de archivos ISO -> SHA256 original fijado.

    La autorización no aprueba los cambios dentro del archivo: es obligatorio
    pasar además los validadores de sus formatos y, finalmente, PPSSPP real.
    """
    original=Path(original);candidate=Path(candidate)
    allowed={} if allowed is None else allowed
    if not isinstance(allowed,dict) or any(not isinstance(k,str) or not isinstance(v,str) or not re.fullmatch(r"[0-9a-fA-F]{64}",v) for k,v in allowed.items()):
        raise ISOIsolationError("La autorización requiere {ruta_ISO: SHA256_original} exacto")
    if expected_source_iso_sha256:
        with original.open("rb") as f:
            real=hashlib.file_digest(f,"sha256").hexdigest()
        if real.lower()!=expected_source_iso_sha256.lower():
            raise ISOIsolationError("Original distinto al hash autenticado")
    a,adirs=inventory(original);b,bdirs=inventory(candidate)
    if adirs!=bdirs or a.keys()!=b.keys():
        raise ISOIsolationError("Árbol de archivos/directorios ISO modificado")
    if not set(allowed).issubset(a):
        raise ISOIsolationError("Se autoriza un recurso ISO inexistente")
    modified=[];identical=0
    with original.open("rb") as fa, candidate.open("rb") as fb:
        for name in sorted(a):
            old=_hash_member(fa,*a[name]);new=_hash_member(fb,*b[name])
            if name in allowed and old!=allowed[name].lower():
                raise ISOIsolationError("Hash fuente no coincide: "+name)
            if old!=new:
                if name not in allowed:
                    raise ISOIsolationError("Recurso no autorizado modificado: "+name)
                modified.append({"recurso":name,"hash_origen":old,"hash_destino":new,"tamano_original":a[name][1],"tamano_candidato":b[name][1]})
            else:identical+=1
    return {"estado":"AISLAMIENTO_RECURSOS_APROBADO_NO_PPSSPP",
            "archivos_comparados":len(a),"directorio_igual":True,
            "recursos_idénticos":identical,"recursos_modificados_autorizados":modified,
            "nota":"No verifica datos sin entrada ISO ni la estructura interior de archivos autorizados ni el juego ejecutado."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",required=True,type=Path)
    p.add_argument("--iso-candidata",required=True,type=Path)
    p.add_argument("--hash-original-iso")
    p.add_argument("--allow-json",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    allow=json.loads(args.allow_json.read_text(encoding="utf-8")) if args.allow_json else None
    result=verify(args.iso_original,args.iso_candidata,allow,args.hash_original_iso)
    output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:print(output)

if __name__=="__main__":main()
