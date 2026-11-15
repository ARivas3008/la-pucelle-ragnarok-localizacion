"""Lossless structural TXP inspector (no palette conversion, no image edits)."""
import struct,hashlib
class TXPError(ValueError):pass

def inspect(data:bytes):
    if len(data)<80:raise TXPError('TXP too small')
    w,h,colors,unused,palette_declared,one,two,three=struct.unpack_from('<8H',data,0)
    if not (0<w<=4096 and 0<h<=4096 and colors in (16,256) and palette_declared==colors and one in (1,16) and two==three==1):
        raise TXPError('Unexpected TXP dimensions or header')
    depth=4 if colors==16 else 8
    expected=16+4*colors*one+(w*h*depth//8)
    if w*h*depth%8 or expected!=len(data):
        raise TXPError(f'Unexpected indexed payload: expected {expected}, got {len(data)}')
    pal=data[16:16+4*colors*one]
    pixels=data[16+4*colors*one:]
    if len(pixels)!=w*h*depth//8:raise TXPError('Pixel truncation')
    return {'width':w,'height':h,'palette_colors':colors,'palette_banks':one,'bpp':depth,'palette_sha256':hashlib.sha256(pal).hexdigest(),
            'pixel_sha256':hashlib.sha256(pixels).hexdigest(),'size':len(data)}
