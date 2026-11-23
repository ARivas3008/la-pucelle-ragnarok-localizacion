import sys,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'app/scripts'),str(ROOT/'investigacion/v0.12')]
from fuentes_es import encode_es,encode_script_text,decode_es
from reubicador_anclas_v012 import Reubicador,Edicion
from construir_parche import sustituir_eboot_ascii

def consumo_motor(data):
    pos=0
    while pos<len(data):
        lead=data[pos];pos+=1
        if lead==0:return pos
        if lead==32:continue
        pos+=1
        if lead==45 or 46<=lead<127:pos-=1
    raise ValueError('Motor sobrepasó el búfer')

class Capturas(unittest.TestCase):
    def test_signos_originales_no_se_redibujan_ni_traducen(self):
        from formato_talk import inspect
        from recompilar_talk import compile_one
        raw=struct.pack('<10I',1,1,0,101,0,0,0,0,0,0)+b'\1'+'…………。'.encode('cp932')+b'\0\3'
        out,ok,bad,journal=compile_one('ISO_START/talk00.dat',raw,inspect(raw),{}, {})
        self.assertEqual(out,raw);self.assertFalse(ok);self.assertFalse(journal)
        self.assertEqual(bad[0]['motivo'],'SIGNOS_ORIGINALES_CONSERVADOS')

    def test_iglesia_no_amplia_un_offset_no_verificado(self):
        raw=bytearray(b'Church\0ABC')
        row=dict(recurso='ISO/PSP_GAME/SYSDIR/EBOOT.BIN',unit_id='3540',grupo_id='3025',offset='0',original='Church')
        changed,bad=sustituir_eboot_ascii(raw,[row],{}, {},{'Church':'Iglesia'},True)
        self.assertFalse(changed);self.assertTrue(bad)
        self.assertEqual(raw,b'Church\0ABC')

    def test_coma_no_consume_terminador_ni_restos(self):
        text='Aunque llevamos más tiempo en la Iglesia,'
        old=encode_es(text)
        self.assertGreater(consumo_motor(old+b'\0sia\0'),len(old)+1)
        new=encode_script_text(text)
        self.assertEqual(consumo_motor(new+b'\0sia\0'),len(new)+1)
        self.assertEqual(decode_es(new).replace('，',','),text)

    def test_puntos_suspensivos_originales(self):
        self.assertEqual(encode_script_text('...'),b'...')

    def test_tabla_ids_script_se_conserva(self):
        raw=struct.pack('<5I',2,0,8,2000001,2000002)+b'\x32\x06hello\0\x03'
        parser=Reubicador(raw)
        out,journal=parser.aplicar([Edicion(22,b'hello',b'Buenos dias','1')])
        self.assertEqual(Reubicador(out).identifiers,[2000001,2000002])
        self.assertEqual(Reubicador(out).pointers,[0,14])
        self.assertEqual(Reubicador.revertir(out,journal),raw)

    def test_iglesia_usa_reserva_y_no_toca_siguiente_campo(self):
        off=708478;raw=bytearray(off+24)
        raw[off:off+6]=b'Church';raw[-4:]=b'TEST'
        row=dict(recurso='ISO/PSP_GAME/SYSDIR/EBOOT.BIN',unit_id='3540',grupo_id='3025',offset=str(off),original='Church')
        changes,bad=sustituir_eboot_ascii(raw,[row],{}, {},{'Church':'Iglesia'},True)
        self.assertFalse(bad);self.assertIn('3540',changes)
        self.assertEqual(raw[off:off+8],b'Iglesia\0')
        self.assertEqual(raw[-4:],b'TEST')

if __name__=='__main__':unittest.main()
