import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrar_scripts_v014 import load_rows,Peligro

class TestSnapshot(unittest.TestCase):
    def test_segunda_fase_consulta_revision_y_estado_actuales(self):
        with tempfile.TemporaryDirectory() as td:
            m=Path(td)/'manifest.csv';r=Path(td)/'report.csv'
            item=dict(unit_id='1',grupo_id='99',recurso='ISO_START/script00.dat',offset='10',original='hello')
            for path,row in ((m,item),(r,dict(item,es_revisado='Antiguo',estado_editorial='revisado'))):
                with path.open('w',newline='',encoding='utf-8') as f:
                    w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
            with patch('construir_parche.read_reviews',return_value=({'99':{'es_revisado':'Texto actual','estado':'requiere_investigacion'}},[],{})):
                got=load_rows(m,r,'snapshot')['ISO_START/script00.dat'][0]
            self.assertEqual(got['es_revisado'],'Texto actual')
            self.assertEqual(got['estado_editorial'],'requiere_investigacion')
            with r.open('a',newline='',encoding='utf-8') as f:
                csv.writer(f).writerow(['1','99','ISO_START/script00.dat','10','hello','Duplicado','revisado'])
            with self.assertRaises(Peligro):load_rows(m,r)

if __name__=='__main__':unittest.main()
