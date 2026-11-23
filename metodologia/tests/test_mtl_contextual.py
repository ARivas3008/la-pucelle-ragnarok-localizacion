"""Pruebas sin assets comerciales del puente MTL contextual."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from preparar_mtl_contextual import exportar, importar


class TestPuenteMTL(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        lot = self.base / "lotes" / "001"
        lot.mkdir(parents=True)
        with (lot / "entrada.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "unit_id", "grupo_id", "recurso", "original", "escena",
                "contexto_previo", "contexto_siguiente", "hablante"])
            w.writeheader()
            w.writerows([
                dict(unit_id="1", grupo_id="a", recurso="r", original="Hello {0}",
                     escena="intro", contexto_previo="", contexto_siguiente="Bye",
                     hablante="Personaje"),
                dict(unit_id="2", grupo_id="a", recurso="r", original="Bye",
                     escena="intro", contexto_previo="Hello {0}", contexto_siguiente="",
                     hablante="Personaje")
            ])

    def test_exportar_grupo_atómico_y_contexto(self):
        out = self.base / "solicitudes.jsonl"
        result = exportar(self.base / "lotes", out)
        self.assertEqual(result["solicitudes_grupos"], 1)
        req = json.loads(out.read_text(encoding="utf-8").strip())
        self.assertEqual([r["unit_id"] for r in req["unidades"]], ["1", "2"])
        self.assertEqual(req["unidades"][0]["marcadores"], ["{0}"])

    def test_importar_borradores_nunca_los_aprueba(self):
        src = self.base / "respuestas.jsonl"
        src.write_text('{"unit_id":"1","mtl_es":"Hola {0}"}\n'
                       '{"unit_id":"2","mtl_es":"Adiós"}\n', encoding="utf-8")
        output = self.base / "mtl.csv"
        result = importar(self.base / "lotes", src, output)
        self.assertEqual(result["revisadas"], 0)
        self.assertEqual(result["estados"]["BORRADOR_PENDIENTE_REVISION"], 2)
        self.assertTrue(output.is_file())

    def test_marcador_perdido_se_detecta(self):
        src = self.base / "respuestas.jsonl"
        src.write_text('{"unit_id":"1","mtl_es":"Hola"}\n', encoding="utf-8")
        result = importar(self.base / "lotes", src, self.base / "mtl.csv")
        self.assertEqual(result["estados"]["MTL_MARCADORES_ALTERADOS"], 1)
        self.assertEqual(result["estados"]["SIN_BORRADOR"], 1)

    def test_id_extra_no_se_acepta(self):
        src = self.base / "respuestas.jsonl"
        src.write_text('{"unit_id":"999","mtl_es":"Hola"}\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            importar(self.base / "lotes", src, self.base / "mtl.csv")


if __name__ == "__main__":
    unittest.main()
