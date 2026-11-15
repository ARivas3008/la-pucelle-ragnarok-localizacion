import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from campos_fijos import capacidad_verificada,ampliar_campo,CampoError,PERFILES
from construir_parche import match_source
from fuentes_es import encode_es

class TestCamposFijos(unittest.TestCase):
 def test_capacity_in_synthetic_record(self):
  data=bytearray(8+2*200)
  data[8:14]=b'Prier\0'
  data[33:37]=b'\x02\x03\x04\x05'
  cap=capacidad_verificada('ISO_START/char.dat',data,8,5)
  self.assertEqual(cap,24)
  result=ampliar_campo(bytes(data[8:8+cap]),5,encode_es('Personaje'),cap)
  self.assertEqual(result[:10],b'Personaje\0')
  self.assertTrue(all(x==0 for x in result[10:]))
  old=data[:]
  data[8:8+cap]=result
  self.assertEqual(data[33:],old[33:])
 def test_cero_fields_are_never_overwritten(self):
  data=bytearray(8+200);data[8:14]=b'Prier\0';data[29]=7
  self.assertIsNone(capacidad_verificada('ISO_START/char.dat',data,8,5))
 def test_no_expands_beyond_slot_or_invalid_alignment(self):
  data=bytearray(8+200);data[8:14]=b'Prier\0'
  self.assertIsNone(capacidad_verificada('ISO_START/char.dat',data,9,4))
  with self.assertRaises(CampoError):ampliar_campo(b'A\0'+b'\0'*23,1,b'X'*25,25)
 def test_real_fixed_slot_matches_8_resources(self):
  files=Path('/mnt/data/unpacked/ISO_START')
  if not files.exists():self.skipTest('No original resource files')
  positions={'char.dat':8,'magic.dat':26,'mapinfo.dat':20,'name.dat':12,
             'kis.dat':8,'ritem.dat':12,'skill.dat':24,'com.dat':8}
  for name,off in positions.items():
   raw=(files/name).read_bytes();end=raw.find(b'\0',off)
   self.assertGreater(end,off)
   cap=capacidad_verificada('ISO_START/'+name,raw,off,end-off)
   self.assertIsNotNone(cap,name)
   self.assertGreater(cap,end-off+1,name)
 def test_reject_other_resource(self):
  self.assertIsNone(capacidad_verificada('ISO_START/talk00.dat',bytearray(b'ABC\0'+b'\0'*200),0,3))

if __name__=='__main__':unittest.main()
