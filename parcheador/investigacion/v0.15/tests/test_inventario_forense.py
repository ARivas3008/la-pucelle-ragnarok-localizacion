import sys
import struct
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inventario_forense import fichar

class TestInventario(unittest.TestCase):
    def test_nispack_sintetico(self):
        raw=bytearray(2052)
        raw[:8]=b"NISPACK\0"
        struct.pack_into("<I",raw,8,0)
        struct.pack_into("<I",raw,12,1)
        struct.pack_into("<32sIII",raw,16,b"magic.dat",2048,4,123)
        raw[2048:2052]=b"ABCD"
        nodes=[]
        fichar(nodes,"DL_JP_00.EDAT",bytes(raw),"DLC")
        self.assertEqual(len(nodes),2)
        self.assertEqual(nodes[0]["clase"],"NISPACK")
        self.assertEqual(nodes[1]["offset_en_padre"],2048)

    def test_dat_sintetico(self):
        raw=bytearray(51)
        struct.pack_into("<I",raw,0,1)
        struct.pack_into("<I",raw,16,3)
        raw[20:27]=b"foo.dat"
        raw[48:51]=b"ABC"
        nodes=[]
        fichar(nodes,"START::DAT_DESCOMPRIMIDO",bytes(raw),"START")
        self.assertEqual(nodes[0]["clase"],"DAT_INDEXADO")
        self.assertEqual(nodes[1]["tamano_bytes"],3)

    def test_textura_desconocida_no_es_fontb(self):
        nodes=[]
        fichar(nodes,"algo.txp",b"123456789","START")
        self.assertEqual(nodes[0]["clase"],"TXP_GRAFICO_FORMATO_PENDIENTE")

if __name__=="__main__":unittest.main()
