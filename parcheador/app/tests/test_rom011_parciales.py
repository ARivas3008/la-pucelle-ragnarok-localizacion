"""ROM-011: regresiones de inserción parcial fail-closed con bytecode talk sintético."""
import struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import recompilar_talk as rt
from formato_talk import inspect

RES="ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat"
def fixture():
 first="Ｈｅｌｌｏ".encode("cp932")
 second="ｗｏｒｌｄ".encode("cp932")
 return (struct.pack("<II",1,1)+struct.pack("<II",0,123)+bytes(24)
         +b"\x01"+first+b"\x00\x01"+second+b"\x00\x03")
class PartialTalk(unittest.TestCase):
 def setUp(self):
  self.raw=fixture()
  self.meta=inspect(self.raw)
  self.first=self.meta["strings"][0]
  self.second=self.meta["strings"][1]
  self.unit={"grupo_id":"2","unit_id":"5","recurso":RES,
             "offset":str(self.first["offset"]),"original":"Hello"}
  self.rev={"2":{"estado":"revisado","es_revisado":"Hola"}}
 def catalogue(self):
  t,rejected=rt.catalog([self.unit],self.rev,{RES:self.raw},{RES:self.meta})
  self.assertFalse(rejected)
  return t
 def compile(self,trie):
  with patch.object(rt,"missing_render_glyphs",return_value=[]):
   return rt.compile_one(RES,self.raw,self.meta,trie, {})
 def test_insert_singleton_and_preserve_unknown_second_line(self):
  out,ok,bad,journal=self.compile(self.catalogue())
  self.assertEqual(len(ok),1)
  self.assertEqual(len(journal),1)
  self.assertEqual(len(bad),1)
  self.assertEqual(ok[0]["modo"],"SUBBLOQUE_EXACTO_SIN_CAMBIAR_CONTROLES")
  decoded=inspect(out)
  self.assertEqual(decoded["strings"][0]["raw"].decode("cp932"),"Ｈｏｌａ")
  self.assertEqual(decoded["strings"][1]["raw"],self.second["raw"])
  self.assertEqual(decoded["n"],1)
  self.assertIn("parcial",bad[0]["motivo"].lower())
 def test_rechazar_diferente_posicion(self):
  trie=self.catalogue()
  trie["Hello"][None][0]["offset"]+=2
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(out,self.raw);self.assertFalse(ok)
 def test_rechazar_variantes_ambiguas(self):
  trie=self.catalogue()
  trie["Hello"][None].append({**trie["Hello"][None][0],"es":"Adiós"})
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(out,self.raw);self.assertFalse(ok)
 def test_rechazar_texto_sin_aprobacion(self):
  trie=self.catalogue()
  trie["Hello"][None][0]["estado"]="pendiente"
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(out,self.raw);self.assertFalse(ok)
 def test_rechazar_texto_mayor_que_una_linea(self):
  trie=self.catalogue()
  trie["Hello"][None][0]["es"]="Una traducción mucho más extensa de lo que cabe en una sola línea de la caja"
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(out,self.raw);self.assertFalse(ok)
 def test_rechazar_unidad_multiple(self):
  trie=self.catalogue()
  trie["Hello"][None][0]["unit_ids"]=["5","6"]
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(out,self.raw);self.assertFalse(ok)
 def test_traduccion_de_run_completo_sigue_siendo_prioritaria(self):
  second={"grupo_id":"2","unit_id":"6","recurso":RES,
          "offset":str(self.second["offset"]),"original":"world"}
  reviews={"2":{"estado":"revisado","es_revisado":"Hola mundo"}}
  trie,rejected=rt.catalog([self.unit,second],reviews,{RES:self.raw},{RES:self.meta})
  self.assertFalse(rejected)
  out,ok,bad,journal=self.compile(trie)
  self.assertEqual(len(ok),1)
  self.assertNotIn("modo",ok[0])
  self.assertFalse(bad)
  self.assertNotEqual(out,self.raw)
if __name__=="__main__":unittest.main()
