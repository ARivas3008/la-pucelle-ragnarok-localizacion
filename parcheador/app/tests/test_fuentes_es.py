import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from fuentes_es import (
    encode_es,decode_es, CODIGOS,EXTRAS,index_sjis,
    unpack_pixels,pack_pixels,box_for_gid, add_spanish_fonts,
    missing_render_glyphs, FontError
)

class TestFuentesEspanol(unittest.TestCase):
    def test_indice_juego(self):
        self.assertEqual(index_sjis('A'.encode('cp932')),34)
        self.assertEqual(index_sjis('あ'.encode('cp932')),384)
        self.assertEqual(index_sjis('ァ'.encode('cp932')),480)
        self.assertEqual(index_sjis(CODIGOS['á']),9120)
        self.assertNotEqual(index_sjis(CODIGOS['é']),index_sjis(CODIGOS['á']))

    def test_codec_roundtrip(self):
        for txt in ['¡Hola, mundo!','¿Qué pasó?','«Éclair» — ñandú','Miércoles, 29 de abril','Árbol, raíz, acción','Umlaut: Ü ü','“Sin miedo” – ¡Sí!']:
            self.assertEqual(decode_es(encode_es(txt)),txt)
        self.assertEqual(len(encode_es('ñ')),2)
        self.assertEqual(encode_es('A'),'A'.encode('cp932'))
        with self.assertRaises(FontError):encode_es('🙂')

    def test_codigos_estables(self):
        self.assertEqual(len(CODIGOS),len(EXTRAS))
        self.assertTrue(all(len(b)==2 and b[0]==0xf0 for b in CODIGOS.values()))
        self.assertEqual(len(set(CODIGOS.values())),len(EXTRAS))

    def test_swizzle_y_celdas(self):
        # Textura sintética para que las pruebas no dependan de datos comerciales.
        src=bytearray(132112)
        src[:4]=b'\x00\x02\x00\x02'
        for i in range(131072):src[1040+i]=(i*17+123)&255
        pix=unpack_pixels(src)
        self.assertEqual(pack_pixels(src,pix),bytes(src))
        self.assertEqual(box_for_gid(1),(0,14,0))
        self.assertEqual(box_for_gid(1296),(1,0,0))
        self.assertEqual(box_for_gid(2417),(1,70,434))

    def test_mapa_de_glyphs(self):
        import struct
        from fuentes_es import FONT_SIZE
        # Tablas sintetizadas: 30 glifos base al inicio; dos atlas vacíos.
        base=''.join(dict.fromkeys('aAeEiIoOuUnNcCyYEspQlSt？！'))
        mp=[0]*11616;mt=[0]*11616;mp[0]=mt[0]=11615
        for gid,c in enumerate(base,1):
            ix=index_sjis(c.encode('cp932'))
            mp[ix]=gid;mt[ix]=0x0700
        b=bytearray(132112);b[:4]=b'\x00\x02\x00\x02'
        members={'fontB.fnt':bytearray(struct.pack('<11616H',*mp)),
                 'fontB.ftd':bytearray(struct.pack('<11616H',*mt)),
                 'FontB0000.txp':bytearray(b),
                 'FontB0001.txp':bytearray(b)}
        # Hace visible cada glifo base con un píxel. No contiene letras de un juego.
        from fuentes_es import unpack_pixels, pack_pixels, box_for_gid
        pixels=unpack_pixels(b)
        for gid in range(1,len(base)+1):
            _,x,y=box_for_gid(gid)
            pixels[y*512+x]=15
        members['FontB0000.txp']=bytearray(pack_pixels(b,pixels))
        r=add_spanish_fonts(members)
        self.assertEqual(r['glifos_agregados'],len(EXTRAS))
        self.assertFalse(missing_render_glyphs('¡Español! ¿Qué tal? «Sí»',members))
        snap={k:bytes(v) for k,v in members.items()}
        again=add_spanish_fonts(members)
        self.assertEqual(again['glifos_agregados'],0)
        self.assertEqual({k:bytes(v) for k,v in members.items()},snap)

if __name__=='__main__':unittest.main()
