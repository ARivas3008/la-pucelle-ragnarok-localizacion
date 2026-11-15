"""Fixtures artificiales: no requieren archivos comerciales."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrar_scripts_v014 import match, plan, Peligro, contains_unsafe_reference

class TestScripts(unittest.TestCase):
    def build(self, raw,ptrs):
        return struct.pack('<I',len(ptrs))+struct.pack('<%dI'%len(ptrs),*ptrs)+raw

    def test_fuente_exacta_y_espacios(self):
        self.assertEqual(match(b'hello  \0',0,'hello'),b'hello  ')
        self.assertIsNone(match(b'hello  \0',0,'world'))
        self.assertIsNone(match(b'hello  \0',100,'hello'))

    def test_texto_largo_reubicable_sin_dividir(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*15,[0,8])
        off=4+8+2
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':off,'original':'hello','es_revisado':'Hola, mundo entero','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(counts['REUBICACION_ESTRUCTURAL'],1)
        self.assertEqual(ch['ISO_START/script00.dat']['cadenas'],1)
        self.assertIn(b'Hola, mundo entero',ch['ISO_START/script00.dat']['raw'])

    def test_preserva_now_loading(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':10,'original':'Now Loading','es_revisado':'Cargando','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['EXCLUIDO_NOW_LOADING'],1)

    def test_estado_no_aprobado(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':10,'original':'hello','es_revisado':'hola','estado_editorial':'requiere_investigacion'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['PENDIENTE_EDITORIAL'],1)

    def test_puntero_dentro_de_caracter(self):
        raw=self.build(b'\x32\x03\x81\x40\0'+b'\0'*10,[0,3])
        off=4+8+2
        self.assertTrue(contains_unsafe_reference(raw,off,b'\x81\x40'))
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':off,'original':'　','es_revisado':'Texto largo','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(counts['REFERENCIA_SUBCARACTER'],1)
        self.assertEqual(ch,{})
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw},mode='experimental')
        self.assertEqual(counts['REUBICACION_ESTRUCTURAL'],1)

    def test_original_malo_no_se_toca(self):
        raw=self.build(b'\x32\x06hello\0'+b'\0'*10,[0])
        rows={'ISO_START/script00.dat':[{'unit_id':'1','offset':10,'original':'wrong','es_revisado':'hola','estado_editorial':'revisado'}]}
        ch,rs,counts=plan(rows,{'ISO_START/script00.dat':raw})
        self.assertEqual(ch,{})
        self.assertEqual(counts['NO_COINCIDE_ORIGINAL'],1)

if __name__=='__main__':unittest.main()