#!/usr/bin/env python3
"""Extensión experimental, reversible y de tamaño fijo de fontB PSP.

La codificación es interna al juego: **no** se afirma compatibilidad automática
con el decodificador del EBOOT, que requiere prueba en hardware/PPSSPP.
No necesita Pillow para parchear; Pillow solo para vista previa opcional.
"""
from __future__ import annotations
import hashlib
import string
import struct
import unicodedata
from collections import Counter

W=512
H=512
CELDA=14
COLUMNAS=36
FILAS=36
CAPACIDAD=COLUMNAS*FILAS
TXP_SIZE=132112
DATA_OFFSET=1040
META_COUNT=11616
FONT_SIZE=META_COUNT*2
# Orden estable: no cambiar sin migrar las cadenas publicadas.
EXTRAS=(
    'áéíóúÁÉÍÓÚñÑüÜ¿¡«»'
    'àèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöÄËÏÖŸ'
    'çÇōūŌŪºª©†♀♂–—‘’“”'
)
EXTRAS=''.join(dict.fromkeys(EXTRAS))
# F0 es parte de los códigos definidos por usuario de Shift-JIS. No se cambia
# ninguna asignación ya existente y se comprueban las ranuras libres.
GAIJI_LEAD=0xF0
GAIJI_TRAILS=tuple(list(range(0x40,0x7F))+list(range(0x80,0xFD)))
if len(EXTRAS)>len(GAIJI_TRAILS):raise RuntimeError('Rango de caracteres insuficiente')
CODIGOS={c:bytes([GAIJI_LEAD,GAIJI_TRAILS[i]]) for i,c in enumerate(EXTRAS)}

class FontError(ValueError):pass


def index_sjis(pair):
    if len(pair)==1:
        i=pair[0]-31
        if i<1 or i>=96:raise FontError('ASCII fuera del mapeo fontB')
        return i
    if len(pair)!=2:raise FontError('Se necesitan uno o dos bytes')
    a,b=pair
    if not ((0x81<=a<=0x9F) or (0xE0<=a<=0xFC)) or not (0x40<=b<=0xFC):
        raise FontError(f'Par Shift-JIS no válido: {pair.hex()}')
    lead_index=a-0x81 if a<=0x9F else 31+a-0xE0
    i=96+lead_index*192+(b-0x40)
    if i>=META_COUNT:raise FontError('Índice fuera de fnt')
    return i


def encode_es(s):
    """UTF-8/Unicode a bytes de fuente PSP extendida; sin degradar tildes.

    Solo los caracteres en EXTRAS se convierten a códigos privados; todos los
    demás se codifican con CP932 original. No toca marcadores ni escapes.
    """
    out=bytearray()
    for c in s:
        if c in CODIGOS:out+=CODIGOS[c]
        else:
            try:out+=c.encode('cp932')
            except UnicodeError as e:raise FontError(f'No hay glifo/codec para U+{ord(c):04X} {c!r}') from e
    return bytes(out)


def decode_es(data):
    rev={v:k for k,v in CODIGOS.items()}
    out=[];i=0
    while i<len(data):
        if data[i]==GAIJI_LEAD and i+1<len(data) and data[i:i+2] in rev:
            out.append(rev[data[i:i+2]]);i+=2
        else:
            # separa Shift JIS sin consumir bytes posteriores por error
            if data[i]<0x80 or 0xA1<=data[i]<=0xDF:
                n=1
            else:n=2
            try:out.append(data[i:i+n].decode('cp932'))
            except UnicodeError as e:raise FontError(f'No se puede decodificar byte en {i}') from e
            i+=n
    return ''.join(out)


def unpack_pixels(raw):
    if len(raw)!=TXP_SIZE or raw[:4]!=b'\x00\x02\x00\x02':
        raise FontError('Textura fontB inesperada (cabecera/tamaño); no modificar')
    d=raw[DATA_OFFSET:]
    if len(d)!=512*512//2:raise FontError('Atlas de tamaño no esperado')
    pixels=bytearray(W*H)
    for by in range(64):
        for bx in range(16):
            bo=(by*16+bx)*128
            for yy in range(8):
                base=(by*8+yy)*W+bx*32
                off=bo+yy*16
                for xx in range(16):
                    b=d[off+xx]
                    pixels[base+xx*2]=b&15
                    pixels[base+xx*2+1]=b>>4
    return pixels


def pack_pixels(original,pixels):
    if len(pixels)!=W*H:raise FontError('Plano inválido')
    raw=bytearray(original)
    for by in range(64):
        for bx in range(16):
            bo=(by*16+bx)*128+DATA_OFFSET
            for yy in range(8):
                base=(by*8+yy)*W+bx*32
                off=bo+yy*16
                for xx in range(16):
                    a=pixels[base+xx*2];b=pixels[base+xx*2+1]
                    if a>15 or b>15:raise FontError('Índice de paleta fuera de rango')
                    raw[off+xx]=a|(b<<4)
    return bytes(raw)


def box_for_gid(gid):
    if gid<0 or gid>=2*CAPACIDAD:raise FontError('No hay página atlas disponible')
    page,slot=divmod(gid,CAPACIDAD)
    return page, (slot%COLUMNAS)*CELDA, (slot//COLUMNAS)*CELDA


def get_tile(atlas,gid):
    page,x,y=box_for_gid(gid)
    im=atlas[page]
    return [[im[(y+dy)*W+x+dx] for dx in range(CELDA)] for dy in range(CELDA)]


def set_tile(atlas,gid,tile,only_if_empty=True):
    page,x,y=box_for_gid(gid)
    im=atlas[page]
    if only_if_empty and any(im[(y+dy)*W+x+dx] for dy in range(CELDA) for dx in range(CELDA)):
        raise FontError(f'Ranura gid {gid} no estaba vacía')
    for dy in range(CELDA):
        for dx in range(CELDA):im[(y+dy)*W+x+dx]=tile[dy][dx]


def spanish_glyph(char,base_tile):
    """Redibuja el diacrítico sobre la misma letra del juego (14x14 4bpp).

    No se modifica la anchura ni se inventa un font externo incompatible.
    """
    t=[list(line) for line in base_tile]
    # La segunda página de las cinco fuentes usa índice 15 = opaco blanco.
    strength=15
    def pix(x,y):
        if 0<=x<14 and 0<=y<14:t[y][x]=strength
    def line(points):
        for x,y in points:pix(x,y)
    def shift_down(n):
        nonlocal t
        t=[[0]*14 for _ in range(n)]+[r[:] for r in t[:14-n]]
    decomp=unicodedata.normalize('NFD',char)
    base=decomp[0] if decomp else char
    accent=''.join(x for x in decomp[1:] if unicodedata.combining(x))
    if base in 'AEIOUN' and accent:shift_down(2)
    if accent:
        if '\u0301' in accent:line([(3,2),(4,1),(5,0)])
        elif '\u0300' in accent:line([(3,0),(4,1),(5,2)])
        elif '\u0303' in accent:line([(1,1),(2,0),(3,0),(4,1),(5,1),(6,0)])
        elif '\u0308' in accent:line([(1,0),(2,0),(5,0),(6,0)])
        elif '\u0304' in accent:line([(1,0),(2,0),(3,0),(4,0),(5,0)])
        elif '\u0302' in accent:line([(2,2),(3,1),(4,0),(5,1),(6,2)])
        elif '\u0327' in accent:line([(2,12),(3,13),(4,13)])
        else:raise FontError(f'Marca Unicode no implementada para {char!r}')
    elif char in ('¿','¡'):
        t=[list(reversed(row)) for row in reversed(t)]
    elif char in ('«','»'):
        t=[[0]*14 for _ in range(14)]
        for cx in (2,7):
            for j in range(5):
                x=cx+(4-j if char=='«' else j)
                pix(x,4+j)
                pix(x,12-j)
    elif char in ('–','—'):
        t=[[0]*14 for _ in range(14)]
        line([(x,7) for x in range(0 if char=='—' else 2,13 if char=='—' else 10)])
    elif char in ('‘','’','“','”'):
        t=[[0]*14 for _ in range(14)]
        origin=[3,7] if char in '“”' else [4]
        for x in origin:
            if char in '‘“':line([(x+1,0),(x,1),(x,2),(x+1,2)])
            else:line([(x,0),(x+1,0),(x+1,1),(x,2)])
    elif char=='†':
        t=[[0]*14 for _ in range(14)]
        line([(5,y) for y in range(1,13)]+[(x,4) for x in range(2,9)])
    elif char=='©':
        t=[[0]*14 for _ in range(14)]
        line([(x,1) for x in range(3,9)]+[(x,12) for x in range(3,9)] + [(2,y) for y in range(3,11)]+[(9,y) for y in range(3,11)]+[(x,3) for x in range(5,8)]+[(4,y) for y in range(4,10)]+[(x,10) for x in range(5,8)])
    elif char in ('♀','♂'):
        t=[[0]*14 for _ in range(14)]
        line([(x,2) for x in range(4,8)]+[(x,8) for x in range(4,8)]+[(3,y) for y in range(3,8)]+[(8,y) for y in range(3,8)])
        if char=='♀':line([(5,y) for y in range(9,14)]+[(x,11) for x in range(3,8)])
        else:line([(x,0) for x in range(9,13)]+[(12,y) for y in range(0,4)]+[(8,4),(9,3),(10,2)])
    elif char in ('º','ª'):
        t=[[0]*14 for _ in range(14)]
        line([(x,2) for x in range(3,7)]+[(x,7) for x in range(3,7)]+[(2,y) for y in range(3,7)]+[(7,y) for y in range(3,7)])
    else:
        raise FontError(f'Diseño de glifo no implementado: {char!r}')
    return t


def base_char(c):
    if c=='¿':return '？'
    if c=='¡':return '！'
    if c=='ª':return 'a'
    if c=='º':return 'o'
    if c in '©†♀♂–—‘’“”«»':return 'a' # se sustituye completamente
    return unicodedata.normalize('NFD',c)[0]


def add_spanish_fonts(members):
    """Parchea SOLO cuatro recursos fontB de un DAT descomprimido.

    Entrada: dict nombre->bytearray. Salida: informe (tamaños constantes).
    Operación idempotente cuando los glifos y slots ya fueron insertados.
    """
    names=('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')
    if any(n not in members for n in names):raise FontError('Faltan fuentes fontB')
    raw_fnt=bytes(members['fontB.fnt']);raw_ftd=bytes(members['fontB.ftd'])
    if len(raw_fnt)!=FONT_SIZE or len(raw_ftd)!=FONT_SIZE:raise FontError('Tabla fontB inesperada')
    fnt=list(struct.unpack('<11616H',raw_fnt));ftd=list(struct.unpack('<11616H',raw_ftd))
    if fnt[0]!=11615 or ftd[0]!=11615:raise FontError('Encabezado fontB desconocido')
    atlas_raw=[bytes(members[n]) for n in ('FontB0000.txp','FontB0001.txp')]
    pix=[unpack_pixels(raw) for raw in atlas_raw]
    palettes=[[raw[16+i*4:16+(i+1)*4] for i in range(16)] for raw in atlas_raw]
    # ignorar fnt[0]: es el encabezado, no un identificador de glifo.
    max_gid=max(fnt[1:]); changes=0;alias=0;add=[]
    for c,code in CODIGOS.items():
        ix=index_sjis(code)
        current=fnt[ix]
        if current:
            if not (max_gid-len(CODIGOS)+1 <= current <= max_gid):
                raise FontError(f'Ranura gaiji ya utilizada: {c} en {code.hex()}')
            continue
        base=base_char(c)
        if base not in ('a','o') or c not in 'ºª©†♀♂–—‘’“”«»':
            try:b=base.encode('cp932')
            except UnicodeError as e:raise FontError(f'Base no codificable para {c}') from e
        else:b=base.encode('cp932')
        base_idx=index_sjis(b)
        gid=fnt[base_idx]
        if not gid:raise FontError(f'Glifo base {base!r} no localizado para {c!r}')
        max_gid+=1
        if max_gid>=CAPACIDAD*2:raise FontError('Atlas de 2 páginas sin hueco para más glifos')
        src_page=box_for_gid(gid)[0]
        dst_page=box_for_gid(max_gid)[0]
        tile=get_tile(pix,gid)
        # ISO FontB0000 tiene CLUT en un orden distinto al de FontB0001.
        # Remapear RGBA al cambiar de página, evitando perder opacidad.
        if src_page!=dst_page:
            code_map={}
            for j,rgba in enumerate(palettes[src_page]):
                matches=[ix for ix,color in enumerate(palettes[dst_page]) if color==rgba]
                if not matches:raise FontError('Las paletas fontB no permiten copia de glifo sin alterar colores')
                code_map[j]=matches[0]
            tile=[[code_map[value] for value in line] for line in tile]
        tile=spanish_glyph(c,tile)
        set_tile(pix,max_gid,tile)
        fnt[ix]=max_gid
        ftd[ix]=0x0101 if c in '«»–—©†♀♂' else ftd[base_idx]
        add.append({'caracter':c,'utf8':c.encode('utf-8').hex(),'codigo':code.hex(),'gid':max_gid,'base':base,'ftd':ftd[ix]})
        changes+=1
    # Los signos ASCII faltantes no se borran: se vinculan a los fullwidth
    # idénticos cuando el juego no incluyó glifo halfwidth.
    for c in string.ascii_letters + string.digits + string.punctuation:
        ix=index_sjis(c.encode('ascii'))
        if not fnt[ix]:
            full=chr(ord(c)+0xFEE0)
            try:fi=index_sjis(full.encode('cp932'))
            except UnicodeError:continue
            if fnt[fi]:
                fnt[ix]=fnt[fi];ftd[ix]=ftd[fi];alias+=1
    changed=bool(changes or alias)
    if changed:
        members['fontB.fnt']=bytearray(struct.pack('<11616H',*fnt))
        members['fontB.ftd']=bytearray(struct.pack('<11616H',*ftd))
        for n,p in zip(('FontB0000.txp','FontB0001.txp'),pix):
            members[n]=bytearray(pack_pixels(bytes(members[n]),p))
    return {'glifos_agregados':changes,'alias_ascii':alias,'glifos':add,
            'gid_final':max_gid,'cobertura_gaiji':{k:v.hex() for k,v in CODIGOS.items()},
            'fontB_fnt_sha256':hashlib.sha256(members['fontB.fnt']).hexdigest()}


def missing_render_glyphs(text,members):
    """Comprueba cobertura de fontB para una cadena sin degradar Unicode.

    El espacio (ASCII/fullwidth) y los códigos de salto son excepciones que
    pueden renderizarse sin imagen. Rechaza caracteres no mapeados.
    """
    fnt=struct.unpack('<11616H',members['fontB.fnt'])
    missing=[]
    for c in dict.fromkeys(text):
        if c in (' ', '　','\n','\r','\t'):continue
        try:
            code=CODIGOS[c] if c in CODIGOS else c.encode('cp932')
            i=index_sjis(code)
            if fnt[i]==0:missing.append(c)
        except (FontError,UnicodeError):missing.append(c)
    return missing


def audit_glyphs(members):
    fnt=struct.unpack('<11616H',members['fontB.fnt'])
    return {c:fnt[index_sjis(code)] for c,code in CODIGOS.items()}

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    a=argparse.ArgumentParser();a.add_argument('folder');a.add_argument('--salida',required=True)
    p=a.parse_args();inp=Path(p.folder);out=Path(p.salida);out.mkdir(parents=True,exist_ok=True)
    m={n:bytearray((inp/n).read_bytes()) for n in ('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')}
    r=add_spanish_fonts(m)
    for n,b in m.items():(out/n).write_bytes(b)
    (out/'informe_fuentes.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'glifos':r['glifos_agregados'],'alias':r['alias_ascii'],'gid':r['gid_final']},ensure_ascii=False))
