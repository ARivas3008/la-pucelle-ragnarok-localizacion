import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from planificar_corpus import normalizar,lotear
from verificar_presupuesto import evaluar,codificar
class TestMetodologia(unittest.TestCase):
 def test_grupos_nunca_se_dividen(self):
  rows=[{"unit_id":str(i),"grupo_id":"A" if i<4 else "B",
         "recurso":"ISO/script","original":"T"+str(i),
         "escena":"intro"} for i in range(1,6)]
  lots=lotear(normalizar(rows),1)
  self.assertEqual([len(q) for q in lots],[1,1])
  self.assertEqual([sum(len(m) for _,m in lot) for lot in lots],[3,2])
 def test_fuente_no_admite_control_perdido(self):
  a={"unit_id":"1","recurso":"x","original":"Hola {0}","capacidad_bytes":"20"}
  b={"unit_id":"1","es_revisado":"Hola","estado":"revisado"}
  self.assertEqual(evaluar(a,b)["estado"],"CONTROLES_MODIFICADOS")
 def test_utf8_no_es_presupuesto_cp932(self):
  a={"unit_id":"2","recurso":"x","original":"a","tipo":"fijo","capacidad_bytes":"2"}
  b={"unit_id":"2","es_revisado":"á","estado":"revisado"}
  self.assertEqual(evaluar(a,b,gaiji={"á":"f040"})["estado"],"EXCEDE_CAMPO_FIJO")
 def test_no_cambiar_utf8_en_ascii(self):
  self.assertEqual(len(codificar("¿",gaiji={"¿":"f04e"})),2)
 def test_no_aprobado_no_se_inserta(self):
  a={"unit_id":"3","original":"a","capacidad_bytes":"100"}
  b={"es_revisado":"Uno","estado":"requiere_investigacion"}
  self.assertEqual(evaluar(a,b)["estado"],"PENDIENTE_EDITORIAL")
 def test_sin_capacidad_no_inventa(self):
  a={"unit_id":"4","original":"test","capacidad_bytes":""}
  b={"es_revisado":"texto","estado":"revisado"}
  self.assertEqual(evaluar(a,b)["estado"],"CAPACIDAD_FISICA_NO_DOCUMENTADA")
if __name__=="__main__":unittest.main()
