import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrar_scripts_v014 import plan

class FixedScripts(unittest.TestCase):
 def fixture(self,text):
  # El salto embebido representa una referencia fuera de la tabla principal.
  raw=struct.pack('<3I',1,0,100)+b'\x32\x06hello\0'+b'\x99\x08\x00\x00\x00'+b'Z'*16
  rows={'ISO_START/script00.dat':[dict(unit_id='1',offset=14,original='hello',es_revisado=text,estado_editorial='revisado')]}
  return raw,rows
 def test_texto_corto_conserva_referencias_embebidas_y_longitud(self):
  raw,rows=self.fixture('hola')
  changes,_,stats=plan(rows,{'ISO_START/script00.dat':raw},mode='fijo')
  new=changes['ISO_START/script00.dat']['raw']
  self.assertEqual(len(new),len(raw))
  self.assertEqual(new[:14],raw[:14])
  self.assertEqual(new[14:19],b'hola ')
  self.assertEqual(new[19:],raw[19:])
  self.assertEqual(stats['APLICADO_SCRIPT_FIJO'],1)
 def test_texto_largo_no_desplaza_codigo(self):
  raw,rows=self.fixture('hola, mundo')
  changes,_,stats=plan(rows,{'ISO_START/script00.dat':raw},mode='fijo')
  self.assertFalse(changes)
  self.assertEqual(stats['SCRIPT_EXCEDE_ESPACIO_ORIGINAL'],1)
