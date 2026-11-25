"""ROM-031: subgrupos y variables TALK; fixtures sintéticos, no certifican juego."""
import struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import recompilar_talk as rt
from formato_talk import inspect,TalkError

RES='ISO_START/talk00.dat'
def fixture(lines,gaps=None):
 raw=struct.pack('<II',1,1)+struct.pack('<II',0,123)+bytes(24)
 gaps=gaps or [b'\0\1']*(len(lines)-1)
 return raw+b'\1'+b''.join(x+gaps[i] if i<len(gaps) else x for i,x in enumerate(lines))+b'\0\3'
def wide(s):return rt.encode(s)
def compile_case(raw,indices,phrase):
 meta=inspect(raw)
 rows=[dict(grupo_id='1',unit_id=str(i+1),recurso=RES,
            offset=str(meta['strings'][i]['offset']),
            original=meta['strings'][i]['raw'].decode('cp932')) for i in indices]
 trie,rejected=rt.catalog(rows,{'1':dict(estado='revisado',es_revisado=phrase)},{RES:raw},{RES:meta})
 with patch.object(rt,'missing_render_glyphs',return_value=[]):
  return rt.compile_one(RES,raw,meta,trie,{}),rejected

class Rom031(unittest.TestCase):
 def test_partial_two_slots_keeps_page_and_orphan(self):
  raw=fixture([wide('One'),wide('Two'),wide('Unknown')],[b'\0\2\1',b'\0\1'])
  (out,ok,bad,journal),rej=compile_case(raw,[0,1],'Hola mundo')
  self.assertFalse(rej);self.assertEqual(len(ok),1);self.assertEqual(len(bad),1)
  self.assertEqual(ok[0]['unidades_origen'],['1','2'])
  self.assertEqual(len(journal),2)
  a=inspect(raw);b=inspect(out)
  self.assertEqual([op for _,_,op in a['tokens']],[op for _,_,op in b['tokens']])
  self.assertEqual(b['strings'][2]['raw'],a['strings'][2]['raw'])
  self.assertEqual(' '.join(x['raw'].decode('cp932') for x in b['strings'][:2]),'Ｈｏｌａ ｍｕｎｄｏ')
 def test_group_across_portrait_is_rejected(self):
  raw=fixture([wide('One'),wide('Two')],[b'\0\x09\x01\x01\x01'])
  (out,ok,bad,journal),rej=compile_case(raw,[0,1],'Hola mundo')
  self.assertIn('1',rej);self.assertEqual(out,raw);self.assertFalse(ok)
 def test_variable_preserved(self):
  raw=fixture([wide('Hello ')+b'A1'])
  (out,ok,bad,journal),rej=compile_case(raw,[0],'Hola A1')
  self.assertFalse(rej);self.assertFalse(bad);self.assertEqual(len(ok),1)
  self.assertEqual(rt.variables(inspect(out)['strings'][0]['raw']),('A1',))
 def test_variable_loss_or_reorder_rejected(self):
  raw=fixture([b'A1'+wide(' and ')+b'A2'])
  for text in ('Hola','Hola A2 A1','Hola A1 A1','Hola A1 A2 A3'):
   (out,ok,bad,journal),_=compile_case(raw,[0],text)
   self.assertEqual(out,raw);self.assertFalse(ok);self.assertTrue(bad)
 def test_literal_A1_stays_fullwidth(self):
  raw=fixture([wide('Hello')])
  (out,ok,bad,journal),_=compile_case(raw,[0],'A1')
  self.assertEqual(len(ok),1);self.assertFalse(bad)
  self.assertEqual(inspect(out)['strings'][0]['raw'],wide('A1'))
 def test_partial_refuses_overflow(self):
  raw=fixture([wide('One'),wide('Two'),wide('Unknown')])
  (out,ok,bad,journal),_=compile_case(raw,[0,1],'palabra '*14+'palabra')
  self.assertFalse(ok);self.assertEqual(out,raw)
 def test_partial_variable_stays_in_same_slot(self):
  raw=fixture([wide('One')+b'A1',wide('Two'),wide('Unknown')])
  (out,ok,bad,journal),_=compile_case(raw,[0,1],'Hola A1 mundo')
  self.assertEqual(len(ok),1)
  self.assertEqual(rt.variables(inspect(out)['strings'][0]['raw']),('A1',))
  self.assertEqual(rt.variables(inspect(out)['strings'][1]['raw']),())
 def test_no_partial_when_variable_in_wrong_slot(self):
  raw=fixture([wide('One')+b'A1',wide('Two'),wide('Unknown')])
  (out,ok,bad,journal),_=compile_case(raw,[0,1],'Hola mundo A1')
  self.assertFalse(ok);self.assertEqual(out,raw)
if __name__=='__main__':unittest.main()
