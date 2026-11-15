import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from campos_v011 import CampoError, reemplazar_en_hueco_original, replace
from script_relocator import ScriptTable,ScriptEdit,UnsafeScript
from txp_verify import inspect,TXPError

class Pruebas66(unittest.TestCase):
 def test_hueco_original_preserva_metadatos(self):
  raw=b'CABALLERO\x00\x12\x44\x19'+b'OTRO\x00'
  after=reemplazar_en_hueco_original(raw,0,b'CABALLERO',b'REY')
  self.assertEqual(len(raw),len(after))
  self.assertEqual(after[9:],raw[9:])
  self.assertEqual(after[:9],b'REY'+b'\x00'*6)
 def test_hueco_no_admite_mayor_largo(self):
  with self.assertRaises(CampoError):
   reemplazar_en_hueco_original(b'A\x00\xff',0,b'A',b'AB')
 def test_hueco_rechaza_original_alterado(self):
  with self.assertRaises(CampoError):
   reemplazar_en_hueco_original(b'A\x02\x00',0,b'A',b'B')
 def test_script_expansion_sin_index_interno(self):
  # count=2, rel offsets 0 and 9, opcode 0x32, len=4, 'ABC'+NUL
  body=b'\x32\x04ABC\x00\x22\x00\x00'+b'\xff\x00'
  raw=struct.pack('<3I',2,0,9)+body
  off=14
  original=ScriptTable(raw)
  updated,where=original.apply([ScriptEdit(off,b'ABC',b'PALABRA')])
  self.assertEqual(where,[off]);self.assertEqual(ScriptTable(updated).pointers,[0,13])
  self.assertEqual(updated[off-1],8)
 def test_script_rechaza_index_interno(self):
  # segunda entrada apunta al interior del texto de la primera
  body=b'\x32\x04ABC\x00\x20\x00'
  raw=struct.pack('<3I',2,0,4)+body
  with self.assertRaises(UnsafeScript):ScriptTable(raw).apply([ScriptEdit(14,b'ABC',b'PALABRA')])
 def test_txp_4bpp(self):
  raw=struct.pack('<8H',4,4,16,0,16,1,1,1)+b'\x00'*64+b'\x01'*8
  info=inspect(raw)
  self.assertEqual(info['bpp'],4)
  self.assertEqual(info['width'],4)
 def test_txp_wrong_size(self):
  raw=struct.pack('<8H',4,4,16,0,16,1,1,1)+b'\x00'*64+b'\x01'*7
  with self.assertRaises(TXPError):inspect(raw)

if __name__=='__main__':unittest.main()
