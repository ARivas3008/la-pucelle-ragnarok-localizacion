import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_nominal
from fuentes_es import encode_script_text

class TestCompactos(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/nombres_compactos_rom017.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}
        self.raw=b'fixture'
        self.patcher=patch('campos_revisados.hashlib.sha256')
        self.mock=self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.mock.return_value.hexdigest.return_value='6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c'
    def test_all_twenty_eight_variants_fit(self):
        self.assertEqual(len(self.variants),28)
        for row in self.rows:
            with self.subTest(unit=row['unit_id']):
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),12)
                text,data=variante_nominal(row,row['revision'],self.raw,12,self.variants)
                self.assertEqual(text,row['compacto'])
                self.assertLessEqual(len(data),11)
    def test_spanish_gaiji_variant(self):
        row=next(r for r in self.rows if r['grupo_id']=='14271')
        text,data=variante_nominal(row,row['revision'],self.raw,12,self.variants)
        self.assertEqual(text,'También')
        self.assertIn(bytes.fromhex('f041'),data)
    def test_embedded_control_rejected(self):
        row=self.rows[0]
        for bad in ('a\x00b','a\nb','a\u200db','a😀'):
            with self.subTest(bad=bad):
                variants={row['unit_id']:dict(row,compacto=bad)}
                self.assertIsNone(variante_nominal(row,row['revision'],self.raw,12,variants))
    def test_stale_revision(self):
        row=self.rows[0]
        self.assertIsNone(variante_nominal(row,'otra revisión',self.raw,12,self.variants))
    def test_wrong_offset(self):
        row=dict(self.rows[0],offset=99)
        self.assertIsNone(variante_nominal(row,row['revision'],self.raw,12,self.variants))
    def test_wrong_hash(self):
        row=self.rows[0];self.mock.return_value.hexdigest.return_value='bad'
        self.assertIsNone(variante_nominal(row,row['revision'],self.raw,12,self.variants))
    def test_wrong_resource(self):
        row=dict(self.rows[0],recurso='DLC_00/name.dat')
        self.assertIsNone(variante_nominal(row,row['revision'],self.raw,12,self.variants))
    def test_wrong_capacity(self):
        row=self.rows[0]
        self.assertIsNone(variante_nominal(row,row['revision'],self.raw,13,self.variants))
    def test_oversize_compact(self):
        row=self.rows[0]
        variants={row['unit_id']:dict(row,compacto='ABCDEFGHIJKL')}
        self.assertIsNone(variante_nominal(row,row['revision'],self.raw,12,variants))

if __name__=='__main__':unittest.main()
