"""V0.17.2: QA del presupuesto real de tres grupos visibles en PPSSPP.

No utiliza ni distribuye archivos comerciales. Comprueba que los ajustes
contextuales versionados caben en los cuadros CP932 de ancho completo que
se midieron sobre el script de la ISO del titular.
"""
import csv
import sys
import unittest
from pathlib import Path

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP/"scripts"))
from construir_parche import to_full
from fuentes_es import encode_es
from segmentacion import repartir

AJUSTES=APP/"datos"/"ajustes_contextuales.csv"
CASOS={
 "5056":([46,46,32,40,8],["6277","6278","6279","6280","6281"]),
 "5064":([40,30,30],["6293","6294","6295"]),
 "5072":([32,46,46],["6306","6307","6308"]),
}
class TestCuadrosIntro(unittest.TestCase):
 def test_tres_grupos_encajan_sin_mover_opcodes(self):
  with AJUSTES.open(encoding="utf-8-sig",newline="") as f:
   data={r["grupo_id"]:r for r in csv.DictReader(f)}
  for gid,(caps,ids) in CASOS.items():
   with self.subTest(grupo=gid):
    text=data[gid]["ajuste"]
    encoder=lambda s:encode_es(to_full(s))
    chunks=repartir(text,caps,encoder=encoder)
    self.assertEqual(len(chunks),len(caps))
    self.assertEqual(" ".join(chunks),text)
    self.assertTrue(all(len(encoder(chunk))<=limit
                        for chunk,limit in zip(chunks,caps)))
    self.assertTrue(all(chunks))
    if gid=="5056":
     self.assertEqual(chunks[-1],"sola")
     self.assertEqual(len(encoder(chunks[-1])),8)
 def test_conserva_campos_de_origen_editorial(self):
  with AJUSTES.open(encoding="utf-8-sig",newline="") as f:
   data={r["grupo_id"]:r for r in csv.DictReader(f)}
  for gid in CASOS:
   self.assertTrue(data[gid]["origen"].strip())
   self.assertTrue(data[gid]["motivo"].strip())
   self.assertNotEqual(data[gid]["origen"],data[gid]["ajuste"])

if __name__=="__main__":
 unittest.main()
