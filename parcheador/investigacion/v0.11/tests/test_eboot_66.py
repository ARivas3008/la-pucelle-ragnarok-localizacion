import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aplicar_eboot_66 import apply

class EbootAscii(unittest.TestCase):
 def fixtures(self):
  names=['Start','Continue','Now Loading']+['Item'+str(i).zfill(4) for i in range(256)]
  assert len(names)==259
  fields=[];manifest=[];report=[];off=0
  for i,name in enumerate(names):
   fields.append(name.encode('ascii')+b'\x00\xaa')
   manifest.append({'recurso':'ISO/PSP_GAME/SYSDIR/EBOOT.BIN', 'unit_id':str(i), 'offset':str(off),'original':name})
   report.append({'unit_id':str(i),'es_revisado':name,'estado_editorial':'central'})
   off+=len(fields[-1])
  return b''.join(fields),manifest,report
 def test_ascii_menus_no_changes_elsewhere(self):
  raw,m,r=self.fixtures()
  out,rows=apply(raw,m,r,[{'original':'Start','es':'Jugar'}, {'original':'Continue','es':'Seguir'}, {'original':'Now Loading','es':'Cargando'}])
  self.assertEqual(len(out),len(raw))
  self.assertTrue(out.startswith(b'Jugar\0\xaaSeguir  \0\xaaNow Loading\0\xaa'))
  self.assertEqual(sum(x['estado']=='ASCII_TAMANO_FIJO' for x in rows),2)
  self.assertEqual(sum(x['estado']=='OMITIDO_NOW_LOADING' for x in rows),1)
 def test_reject_length_overflow(self):
  raw,m,r=self.fixtures()
  out,rows=apply(raw,m,r,[{'original':'Start','es':'Comenzar'}])
  self.assertEqual(raw,out)
  self.assertEqual(rows[0]['estado'],'EXCEDE_CAMPO')
 def test_reject_non_ascii(self):
  raw,m,r=self.fixtures()
  out,rows=apply(raw,m,r,[{'original':'Start','es':'Menú'}])
  self.assertEqual(raw,out)
  self.assertEqual(rows[0]['estado'],'NO_APTO_ASCII')

if __name__=='__main__':unittest.main()
