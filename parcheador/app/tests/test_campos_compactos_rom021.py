import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_tabla_rom021
from fuentes_es import encode_script_text

class TestRom021(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/campos_compactos_rom021.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}

    def invoke(self,row,cap=None,variants=None,text=None,hash_value=None):
        with patch('campos_revisados.hashlib.sha256') as mock:
            mock.return_value.hexdigest.return_value=hash_value or row['sha256_recurso']
            return variante_tabla_rom021(row,row['revision'] if text is None else text,b'fixture',row['capacidad'] if cap is None else cap,self.variants if variants is None else variants)

    def test_30_compacts_fit(self):
        self.assertEqual(len(self.rows),30)
        for row in self.rows:
            with self.subTest(unit=row['unit_id']):
                cap=row['capacidad']
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),cap)
                text,data,c=self.invoke(row)
                self.assertEqual(text,row['compacto'])
                self.assertEqual(c,cap)
                self.assertLess(len(data),cap)
                self.assertNotIn(b'\0',data)

    def test_square_button_retained(self):
        row=next(r for r in self.rows if r['unit_id']=='22911')
        self.assertIn('□'.encode('cp932'),self.invoke(row)[1])
        self.assertIsNone(self.invoke(row,variants={row['unit_id']:dict(row,compacto='Pulsa para invertir energía.')}))

    def test_wrong_hash(self):
        self.assertIsNone(self.invoke(self.rows[0],hash_value='bad'))

    def test_stale_review(self):
        self.assertIsNone(self.invoke(self.rows[0],text='Otro texto'))

    def test_wrong_offset(self):
        self.assertIsNone(self.invoke(dict(self.rows[0],offset='999')))

    def test_wrong_resource(self):
        self.assertIsNone(self.invoke(dict(self.rows[0],recurso='DLC_00/kis.dat')))

    def test_wrong_capacity(self):
        self.assertIsNone(self.invoke(self.rows[0],cap=57))

    def test_invalid_variants(self):
        row=self.rows[0]
        for text in ('a\0b','a\nb','a\u200db','😀','X'*21):
            with self.subTest(text=text):
                self.assertIsNone(self.invoke(row,variants={row['unit_id']:dict(row,compacto=text)}))

if __name__=='__main__':unittest.main()
