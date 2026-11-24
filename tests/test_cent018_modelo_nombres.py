"""CENT-018: pruebas del algoritmo MIPS y del límite de 16 bytes."""
import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"scripts/cent018_modelo_nombres.py"
spec=importlib.util.spec_from_file_location('cent018',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Names(unittest.TestCase):
 def test_clase_1_sufijo_sin_espacio(self):
  self.assertEqual(m.combinar("Prier","Kind",1),"PrierKind")
 def test_clase_2_prefijo_sin_espacio(self):
  self.assertEqual(m.combinar("Prier","Pass",2),"PassPrier")
 def test_clase_3_admite_ambos_ordenes(self):
  self.assertEqual(m.combinar("Croix","Co",3,1),"CroixCo")
  self.assertEqual(m.combinar("Croix","Co",3,2),"CoCroix")
 def test_clase_3_sin_sorteo_no_aprobable(self):
  with self.assertRaises(m.CombinacionInvalida):m.combinar("Prier","Co",3)
 def test_clase_1_sentido_contrario_rechazado(self):
  with self.assertRaises(m.CombinacionInvalida):m.combinar("Prier","Kind",1,2)
 def test_maximo_16_bytes_permitido(self):
  self.assertEqual(len(m.combinar("abcdefghij","123456",1).encode('cp932')),16)
 def test_17_bytes_rechazado(self):
  with self.assertRaisesRegex(m.CombinacionInvalida,"16 bytes"):
   m.combinar("abcdefghijk","123456",1)
 def test_slot_11_bytes_utiles_permitido(self):
  self.assertEqual(len(m.comprobar_slot("abcdefghijk")),11)
 def test_slot_12_bytes_rechazado(self):
  with self.assertRaisesRegex(m.CombinacionInvalida,"11 bytes"):
   m.comprobar_slot("abcdefghijkl")
 def test_nul_rechazado(self):
  with self.assertRaises(m.CombinacionInvalida):m.combinar("Prier","Kind\x00",1)
 def test_incompatible_cp932_rechazado(self):
  with self.assertRaises(m.CombinacionInvalida):m.combinar("Prier","😀",1)
 def test_incorrect_class_rechazado(self):
  with self.assertRaises(m.CombinacionInvalida):m.combinar("Prier","Kind",4)
 def test_evaluacion_no_certifica(self):
  r=m.evaluar([('1',3,'Co')],['Prier','Croix'])
  self.assertEqual(len(r),1)
  self.assertEqual(r[0]['combinaciones_validas'],4)
  self.assertFalse(r[0]['certificado_visual'])
if __name__=='__main__':unittest.main()
