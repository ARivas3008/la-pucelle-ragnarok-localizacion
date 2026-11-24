"""Inserta exclusivamente nombres aprobados fuera del manifiesto, en slots fijos."""
import csv,hashlib
from pathlib import Path

SOURCE_SHA='6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c'
RESOURCE='ISO_START/name.dat'

def aplicar(original,current,manifest,sidecar,missing_glyphs):
    raw=bytes(original['name.dat']);dest=bytes(current['name.dat'])
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA or len(dest)!=len(raw):
        raise ValueError('name.dat fuente o longitud distinta')
    known={int(r['offset']) for r in manifest if r['recurso']==RESOURCE}
    with Path(sidecar).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=17:raise ValueError('Se esperaban 17 slots adicionales')
    edits=[];preserved=[];seen=set();result=bytearray(dest)
    for row in rows:
        off=int(row['offset']);kind=int(row['clase']);uid=row['id']
        if (row['recurso']!=RESOURCE or row['sha256_recurso']!=SOURCE_SHA or uid!=f'GNAME-ISO-{off}'
            or off in seen or off in known or off<12 or (off-12)%16 or off+12>len(raw)
            or kind not in (1,2,3) or raw[off-2:off]!=bytes((1,kind))
            or dest[off-4:off]!=raw[off-4:off]):
            raise ValueError('Ancla nominal inválida: '+uid)
        seen.add(off);before=raw[off:off+12];old=row['original'].encode('cp932')
        if not old or len(old)>=12 or before!=old.ljust(12,b'\0'):
            raise ValueError('Texto o reserva original distinta: '+uid)
        text=row['es_propuesta'];state=row['estado']
        if state=='conservar_simbolo':
            if text!=row['original'] or dest[off:off+12]!=before:
                raise ValueError('Símbolo original alterado: '+uid)
            preserved.append(uid);continue
        if state!='revisado_editorial_fuera_manifiesto' or not text or not text.isascii() or not text.isalpha():
            raise ValueError('Adaptación nominal no aprobada o no ASCII: '+uid)
        data=text.encode('ascii');after=data.ljust(12,b'\0')
        if len(data)>11 or missing_glyphs(text,current) or dest[off:off+12] not in (before,after):
            raise ValueError('Capacidad, glifo o conflicto de revisión: '+uid)
        result[off:off+12]=after
        edits.append(dict(id=uid,recurso=RESOURCE,offset=off,clase=kind,antes_hex=before.hex(),despues_hex=after.hex(),es=text))
    if len(edits)!=10 or len(preserved)!=7:raise ValueError('Inventario nominal incompleto')
    current['name.dat']=result
    return dict(aplicados=edits,conservados=preserved,sha256_origen=SOURCE_SHA,
                sha256_destino=hashlib.sha256(result).hexdigest(),fuera_manifiesto=True)
