"""Regresiones sintéticas de la codificación del corazón original."""
import struct
import unittest
from auditar_corazon_original import heart_tile_rows,CODE,MARKER,dat_members
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"parcheador/app/scripts"))
from fuentes_es import index_sjis,encode_es

class TestSimboloCorazon(unittest.TestCase):
    def test_cp932_no_confundir_yen_ascii(self):
        self.assertEqual(MARKER.encode("cp932"),b"\x81\x8f")
        self.assertEqual(CODE.decode("cp932"),MARKER)
        self.assertNotEqual("¥".encode("cp932"),CODE)
        self.assertEqual(index_sjis(CODE),175)
        self.assertEqual(encode_es("eri￥"),b"eri\x81\x8f")
    def test_verificacion_DAT_sintetico(self):
        member=b"\x01\x02\x03\x04"
        # header con 1 entrada, fin relativo a base, relleno del 32-byte name
        base=48
        raw=bytearray(base+len(member))
        struct.pack_into("<I",raw,0,1)
        struct.pack_into("<I",raw,16,len(member))
        raw[20:27]=b"a.txp\x00\x00"
        raw[base:]=member
        self.assertEqual(dat_members(bytes(raw))["a.txp"],member)
        with self.assertRaises(ValueError):dat_members(bytes(raw[:-1]))
    def test_font_index_consistente(self):
        self.assertEqual(index_sjis(bytes.fromhex("818f")),175)

if __name__=="__main__":
    unittest.main()
