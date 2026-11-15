"""Las pruebas no necesitan ISO ni copias comerciales."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from auditar_anclas import proponer_fase

class TestAnclas(unittest.TestCase):
    def test_preserva_segundo_byte(self):
        source="あい".encode("cp932")
        target=b"\xf0\x40"+b"BI"
        r=proponer_fase(source,target,1)
        self.assertEqual(r["mapeo_fase"] if "mapeo_fase" in r else r["fase"],1)
        self.assertEqual(r["byte_destino"],1)
        self.assertEqual(r["estado"],"PROPUESTA_FASE_CERCANA")

    def test_rechaza_destino_ascii_sin_segundo_byte(self):
        r=proponer_fase("あ".encode("cp932"),b"AB",1)
        self.assertEqual(r["estado"],"SIN_CARACTER_DE_LA_MISMA_FASE")

    def test_fin_de_cadena(self):
        r=proponer_fase("あ".encode("cp932"),b"hola",2)
        self.assertEqual(r["estado"],"TERMINADOR")
        self.assertEqual(r["byte_destino"],4)

    def test_origen_fuera(self):
        with self.assertRaises(ValueError):
            proponer_fase(b"abc",b"123",-1)

    def test_destino_gaiji_f0(self):
        a="恋".encode("cp932")
        r=proponer_fase(a,b"\xf0\x41",1)
        self.assertEqual(r["byte_destino"],1)

if __name__=="__main__":unittest.main()
