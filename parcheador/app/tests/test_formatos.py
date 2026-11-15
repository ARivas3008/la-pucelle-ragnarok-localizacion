import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nis_formats import lzs_decompress,nispack
from construir_parche import dat_entries,members_from_dat,replace_dat_members,match_source,safe_encoding,Fail

class Pruebas(unittest.TestCase):
 def test_dat_roundtrip_sintetico(self):
  # Un DAT de dos recursos con offsets relativos al final del índice.
  base=16+32*2
  a=bytearray(base);struct.pack_into('<I',a,0,2)
  struct.pack_into('<I',a,16,5);a[20:26]=b'a.dat\0'
  struct.pack_into('<I',a,48,10);a[52:58]=b'b.dat\0'
  raw=bytes(a)+b'ab\x00cd'+b'efg\x00x'
  self.assertEqual(members_from_dat(raw)['a.dat'],b'ab\0cd')
  self.assertEqual(raw,replace_dat_members(raw,members_from_dat(raw)))
 def test_sustitucion_fija(self):
  b=bytearray('プリエ'.encode('cp932')+b'\0\xff')
  style,s=match_source(b,0,'プリエ')
  self.assertEqual(style,'normal')
  b[:len(s)]=safe_encoding('Prier',style,len(s))
  self.assertEqual(b[len(s):],b'\0\xff')
  self.assertEqual(len(b),8)
 def test_no_se_alteran_controles(self):
  with self.assertRaises(Fail):safe_encoding('Hola\nAdiós','normal',32)
  with self.assertRaises(Fail):safe_encoding('¿Hola?','normal',32)
  with self.assertRaises(Fail):safe_encoding('Demasiado largo','normal',4)
 def test_referencia_lzs_real_si_existe(self):
  p=Path('/mnt/data/START_JP.LZS')
  if p.exists():
   d=lzs_decompress(p.read_bytes())
   self.assertEqual(len(d),11706208)
   self.assertEqual(len(dat_entries(d)),36)
 def test_edat_real_si_existe(self):
  p=Path('/mnt/data/dlc_original/ULJS00244/DL_JP_00.EDAT')
  if p.exists():
   e=nispack(p.read_bytes())
   self.assertEqual(len(e),1)
   self.assertEqual(e[0]['name'].lower(),'start_jp.lzs')
   raw=lzs_decompress(e[0]['content'])
   self.assertEqual(len(dat_entries(raw)),36)
if __name__=='__main__':unittest.main()
