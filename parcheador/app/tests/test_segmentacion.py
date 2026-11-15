import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from segmentacion import repartir,SegmentacionError
from fuentes_es import encode_es

class TestReparticion(unittest.TestCase):
    def test_roundtrip_sin_desperdicio(self):
        text='¿Cómo estás hoy?'
        r=repartir(text,[12,12])
        self.assertEqual(' '.join(r),text)
        self.assertEqual(len(r),2)
        self.assertTrue(all(len(encode_es(c))<=n for c,n in zip(r,[12,12])))
    def test_sin_modificar_palabras(self):
        text='Hola, mundo maravilloso'
        r=repartir(text,[15,16])
        self.assertEqual(r,['Hola, mundo','maravilloso'])
    def test_rechaza_overflow(self):
        with self.assertRaises(SegmentacionError):repartir('palabras enormes que no caben',[4,4])
    def test_reparticion_ancho_respeta_espacios_dos_bytes(self):
        from construir_parche import safe_encoding, to_full, Fail
        from fuentes_es import encode_es
        enc=lambda t:encode_es(to_full(t))
        # En ancho completo también los espacios ocupan dos bytes.
        self.assertEqual(len(enc('A B')), 6)
        with self.assertRaises(SegmentacionError):
            repartir('A B C', [4, 4], encoder=enc)
        trozos=repartir('A B C', [6,4],encoder=enc)
        self.assertEqual(' '.join(trozos),'A B C')
        for trozo,cap in zip(trozos,[6,4]):
            self.assertEqual(len(safe_encoding(trozo,'ancho',cap,fuentes_es=True)),cap)
    def test_overflow_codificador_en_una_caja(self):
        from construir_parche import safe_encoding, Fail
        # Antes esto escapaba sin capturar desde la preparacion de segmentos.
        with self.assertRaisesRegex(Fail,'excede'):
            safe_encoding('A'*52,'normal',36,fuentes_es=True)
    def test_rechaza_control(self):
        with self.assertRaises(SegmentacionError):repartir('¡Hola!\\nAdiós',[7,8])
        with self.assertRaises(SegmentacionError):repartir('Nombre: %s',[8,9])

if __name__=='__main__':unittest.main()
