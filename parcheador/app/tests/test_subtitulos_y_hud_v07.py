import sys, unittest, hashlib, csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from subtitulos_script import aplicar, CaptionError, CAPTIONS, SOURCE_HASH
from construir_parche import cargar_menus_centrales,sustituir_eboot_ascii

class SubtitulosYHudV07(unittest.TestCase):
 def test_script_real_inalterado_fuera_de_zonas(self):
  sample=Path('/mnt/data/unpacked/ISO_START/script00.dat')
  if not sample.is_file():self.skipTest('No hay copia del recurso original')
  raw=sample.read_bytes();patched,report=aplicar(raw)
  self.assertEqual(len(report),4)
  self.assertEqual(len(raw),len(patched))
  self.assertNotEqual(raw,patched)
  allowed=set()
  for caption in CAPTIONS:
   a=caption.off;b=a+len(caption.source.encode('cp932'))
   allowed.update(range(a,b))
  self.assertTrue(all(i in allowed for i,(a,b) in enumerate(zip(raw,patched)) if a!=b))
  self.assertEqual(raw[0:900853],patched[0:900853])
  self.assertEqual(raw[901056:],patched[901056:])
 def test_no_tocar_script_de_version_desconocida(self):
  with self.assertRaises(CaptionError):aplicar(b'XXXXX')
 def test_menu_corto_ascii_en_campo_original(self):
  menu=cargar_menus_centrales()
  for key in ('Church','Ghost Village','Demon Lord','Inventory','Voice Vol','All Items'):
   self.assertIn(key,menu)
   self.assertTrue(menu[key].isascii())
   self.assertLessEqual(len(menu[key]),len(key))
   src=bytearray(key.encode('ascii')+b'\x00')
   row={'recurso':'ISO/PSP_GAME/SYSDIR/EBOOT.BIN','unit_id':'1','grupo_id':'1','offset':'0','original':key}
   updated,fail=sustituir_eboot_ascii(src,[row],{}, {},menu)
   self.assertFalse(fail)
   self.assertEqual(len(updated),1)
   self.assertEqual(len(src),len(key)+1)
 def test_now_loading_no_incluido_en_sustituciones(self):
  self.assertNotIn('Now Loading',cargar_menus_centrales())
  self.assertFalse(any('Loading' in c.source or 'Loading' in c.target for c in CAPTIONS))
 def test_todas_las_traducciones_hud_ascii_y_misma_longitud(self):
  menu=cargar_menus_centrales()
  # Algunas etiquetas largas del menú siguen rechazándose deliberadamente:
  # nunca se las corta sin validación ni se modifica la longitud de EBOOT.
  for key in ('Church','Udon Shop','Ghost Village','Dark Shrine','Castle Bar','Demon','Great Demon','Demon Lord','Overlord','Tiny','Whale','Ghost','Priest','Fallen Angel','Equip','Quit','Human','Inventory','Skills','Special','All Items','Dark Gate','Move','Decide','BGM','Voice Vol','Battle Vol','System Speed Fast','Move Speed  Fast','Text Speed  Fast'):
   self.assertTrue(menu[key].isascii(),key)
   self.assertLessEqual(len(menu[key]),len(key),key)

if __name__=='__main__':unittest.main()
