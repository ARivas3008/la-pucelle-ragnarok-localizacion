"""Regresión de la omisión del CSV central y anclaje de líneas recuperadas."""
import csv,hashlib,json,struct,sys,tempfile,unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from revisiones_coordinadas import merge_central,scoped_segments,lines_sha,RevisionError,CENTRAL
from formato_talk import inspect
from recompilar_talk import catalog,runs

def talk():
    return struct.pack("<II",1,1)+struct.pack("<II",0,123)+bytes(24)+b"\1"+ "Ｈｅｌｌｏ".encode("cp932")+b"\0\1"+"ｗｏｒｌｄ".encode("cp932")+b"\0\3"

class TestCoordinacion(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/CENTRAL
        self.path.parent.mkdir(parents=True)
        self.path.write_text("grupo_id,es_revisado,estado\n2,Hola,revisado\n",encoding="utf-8")
        self.reviews={"1":{"es_revisado":"Texto","estado":"revisado"}}
        self.manifest=[{"grupo_id":"1"},{"grupo_id":"2"}]
    def tearDown(self):self.tmp.cleanup()
    def test_merges_central_and_hash(self):
        rev,proof,states=merge_central(self.tmp.name,self.reviews,self.manifest,[],Counter(revisado=1),1)
        self.assertEqual(rev["2"]["es_revisado"],"Hola")
        self.assertEqual(states["revisado"],2)
        self.assertEqual(proof[-1]["sha256"],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertNotIn("2",self.reviews)
    def test_duplicate_rejected(self):
        self.path.write_text("grupo_id,es_revisado,estado\n1,Otro,revisado\n")
        with self.assertRaises(RevisionError):merge_central(self.tmp.name,self.reviews,self.manifest,[],{},1)
    def test_pending_text_rejected(self):
        self.path.write_text("grupo_id,es_revisado,estado\n2,Otro,pendiente\n")
        with self.assertRaises(RevisionError):merge_central(self.tmp.name,self.reviews,self.manifest,[],{},1)
    def test_missing_central_rejected(self):
        self.path.unlink()
        with self.assertRaises(RevisionError):merge_central(self.tmp.name,self.reviews,self.manifest,[],{},1)
    def fixture(self):
        res="ISO_START/talk00.dat";raw=talk();meta=inspect(raw);run=runs(raw,meta)[0]
        manifest=[{"grupo_id":"2","unit_id":"5","recurso":res,"offset":str(run[0]["offset"]),"original":"Hello"}]
        rev={"2":{"estado":"revisado","es_revisado":"Hola mundo"}}
        doc={"schema":1,"recursos":{res:hashlib.sha256(raw).hexdigest()},"segmentos":[{"recurso":res,"offset":run[0]["offset"],"grupos_objetivo":["2"],"grupos":["2"],"sha256_lineas":lines_sha(run),"es":"Hola mundo"}]}
        return res,raw,meta,manifest,rev,doc
    def test_whole_run_with_unlisted_line(self):
        res,raw,meta,manifest,rev,doc=self.fixture()
        trie,_=catalog(manifest,rev,{res:raw},{res:meta},scoped=doc)
        self.assertNotIn(None,trie["Hello"])
        exact=trie["Hello"]["world"][None][0]
        self.assertTrue(exact["solo_origen"])
        self.assertEqual(exact["unit_ids"],["5"])
        self.assertEqual(exact["grupos"],["2"])
    def test_bad_hash_fails_closed(self):
        res,raw,meta,manifest,rev,doc=self.fixture()
        doc["segmentos"][0]["sha256_lineas"]="0"*64
        with self.assertRaises(RevisionError):catalog(manifest,rev,{res:raw},{res:meta},scoped=doc)
    def test_wrong_original_rejected(self):
        res,raw,meta,manifest,rev,doc=self.fixture()
        doc["recursos"][res]="0"*64
        with self.assertRaises(RevisionError):catalog(manifest,rev,{res:raw},{res:meta},scoped=doc)
    def test_no_legacy_override(self):
        res,raw,meta,manifest,rev,doc=self.fixture()
        with self.assertRaises(RevisionError):catalog(manifest,rev,{res:raw},{res:meta},segments=[dict(recurso=res,offset=doc["segmentos"][0]["offset"])],scoped=doc)
    def test_preserve_preexisting_approved_segment(self):
        res,raw,meta,manifest,rev,doc=self.fixture()
        row=doc["segmentos"][0]
        run=runs(raw,meta)[0]
        prior=dict(recurso=res,offset=row["offset"],grupo_id="legacy",original_hex=[x["raw"].hex() for x in run],es=row["es"])
        trie,_=catalog(manifest,rev,{res:raw},{res:meta},segments=[prior],scoped=doc)
        candidates=trie["Hello"]["world"][None]
        self.assertEqual(len(candidates),2)
        self.assertTrue(any(c["solo_origen"] for c in candidates))
if __name__=="__main__":unittest.main()
