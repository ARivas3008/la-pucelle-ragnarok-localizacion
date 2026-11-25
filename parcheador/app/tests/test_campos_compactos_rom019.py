import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_tabla_rom019
from fuentes_es import encode_script_text

class TestRom019(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/campos_compactos_rom019.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}
        self.compacts=[r for r in self.rows if r['tipo']=='compacto']
        self.special=next(r for r in self.rows if r['tipo']=='reserva_original')

    def run_variant(self,row,raw=b'fixture',cap=24,variants=None,text=None,hash_value=None):
        with patch('campos_revisados.hashlib.sha256') as mock:
            mock.return_value.hexdigest.return_value=hash_value or row['sha256_recurso']
            return variante_tabla_rom019(row,row['revision'] if text is None else text,raw,cap,self.variants if variants is None else variants)

    def test_13_variants_fit(self):
        self.assertEqual(len(self.compacts),13)
        for row in self.compacts:
            with self.subTest(unit=row['unit_id']):
                cap=row['capacidad']
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),cap)
                text,data,result_cap=self.run_variant(row,cap=cap)
                self.assertEqual(text,row['compacto'])
                self.assertLess(len(data),cap)
                self.assertEqual(result_cap,cap)
                self.assertNotIn(b'\0',data)

    def test_cafeteria_preserves_metadata(self):
        row=self.special
        raw=bytearray(3600);off=int(row['offset'])
        raw[off:off+12]=b'Cafeteria\x00\x00\x03'
        text,data,cap=self.run_variant(row,raw=raw,cap=None)
        self.assertEqual((text,cap),('Comedor',10))
        raw[off:off+cap]=data.ljust(cap,b'\0')
        self.assertEqual(raw[off:off+12],b'Comedor\x00\x00\x00\x00\x03')

    def test_cafeteria_refuses_unexpected_tail(self):
        row=self.special;raw=bytearray(3600);off=int(row['offset'])
        raw[off:off+12]=b'Cafeteria\x00\x00\x04'
        self.assertIsNone(self.run_variant(row,raw=raw,cap=None))

    def test_wrong_hash(self):
        self.assertIsNone(self.run_variant(self.compacts[0],hash_value='bad'))

    def test_stale_review(self):
        self.assertIsNone(self.run_variant(self.compacts[0],text='Texto nuevo'))

    def test_wrong_capacity(self):
        self.assertIsNone(self.run_variant(self.compacts[0],cap=28))

    def test_wrong_resource(self):
        row=dict(self.compacts[0],recurso='DLC_00/char.dat')
        self.assertIsNone(self.run_variant(row))

    def test_wrong_offset(self):
        row=dict(self.compacts[0],offset='9')
        self.assertIsNone(self.run_variant(row))

    def test_invalid_compact(self):
        row=self.compacts[0]
        for text in ('a\x00b','a\nb','a\u200db','a😀','A'*24):
            with self.subTest(text=text):
                self.assertIsNone(self.run_variant(row,variants={row['unit_id']:dict(row,compacto=text)}))

if __name__=='__main__':unittest.main()
