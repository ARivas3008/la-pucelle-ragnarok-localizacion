import unittest,csv,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from informe_integracion_v012 import hacer
ROOT=Path(__file__).resolve().parents[2]
V=ROOT/'v0.12'

def table(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

class TestBalancesV012(unittest.TestCase):
 def test_843_unidades_sin_duplicados(self):
  rows=table(ROOT.parent/'informes/estado_unificado_66.csv')
  blocked=[r for r in rows if r['estado_tecnico'] not in ('CANDIDATO_DAT','CANDIDATO_EBOOT')]
  self.assertEqual(len(rows),4507)
  self.assertEqual(len(blocked),843)
  self.assertEqual(len({r['unit_id'] for r in blocked}),843)
 def test_consolidacion_completa_reproduce_resultado(self):
  with tempfile.TemporaryDirectory() as d:
   result=hacer(ROOT.parent/'informes/estado_unificado_66.csv',V/'propuestas_reduccion.csv',V/'ensayo_scripts/auditoria_scripts.csv',V/'ensayo_especiales/casos_especiales.csv',d)
   self.assertEqual(result['nuevas_simulaciones_estructurales_satisfactorias'],296)
   self.assertEqual(result['pendientes_sin_validacion_estructural_conservadora'],547)
   self.assertEqual(sum(result['estados'].values()),843)
 def test_script_modo_seguro_y_experimental(self):
  a=json.loads((V/'ensayo_scripts/resumen_scripts.json').read_text())
  b=json.loads((V/'ensayo_scripts_experimental/resumen_scripts.json').read_text())
  self.assertEqual(a['estados']['REUBICACION_ESTRUCTURAL_OK'],489)
  self.assertEqual(a['estados']['ANCLA_SUBCARACTER_NO_RESUELTA'],14)
  self.assertEqual(b['estados']['REUBICACION_ESTRUCTURAL_OK'],503)
  self.assertEqual(b['correcciones_subcaracter'],15)

if __name__=='__main__':unittest.main()
