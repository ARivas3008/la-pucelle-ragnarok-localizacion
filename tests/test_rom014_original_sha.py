"""ROM-014: auditor no certifica versiones de ISO ajenas al original autenticado."""
import ast,unittest,tempfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'scripts/auditar_entrega.py'
tree=ast.parse(P.read_text(encoding='utf-8'))
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='autenticar_iso_original')
compiled=compile(ast.Module(body=[fn],type_ignores=[]),str(P),'exec')
ISO_SHA='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
class Autenticar(unittest.TestCase):
 def exercise(self,hash_value):
  class C:
   def sha_file(self,path):return hash_value
  ns={'c':C(),'ISO_BASE_SHA256':ISO_SHA}
  exec(compiled,ns)
  return ns['autenticar_iso_original']
 def test_original_autenticado(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'original.iso';f.write_bytes(b'fixture')
   self.assertEqual(self.exercise(ISO_SHA)(f),ISO_SHA)
 def test_version_distinta_falla(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'original.iso';f.write_bytes(b'fixture')
   with self.assertRaisesRegex(ValueError,'no reconocida'):
    self.exercise('0'*64)(f)
 def test_iso_ausente_falla_antes_hash(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaisesRegex(ValueError,'inexistente'):
    self.exercise(ISO_SHA)(Path(t)/'missing.iso')
if __name__=='__main__':unittest.main()
