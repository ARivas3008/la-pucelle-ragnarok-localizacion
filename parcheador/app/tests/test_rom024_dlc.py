import json,sys,unittest,struct,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from campos_revisados import variante_tabla_rom024
from fuentes_es import encode_script_text
from dlc_originales import verificar_dlc_originales

class TestRom024(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((ROOT/'datos/campos_compactos_rom024.json').read_text(encoding='utf8'))
        self.variants={r['unit_id']:r for r in self.rows}
    def invoke(self,row,cap=None,text=None,variants=None,digest=None):
        with patch('campos_revisados.hashlib.sha256') as h:
            h.return_value.hexdigest.return_value=digest or row['sha256_recurso']
            return variante_tabla_rom024(row,row['revision'] if text is None else text,b'fixture',row['capacidad'] if cap is None else cap,self.variants if variants is None else variants)
    def test_compacts_fit(self):
        self.assertEqual(len(self.rows),13)
        for row in self.rows:
            with self.subTest(unit=row['unit_id']):
                self.assertGreaterEqual(len(encode_script_text(row['revision'])),row['capacidad'])
                t,b,c=self.invoke(row)
                self.assertEqual((t,c),(row['compacto'],row['capacidad']))
                self.assertLess(len(b),c)
                self.assertNotIn(b'\0',b)
    def test_anchor_and_revision(self):
        row=self.rows[0]
        for altered in (dict(row,offset='1'),dict(row,recurso='ISO_START/char.dat'),dict(row,grupo_id='0')):
            self.assertIsNone(self.invoke(altered))
        self.assertIsNone(self.invoke(row,digest='bad'))
        self.assertIsNone(self.invoke(row,text='Otro'))
        self.assertIsNone(self.invoke(row,cap=23))
    def test_markers_and_square_button(self):
        row=self.variants['3269'];t,b,_=self.invoke(row)
        self.assertTrue(b.startswith('②'.encode('cp932')))
        self.assertIn('□'.encode('cp932'),b)
        for bad in (t[1:],t.replace('□',''),t.replace('②','③'),t+'\0',t+'\n'):
            self.assertIsNone(self.invoke(row,variants={row['unit_id']:dict(row,compacto=bad)}))
    def test_preflight_missing_and_wrong_original(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'Falta DLC'):verificar_dlc_originales(d)
            (Path(d)/'DL_JP_00.EDAT').write_bytes(b'not original')
            with self.assertRaisesRegex(ValueError,'no reconocido'):verificar_dlc_originales(d)
    def test_preflight_valid_synthetic_envelope(self):
        with tempfile.TemporaryDirectory() as d:
            from hashlib import sha256
            b=bytearray(2052);b[:8]=b'NISPACK\0';struct.pack_into('<II',b,8,0,1)
            struct.pack_into('<32sIII',b,16,b'start_jp.lzs',2048,4,0)
            for n in range(4):(Path(d)/f'DL_JP_{n:02d}.EDAT').write_bytes(b)
            with patch('dlc_originales.SHA_DLC',[sha256(b).hexdigest()]*4),patch('dlc_originales.SIZE_DLC',[len(b)]*4):
                self.assertEqual(len(verificar_dlc_originales(d)),4)
if __name__=='__main__':unittest.main()
