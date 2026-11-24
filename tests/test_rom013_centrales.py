"""ROM-013: auditor integra 509 grupos centrales, no solo corpus repartidos."""
import ast,unittest,types
from pathlib import Path
from collections import Counter
FILE=Path(__file__).resolve().parents[1]/'scripts/auditar_entrega.py'
source=FILE.read_text(encoding='utf-8')
astree=ast.parse(source)
fn=next(n for n in astree.body if isinstance(n,ast.FunctionDef) and n.name=='revisiones_completas')
compiled=compile(ast.Module(body=[fn],type_ignores=[]),str(FILE),'exec')
class Catalogo(unittest.TestCase):
 def test_conserva_revisiones_centrales(self):
  a={'1':{'estado':'revisado','es_revisado':'A'}}
  b={'2':{'estado':'revisado','es_revisado':'B'}}
  called=[]
  class FakeC:
   def read_reviews(self,repo,fetch):
    called.append(('read',fetch))
    return a,[],Counter(revisado=1)
  def merge(repo,distributed,manifest,checks,states,expected):
   self.assertEqual(distributed,a)
   self.assertEqual(expected,509)
   self.assertEqual(states['revisado'],1)
   return {**a,**b,**{str(i):{'estado':'pendiente','es_revisado':''} for i in range(3,15526)}},[],Counter(revisado=2)
  ns={'c':FakeC(),'merge_central':merge}
  exec(compiled,ns)
  output=ns['revisiones_completas']('/repo',[])
  self.assertIn('2',output)
  self.assertEqual(len(output),15525)
  self.assertEqual(called,[('read',False)])
 def test_catalogo_incompleto_falla(self):
  class FakeC:
   def read_reviews(self,repo,fetch):return {'1':{'estado':'revisado','es_revisado':'A'}},[],Counter()
  ns={'c':FakeC(),'merge_central':lambda *args,**kwargs:({'1':{}},[],Counter())}
  exec(compiled,ns)
  with self.assertRaisesRegex(ValueError,'incompleto'):ns['revisiones_completas']('/repo',[])
 def test_fallo_merge_no_se_oculta(self):
  class FakeC:
   def read_reviews(self,repo,fetch):return {},[],Counter()
  def error(*a,**kw):raise ValueError('CENTRAL_DUPLICADO')
  ns={'c':FakeC(),'merge_central':error}
  exec(compiled,ns)
  with self.assertRaisesRegex(ValueError,'CENTRAL_DUPLICADO'):ns['revisiones_completas']('/repo',[])
if __name__=='__main__':unittest.main()
