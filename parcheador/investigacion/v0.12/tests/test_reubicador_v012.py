import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reubicador_anclas_v012 import Reubicador,Edicion,ReubicacionInsegura,limites_cp932

class TestAnclas(unittest.TestCase):
 def script(self,content,pointers):
  return struct.pack('<I',len(pointers))+struct.pack('<'+'I'*len(pointers),*pointers)+content
 def test_anclas_ascii_reversibles(self):
  body=b'\x32\x06hello\x00\x32\x01\x00'
  old=self.script(body,[0,4,8])
  off=4+3*4+2
  new,j=Reubicador(old).aplicar([Edicion(off,b'hello',b'hola mundo','U1')])
  self.assertEqual(Reubicador.revertir(new,j),old)
  self.assertEqual(new[4+12:4+12+2],b'\x32\x0b')
 def test_subcaracter_bloqueado_por_defecto(self):
  old=self.script(b'\x32\x03\x81\x40\x00'+b'\x00'*6,[0,3]) # pointer to trail byte
  with self.assertRaises(ReubicacionInsegura):Reubicador(old).aplicar([Edicion(14,b'\x81\x40',b'ab')])
 def test_subcaracter_solo_opcion_experimental(self):
  old=self.script(b'\x32\x03\x81\x40\x00'+b'\x00'*6,[0,3])
  new,j=Reubicador(old,permitir_subcaracter=True).aplicar([Edicion(14,b'\x81\x40',b'ab')])
  self.assertEqual(len(j['anclas_subcaracter_corregidas_experimentalmente']),1)
  self.assertEqual(Reubicador.revertir(new,j),old)
 def test_rechaza_longitud_255(self):
  old=self.script(b'\x32\x03ab\x00'+b'\x00'*15,[0])
  with self.assertRaises(ReubicacionInsegura):Reubicador(old).aplicar([Edicion(10,b'ab',b'x'*255)])
 def test_rechaza_cambio_fuente(self):
  old=self.script(b'\x32\x03ab\x00'+b'\x00'*15,[0])
  with self.assertRaises(ReubicacionInsegura):Reubicador(old).aplicar([Edicion(10,b'XY',b'zz')])
 def test_limites_cp932(self):
  self.assertEqual(limites_cp932(b'a\x81\x40z'),[0,1,3,4])

if __name__=='__main__':unittest.main()
