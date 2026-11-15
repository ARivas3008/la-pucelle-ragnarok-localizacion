"""Expansión conservadora de texto dentro de campos de ancho FIJO.

Los registros no se reubican y no cambian tamaño. Solo se usan posiciones
verificadas de nombre/descripción que ya son C-strings seguidas de NUL y
relleno cero. Los bytes de estadísticas y las tablas de índices son intocables.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Campo:
    stride: int
    header: int
    comienzo: int   # Offset dentro del registro
    longitud: int   # Campo completo, incluyendo NUL

# Deducidos por repetición de offsets en los archivos originales ISO/DLC.
# Los límites son deliberadamente conservadores para no invadir metadatos.
PERFILES={
    'char.dat': (Campo(200,8,0,24),),
    'magic.dat': (Campo(116,8,18,23),Campo(116,8,41,57)),
    'mapinfo.dat': (Campo(96,8,12,28),),
    'name.dat': (Campo(16,8,4,12),),
    'kis.dat': (Campo(148,8,0,21),Campo(148,8,21,57)),
    'ritem.dat': (Campo(92,8,4,13),Campo(92,8,17,43)),
    'skill.dat': (Campo(94,8,16,21),Campo(94,8,37,57)),
    'com.dat': (Campo(92,8,0,23),Campo(92,8,23,49)),
}

class CampoError(ValueError): pass

def capacidad_verificada(resource,buf,offset,old_length):
    """Devuelve el tamaño TOTAL del campo a partir de offset, o None.

    Rechaza terminadores ausentes, relleno no cero, alineaciones extrañas,
    campos que sobrepasen el recurso o colisiones con otros datos.
    No intenta adivinar registros, saltos del script ni punteros.
    """
    res=resource.split('/')[-1].lower()
    profiles=PERFILES.get(res,())
    for c in profiles:
        if offset<c.header+c.comienzo:
            continue
        if (offset-c.header-c.comienzo)%c.stride!=0:
            continue
        start=offset;end=offset+c.longitud
        # El campo completo debe caber y el original terminar ANTES del final.
        if end>len(buf) or old_length>=c.longitud:
            continue
        if buf[start+old_length]!=0:
            continue
        # Campos de texto con relleno cero; NUNCA invadir estadísticas.
        if any(buf[start+old_length+1:end]):
            continue
        return c.longitud
    return None


def ampliar_campo(original,source_len,translated,capacity):
    """Prepara reemplazo terminado en NUL y con padding CERO.
    `translated` ya viene codificado con encode_es o cp932.
    """
    if capacity<=source_len or len(translated)+1>capacity:
        raise CampoError('no cabe el texto dentro del campo reservado')
    if not original.startswith(original[:source_len]+b'\x00'):
        raise CampoError('falta terminador NUL')
    if len(original)!=capacity or any(original[source_len+1:]):
        raise CampoError('el relleno no está vacío')
    return translated+b'\x00'*(capacity-len(translated))
