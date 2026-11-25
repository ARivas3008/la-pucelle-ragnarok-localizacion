"""ROM-009: pruebas de preflight aisladas, sin ISO ni EDAT protegidos."""
import ast
import tempfile
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'parcheador/app/scripts/integracion_total.py'
tree=ast.parse(SOURCE.read_text(encoding='utf-8'))
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verificar_destinos')
namespace={'Path':Path}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),namespace)
check=namespace['verificar_destinos']

class PreflightTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  self.iso=self.root/'original.iso'
  self.iso.write_bytes(b'original')
  self.dlc=self.root/'DLC'
  self.dlc.mkdir()
  for i in range(4):(self.dlc/f'DL_JP_{i:02d}.EDAT').write_bytes(b'edat')

 def test_salida_nueva_valida(self):
  out=self.root/'salida'
  self.assertEqual(check(self.iso,self.dlc,out),out)
  self.assertFalse(out.exists())

 def test_salida_vacia_existente(self):
  out=self.root/'salida';out.mkdir()
  self.assertEqual(check(self.iso,self.dlc,out),out)

 def test_salida_con_datos_rechazada(self):
  out=self.root/'salida';out.mkdir();(out/'informe.json').write_text('x')
  with self.assertRaises(ValueError):check(self.iso,self.dlc,out)

 def test_salida_igual_iso_rechazada(self):
  with self.assertRaises(ValueError):check(self.iso,None,self.iso)

 def test_salida_padre_iso_rechazada(self):
  with self.assertRaises(ValueError):check(self.iso,None,self.root)

 def test_salida_dentro_dlc_rechazada(self):
  with self.assertRaises(ValueError):check(self.iso,self.dlc,self.dlc/'salida')

 def test_salida_igual_dlc_rechazada(self):
  with self.assertRaises(ValueError):check(self.iso,self.dlc,self.dlc)

 def test_dlc_incompleto_rechazado(self):
  (self.dlc/'DL_JP_03.EDAT').unlink()
  with self.assertRaisesRegex(ValueError,'DL_JP_03'):check(self.iso,self.dlc,self.root/'salida')

 def test_dlc_ausente_rechazado(self):
  with self.assertRaises(ValueError):check(self.iso,self.root/'no-existe',self.root/'salida')

 def test_salida_archivo_rechazada(self):
  out=self.root/'salida';out.write_bytes(b'no')
  with self.assertRaises(ValueError):check(self.iso,None,out)

 def test_sin_iso_con_dlc(self):
  self.assertEqual(check(None,self.dlc,self.root/'salida'),self.root/'salida')

 def test_sin_entradas_directorio(self):
  self.assertEqual(check(None,None,self.root/'salida'),self.root/'salida')

if __name__=='__main__':unittest.main()
