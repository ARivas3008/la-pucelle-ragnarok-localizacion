"""Regresiones GFX-008 sin distribuir ni necesitar una ISO de juego."""
import ast
import hashlib
import json
import struct
import tempfile
import types
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/"parcheador/app/scripts/integracion_total.py"
tree=ast.parse(SOURCE.read_text(encoding="utf-8"))
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="aplicar_capitulos_gfx008")
code=compile(ast.Module(body=[fn],type_ignores=[]),str(SOURCE),"exec")
sha=lambda b:hashlib.sha256(b).hexdigest()

class Image:
 def __init__(self,path):self.path=Path(path)
 def records(self):
  yield "/PSP_GAME/USRDIR/BGPACK.DAT",64,68,None
 def read(self,start,size):
  with self.path.open("rb") as f:f.seek(start);return f.read(size)

class TestGFX008(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory()
  self.addCleanup(temp.cleanup)
  self.root=Path(temp.name)
  app=self.root/"parcheador/app";app.mkdir(parents=True)
  script=self.root/"scripts/gfx007_editar_capitulos.py";script.parent.mkdir()
  script.write_text("import hashlib\ndef edit(raw,num,fontpath):\n"
                    " assert num==1\n"
                    " new=b'EDITED!!'\n"
                    " return new,{'nuevo_sha256':hashlib.sha256(new).hexdigest()}\n",encoding="utf-8")
  self.script=script
  bg=bytearray(68)
  struct.pack_into("<I",bg,12,1)
  struct.pack_into("<32sIII",bg,16,b"at01.txp",60,8,0)
  bg[60:68]=b"ORIGINAL"
  self.before=bytes(bg)
  self.after=bytes(bg[:60]+b"EDITED!!")
  self.original=self.root/"original.iso"
  self.destination=self.root/"candidate.iso"
  self.original.write_bytes(bytes(64)+self.before)
  self.destination.write_bytes(bytes(64)+self.before)
  manifest=self.root/"docs/seguimiento/informes/GFX-007_capitulos_piloto.json"
  manifest.parent.mkdir(parents=True)
  manifest.write_text(json.dumps({
   "iso_original_sha256":sha(self.original.read_bytes()),
   "BGPACK_original_sha256":sha(self.before),
   "BGPACK_piloto_sha256":sha(self.after),
   "assets":{"at01.txp":{"original_sha256":sha(b"ORIGINAL"),
                         "nuevo_sha256":sha(b"EDITED!!")}}
  }),encoding="utf-8")
  self.manifest=manifest
  self.c=types.SimpleNamespace(ROOT=app,Image=Image,sh=sha,
     sha_file=lambda path:sha(Path(path).read_bytes()))
  ns={"c":self.c,"json":json,"struct":struct}
  exec(code,ns)
  self.apply=ns["aplicar_capitulos_gfx008"]

 def test_aplica_titulo_autorizado_sin_cambiar_original(self):
  report=self.apply(self.original,self.destination,self.root/"font.ttf")
  self.assertEqual(self.destination.read_bytes(),bytes(64)+self.after)
  self.assertEqual(self.original.read_bytes(),bytes(64)+self.before)
  self.assertEqual(set(report["assets"]),{"at01.txp"})
  self.assertFalse(report["ppsspp"])

 def test_nombre_tiene_terminador_nulo_real(self):
  self.apply(self.original,self.destination,self.root/"font.ttf")
  self.assertEqual(self.destination.read_bytes()[124:],b"EDITED!!")

 def test_rechaza_iso_original_diferente(self):
  self.original.write_bytes(self.original.read_bytes()+b"x")
  with self.assertRaisesRegex(ValueError,"ISO original"):self.apply(self.original,self.destination,self.root/"font.ttf")

 def test_rechaza_bgpack_destino_modificado(self):
  self.destination.write_bytes(bytes(64)+b"x"+self.before[1:])
  with self.assertRaisesRegex(ValueError,"ya alteró BGPACK"):self.apply(self.original,self.destination,self.root/"font.ttf")

 def test_rechaza_editor_ausente(self):
  self.script.unlink()
  with self.assertRaisesRegex(ValueError,"falta el editor"):self.apply(self.original,self.destination,self.root/"font.ttf")

 def test_rechaza_sha_txps_diferente(self):
  doc=json.loads(self.manifest.read_text(encoding="utf-8"))
  doc["assets"]["at01.txp"]["nuevo_sha256"]="0"*64
  self.manifest.write_text(json.dumps(doc),encoding="utf-8")
  with self.assertRaisesRegex(ValueError,"edición no reproducible"):self.apply(self.original,self.destination,self.root/"font.ttf")

if __name__=="__main__":unittest.main()
