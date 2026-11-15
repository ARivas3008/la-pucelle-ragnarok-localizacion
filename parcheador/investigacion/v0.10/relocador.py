#!/usr/bin/env python3
"""Reubicador experimental y verificable de las tablas talk de La Pucelle: Ragnarok.

IMPORTANTE: valida la tabla principal, no garantiza que el motor carezca de
referencias internas en el bytecode. NO es una aprobación de jugabilidad.
No contiene archivos del juego ni su traducción.
"""
from dataclasses import dataclass
from bisect import bisect_right
from pathlib import Path
import struct


class RelocacionError(ValueError):
    pass


@dataclass(frozen=True)
class Edicion:
    # Offset absoluto de la primera letra, no del opcode de presentación.
    offset: int
    antiguo: bytes
    nuevo: bytes


class TablaTalk:
    """Tabla [count u32][count u32][count * (8 x u32)] + bytecode.

    El primer campo de cada registro es un desplazamiento relativo al bytecode.
    Los otros siete campos se preservan; todavía no se ha demostrado su función.
    """
    def __init__(self, datos: bytes):
        self.datos = bytes(datos)
        if len(datos) < 40:
            raise RelocacionError('Recurso talk demasiado corto')
        n, n2 = struct.unpack_from('<II', datos)
        if not (1 <= n <= 10000 and n == n2):
            raise RelocacionError('Cabecera talk no reconocida')
        self.cuenta = n
        self.base = 8 + n * 32
        if self.base > len(datos):
            raise RelocacionError('Tabla talk truncada')
        self.punteros = [struct.unpack_from('<I',datos,8+i*32)[0] for i in range(n)]
        fin = len(datos) - self.base
        if self.punteros[0] != 0 or self.punteros[-1] > fin or any(a>b for a,b in zip(self.punteros,self.punteros[1:])):
            raise RelocacionError('Los punteros principales no son monótonos/válidos')

    def aplicar(self, cambios: list[Edicion]):
        """Sustituye cadenas NUL y recalcula TODOS los punteros de entradas.

        Si una entrada apunta dentro de la región modificada se rechaza. Se
        devuelven los offsets nuevos de las ediciones para poder revertirlas.
        """
        if not cambios:
            return self.datos, []
        cambios=sorted(cambios,key=lambda x:x.offset)
        ult=self.base
        deltas=[]
        offsets=[]
        body=self.datos[self.base:]
        partes=[]
        pos=0
        delta=0
        for ed in cambios:
            if not ed.antiguo or not ed.nuevo:
                raise RelocacionError('Texto vacío: no es una traducción válida')
            if b'\x00' in ed.antiguo or b'\x00' in ed.nuevo:
                raise RelocacionError('NUL interior: fuera de la gramática de cadena')
            if ed.offset < self.base or ed.offset >= len(self.datos):
                raise RelocacionError('Offset fuera del área de bytecode')
            if ed.offset < ult:
                raise RelocacionError('Colisión entre dos cadenas editadas')
            fin=ed.offset+len(ed.antiguo)
            if self.datos[ed.offset:fin] != ed.antiguo or fin>=len(self.datos) or self.datos[fin] != 0:
                raise RelocacionError('Texto original o terminador no coincide')
            if self.datos[ed.offset-1] != 1:
                raise RelocacionError('El texto no comienza después del opcode 0x01')
            start_rel=ed.offset-self.base
            end_rel=fin+1-self.base
            idx=bisect_right(self.punteros,start_rel)
            if idx < len(self.punteros) and self.punteros[idx] < end_rel:
                raise RelocacionError('Una entrada apunta dentro de la cadena editada')
            partes.append(body[pos:start_rel]);partes.append(ed.nuevo+b'\x00')
            offsets.append(ed.offset+delta)
            diff=len(ed.nuevo)-len(ed.antiguo)
            delta+=diff
            deltas.append((end_rel,diff))
            pos=end_rel
            ult=fin+1
        partes.append(body[pos:])
        reconstruido=bytearray(self.datos[:self.base]+b''.join(partes))
        cambios_acumulados=[]
        shift=0
        for end_rel,diff in deltas:
            shift+=diff
            cambios_acumulados.append((end_rel,shift))
        ends=[x[0] for x in cambios_acumulados]
        for i,ptr in enumerate(self.punteros):
            ix=bisect_right(ends,ptr)-1
            nuevo_ptr=ptr+(cambios_acumulados[ix][1] if ix>=0 else 0)
            if not 0<=nuevo_ptr<=0xffffffff:
                raise RelocacionError('Overflow de u32 al mover punteros')
            struct.pack_into('<I',reconstruido,8+32*i,nuevo_ptr)
        verificada=TablaTalk(reconstruido)
        if verificada.cuenta != self.cuenta or len(reconstruido)!=len(self.datos)+delta:
            raise RelocacionError('Verificación estructural de desplazamientos fallida')
        # Reconstrucción exacta inversa: prueba fuerte de que sólo cambió lo esperado.
        reversas=[Edicion(p,e.nuevo,e.antiguo) for p,e in zip(offsets,cambios)]
        # La inversa trabaja sobre una nueva tabla, sin ejecutar una recursión.
        if _restaurar_exactamente(verificada,reversas)!=self.datos:
            raise RelocacionError('La reconstrucción reversible no coincide byte a byte')
        return bytes(reconstruido), offsets


def _restaurar_exactamente(tabla, cambios):
    """Escritura inversa de cuerpo+tabla sin verificación recursiva."""
    if not cambios:return tabla.datos
    cambios=sorted(cambios,key=lambda x:x.offset)
    part=[];pos=0;cor=0;deltas=[]
    body=tabla.datos[tabla.base:]
    for ed in cambios:
        start=ed.offset-tabla.base
        end=start+len(ed.antiguo)+1
        if body[start:end]!=ed.antiguo+b'\x00':raise RelocacionError('Reversión: cadena no coincide')
        part += [body[pos:start],ed.nuevo+b'\x00']
        pos=end;d=len(ed.nuevo)-len(ed.antiguo);cor+=d;deltas.append((end,cor))
    part.append(body[pos:])
    out=bytearray(tabla.datos[:tabla.base]+b''.join(part))
    boundaries=[p for p,_ in deltas]
    for i,ptr in enumerate(tabla.punteros):
        ix=bisect_right(boundaries,ptr)-1
        newptr=ptr+(deltas[ix][1] if ix>=0 else 0)
        struct.pack_into('<I',out,8+32*i,newptr)
    return bytes(out)


def iso_vista(path):
    """Resumen estructural de todos los talk de una carpeta extraída."""
    lines=[]
    for p in sorted(Path(path).glob('talk*.dat')):
        t=TablaTalk(p.read_bytes())
        lines.append({'archivo':p.name,'entradas':t.cuenta,'cabecera_bytes':t.base,
                      'bytes_codigo':len(t.datos)-t.base,'ultimo_puntero':t.punteros[-1]})
    return lines
