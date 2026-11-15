import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from construir_parche import cadenas_dialogo,sustituir_eboot_ascii,leer_refinamientos,to_full
from segmentacion import repartir
from fuentes_es import encode_es

class ProteccionesV05(unittest.TestCase):
    def test_concatena_solo_opcode_literal_01(self):
        key='ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat'
        data=bytearray(b'\x01Hello\x00\x01World\x00\x02')
        rows=[{'unit_id':'1','grupo_id':'1','recurso':key,'offset':'1','original':'Hello'},
              {'unit_id':'2','grupo_id':'2','recurso':key,'offset':'8','original':'World'}]
        chains, ids, orphan = cadenas_dialogo(rows,{key:data})
        self.assertEqual(len(chains),1)
        self.assertEqual([x['unit_id'] for x in chains[0]],['1','2'])
        self.assertEqual(ids,{'1','2'})
        self.assertFalse(orphan)

    def test_marca_cadena_incompleta(self):
        key='ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat'
        b=bytearray(b'\x01Hello\x00\x01World\x00\x02')
        rows=[{'unit_id':'1','grupo_id':'1','recurso':key,'offset':'1','original':'Hello'}]
        chains, ids, orphan=cadenas_dialogo(rows,{key:b})
        self.assertFalse(chains)
        self.assertEqual(orphan,{'1'})

    def test_eBOOT_ascii_mismos_offsets_y_terminadores(self):
        p=bytearray(b'XXXXXXXXStart     \x00\x00Continue  \x00\x00Settings\x00YYYY')
        original=p[:]
        records=[]
        for id,off,src,dst in [('3091',8,'Start','Empezar'),('3092',20,'Continue','Continuar'),('3093',32,'Settings','Opciones')]:
            records.append({'unit_id':id,'grupo_id':id,'recurso':'ISO/PSP_GAME/SYSDIR/EBOOT.BIN','offset':str(off),'original':src})
        reviews={r['grupo_id']:{'estado':'revisado','es_revisado':dst} for r,dst in zip(records,['Empezar','Continuar','Opciones'])}
        changes,fail=sustituir_eboot_ascii(p,records,reviews,{})
        self.assertFalse(fail)
        self.assertEqual(len(changes),3)
        self.assertEqual(len(p),len(original))
        self.assertEqual(p[8:18],b'Empezar   ')
        self.assertEqual(p[20:30],b'Continuar ')
        self.assertEqual(p[32:40],b'Opciones')
        for start,end in [(0,8),(18,20),(30,32),(40,len(p))]:
            self.assertEqual(p[start:end],original[start:end])

    def test_reflujos_de_las_capturas(self):
        enc=lambda x:encode_es(to_full(x))
        for src,caps in [ ('¡Ya estoy harta! ¡No aguanto más!',[36,36]),
                          ('¡No digas eso! El padre Salade tiene razón.',[46,46])]:
            chunks=repartir(src,caps,encoder=enc)
            self.assertEqual(' '.join(chunks),src)
            for c,limit in zip(chunks,caps):self.assertLessEqual(len(enc(c)),limit)

    def test_nunca_parchear_textos_utf8_en_el_eBOOT_sin_fuente(self):
        b=bytearray(b'Settings\0')
        r={'unit_id':'1','grupo_id':'1','recurso':'ISO/PSP_GAME/SYSDIR/EBOOT.BIN','offset':'0','original':'Settings'}
        ch,fail=sustituir_eboot_ascii(b,[r],{'1':{'estado':'revisado','es_revisado':'Opcióñ'}},{})
        self.assertFalse(ch)
        self.assertTrue(fail)
        self.assertEqual(b,b'Settings\0')

if __name__=='__main__':unittest.main()
