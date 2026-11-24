"""ROM-010: regresiones con ISO y EDAT simulados; no demuestran juego real."""
import ast
import csv
import tempfile
import types
import unittest
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/"scripts/auditar_entrega.py"
tree=ast.parse(SOURCE.read_text(encoding="utf-8"))
load=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=="load")
def nispack(data):
 if data==b"SCRIPTPACK":return [dict(name="talk01_jp.dat",content=b"test")]
 if data==b"BGPACK":return [dict(name="at01.txp",content=b"png")]
 if data==b"DLCVALID":return [dict(name="START_JP.LZS",content=b"start")]
 if data==b"INVALID":return [dict(name="unknown",content=b"not-LZS")]
 raise ValueError("Objeto desconocido")
class FakeImage:
 def __init__(self,path):self.path=path
 def records(self):
  for i,name in enumerate(("/PSP_GAME/USRDIR/START_JP.LZS",
                           "/PSP_GAME/USRDIR/SCRIPTPACK.DAT",
                           "/PSP_GAME/USRDIR/BGPACK.DAT",
                           "/PSP_GAME/SYSDIR/EBOOT.BIN")):
   yield name,i,1,None
 def read(self,i,n):
  return [b"start",b"SCRIPTPACK",b"BGPACK",b"EBOOT"][i]
fake=types.SimpleNamespace(Image=FakeImage,members_from_dat=lambda raw:{"talk00.dat":b"src"})
def validate_lzs(blob):
 if blob!=b"start":raise ValueError("bad LZS")
 return dict(raw_size=3)
ns=dict(c=fake,nispack=nispack,lzs_decompress=lambda blob,allow_overlap:blob,
        lzs_header=validate_lzs)
exec(compile(ast.Module(body=[load],type_ignores=[]),str(SOURCE),"exec"),ns)
run=ns["load"]
class ROM010(unittest.TestCase):
 def test_load_iso_sola_sin_dlc(self):
  a=run(Path("original.iso"))
  self.assertEqual(a["ISO_START/talk00.dat"],b"src")
  self.assertEqual(a["ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat"],b"test")
  self.assertEqual(a["ISO/PSP_GAME/USRDIR/BGPACK.DAT/at01.txp"],b"png")
  self.assertFalse(any(k.startswith("DLC_") for k in a))
 def test_load_con_cuatro_dlc(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)
   for i in range(4):(p/f"DL_JP_{i:02d}.EDAT").write_bytes(b"DLCVALID")
   d=run(Path("original.iso"),p)
   for i in range(4):self.assertEqual(d[f"DLC_{i:02d}/talk00.dat"],b"src")
 def test_falta_dlc_falla(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)
   for i in range(3):(p/f"DL_JP_{i:02d}.EDAT").write_bytes(b"DLCVALID")
   with self.assertRaisesRegex(FileNotFoundError,"DL_JP_03"):run(Path("original.iso"),p)
 def test_dlc_invalido_falla(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)
   for i in range(4):(p/f"DL_JP_{i:02d}.EDAT").write_bytes(b"INVALID")
   with self.assertRaisesRegex(ValueError,"único LZS validado"):run(Path("original.iso"),p)
 def test_auditor_exige_estado_no_evaluado(self):
  src=SOURCE.read_text(encoding="utf-8")
  self.assertIn("NO_EVALUADO_DLC_AUSENTE",src)
  self.assertIn("unidades_no_evaluadas_por_ausencia_dlc",src)
  self.assertIn("cobertura_iso_sola.json",src)
 def test_manifest_tiene_alcance_real_22721_iso(self):
  manifest=SOURCE.parents[1]/"data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv"
  if not manifest.is_file():self.skipTest("Manifiesto completo no disponible")
  with manifest.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),26258)
  iso=sum(not r["recurso"].startswith("DLC_") for r in rows)
  self.assertEqual(iso,22721)
  self.assertEqual(len(rows)-iso,3537)
if __name__=="__main__":unittest.main()
