import unittest,sys,struct,tempfile,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from relocador import TablaTalk, Edicion,RelocacionError
from contenedores import reconstruir_nispack,entradas_nispack,reconstruir_dat,entradas_dat
from iso_reubicar import anexar_recurso,recorrer

LOCAL=Path(os.environ.get('LAPUCELLE_UNPACKED','/mnt/data/unpacked'))
ISO=Path(os.environ.get('LAPUCELLE_ISO','/mnt/data/game_original/La_Pucelle_Ragnarok_v1.1.2.iso'))
START=Path(os.environ.get('LAPUCELLE_START','/mnt/data/START_JP.LZS'))
ENGINE=Path(os.environ.get('LAPUCELLE_APP_SCRIPTS','/mnt/data/lapucelle_v07/app/scripts'))

@unittest.skipUnless(LOCAL.is_dir(),'Se requieren originales extraidos')
class TestTalk(unittest.TestCase):
 def test_corpus_reales_tablas(self):
  ins=list((LOCAL/'ISO_SCRIPT').glob('talk*_jp.dat'))
  ins+=list((LOCAL/k/'talk00.dat') for k in ('ISO_START','DLC_00','DLC_01','DLC_02','DLC_03'))
  self.assertEqual(len(ins),21)
  for f in ins:
   t=TablaTalk(f.read_bytes());self.assertGreater(t.cuenta,1)
 def test_ediciones_y_reversion_reales(self):
  p=LOCAL/'ISO_SCRIPT/talk01_jp.dat';b=p.read_bytes();t=TablaTalk(b)
  # Del manifiesto: primer diálogo inglés en offset 33641.
  o=b'\x82h\x82\x8e\x81@\x82\x94\x82\x88\x82\x85\x81@\x82\x8b\x82\x89\x82\x8e\x82\x87\x82\x84\x82\x8f\x82\x8d\x81@\x82\x8f\x82\x86'
  self.assertEqual(b[33641:33641+len(o)],o)
  ed=Edicion(33641,o,b'Traducido a una frase espanola deliberadamente mas larga')
  nuevo,ofs=t.aplicar([ed]);self.assertEqual(ofs,[33641]);self.assertEqual(len(nuevo),len(b)+len(ed.nuevo)-len(ed.antiguo))
  self.assertNotEqual(nuevo,b)
 def test_no_modificar_original_incorrecto(self):
  t=TablaTalk((LOCAL/'ISO_SCRIPT/talk01_jp.dat').read_bytes())
  with self.assertRaises(RelocacionError):t.aplicar([Edicion(33641,b'FAIL',b'OK')])
 def test_no_aceptar_opcode_no_talk(self):
  t=TablaTalk((LOCAL/'ISO_SCRIPT/talk01_jp.dat').read_bytes())
  with self.assertRaises(RelocacionError):t.aplicar([Edicion(33640,b'X',b'Y')])
 def test_ediciones_cadenas_reales_distintas(self):
  b=(LOCAL/'ISO_SCRIPT/talk01_jp.dat').read_bytes();t=TablaTalk(b)
  pairs=[]
  for off in (33641,33677,33728,33766):
   e=b.index(b'\x00',off)
   self.assertEqual(b[off-1],1)
   pairs.append(Edicion(off,b[off:e],(f'Texto revisado {off} con mayor longitud: abcdefghijklmnopqr').encode()))
  nuevo,_=t.aplicar(pairs)
  self.assertGreater(len(nuevo),len(b))
 def test_rechazar_nul(self):
  b=(LOCAL/'ISO_SCRIPT/talk01_jp.dat').read_bytes();t=TablaTalk(b)
  with self.assertRaises(RelocacionError):t.aplicar([Edicion(33641,b'A',b'B\x00C')])

@unittest.skipUnless(LOCAL.is_dir() and ISO.is_file() and START.is_file() and ENGINE.is_dir(),'Se requieren originales extraidos e ISO')
class TestContenedores(unittest.TestCase):
 def test_scriptpack_miembros_y_cambio(self):
  from sys import path
  path.insert(0,str(ENGINE))
  from construir_parche import Image
  im=Image(ISO)
  recs={p:(o,n,r) for p,o,n,r in im.records()}
  raw=im.read(*recs['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'][:2])
  endian,old=entradas_nispack(raw)
  self.assertEqual(len(old),32)
  orig=next(x for x in old if x[0]=='talk01_jp.dat')
  data=raw[orig[1]:orig[1]+orig[2]]
  table=TablaTalk(data);off=33641;end=data.index(0,off)
  patched,_=table.aplicar([Edicion(off,data[off:end],b'Una frase algo mas larga dentro del mismo recuadro')])
  newpack=reconstruir_nispack(raw,{'talk01_jp.dat':patched})
  _,entries=entradas_nispack(newpack)
  d={n:newpack[off:off+sz] for n,off,sz,*_ in entries}
  self.assertEqual(d['talk01_jp.dat'],patched)
  self.assertTrue(all(d[n]==raw[o:o+s] for n,o,s,*_ in old if n!='talk01_jp.dat'))
 def test_dat_repack_original(self):
  from sys import path
  path.insert(0,str(ENGINE))
  from nis_formats import lzs_decompress
  raw=lzs_decompress(START.read_bytes())
  ents=entradas_dat(raw)
  self.assertEqual(len(ents),36)
  name,start,end,_=next(x for x in ents if x[0]=='talk00.dat')
  t=TablaTalk(raw[start:end]);b=raw[start:end];off=b.index(b'\x01')+1
  # Insertar al primer texto que tenga un terminador real.
  for j in range(t.base,len(b)-20):
   if b[j-1]==1 and (k:=b.find(b'\x00',j))>j and k-j<64:
    off=j;endtext=k;break
  ed=Edicion(off,b[off:endtext],b'Una pequena ampliacion de prueba')
  changed,_=t.aplicar([ed]);repacked=reconstruir_dat(raw,{'talk00.dat':changed})
  es={n:repacked[s:e] for n,s,e,_ in entradas_dat(repacked)}
  self.assertEqual(es['talk00.dat'],changed)
  self.assertTrue(all(es[n]==raw[s:e] for n,s,e,_ in ents if n!='talk00.dat'))

if __name__=='__main__':unittest.main()
