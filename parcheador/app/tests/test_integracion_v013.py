"""Regresiones del puente v0.12 -> v0.13: fail-closed y sin sobrescribir otros datos."""
import csv,sys,unittest,copy,tempfile
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from integracion_v013 import aplicar,cargar_propuestas,IntegracionError
from construir_parche import match_source

class IntegracionV013(unittest.TestCase):
 def preparacion(self):
  raw=bytearray(b'\0'*208)
  old='Prueba'.encode('cp932')
  raw[8:8+len(old)+1]=old+b'\0'
  raw[32:36]=b'\xaa\xbb\xcc\xdd'
  uid='X1';res='ISO_START/char.dat'
  manifest=[{'unit_id':uid,'grupo_id':'G1','original':'Prueba','recurso':res,'offset':'8'}]
  report=[{'unit_id':uid,'grupo_id':'G1','estado':'BLOQUEADO_CODIFICACION_O_TAMANO',
           'estado_editorial':'revisado','es_revisado':'Prueba extraordinaria','motivo':''}]
  proposal=[{'unit_id':uid,'grupo_id':'G1','recurso':res,'original':'Prueba','es_revisado':'Prueba extraordinaria',
             'tipo':'TABLA_FIJA','propuesta':'Muy buena','estado_propuesta':'CABE_ESTRUCTURAL'}]
  return raw,manifest,report,proposal,res
 def prueba(self,raw,manifest,report,proposal,res,reviews=None,**kwargs):
  return aplicar(proposal,manifest,report,{res:raw},None,defaultdict(list),{},match_source,
                reviews or {'G1':{'es_revisado':'Prueba extraordinaria'}},fuentes_activas=False,**kwargs)
 def test_terminadores_y_metadatos_intactos(self):
  raw,manifest,report,proposal,res=self.preparacion();antes=bytes(raw)
  r=self.prueba(raw,manifest,report,proposal,res)
  self.assertEqual(r['conteos'].get('APLICADO_REDUCCION_ESTRUCTURAL'),1)
  self.assertEqual(raw[8:8+10],b'Muy buena\0')
  self.assertEqual(raw[:8],antes[:8]);self.assertEqual(raw[32:],antes[32:]);self.assertEqual(len(raw),len(antes))
 def test_no_sobrescribe_una_unidad_ya_insertada(self):
  raw,manifest,report,proposal,res=self.preparacion();report[0]['estado']='APLICADO'
  original=raw[:];r=self.prueba(raw,manifest,report,proposal,res)
  self.assertEqual(raw,original);self.assertEqual(r['conteos'].get('YA_MODIFICADO'),1)
 def test_traduccion_actualizada_bloquea_propuesta_antigua(self):
  raw,manifest,report,proposal,res=self.preparacion();original=raw[:]
  r=self.prueba(raw,manifest,report,proposal,res,reviews={'G1':{'es_revisado':'Otro texto actual'}})
  self.assertEqual(raw,original);self.assertEqual(r['conteos'].get('TRADUCCION_DESACTUALIZADA'),1)
 def test_editorial_no_revisado_bloquea(self):
  raw,manifest,report,proposal,res=self.preparacion();report[0]['estado_editorial']='requiere_investigacion'
  r=self.prueba(raw,manifest,report,proposal,res)
  self.assertEqual(r['conteos'].get('SIN_REVISION_EDITORIAL'),1)
 def test_now_loading_protegido(self):
  raw,manifest,report,proposal,res=self.preparacion();proposal[0]['original']='Now Loading'
  manifest[0]['original']='Now Loading'
  r=self.prueba(raw,manifest,report,proposal,res)
  self.assertEqual(r['conteos'].get('NOW_LOADING_PROTEGIDO'),1)
 def test_no_supera_capacidad(self):
  raw,manifest,report,proposal,res=self.preparacion();original=raw[:]
  proposal[0]['propuesta']='Un texto demasiado extenso para este campo'
  r=self.prueba(raw,manifest,report,proposal,res)
  self.assertEqual(r['conteos'].get('RECHAZADO_ESTRUCTURAL'),1);self.assertEqual(raw,original)
 def test_csv_rechaza_duplicados(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'reducciones.csv'
   _,_,_,rows,_=self.preparacion()
   with p.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows+rows)
   with self.assertRaises(IntegracionError):cargar_propuestas(p)
 def test_eboot_solo_ascii_con_longitud_original(self):
  raw,manifest,report,proposal,res=self.preparacion()
  source='Continue';es='Seguir';off=12
  eboot=bytearray(b'\0'*100);eboot[off:off+len(source)+1]=source.encode()+b'\0'
  resource='ISO/PSP_GAME/SYSDIR/EBOOT.BIN';manifest[0].update(recurso=resource,original=source,offset=str(off))
  proposal[0].update(recurso=resource,original=source,tipo='EBOOT',propuesta=es)
  ret=aplicar(proposal,manifest,report,{},eboot,defaultdict(list),{},match_source,
             {'G1':{'es_revisado':'Prueba extraordinaria'}},fuentes_activas=False)
  self.assertEqual(ret['conteos'].get('APLICADO_REDUCCION_EBOOT'),1)
  self.assertEqual(eboot[off:off+len(source)],b'Seguir  ')
  self.assertEqual(eboot[off+len(source)],0)

if __name__=='__main__':unittest.main()
