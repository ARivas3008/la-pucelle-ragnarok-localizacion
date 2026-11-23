import csv
import io
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from construir_parche import read_reviews, match_source
from integracion_v013 import aplicar

class TestIntegracion018(unittest.TestCase):
    def test_reducciones_respetan_eboot_protegido(self):
        for protected in (True,False):
            with self.subTest(protegido=protected):
                raw=bytearray(b'XXXXContinue\0SENTINEL')
                original=bytes(raw)
                resource='ISO/PSP_GAME/SYSDIR/EBOOT.BIN'
                manifest=[dict(unit_id='1',grupo_id='1',recurso=resource,original='Continue',offset='4')]
                report=[dict(unit_id='1',estado='BLOQUEADO',estado_editorial='revisado')]
                proposal=[dict(unit_id='1',grupo_id='1',recurso=resource,original='Continue',
                               es_revisado='Continuar',propuesta='Seguir',tipo='EBOOT',estado_propuesta='CABE_ESTRUCTURAL')]
                result=aplicar(proposal,manifest,report,{},raw,defaultdict(list),{},match_source,
                               {'1':{'es_revisado':'Continuar'}},conservar_eboot=protected)
                if protected:
                    self.assertEqual(bytes(raw),original)
                    self.assertEqual(result['eboot_cambios'],{})
                else:
                    self.assertEqual(raw,bytearray(b'XXXXSeguir  \0SENTINEL'))

    def test_csv_multilinea_no_elimina_controles(self):
        # Todas las revisiones se simulan; prueba el lector real y su censo exacto.
        blobs=[]
        for n in range(15):
            f=io.StringIO(newline='');w=csv.writer(f)
            w.writerow(['grupo_id','es_revisado','estado'])
            for j in range(1001 if n<1 else 1000 if n<14 else 1015):
                w.writerow([f'{n}-{j}','Línea uno\nLínea dos' if n==0 and j==0 else 'Hola','revisado'])
            blobs.append(f.getvalue().encode('utf-8'))
        with patch.object(Path,'exists',return_value=True),patch.object(Path,'read_bytes',side_effect=blobs):
            reviews,_,_=read_reviews('snapshot',False)
        self.assertEqual(reviews['0-0']['es_revisado'],'Línea uno\nLínea dos')

if __name__=='__main__':unittest.main()
