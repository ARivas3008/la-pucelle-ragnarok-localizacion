import unittest,sys,struct,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from script_relocator import ScriptTable,ScriptEdit,UnsafeScript
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fuentes_es import encode_es

ROOT=Path(os.environ.get('LAPUCELLE_EXTRAIDOS','/mnt/data/unpacked'))

@unittest.skipUnless(ROOT.is_dir(), "Se necesitan recursos extraídos por el usuario para la prueba con datos reales")
class Tests(unittest.TestCase):
 def samples(self):
  return [ROOT/'ISO_SCRIPT/script18.dat',ROOT/'ISO_SCRIPT/script01.dat',ROOT/'ISO_START/script00.dat',ROOT/'DLC_00/script00.dat']
 def test_headers(self):
  for p in self.samples():
   with self.subTest(file=p.name):self.assertGreater(ScriptTable(p.read_bytes()).count,0)
 def test_roundtrip_edited_strings(self):
  cases={
   'ISO_SCRIPT/script18.dat':(37338,'Cuando desperté,','By the time I woke up、'),
   'ISO_SCRIPT/script01.dat':(3103,'Me llamo Culotte','My name is Culotte'),
   'ISO_START/script00.dat':(896336,'un señor del mal','a Demon Overlord。 Someone who'),
   'DLC_00/script00.dat':(881921,'Cargar fondo','背景を読み込みます。'),
  }
  for name,(off,translated,original) in cases.items():
   with self.subTest(file=name):
    tab=ScriptTable((ROOT/name).read_bytes())
    encoded_orig=tab.raw[off:tab.raw.index(b'\0',off)]
    self.assertEqual(encoded_orig.decode('cp932').strip(),original.strip(),name)
    new=encode_es(translated)
    modified,positions=tab.apply([ScriptEdit(off,encoded_orig,new)])
    self.assertEqual(modified[positions[0]-1],len(new)+1)
    self.assertEqual(modified[positions[0]:positions[0]+len(new)],new)
    self.assertEqual(len(modified)-len(tab.raw),len(new)-len(encoded_orig))
 def test_reject_bad_opcode(self):
  tab=ScriptTable((ROOT/'ISO_SCRIPT/script18.dat').read_bytes())
  with self.assertRaises(UnsafeScript):tab.apply([ScriptEdit(37338,b'x',b'test')])
 def test_reject_large_length(self):
  tab=ScriptTable((ROOT/'ISO_SCRIPT/script18.dat').read_bytes())
  raw=tab.raw[37338:tab.raw.index(b'\0',37338)]
  with self.assertRaises(UnsafeScript):tab.apply([ScriptEdit(37338,raw,b'A'*255)])
 def test_pointer_updates(self):
  tab=ScriptTable((ROOT/'ISO_SCRIPT/script01.dat').read_bytes())
  off=3103;raw=tab.raw[off:tab.raw.index(b'\0',off)]
  out,_=tab.apply([ScriptEdit(off,raw,raw+b'!'*7)])
  new=ScriptTable(out)
  edge=off+len(raw)+1-tab.body
  self.assertEqual([(v+7 if v>=edge else v) for v in tab.pointers],new.pointers)
if __name__=='__main__':unittest.main()
