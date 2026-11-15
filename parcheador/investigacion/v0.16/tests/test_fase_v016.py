"""Pruebas aisladas v0.16 de anclas CP932 sin binarios del videojuego."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "investigacion" / "v0.12"))
from reubicador_anclas_v012 import Edicion, Reubicador, ReubicacionInsegura


def script(texto, referencias=(3,)):
    # 0x32, u8 longitud, bytes CP932, NUL. La posición 3 corresponde
    # al segundo byte del primer glifo (el cuerpo empieza en offset 12).
    n = 1 + len(referencias)
    indices = (0,) + referencias
    return struct.pack("<I", n) + struct.pack("<" + "I"*n, *indices) + (
        b"\\x32" + bytes([len(texto) + 1]) + texto + b"\\0"
    )


class FaseCP932(unittest.TestCase):
    def test_sin_optin_se_rechaza(self):
        old = "あ".encode("cp932")
        raw = script(old)
        off = 4 + 4*2 + 2
        with self.assertRaises(ReubicacionInsegura):
            Reubicador(raw).aplicar([Edicion(off, old, "猫".encode("cp932"), "caso")])

    def test_preserva_fase_y_reversibilidad(self):
        old = "あ".encode("cp932")
        new = "猫犬".encode("cp932")
        raw = script(old)
        off = 4 + 4*2 + 2
        out, diary = Reubicador(raw, preservar_fase=True).aplicar(
            [Edicion(off, old, new, "caso")]
        )
        self.assertEqual(Reubicador.revertir(out, diary), raw)
        self.assertEqual(len(diary["anclas_subcaracter_fase_conservada"]), 1)
        anchor = diary["anclas_subcaracter_fase_conservada"][0]
        self.assertEqual(anchor["fase"], 1)
        self.assertEqual(anchor["byte_destino"], 1)
        self.assertEqual(struct.unpack_from("<I", out, 8)[0], 3)

    def test_no_inventa_un_segundo_byte(self):
        old = "あ".encode("cp932")
        raw = script(old)
        off = 4 + 4*2 + 2
        with self.assertRaisesRegex(ReubicacionInsegura, "segundo byte"):
            Reubicador(raw, preservar_fase=True).aplicar(
                [Edicion(off, old, b"gato", "caso")]
            )

    def test_no_admite_dos_politicas_contradictorias(self):
        with self.assertRaises(ReubicacionInsegura):
            Reubicador(script("あ".encode("cp932")),
                       permitir_subcaracter=True, preservar_fase=True)


if __name__ == "__main__":
    unittest.main()
