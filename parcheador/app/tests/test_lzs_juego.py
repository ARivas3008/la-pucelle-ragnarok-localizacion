"""Regresión: repetir bytes no autoriza copias con origen aún no decodificado."""
import struct,subprocess,sys,tempfile,unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from nis_formats import lzs_decompress

class GameLzsTests(unittest.TestCase):
 def test_decoder_de_qa_rechaza_solapamiento(self):
  tokens=b'A'+bytes([213,1,8])
  blob=struct.pack('<4sIIB3x',b'dat\0',9,12+len(tokens),213)+tokens
  self.assertEqual(lzs_decompress(blob),b'A'*9)
  with self.assertRaisesRegex(ValueError,'solapada'):
   lzs_decompress(blob,allow_overlap=False)

 def test_compresor_real_repeticiones_y_marcador(self):
  exe=SCRIPTS/'nis_lzs_pack.exe'
  if not exe.is_file():self.skipTest('Compilar primero el compresor C++')
  raw=b'\0'*2048+bytes(range(256))*3+b'AB'*1024+bytes([213])*512
  with tempfile.TemporaryDirectory() as tmp:
   src=Path(tmp)/'input';out=Path(tmp)/'output'
   src.write_bytes(raw)
   subprocess.run([str(exe),str(src),str(out),'dat','213'],check=True,capture_output=True)
   self.assertEqual(lzs_decompress(out.read_bytes(),allow_overlap=False),raw)

if __name__=='__main__':unittest.main()
