"""Regresiones de metadatos TXP sin datos comerciales."""
import struct,unittest
from auditar_graficos_manifiesto import txp_structure
def sample(w,h,colors,banks):
    bpp=4 if colors==16 else 8
    return struct.pack("<8H",w,h,colors,0,colors,banks,1,1)+bytes(colors*banks*4+w*h*bpp//8)
class GFXTests(unittest.TestCase):
    def test_partial_height(self):
        t=txp_structure(sample(480,170,256,1))
        self.assertEqual(t["bytes"],82640);self.assertFalse(t["altura_multiplo_8"])
        self.assertFalse(t["decodificador_un_banco_bloques_completos_aplicable"])
    def test_multibank(self):
        t=txp_structure(sample(128,128,16,16))
        self.assertEqual(t["bytes"],9232);self.assertEqual(t["bancos_clut"],16)
        self.assertFalse(t["decodificador_un_banco_bloques_completos_aplicable"])
    def test_complete(self):
        self.assertTrue(txp_structure(sample(256,256,256,1))["decodificador_un_banco_bloques_completos_aplicable"])
    def test_truncated(self):
        with self.assertRaises(ValueError):txp_structure(sample(480,170,256,1)[:-1])
if __name__=="__main__":unittest.main()
