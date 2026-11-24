import csv,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import nombres_fuera_manifiesto as mod

class TestNombres(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'sidecar.csv'
        self.raw=bytearray(8+17*16)
        self.rows=[]
        for i in range(17):
            off=12+16*i
            self.raw[off-4:off]=bytes((i,0,1,1+i%3))
            self.raw[off:off+12]=b'Old'.ljust(12,b'\0')
            self.rows.append(dict(id=f'GNAME-ISO-{off}',recurso=mod.RESOURCE,offset=off,
                clase=1+i%3,original='Old',es_propuesta='Nuevo' if i<10 else 'Old',
                estado='revisado_editorial_fuera_manifiesto' if i<10 else 'conservar_simbolo'))
        self.digest=hashlib.sha256(self.raw).hexdigest()
        for row in self.rows:row['sha256_recurso']=self.digest
        self.src={'name.dat':bytes(self.raw)}
        self.current={'name.dat':bytearray(self.raw)}
    def run_patch(self,manifest=(),missing=lambda *_:[]):
        with self.path.open('w',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(self.rows[0]));w.writeheader();w.writerows(self.rows)
        with patch.object(mod,'SOURCE_SHA',self.digest):
            return mod.aplicar(self.src,self.current,manifest,self.path,missing)
    def test_slots_and_idempotence(self):
        r=self.run_patch()
        self.assertEqual(len(r['aplicados']),10)
        self.assertEqual(len(r['conservados']),7)
        for i in range(17):
            off=12+16*i
            self.assertEqual(self.current['name.dat'][off-4:off],self.raw[off-4:off])
            self.assertEqual(self.current['name.dat'][off:off+12],(b'Nuevo' if i<10 else b'Old').ljust(12,b'\0'))
        self.assertEqual(r,self.run_patch())
    def test_conflict_atomic(self):
        self.current['name.dat'][12+16*9]=ord('X')
        before=bytes(self.current['name.dat'])
        with self.assertRaises(ValueError):self.run_patch()
        self.assertEqual(before,self.current['name.dat'])
    def test_overlap_manifest(self):
        with self.assertRaises(ValueError):self.run_patch([dict(recurso=mod.RESOURCE,offset='12')])
    def test_missing_glyph(self):
        with self.assertRaises(ValueError):self.run_patch(missing=lambda *_:['N'])
    def test_length(self):
        self.rows[0]['es_propuesta']='ABCDEFGHIJKL'
        with self.assertRaises(ValueError):self.run_patch()
    def test_duplicate(self):
        self.rows[-1]=self.rows[0].copy()
        with self.assertRaises(ValueError):self.run_patch()
    def test_wrong_class(self):
        self.rows[0]['clase']=2
        with self.assertRaises(ValueError):self.run_patch()
    def test_wrong_source(self):
        self.src['name.dat']=b'X'+self.src['name.dat'][1:]
        with self.assertRaises(ValueError):self.run_patch()
    def test_symbol_preserved(self):
        self.current['name.dat'][12+16*16]=ord('X')
        with self.assertRaises(ValueError):self.run_patch()

if __name__=='__main__':unittest.main()
