"""Traduce únicamente rótulos narrativos verificados en script00.dat.

NO reescribe un vídeo, no modifica 'Now Loading' y no mueve instrucciones:
reemplaza bytes dentro de una cadena existente de longitud fija + NUL.
El fragmento de la apertura «これは、いにしえより...», visto en PPSSPP,
NO está localizado como cadena editable y no está cubierto por este módulo.
"""
from dataclasses import dataclass
from hashlib import sha256
from fuentes_es import encode_es

SOURCE_HASH = '56caeda08675a6a551407dd68bddda5fe6063ab37102579996b3442cbe62e2ed'

@dataclass(frozen=True)
class Caption:
    off: int
    prefix: bytes
    source: str
    target: str

# Script de cierre/epílogo: son 4 fragmentos que el motor ya dibuja.
# La traducción es editorial y abreviada dentro de los límites del ejecutable.
CAPTIONS = (
    Caption(900853, b'\x00\x32\x31', 'これは、のちに\u3000すべての大魔王を\u3000その配下に置き',
            'Una joven someterá a los grandes demonios'),
    Caption(900907, b'\x00\x32\x23', '『統一大魔王』と呼ばれることになる',
            'y será llamada Soberana Suprema'),
    Caption(900947, b'\x00\x32\x13', '一人の少女の物語。',
            'Su historia.'),
    Caption(901012, b'\x00\x32\x2d', '物語は語り継がれゆき、そして伝説となる───',
            'Su historia perdurará como leyenda...'),
)

class CaptionError(ValueError): pass

def aplicar(raw, miembros_originales=None):
    """Patch un script en modo transaccional (retorna copia y auditoría).
    No parchea si el recurso no coincide exactamente con el de la ISO verificada.
    """
    raw=bytes(raw)
    if sha256(raw).hexdigest()!=SOURCE_HASH:
        raise CaptionError('script00.dat de ISO con hash diferente: se deja sin modificar')
    patched=bytearray(raw); audit=[]; zones=[]
    for caption in CAPTIONS:
        src=caption.source.encode('cp932')
        dest=encode_es(caption.target)
        a=caption.off;b=a+len(src)
        if raw[a-len(caption.prefix):a]!=caption.prefix:
            raise CaptionError('Prefijo de instrucción distinto en offset '+str(a))
        if raw[a:b]!=src or raw[b]!=0:
            raise CaptionError('Texto o NUL distinto en offset '+str(a))
        if raw.count(src)!=1:
            raise CaptionError('El fragmento no es único: '+caption.source)
        if len(dest)>len(src):
            raise CaptionError(f'La traducción rebasa {len(src)} bytes en offset {a}')
        if any(not (b<=x or a>=y) for x,y in zones):
            raise CaptionError('Solapamiento de fragmentos de script')
        patched[a:b]=dest.ljust(len(src),b' ')
        zones.append((a,b))
        audit.append({'offset':a,'original':caption.source,'es':caption.target,
                      'capacidad_bytes':len(src),'texto_bytes':len(dest),
                      'estado':'APLICADO_SCRIPT_VERIFICADO'})
    if len(patched)!=len(raw):raise CaptionError('Se alteró el tamaño del script')
    for a,b in zones:
        if patched[b]!=0:raise CaptionError('Se modificó un terminador NUL')
    for i,(old,new) in enumerate(zip(raw,patched)):
        if old!=new and not any(a<=i<b for a,b in zones):
            raise CaptionError('Se modificó byte de instrucción fuera de las zonas')
    return patched,audit


def comprobar_no_pmf(texto):
    """No presupone que un subtítulo esté en el script solo por verse encima de vídeo."""
    return texto in {c.source for c in CAPTIONS}
