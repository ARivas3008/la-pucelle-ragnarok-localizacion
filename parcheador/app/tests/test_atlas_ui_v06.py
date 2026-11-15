import hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from atlas_ui_es import expected_patch, AtlasError, validate, apply
from construir_parche import members_from_dat, sustituir_eboot_ascii, cargar_menus_centrales, Image
from nis_formats import lzs_decompress

class AtlasUIV06(unittest.TestCase):
 def setUp(self):
  sample=Path('/mnt/data/START_JP.LZS')
  if not sample.exists():self.skipTest('Se requiere archivo de prueba propio')
  self.m=members_from_dat(lzs_decompress(sample.read_bytes()))
 def test_patches_hash_pinned(self):
  old={k:bytes(v) for k,v in self.m.items()}
  a=apply(self.m)
  self.assertEqual(set(a),{'sys3.txp','sys4.txp'})
  validate(old,self.m)
  self.assertEqual(old['sys4.txp'][:1040],self.m['sys4.txp'][:1040])
 def test_reject_unknown_source(self):
  raw=bytearray(self.m['sys3.txp']);raw[1800]^=0x20
  with self.assertRaises(AtlasError):expected_patch('sys3.txp',bytes(raw))
 def test_ascii_contextual_stays_in_null_terminated_field(self):
  iso=Path('/mnt/data/game_original/La_Pucelle_Ragnarok_v1.1.2.iso')
  if not iso.exists():self.skipTest('Se requiere ISO de prueba propia')
  i=Image(iso);recs={p:(o,n) for p,o,n,_ in i.records()};data=bytearray(i.read(*recs['/PSP_GAME/SYSDIR/EBOOT.BIN'][:2]))
  import csv
  with (Path(__file__).resolve().parents[1]/'datos/mapa_26258_unidades.csv').open(encoding='utf-8-sig') as f:
   manifest=list(csv.DictReader(f))
  changes,_=sustituir_eboot_ascii(data,manifest,{}, {}, cargar_menus_centrales())
  self.assertGreater(len(changes),50)
  for k,(a,b,off) in changes.items():
   self.assertTrue(b.isascii())
   self.assertIn(b.encode('ascii'),data[off:off+256])

if __name__=='__main__':unittest.main()
