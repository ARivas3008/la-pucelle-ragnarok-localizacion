"""Pruebas sintéticas NISPACK BGPACK, sin recursos del juego."""
import struct
import unittest
from auditar_bgpack_original import parse_bgpack

def fixture():
    b=bytearray(4104)
    b[:8]=b'NISPACK\0'
    struct.pack_into('<I',b,12,2)
    for i,(name,offset) in enumerate([('a.txp',2048),('b.dat',4096)]):
        p=16+i*44
        b[p:p+32]=name.encode().ljust(32,b'\0')
        struct.pack_into('<III',b,p+32,offset,8,0)
    b[2048:2056]=b'12345678'
    b[4096:4104]=b'ABCDEFGH'
    return b

class BGPACKTests(unittest.TestCase):
    def test_miembros_validos(self):
        self.assertEqual([x['name'] for x in parse_bgpack(fixture())],['a.txp','b.dat'])
    def test_solapamiento_rechazado(self):
        b=fixture()
        struct.pack_into('<I',b,16+44+32,2048)
        with self.assertRaises(ValueError):
            parse_bgpack(b)
    def test_cabecera_invalida(self):
        b=fixture()
        b[:8]=b'XXXXXXXX'
        with self.assertRaises(ValueError):
            parse_bgpack(b)
    def test_intervalo_excede_recurso(self):
        b=fixture()
        struct.pack_into('<I',b,16+32,65536)
        with self.assertRaises(ValueError):
            parse_bgpack(b)

if __name__=='__main__':
    unittest.main()
