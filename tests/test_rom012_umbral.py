"""ROM-012: no premiar porcentajes sin fuentes auténticas ni denominador completo."""
import importlib.util,copy,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'scripts/umbral_rom012.py'
spec=importlib.util.spec_from_file_location('umbral_rom012',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def fixture(n=25956):
 total=26258
 return ({'alcance':'ISO_Y_CUATRO_DLC','unidades_total':total,
  'unidades_alcance_auditado':total,'unidades_no_evaluadas_por_ausencia_dlc':0,
  'unidades_insertadas_verificadas':n,
  'estados':{'TALK_BLOQUE_INSERTADO':n,'TALK_PENDIENTE':total-n},
  'originales_autenticados':{'iso_sha256':m.ISO_BASE_SHA,
   'dlc_sha256':{f'DL_JP_{i:02d}.EDAT':f'{i+1:064x}' for i in range(4)}},
  'sha256':'a'*64,'recursos_compilados_releidos':[{'recurso':'ISO_START/talk00.dat','sha256':'b'*64}]},
  {'editorial_catalogo':{'revisados_editoriales_conocidos':15346,'total_grupos_conocidos':15525}})
class Umbral(unittest.TestCase):
 def test_25956_alcanza_ratio_editorial(self):
  c,e=fixture();result=m.comprobar(c,e)
  self.assertEqual(result['objetivo_minimo'],25956)
  self.assertEqual(result['porcentaje_tecnico'],98.85)
 def test_25955_no_alcanza(self):
  c,e=fixture(25955)
  with self.assertRaisesRegex(m.CoberturaInvalida,'Faltan 1'):m.comprobar(c,e)
 def test_iso_sola_rechazada(self):
  c,e=fixture();c['alcance']='ISO_SOLA'
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
 def test_dlc_sin_comprobar_rechazado(self):
  c,e=fixture();c['unidades_no_evaluadas_por_ausencia_dlc']=3537
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
 def test_original_no_autenticado_rechazado(self):
  c,e=fixture();c['originales_autenticados']['iso_sha256']='0'*64
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
 def test_no_cuatro_hashes_dlc_rechazado(self):
  c,e=fixture();c['originales_autenticados']['dlc_sha256'].pop('DL_JP_03.EDAT')
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
 def test_no_doble_contabilidad(self):
  c,e=fixture();c['estados']['CAMPO_COINCIDE_REVISION']=1
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
 def test_sin_diarios_rechazado(self):
  c,e=fixture();c['recursos_compilados_releidos']=[]
  with self.assertRaises(m.CoberturaInvalida):m.comprobar(c,e)
if __name__=='__main__':unittest.main()
