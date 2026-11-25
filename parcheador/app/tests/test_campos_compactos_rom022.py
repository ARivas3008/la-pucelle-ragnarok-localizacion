import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_tabla_rom022, conservar_icono
from fuentes_es import encode_script_text

class TestRom022(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/campos_compactos_rom022.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}

    def invoke(self,row,cap,raw=b'fixture',variants=None,text=None,hash_value=None):
        with patch('campos_revisados.hashlib.sha256') as mock:
            mock.return_value.hexdigest.return_value=hash_value or row['sha256_recurso']
            return variante_tabla_rom022(row,row['revision'] if text is None else text,raw,cap,self.variants if variants is None else variants)

    def fixture(self,row):
        off=int(row['offset']);cap=row['capacidad']
        raw=bytearray(off+cap+16)
        raw[off:off+cap]=bytes.fromhex(row['fuente_hex'])
        tail=b'\x09' if row['unit_id']=='23133' else b'\x87\x41'
        raw[off+cap:off+cap+len(tail)]=tail
        return raw,off,cap,tail

    def test_twelve_normal_compacts(self):
        normal=[r for r in self.rows if r['tipo']=='compacto']
        self.assertEqual(len(normal),12)
        for row in normal:
            with self.subTest(unit=row['unit_id']):
                cap=row['capacidad']
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),cap)
                text,data,c=self.invoke(row,cap)
                self.assertEqual((text,c),(row['compacto'],cap))
                self.assertLess(len(data),cap)
                self.assertNotIn(b'\0',data)

    def test_exceptional_fields_preserve_following_bytes(self):
        special=[r for r in self.rows if r['tipo'].startswith('reserva')]
        self.assertEqual(len(special),2)
        for row in special:
            raw,off,cap,tail=self.fixture(row)
            text,data,c=self.invoke(row,None,raw)
            self.assertEqual((text,c),(row['compacto'],cap))
            raw[off:off+cap]=data.ljust(cap,b'\0')
            self.assertEqual(raw[off+cap:off+cap+len(tail)],tail)

    def test_changed_tail_rejected(self):
        for row in [r for r in self.rows if r['tipo'].startswith('reserva')]:
            raw,off,cap,tail=self.fixture(row)
            raw[off+cap]=0xff
            self.assertIsNone(self.invoke(row,None,raw))

    def test_prefixes_keep_exact_cp932(self):
        for c in '①②③':
            self.assertEqual(conservar_icono(c.encode('cp932')+b'text','123'['①②③'.index(c)]+'Texto'),c+'Texto')
        for row in [r for r in self.rows if r['revision'][0] in '①②③']:
            text,data,_=self.invoke(row,row['capacidad'])
            self.assertEqual(data[:2],row['revision'][0].encode('cp932'))
            self.assertIsNone(self.invoke(row,row['capacidad'],variants={row['unit_id']:dict(row,compacto='Sin icono')}))

    def test_wrong_sha_anchor_capacity_and_review(self):
        row=self.rows[0]
        self.assertIsNone(self.invoke(row,23,hash_value='bad'))
        self.assertIsNone(self.invoke(dict(row,offset='1'),23))
        self.assertIsNone(self.invoke(row,57))
        self.assertIsNone(self.invoke(row,23,text='Otro texto'))
        self.assertIsNone(self.invoke(dict(row,recurso='DLC_00/magic.dat'),23))

    def test_reject_invalid_compact(self):
        row=self.rows[0]
        for t in ('X'*23,'a\0b','a\nb','a\u200db','😀'):
            self.assertIsNone(self.invoke(row,23,variants={row['unit_id']:dict(row,compacto=t)}))

if __name__=='__main__':unittest.main()
