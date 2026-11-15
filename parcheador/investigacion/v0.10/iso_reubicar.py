#!/usr/bin/env python3
"""Reubica un archivo ISO9660 al final de una COPIA, sin tocar el original.

Se comprueban el descriptor primario, el registro de directorio y el contenido
relocado. Esto no constituye una prueba de carga en PPSSPP.
"""
from pathlib import Path
import os,shutil,struct
from dataclasses import dataclass

SECTOR=2048
class IsoError(ValueError):pass

@dataclass
class Registro:
    ruta: str
    offset: int
    size: int
    entrada: int


def recorrer(fp):
    fp.seek(16*SECTOR)
    pvd=fp.read(SECTOR)
    if pvd[0]!=1 or pvd[1:6]!=b'CD001' or pvd[6]!=1:
        raise IsoError('No ISO9660 simple con descriptor primario')
    if pvd[156]==0:raise IsoError('No hay raíz ISO')
    root=pvd[156:156+pvd[156]]
    records=[];vistos=set()
    def from_record(rec):
        if len(rec)<34:raise IsoError('Registro ISO truncado')
        lba=struct.unpack_from('<I',rec,2)[0]
        sz=struct.unpack_from('<I',rec,10)[0]
        if lba!=struct.unpack_from('>I',rec,6)[0] or sz!=struct.unpack_from('>I',rec,14)[0]:
            raise IsoError('Campos ISO endian inconsistente')
        n=rec[32]
        name=rec[33:33+n].decode('ascii','strict').split(';')[0]
        return name,lba*SECTOR,sz,bool(rec[25]&2)
    def walk(rec,prefix):
        _,start,size,_=from_record(rec)
        if start in vistos:raise IsoError('Bucle en árbol de directorios')
        vistos.add(start)
        if start+size>os.fstat(fp.fileno()).st_size:raise IsoError('Directorio fuera de ISO')
        fp.seek(start);d=fp.read(size)
        i=0
        while i<len(d):
            ln=d[i]
            if ln==0:i=(i//SECTOR+1)*SECTOR;continue
            if i+ln>len(d):raise IsoError('Directorio truncado')
            dat=d[i:i+ln];off=start+i;i+=ln
            name,sector,sz,isdir=from_record(dat)
            if name in ('\0','\1'):continue
            full=prefix+'/'+name
            records.append(Registro(full,sector,sz,off))
            if isdir:walk(dat,full)
    walk(root,'')
    return records


def anexar_recurso(origen,salida,ruta,reemplazo: bytes):
    origen=Path(origen);salida=Path(salida)
    if origen.resolve()==salida.resolve():raise IsoError('Nunca modificar el original')
    if not isinstance(reemplazo,bytes) or len(reemplazo)<1:raise IsoError('Reemplazo inválido')
    if not origen.is_file():raise IsoError('Falta ISO')
    salida.parent.mkdir(parents=True,exist_ok=True)
    try:
        shutil.copyfile(origen,salida)
        with salida.open('r+b') as fp:
            recs=recorrer(fp)
            rec=[x for x in recs if x.ruta==ruta]
            if len(rec)!=1:raise IsoError('Recurso inexistente o ambiguo')
            entry=rec[0]
            fp.seek(0,2);final=fp.tell()
            newoff=((final+SECTOR-1)//SECTOR)*SECTOR
            if newoff!=final:fp.write(b'\0'*(newoff-final))
            fp.write(reemplazo)
            if fp.tell()%SECTOR:fp.write(b'\0'*(SECTOR-fp.tell()%SECTOR))
            newsector=(newoff+len(reemplazo)+SECTOR-1)//SECTOR
            if newsector >= 0xffffffff:raise IsoError('ISO demasiado grande')
            fp.seek(entry.entrada+2)
            fp.write(struct.pack('<I',newoff//SECTOR))
            fp.write(struct.pack('>I',newoff//SECTOR))
            fp.write(struct.pack('<I',len(reemplazo)))
            fp.write(struct.pack('>I',len(reemplazo)))
            fp.seek(16*SECTOR+80)
            fp.write(struct.pack('<I',newsector))
            fp.write(struct.pack('>I',newsector))
            fp.flush();os.fsync(fp.fileno())
        with salida.open('rb') as fp:
            newrec=[x for x in recorrer(fp) if x.ruta==ruta]
            if len(newrec)!=1 or newrec[0].size!=len(reemplazo):raise IsoError('Registro ISO no actualizado')
            fp.seek(newrec[0].offset)
            if fp.read(newrec[0].size)!=reemplazo:raise IsoError('Contenido reubicado no coincide')
        return {'recurso':ruta,'offset_anterior':entry.offset,'offset_nuevo':newoff,
                'bytes_anteriores':entry.size,'bytes_nuevos':len(reemplazo)}
    except Exception:
        if salida.exists():salida.unlink()
        raise
