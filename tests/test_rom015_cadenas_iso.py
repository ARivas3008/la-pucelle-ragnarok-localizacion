"""ROM-015: comprobar que la comparación física no interpreta prefijos como campos completos."""
import ast,unittest,unicodedata,re
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/'scripts/rom015_auditar_campos_y_scripts_iso.py'
fn=next(x for x in ast.parse(SOURCE.read_text(encoding='utf-8')).body
        if isinstance(x,ast.FunctionDef) and x.name=='cotejar_cadena')
ns={'canon':lambda s:re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('、',',').replace('。','.'))}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(SOURCE),'exec'),ns)
check=ns['cotejar_cadena']
class Fields(unittest.TestCase):
 def test_exact_kanji(self):self.assertEqual(check('魔王'.encode('cp932')+b'\0',0,'魔王'),'COINCIDE')
 def test_nfkc_anchura(self):self.assertEqual(check('ＡＢＣ'.encode('cp932')+b'\0',0,'ABC'),'COINCIDE')
 def test_prefijo_prohibido(self):self.assertEqual(check('ＢＯＮＵＳ'.encode('cp932')+b'\0',0,'BON'),'CONTENIDO_DISTINTO')
 def test_sufijo_diferente(self):self.assertEqual(check('魔王'.encode('cp932')+b'\0',0,'魔王さま'),'CONTENIDO_DISTINTO')
 def test_offset_fuera(self):self.assertEqual(check(b'A\0',2,'A'),'OFFSET_FUERA')
 def test_vacio(self):self.assertEqual(check(b'\0',0,'A'),'CADENA_VACIA')
 def test_sin_nul(self):self.assertEqual(check(b'AAA',0,'AAA'),'SIN_TERMINADOR')
 def test_codificacion_invalida(self):self.assertEqual(check(b'\x81\0',0,'X'),'CP932_INVALIDO')
if __name__=='__main__':unittest.main()
