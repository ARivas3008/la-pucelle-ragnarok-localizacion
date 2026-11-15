#!/usr/bin/env python3
"""Reconstrucción reversible de índices NISPACK y START.DAT, sin copiar juegos."""
import struct
from pathlib import Path

class FormatoError(ValueError):pass

def entradas_nispack(data):
    if data[:8]!=b'NISPACK\x00':raise FormatoError('No NISPACK')
    flag=struct.unpack_from('<I',data,8)[0]
    if flag not in (0,1):raise FormatoError('Endianness inválida')
    endian='>' if flag else '<'
    n=struct.unpack_from(endian+'I',data,12)[0]
    if not 1<=n<=200:raise FormatoError('Número de miembros inválido')
    out=[]
    for i in range(n):
        loc=16+44*i
        name,off,size,aux=struct.unpack_from(endian+'32sIII',data,loc)
        name=name.partition(b'\0')[0].decode('cp932')
        if off+size>len(data):raise FormatoError('Miembro fuera de límites')
        out.append((name,off,size,aux,loc))
    if len(set(x[0] for x in out))!=n:raise FormatoError('Nombres repetidos')
    if any(x[1]%2048 for x in out):raise FormatoError('Alineación no reconocida')
    if out[0][1]<16+44*n:raise FormatoError('Índice y contenido solapados')
    return endian,out

def reconstruir_nispack(data,cambios):
    if not cambios:return data
    endian,ls=entradas_nispack(data)
    if not set(cambios).issubset({x[0] for x in ls}):raise FormatoError('Miembros desconocidos')
    out=bytearray(data[:ls[0][1]])
    for i,(name,off,size,aux,loc) in enumerate(ls):
        if len(out)%2048:out+=b'\x00'*(2048-len(out)%2048)
        new_off=len(out);blob=cambios.get(name,data[off:off+size])
        if not isinstance(blob,bytes):raise FormatoError('Miembro no es bytes')
        out+=blob
        struct.pack_into(endian+'III',out,loc+32,new_off,len(blob),aux)
    _,check=entradas_nispack(out)
    if any(out[e[1]:e[1]+e[2]]!=cambios.get(e[0],data[next(x[1] for x in ls if x[0]==e[0]):next(x[1]+x[2] for x in ls if x[0]==e[0])]) for e in check):
        raise FormatoError('Validación de contenido falló')
    return bytes(out)

def entradas_dat(raw):
    if len(raw)<20:raise FormatoError('DAT demasiado corto')
    n=struct.unpack_from('<I',raw)[0]
    if not (1<=n<=300 and 16+32*n<=len(raw)):raise FormatoError('DAT no reconocido')
    base=16+32*n;pos=base;rows=[]
    for i in range(n):
        loc=16+32*i
        end=base+struct.unpack_from('<I',raw,loc)[0]
        name=raw[loc+4:loc+32].partition(b'\x00')[0].decode('cp932')
        if end<pos or end>len(raw):raise FormatoError('DAT archivo fuera de rango')
        rows.append((name,pos,end,loc));pos=end
    if pos!=len(raw):raise FormatoError('DAT no cubre todos los bytes')
    return rows

def reconstruir_dat(data,cambios):
    if not cambios:return data
    rows=entradas_dat(data)
    if not set(cambios).issubset({x[0] for x in rows}):raise FormatoError('Miembros DAT desconocidos')
    base=16+32*len(rows)
    out=bytearray(data[:base])
    for name,start,end,loc in rows:
        blob=cambios.get(name,data[start:end])
        if not isinstance(blob,bytes):raise FormatoError('DAT miembro no es bytes')
        out+=blob
        struct.pack_into('<I',out,loc,len(out)-base)
    new_rows=entradas_dat(out)
    if any(out[s:e]!=cambios.get(name,data[rows[i][1]:rows[i][2]]) for i,(name,s,e,loc) in enumerate(new_rows)):
        raise FormatoError('Validación DAT falló')
    return bytes(out)
