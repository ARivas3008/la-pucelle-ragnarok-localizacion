"""Fixtures artificiales: no requieren archivos comerciales."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrar_scripts_v014 import match, plan, Peligro, contains_unsafe_reference, carga_dlc_rom029
from unittest.mock import patch

class TestScripts(unittest.TestCase):
    def build(self, raw,ptrs):
        return struct.pack('<I',len(ptrs))+struct.pack('<%dI'%len(ptrs),*ptrs)+struct.pack('<%dI'%len(ptrs),*range(100,100+len(ptrs)))+raw

    def test_fuente_exacta_y_espacios(self):
        self.assertEqual(match(b'hello  \0',0,'hello'),b'hello  ')
        self.assertIsNone(match(b'hello  \0',0,'world'))
        self.assertIsNone(match(b'hello  \0',100,'hello'))

    def test_texto_largo_reubicable_sin_dividir(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*15,[0,8])
        off=4+16+2
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':off,'original':'hello','es_revisado':'Hola, mundo entero','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(counts['REUBICACION_ESTRUCTURAL'],1)
        self.assertEqual(ch['ISO_START/script00.dat']['cadenas'],1)
        self.assertIn('Hola， mundo entero'.encode('cp932'),ch['ISO_START/script00.dat']['raw'])

    def test_preserva_now_loading(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':14,'original':'Now Loading','es_revisado':'Cargando','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['EXCLUIDO_NOW_LOADING'],1)

    def test_estado_no_aprobado(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':14,'original':'hello','es_revisado':'hola','estado_editorial':'requiere_investigacion'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['PENDIENTE_EDITORIAL'],1)

    def test_puntero_dentro_de_caracter(self):
        raw=self.build(b'\x32\x03\x81\x40\0'+b'\0'*10,[0,3])
        off=4+16+2
        self.assertTrue(contains_unsafe_reference(raw,off,b'\x81\x40'))
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':off,'original':'　','es_revisado':'Texto largo','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(counts['REFERENCIA_SUBCARACTER'],1)
        self.assertEqual(ch,{})
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw},mode='experimental')
        self.assertEqual(counts['REUBICACION_ESTRUCTURAL'],1)

    def test_original_malo_no_se_toca(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':14,'original':'wrong','es_revisado':'hola','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['NO_COINCIDE_ORIGINAL'],1)


    def test_rom029_excepcion_delimitada(self):
        raw=bytearray(882041)
        raw[882020:882041]=bytes.fromhex('32138cbb8ddd93c782dd8d9e82dd92868163816300')
        r=dict(unit_id='1744',offset=882022,original='現在読み込み中......',
               es_revisado='Cargando...',estado_editorial='revisado')
        res='DLC_00/script00.dat'
        self.assertFalse(carga_dlc_rom029(res,r,raw))
        with patch('integrar_scripts_v014.sha',return_value='539dcc66c6233471a0814bad296bce709602fbbfa9b566faac5be0337d059eae'):
            self.assertTrue(carga_dlc_rom029(res,r,raw))
            self.assertFalse(carga_dlc_rom029('ISO_START/script00.dat',r,raw))
            for changed in (dict(r,unit_id='1745'),dict(r,offset=882023),
                            dict(r,original='Now Loading'),dict(r,es_revisado='Cargando'),
                            dict(r,estado_editorial='pendiente')):
                self.assertFalse(carga_dlc_rom029(res,changed,raw))
            raw[882021]=0
            self.assertFalse(carga_dlc_rom029(res,r,raw))

if __name__=='__main__':unittest.main()