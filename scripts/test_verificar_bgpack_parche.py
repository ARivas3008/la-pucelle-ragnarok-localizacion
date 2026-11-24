"""Regresiones sintéticas de seguridad de BGPACK. Nunca contienen assets comerciales."""
import hashlib,struct,unittest
from verificar_bgpack_parche import verify,BGPACKIntegrityError

def pack():
    raw=bytearray(8192)
    raw[:8]=b"NISPACK\0"
    struct.pack_into("<I",raw,12,2)
    for i,(name,pos,size) in enumerate((("a.txp",2048,208),("b.dat",4096,16))):
        p=16+i*44
        raw[p:p+32]=name.encode().ljust(32,b"\0")
        struct.pack_into("<III",raw,p+32,pos,size,0)
    # 16 x 16 x 8 bpp = 256 data; use 16x8=128 data
    header=struct.pack("<8H",16,8,16,0,16,1,1,1)
    # 4bpp: 16 * 8 / 2 = 64 bytes
    # total 16+64+64=144, so adjust table size to 144
    struct.pack_into("<I",raw,16+32+4,144)
    raw[2048:2064]=header
    raw[2064:2128]=bytes(range(64))
    raw[2128:2192]=bytes(range(64))
    raw[4096:4112]=b"ORIGINAL_CONTENT"
    return bytes(raw)

class BGPACKIntegrityTests(unittest.TestCase):
    def test_ningun_cambio_por_defecto(self):
        original=pack()
        data=verify(original,original)
        self.assertTrue(data["integridad_fuera_de_pixeles"])
        self.assertFalse(data["certificacion_visual"])
    def test_pixel_autorizado_con_hash_y_clut_intacta(self):
        original=pack()
        sha=hashlib.sha256(original[2048:2192]).hexdigest()
        candidate=bytearray(original)
        candidate[2140]^=0xff
        with self.assertRaises(BGPACKIntegrityError):
            verify(original,bytes(candidate))
        report=verify(original,bytes(candidate),{"a.txp":sha})
        self.assertEqual(report["texturas_autorizadas"],["a.txp"])
    def test_cualquier_cambio_en_clut_o_fuera_se_rechaza(self):
        original=pack()
        sha=hashlib.sha256(original[2048:2192]).hexdigest()
        for index in (16,2048,2073,2195,4100,8000):
            with self.subTest(byte=index):
                candidate=bytearray(original)
                candidate[index]^=0x01
                with self.assertRaises(BGPACKIntegrityError):
                    verify(original,bytes(candidate),{"a.txp":sha})
    def test_hash_no_autorizado_se_rechaza(self):
        original=pack()
        with self.assertRaises(BGPACKIntegrityError):
            verify(original,original,{"a.txp":"0"*64})
        with self.assertRaises(BGPACKIntegrityError):
            verify(original,original,{"b.dat":"0"*64})
    def test_rechazar_tamano_y_metadata_cambiados(self):
        original=pack()
        with self.assertRaises(BGPACKIntegrityError):
            verify(original,original+b"\0")
        candidate=bytearray(original)
        struct.pack_into("<I",candidate,16+32,4096)
        with self.assertRaises(BGPACKIntegrityError):
            verify(original,bytes(candidate))

if __name__=="__main__":
    unittest.main()
