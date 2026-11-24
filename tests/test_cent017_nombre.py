"""Regresiones CENT-017: tipos, longitud, terminadores y conteo del generador."""
import ast,struct,unittest
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/'scripts/cent017_auditar_nombre.py'
fun=next(n for n in ast.parse(SRC.read_text(encoding='utf-8')).body
         if isinstance(n,ast.FunctionDef) and n.name=='slots')
env={'struct':struct}
exec(compile(ast.Module(body=[fun],type_ignores=[]),str(SRC),'exec'),env)
scan=env['slots']
def fixture(kind=1):
 return struct.pack('<II',2,2)+bytes([0,0,1,kind])+b'Ma\0'+bytes(9)+bytes([1,0,1,2])+b'Pass\0'+bytes(7)+bytes(8)
class NameSlots(unittest.TestCase):
 def test_slots_con_cabecera_y_tail(self):
  count,rows=scan(fixture())
  self.assertEqual(count,2);self.assertEqual(len(rows),2)
  self.assertEqual([r['offset'] for r in rows],[12,28])
  self.assertEqual([r['clase'] for r in rows],[1,2])
 def test_cabeceras_distintas_rechazadas(self):
  b=bytearray(fixture());struct.pack_into('<I',b,4,3)
  with self.assertRaisesRegex(ValueError,'cantidad incoherentes'):scan(b)
 def test_clase_fuera_de_rango_rechazada(self):
  with self.assertRaisesRegex(ValueError,'tipo'):scan(fixture(4))
 def test_slot_sin_nul_rechazado(self):
  b=bytearray(fixture());b[12:24]=b'ABCDEFGHIJKL'
  with self.assertRaisesRegex(ValueError,'terminador'):scan(b)
 def test_resto_no_nulo_rechazado(self):
  b=bytearray(fixture());b[-1]=99
  with self.assertRaisesRegex(ValueError,'no nulos'):scan(b)
 def test_cabecera_demasiado_corta(self):
  with self.assertRaisesRegex(ValueError,'pequeño'):scan(b'123')
 def test_tres_clases_de_fijos(self):
  n,r=scan(fixture(3));self.assertEqual(r[0]['clase'],3)
if __name__=='__main__':unittest.main()
