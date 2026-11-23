"""Regresiones sintéticas de prefijos de magic.dat. No prueban EDAT reales."""
import sys
import unittest
import unicodedata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from construir_parche import match_source
from campos_revisados import conservar_icono
from campos_fijos import capacidad_verificada, ampliar_campo
from fuentes_es import encode_script_text

class TestPrefijosMagicV020(unittest.TestCase):
    def test_nfkc_marcadores_circulares(self):
        for marker,digit in [('①','1'),('②','2'),('③','3')]:
            with self.subTest(marker=marker):
                self.assertEqual(unicodedata.normalize('NFKC',marker),digit)
                raw=(marker+'UFOでダメージ').encode('cp932')
                style,matched=match_source(raw+b'\0',0,digit+'UFOでダメージ')
                self.assertEqual(matched,raw)
                self.assertEqual(conservar_icono(matched,'Inflige daño.'),marker+'Inflige daño.')
                self.assertEqual(conservar_icono(matched,digit+' Inflige daño.'),marker+'Inflige daño.')
                self.assertEqual(conservar_icono(matched,marker+'Inflige daño.'),marker+'Inflige daño.')

    def test_rechaza_supuesto_de_circulo_si_no_existe(self):
        for source in ['１UFOでダメージ','1UFOでダメージ']:
            with self.subTest(source=source):
                src=source.encode('cp932')
                self.assertEqual(conservar_icono(src,'Inflige daño.'),'Inflige daño.')
        # La política de prefijos del contenido no se adivina sin su EDAT original.

    def test_reserva_descripcion_conserva_resto_de_registro(self):
        stride=116
        offset=8+stride*21+41
        buf=bytearray(8+stride*22)
        source='①強烈な跳び蹴りで相手を爆砕!'.encode('cp932')
        buf[offset:offset+len(source)]=source
        buf[offset+len(source)]=0
        original=bytes(buf)
        cap=capacidad_verificada('DLC_00/magic.dat',buf,offset,len(source))
        self.assertEqual(cap,57)
        _,matched=match_source(buf,offset,'1強烈な跳び蹴りで相手を爆砕!')
        self.assertEqual(matched,source)
        data=encode_script_text(conservar_icono(matched,'Patada demoledora'))
        self.assertTrue(data.startswith('①'.encode('cp932')))
        edited=ampliar_campo(bytes(buf[offset:offset+cap]),len(source),data,cap)
        buf[offset:offset+cap]=edited
        self.assertEqual(len(buf),len(original))
        self.assertEqual(bytes(buf[:offset]),original[:offset])
        self.assertEqual(bytes(buf[offset+cap:]),original[offset+cap:])
        self.assertEqual(bytes(buf[offset:offset+2]),'①'.encode('cp932'))

if __name__=='__main__':
    unittest.main()
