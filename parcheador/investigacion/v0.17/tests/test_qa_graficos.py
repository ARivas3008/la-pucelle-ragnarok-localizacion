"""Pruebas de preservación de arte gráfico sin contenido comercial."""
import struct
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_integridad_graficos import compare_members

def faux_font():
    tex=bytearray(132112)
    tex[:4]=b"\x00\x02\x00\x02"
    fnt=[0]*11616
    fnt[0]=11615
    fnt[1]=1
    return {"fontB.fnt":struct.pack("<11616H",*fnt),
            "FontB0000.txp":bytes(tex),
            "FontB0001.txp":bytes(tex),
            "sys3.txp":b"\x01\x02\x03",
            "sys4.txp":b"\x05\x07"}

class IntegrityUnitTests(unittest.TestCase):
    def test_identidad_no_altera_ui(self):
        inp=faux_font()
        checks,problems=compare_members(inp,inp,"ISO_START")
        self.assertFalse(problems)
        self.assertTrue(checks)
    def test_sys3_modificado_se_detecta(self):
        old=faux_font();new=dict(old);new["sys3.txp"]=b"\x01\x09\x03"
        _,problems=compare_members(old,new,"ISO_START")
        self.assertIn("TEXTURA_UI_CAMBIADA_SIN_AUTORIZACION",
                      [r["incidencia"] for r in problems])
    def test_atlas_explicitamente_autorizado(self):
        old=faux_font();new=dict(old);new["sys3.txp"]=b"\x01\x09\x03"
        _,problems=compare_members(old,new,"ISO_START",allow_atlas=True)
        self.assertFalse(problems)
    def test_clut_font_original_no_se_puede_reescribir(self):
        old=faux_font();new=dict(old)
        tex=bytearray(old["FontB0001.txp"]);tex[40]=17
        new["FontB0001.txp"]=bytes(tex)
        _,problems=compare_members(old,new,"ISO_START")
        self.assertIn("CAMBIO_CABECERA_O_CLUT_FONTB",
                      [r["incidencia"] for r in problems])
    def test_glifo_original_no_se_puede_reescribir(self):
        old=faux_font();new=dict(old)
        tex=bytearray(old["FontB0000.txp"]);tex[1040+7]=15
        new["FontB0000.txp"]=bytes(tex)
        _,problems=compare_members(old,new,"ISO_START")
        self.assertIn("GLIFOS_ORIGINALES_MODIFICADOS",
                      [r["incidencia"] for r in problems])

if __name__=="__main__":
    unittest.main()
