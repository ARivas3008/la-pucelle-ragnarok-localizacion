import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_tabla_rom020
from fuentes_es import encode_script_text

class TestRom020(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/campos_compactos_rom020.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}
        self.compacts=[r for r in self.rows if r['tipo']=='compacto']
        self.specials=[r for r in self.rows if r['tipo']=='reserva_original']

    def invoke(self,row,cap,raw=b'fixture',variants=None,text=None,hash_value=None):
        with patch('campos_revisados.hashlib.sha256') as mock:
            mock.return_value.hexdigest.return_value=hash_value or row['sha256_recurso']
            return variante_tabla_rom020(row,row['revision'] if text is None else text,raw,cap,self.variants if variants is None else variants)

    def test_31_compact_variants(self):
        self.assertEqual(len(self.compacts),31)
        for row in self.compacts:
            with self.subTest(unit=row['unit_id']):
                c=row['capacidad']
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),c)
                text,data,cap=self.invoke(row,c)
                self.assertEqual(text,row['compacto'])
                self.assertEqual(cap,c)
                self.assertLess(len(data),cap)
                self.assertNotIn(b'\0',data)

    def test_two_atypical_fields_and_adjacent_description(self):
        self.assertEqual(len(self.specials),2)
        for row in self.specials:
            with self.subTest(unit=row['unit_id']):
                raw=bytearray(5000);off=int(row['offset'])
                raw[off:off+22]=bytes.fromhex(row['fuente_hex'])
                raw[off+22:off+26]=b'DESC'
                text,data,c=self.invoke(row,None,raw)
                self.assertEqual((text,c),(row['revision'],22))
                raw[off:off+c]=data.ljust(c,b'\0')
                self.assertEqual(raw[off+c:off+c+4],b'DESC')

    def test_wrong_hash(self):
        row=self.compacts[0]
        self.assertIsNone(self.invoke(row,row['capacidad'],hash_value='bad'))

    def test_stale_review(self):
        row=self.compacts[0]
        self.assertIsNone(self.invoke(row,row['capacidad'],text='Otro texto'))

    def test_wrong_offset(self):
        row=dict(self.compacts[0],offset='999')
        self.assertIsNone(self.invoke(row,row['capacidad']))

    def test_wrong_capacity(self):
        row=self.compacts[0]
        self.assertIsNone(self.invoke(row,23))

    def test_wrong_resource(self):
        row=dict(self.compacts[0],recurso='DLC_00/com.dat')
        self.assertIsNone(self.invoke(row,row['capacidad']))

    def test_wrong_atypical_source(self):
        row=self.specials[0];raw=bytearray(5000);off=int(row['offset'])
        raw[off:off+22]=bytes.fromhex(row['fuente_hex']);raw[off+21]=7
        self.assertIsNone(self.invoke(row,None,raw))

    def test_reject_controls_and_overflow(self):
        row=self.compacts[0]
        for text in ('x\0y','x\ny','x\u200dy','😀','X'*49):
            with self.subTest(text=text):
                self.assertIsNone(self.invoke(row,row['capacidad'],variants={row['unit_id']:dict(row,compacto=text)}))

if __name__=='__main__':unittest.main()
