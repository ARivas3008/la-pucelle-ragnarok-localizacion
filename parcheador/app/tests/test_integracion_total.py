import sys,unittest
from pathlib import Path
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import construir_parche as core
from dialogos_completos import planificar

class IntegracionTotal(unittest.TestCase):
 def setUp(self):
  self.previous=core.TEXTO_COMPACTO;core.TEXTO_COMPACTO=True
 def tearDown(self):core.TEXTO_COMPACTO=self.previous
 def test_compacto_no_modifica_cotejo_de_fuente(self):
  raw=bytearray(core.to_full('Hello').encode('cp932')+b'\0')
  style,matched=core.match_source(raw,0,'Hello')
  self.assertEqual(style,'ancho');self.assertEqual(matched,raw[:-1])
  encoded=core.safe_encoding('¡Hola!',style,len(matched),fuentes_es=True)
  self.assertEqual(len(encoded),len(matched));self.assertTrue(encoded.startswith(core.encode_es('¡Hola!')))
 def fixture(self,gap=b'\0\x02\x01',orphan=False):
  res='ISO_START/talk00.dat';raw=bytearray(b'\x01First segment\0\x01Second segment'+gap+b'Third segment\0\x03')
  starts=[1,16,raw.index(b'Third')]
  rows=[dict(unit_id=str(i),grupo_id=g,recurso=res,offset=str(off),original=text)
        for i,g,off,text in zip(range(3),('a','b','b'),starts,('First segment','Second segment','Third segment'))]
  if orphan:rows=rows[:2]
  groups=defaultdict(list)
  for r in rows:groups[r['grupo_id']].append(r)
  reviews={'a':dict(estado='revisado',es_revisado='Hola a todos.'),'b':dict(estado='revisado',es_revisado='Hoy salimos de viaje.')}
  return raw,rows,groups,reviews,res
 def test_un_grupo_entre_paginas_y_otro_en_primera_linea(self):
  raw,rows,groups,reviews,res=self.fixture()
  sol,bad,ids=planificar(core,rows,{res:raw},groups,reviews,False,True,{}, {})
  self.assertFalse(bad);self.assertEqual(set(sol),ids)
  self.assertEqual(' '.join(sol[str(i)][1] for i in range(3)),'Hola a todos. Hoy salimos de viaje.')
  out=raw[:];allowed=set()
  for meta,chunk,data,key in sol.values():
   off,cap=meta[1],meta[3];out[off:off+cap]=data;allowed.update(range(off,off+cap))
  self.assertEqual(len(out),len(raw))
  self.assertTrue(all(a==b for i,(a,b) in enumerate(zip(raw,out)) if i not in allowed))
 def test_no_atraviesa_control_desconocido(self):
  raw,rows,groups,reviews,res=self.fixture(b'\0\x02\x06\x01')
  sol,bad,ids=planificar(core,rows,{res:raw},groups,reviews,False,True,{}, {})
  self.assertFalse(sol);self.assertEqual(set(bad),ids)
 def test_no_traduce_parcialmente_cadena_incompleta(self):
  raw,rows,groups,reviews,res=self.fixture(b'\0\x01',True)
  sol,bad,ids=planificar(core,rows,{res:raw},groups,reviews,False,True,{}, {})
  self.assertFalse(sol);self.assertEqual(set(bad),ids)

if __name__=='__main__':unittest.main()
