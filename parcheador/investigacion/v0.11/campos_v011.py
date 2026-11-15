"""Byte-exact fixed-field layouts for non-dialogue DAT resources.

These layouts were inferred from repeated offsets and checked against the
ISO + DLC binary records. Each capacity includes the NUL terminator.
They preserve all metadata outside each string field. A syntactic field match
is not proof of visible width, ownership, or engine behavior.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class Campo:
    stride:int
    header:int
    comienza:int
    longitud:int

PERFILES={
 'char.dat':(Campo(200,8,0,24),),
 'magic.dat':(Campo(116,8,18,23),Campo(116,8,41,57)),
 'mapinfo.dat':(Campo(96,8,12,28),),
 'name.dat':(Campo(16,8,4,12),),
 'kis.dat':(Campo(148,8,0,21),Campo(148,8,21,57)),
 'ritem.dat':(Campo(92,8,4,13),Campo(92,8,17,43)),
 'skill.dat':(Campo(94,8,16,21),Campo(94,8,37,57)),
 'com.dat':(Campo(92,8,0,23),Campo(92,8,23,49)),
}
class CampoError(ValueError):pass

def locate(resource, buf, off, old):
    name=resource.rsplit('/',1)[-1].lower()
    for c in PERFILES.get(name,()):
        if off<c.header+c.comienza or (off-c.header-c.comienza)%c.stride!=0:
            continue
        if off+c.longitud>len(buf) or len(old)>=c.longitud:continue
        if buf[off:off+len(old)+1]!=old+b'\0':continue
        if any(buf[off+len(old)+1:off+c.longitud]):continue
        return c
    return None

def replace(buf,off,old,new,resource):
    """Return an independent full binary; never overwrite input."""
    c=locate(resource,buf,off,old)
    if c is None:raise CampoError('Schema, original, NUL, or zero padding mismatch')
    if b'\0' in new or not new or len(new)+1>c.longitud:
        raise CampoError('Invalid new text or fixed field overflow')
    out=bytearray(buf)
    out[off:off+c.longitud]=new+b'\0'*(c.longitud-len(new))
    if out[:off]!=buf[:off] or out[off+c.longitud:]!=buf[off+c.longitud:]:
        raise CampoError('Unexpected surrounding-byte change')
    return bytes(out)

def reemplazar_en_hueco_original(buf, off, old, new):
    """Fallback extremadamente conservador para campos con metadatos adyacentes.

    No supone que el espacio hasta el proximo registro sea utilizable.
    Se limita a los bytes que ya ocupaba la cadena de origen y conserva en su
    sitio el terminador NUL y TODOS los bytes posteriores, incluso el metadata.
    """
    if not old or not new or b'\x00' in new or len(new)>len(old):
        raise CampoError('La traduccion no cabe en los bytes de la cadena de origen')
    if off<0 or off+len(old)>=len(buf):
        raise CampoError('Fuera del archivo')
    if buf[off:off+len(old)+1] != old+b'\x00':
        raise CampoError('Fuente o terminador distinto')
    out=bytearray(buf)
    out[off:off+len(old)]=new.ljust(len(old),b'\x00')
    if out[off+len(old):]!=buf[off+len(old):]:
        raise CampoError('Se ha alterado el resto del registro')
    return bytes(out)
