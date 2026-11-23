"""Pruebas sintéticas de TXP 4/8bpp y CLUT, independientes de assets comerciales."""
import struct
import unittest
from inspeccionar_txp_bgpack import TXPError,metadata,swizzle,unswizzle,rgba_bytes

def fake_txp(w,h,bpp):
    colors=16 if bpp==4 else 256
    entries=[bytes((i,i*3%256,255-i,255)) for i in range(colors)]
    palette=b"".join(entries)
    raw_indices=bytes((i*13+7)%256 for i in range(w*h*bpp//8))
    header=struct.pack("<8H",w,h,colors,0,colors,1,1,1)
    return header+palette+swizzle(raw_indices,w,h,bpp),raw_indices

class TestTXPPSP(unittest.TestCase):
    def test_roundtrip_4bit(self):
        raw,indices=fake_txp(64,16,4)
        info,palette,swizzled=metadata(raw)
        linear=unswizzle(swizzled,64,16,4)
        self.assertEqual(info["bpp"],4)
        self.assertEqual(linear,indices)
        self.assertEqual(swizzle(linear,64,16,4),swizzled)
        self.assertEqual(len(rgba_bytes(linear,palette,4)),64*16*4)
    def test_roundtrip_8bit(self):
        raw,indices=fake_txp(32,16,8)
        info,palette,swizzled=metadata(raw)
        self.assertEqual(info["bpp"],8)
        self.assertEqual(unswizzle(swizzled,32,16,8),indices)
        self.assertEqual(swizzle(indices,32,16,8),swizzled)
        self.assertEqual(rgba_bytes(indices[:1],palette,8),palette[indices[0]*4:indices[0]*4+4])
    def test_truncado_y_header_no_admitido(self):
        raw,_=fake_txp(32,16,8)
        with self.assertRaises(TXPError):metadata(raw[:-1])
        damaged=bytearray(raw)
        struct.pack_into("<H",damaged,8,16)
        with self.assertRaises(TXPError):metadata(damaged)
        with self.assertRaises(TXPError):metadata(raw[:10])
    def test_no_ocultar_dimensiones_no_alineadas(self):
        with self.assertRaises(TXPError):swizzle(bytes(30),30,8,8)
        with self.assertRaises(TXPError):unswizzle(bytes(30),30,8,8)
    def test_paleta_invalida(self):
        with self.assertRaises(TXPError):rgba_bytes(b"\0",bytes(4*16),8)

if __name__=="__main__":
    unittest.main()
