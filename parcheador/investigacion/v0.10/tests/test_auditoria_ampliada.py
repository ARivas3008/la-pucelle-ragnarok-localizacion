import unittest,sys,os,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from auditoria_ampliada import nfk_norm, audit
from vincular_continuaciones import norm
from relocador import TablaTalk, Edicion, RelocacionError

ROOT=Path(__file__).parents[1]
ORIGINALS=Path(os.environ.get('LAPUCELLE_UNPACKED','/mnt/data/unpacked'))
MANIFEST=Path(os.environ.get('LAPUCELLE_MANIFEST','/mnt/data/lapucelle_v07/app/datos/mapa_26258_unidades.csv'))

class TestNormalizacion(unittest.TestCase):
    def test_japones_katakana_y_puntuacion(self):
        self.assertEqual(nfk_norm('　見てくれてる？）'),nfk_norm('見てくれてる?)'))
    def test_fullwidth_ingles_y_paddings(self):
        self.assertEqual(nfk_norm(' Ｉｔ ｉｓ  '), nfk_norm('It is'))
    def test_no_admitir_diferencias_de_significado(self):
        self.assertNotEqual(nfk_norm('No puede ir.'),nfk_norm('Puede ir.'))
    def test_no_confundir_cantidad_de_saltos(self):
        self.assertNotEqual(nfk_norm('a\nb'),nfk_norm('ab'))
    def test_normalizacion_compartida(self):
        self.assertEqual(nfk_norm('　ＡＢＣ　'),norm(' ABC '))

@unittest.skipUnless(ORIGINALS.is_dir() and MANIFEST.is_file(),'Los originales de juego y manifiesto no estan montados')
class TestReales(unittest.TestCase):
    def test_coincidencias_con_relleno(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            r=audit(MANIFEST,ORIGINALS,Path(tmp),stress=False)
            self.assertEqual(r['equivalencias_seguras_detectadas_por_relleno'],439)
            self.assertEqual(r['fuentes_normalizadas']['FUENTE_COINCIDE'],21312)
            self.assertEqual(r['fuentes_normalizadas']['COINCIDE_SOLO_CON_RELLENO'],439)
            self.assertEqual(r['continuaciones_cabecera_sin_mapa'],809)
            self.assertEqual(r['cadenas_consecutivas_extraidas_sin_unidad'],837)
    def test_las_21_tablas_permiten_ampliacion_structural(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            r=audit(MANIFEST,ORIGINALS,Path(tmp),stress=True)
            self.assertEqual(len(r['pruebas_expansion_masiva']),21)
            self.assertTrue(all(x['estado']=='EXITO' for x in r['pruebas_expansion_masiva']))
            self.assertEqual(sum(x['ediciones'] for x in r['pruebas_expansion_masiva']),21751)
    def test_no_sobreescribir_opcodes(self):
        original=ORIGINALS/'ISO_SCRIPT/talk01_jp.dat'
        t=TablaTalk(original.read_bytes())
        with self.assertRaises(RelocacionError):
            t.aplicar([Edicion(33640,b'x',b'y')])
    def test_dos_ediciones_pueden_aumentar_los_bytes(self):
        original=ORIGINALS/'ISO_SCRIPT/talk01_jp.dat'
        b=original.read_bytes();t=TablaTalk(b);ed=[]
        for pos in (33641,33677):
            end=b.index(0,pos)
            ed.append(Edicion(pos,b[pos:end],b[pos:end]+b'\x82\xA0'))
        patched,ofs=t.aplicar(ed)
        self.assertEqual(len(patched),len(b)+4)
        self.assertEqual(len(ofs),2)

if __name__=='__main__':unittest.main()
