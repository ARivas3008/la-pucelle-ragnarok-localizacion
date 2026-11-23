#!/usr/bin/env python3
"""Relocalizador experimental de scripts 0x32 con anclas de carácter.

El índice principal contiene referencias a posiciones interiores del texto. Las
alineamos a límites CP932 equivalentes en la traducción. Esto NO certifica el
comportamiento de las escenas: podrían representar tiempo o sincronización.
El archivo original puede recuperarse byte por byte mediante un diario.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,struct,json
from pathlib import Path
from bisect import bisect_right

class ReubicacionInsegura(ValueError):pass
@dataclass(frozen=True)
class Edicion:
    offset:int
    antes:bytes
    despues:bytes
    unit_id:str=''

def limites_cp932(data):
    """Devuelve los límites de los caracteres y el final, en bytes."""
    result=[0];p=0
    while p<len(data):
        b=data[p]
        if b<0x80 or 0xA1<=b<=0xDF:step=1
        elif 0x81<=b<=0x9F or 0xE0<=b<=0xFC:
            if p+1>=len(data) or not(0x40<=data[p+1]<=0xFC and data[p+1]!=0x7F):
                raise ReubicacionInsegura('Par CP932/gaiji incompleto')
            step=2
        else:raise ReubicacionInsegura(f'Código de texto inesperado {b:02x}')
        p+=step;result.append(p)
    return result

class Reubicador:
    def __init__(self,original,permitir_subcaracter=False,preservar_fase=False):
        if permitir_subcaracter and preservar_fase:
            raise ReubicacionInsegura('Selecciona una sola política subcarácter')
        self.permitir_subcaracter=permitir_subcaracter
        self.preservar_fase=preservar_fase
        self.original=bytes(original)
        if len(self.original)<20:raise ReubicacionInsegura('Script demasiado corto')
        self.n=struct.unpack_from('<I',self.original)[0]
        # EBOOT original, 0x08844e88..0x08844ec0: count, N offsets,
        # N identificadores y después bytecode. La versión antigua confundía
        # la tabla de IDs con instrucciones y desplazaba las entradas mal.
        self.body=4+8*self.n
        if not (1<=self.n<=50000 and self.body<len(self.original)):
            raise ReubicacionInsegura('Tabla truncada')
        self.pointers=list(struct.unpack_from(f'<{self.n}I',self.original,4))
        self.identifiers=list(struct.unpack_from(f'<{self.n}I',self.original,4+4*self.n))
        if self.pointers[0]!=0 or any(a>b for a,b in zip(self.pointers,self.pointers[1:])) or self.pointers[-1]>len(self.original)-self.body:
            raise ReubicacionInsegura('Índice inválido')

    def aplicar(self,ediciones):
        ls=sorted(ediciones,key=lambda e:e.offset)
        if not ls:return self.original, {'ediciones':[],'anclas':[]}
        previous=self.body;data=[];start_offset=self.body
        events=[];anclas=[];total=0;new_offs=[];corrigidas=[];fase_conservada=[]
        for e in ls:
            off=e.offset;old=e.antes;new=e.despues
            if not old or not new or b'\0' in old+new:
                raise ReubicacionInsegura('Cadenas vacías/NUL internos')
            if off-2<previous or off+len(old)>=len(self.original):
                raise ReubicacionInsegura('Intervalos solapados/fuera de límites')
            if (self.original[off-2]!=0x32 or self.original[off-1]!=len(old)+1
                or self.original[off:off+len(old)+1]!=old+b'\x00'):
                raise ReubicacionInsegura(f'Fuente u opcode distinto en {off}')
            if len(new)+1>255:raise ReubicacionInsegura('La cadena excede la longitud de opcode 0x32')
            before_limits=limites_cp932(old);after_limits=limites_cp932(new)
            old_start=off-self.body;old_end=old_start+len(old)+1
            inside=[]
            for i,p in enumerate(self.pointers):
                if old_start<=p<old_end:
                    rel=p-old_start
                    if rel==len(old):destination=len(new) # terminador
                    else:
                        if rel not in before_limits and self.preservar_fase:
                            # v0.16: ensayar segundo byte -> segundo byte, sin
                            # fingir que conocemos la semántica del índice.
                            char_index=bisect_right(before_limits,rel)-1
                            phase=rel-before_limits[char_index]
                            if phase!=1:
                                raise ReubicacionInsegura('Fase CP932 desconocida')
                            ideal=round(char_index*(len(after_limits)-2)/max(1,len(before_limits)-2))
                            options=sorted((abs(j-ideal),j)
                                for j in range(len(after_limits)-1)
                                if after_limits[j+1]-after_limits[j]>phase)
                            if not options or options[0][0]>2:
                                raise ReubicacionInsegura(
                                    f'Puntero #{i}: no hay segundo byte CP932 '
                                    f'equivalente a distancia <=2 caracteres')
                            distance,j=options[0]
                            destination=after_limits[j]+phase
                            fase_conservada.append({'indice':i,'offset_fuente':off,
                                'byte_origen':rel,'byte_destino':destination,
                                'distancia_en_caracteres':distance,'fase':phase})
                        else:
                            if rel not in before_limits:
                                if not self.permitir_subcaracter:
                                    raise ReubicacionInsegura(f'Puntero #{i} cae dentro de carácter CP932 en {off}')
                                # Compatibilidad con el ensayo v0.12; NO aprobado.
                                candidates=[v for v in before_limits if v<rel]
                                if not candidates:raise ReubicacionInsegura('No existe carácter anterior')
                                old_rel=rel;rel=max(candidates)
                                corrigidas.append({'indice':i,'offset_fuente':off,'byte_anterior':old_rel,'char_inicio':rel})
                            char_index=before_limits.index(rel)
                            mapped_index=round(char_index*(len(after_limits)-1)/(len(before_limits)-1))
                            destination=after_limits[mapped_index]
                    inside.append((i,p,old_start+total+destination))
            data.extend([self.original[previous:off-1],bytes([len(new)+1]),new,b'\0'])
            new_off=off+total;new_offs.append(new_off)
            difference=len(new)-len(old)
            events.append({'offset':off,'old_end':old_end,'delta_before':total,'delta_after':total+difference,
                           'antes_hex':old.hex(),'despues_hex':new.hex(),'new_offset':new_off,'unit_id':e.unit_id})
            anclas.extend([{'indice':idx,'antes':p,'despues':v,'unit_id':e.unit_id} for idx,p,v in inside])
            total+=difference;previous=off+len(old)+1
        data.append(self.original[previous:]);body=b''.join(data)
        out=bytearray(self.original[:self.body]+body)
        ends=[e['old_end'] for e in events]
        anchor_by_idx={x['indice']:x['despues'] for x in anclas}
        for i,p in enumerate(self.pointers):
            if i in anchor_by_idx:
                newp=anchor_by_idx[i]
            else:
                index=bisect_right(ends,p)-1
                offset=events[index]['delta_after'] if index>=0 else 0
                newp=p+offset
            if not 0<=newp<=len(out)-self.body:
                raise ReubicacionInsegura(f'Puntero fuera de rango #{i}')
            struct.pack_into('<I',out,4+4*i,newp)
        result=bytes(out)
        review=Reubicador(result)
        if review.n!=self.n or len(result)!=len(self.original)+total:
            raise ReubicacionInsegura('No se puede analizar el script reconstruido')
        journal={'sha256_original':hashlib.sha256(self.original).hexdigest(),
                 'sha256_modificado':hashlib.sha256(result).hexdigest(),
                 'tabla_original':self.original[4:self.body].hex(),
                 'ediciones':events,'anclas':anclas,'anclas_reubicadas':len(anclas),
                 'anclas_subcaracter_corregidas_experimentalmente':corrigidas,
                 'anclas_subcaracter_fase_conservada':fase_conservada}
        assert self.revertir(result,journal)==self.original, 'La reversión no coincide byte a byte'
        return result,journal

    @staticmethod
    def revertir(modificado,diario):
        if hashlib.sha256(modificado).hexdigest()!=diario['sha256_modificado']:
            raise ReubicacionInsegura('El archivo modificado no coincide con el diario')
        body=4+len(bytes.fromhex(diario['tabla_original']))
        edits=diario['ediciones']
        pieces=[];pos=body
        for e in edits:
            off=e['new_offset'];old=bytes.fromhex(e['antes_hex']);new=bytes.fromhex(e['despues_hex'])
            if modificado[off-2:off+len(new)+1]!=b'\x32'+bytes([len(new)+1])+new+b'\0':
                raise ReubicacionInsegura('Fragmento modificado no coincide')
            pieces.extend([modificado[pos:off-1],bytes([len(old)+1]),old,b'\0'])
            pos=off+len(new)+1
        pieces.append(modificado[pos:])
        original=modificado[:4]+bytes.fromhex(diario['tabla_original'])+b''.join(pieces)
        if hashlib.sha256(original).hexdigest()!=diario['sha256_original']:
            raise ReubicacionInsegura('La reversión de script falla')
        return original
