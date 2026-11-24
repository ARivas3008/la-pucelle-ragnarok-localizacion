"""CENT-017: inspección estructural, conservadora, de ISO_START/name.dat.

Identifica slots de 16 bytes y clases usadas por el generador de nombres.
NO determina el orden de concatenación, no traduce términos sin contexto
ni convierte revisiones pendientes en aprobadas. Solo exporta metadatos.
"""
import argparse,csv,collections,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'parcheador/app/scripts'))
import construir_parche as c
from nis_formats import lzs_decompress
ISO_SHA='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
MASTER=ROOT/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv'
def slots(data):
 if len(data)<16:raise ValueError('name.dat demasiado pequeño')
 declared,duplicate=struct.unpack_from('<II',data,0)
 if declared!=duplicate or declared<=0:raise ValueError('cabeceras de cantidad incoherentes')
 result=[]
 off=8
 while off+16<=len(data):
  row=data[off:off+16]
  kind=row[3]
  if row[2]!=1 or kind not in (1,2,3):
   raise ValueError('tipo de nombre no reconocido en '+str(off))
  name=row[4:].split(b'\0',1)[0]
  if not name:raise ValueError('slot nominal vacío '+str(off))
  if not (b'\0' in row[4:]):raise ValueError('slot sin terminador NUL '+str(off))
  try:name.decode('cp932')
  except UnicodeError:raise ValueError('caracteres originales fuera CP932 '+str(off))
  result.append(dict(offset=off+4,clase=kind,codigo=row[0]+256*row[1]))
  off+=16
 if any(data[off:]):raise ValueError('datos no nulos después de slots')
 return declared,result
def audit(iso,master=MASTER):
 if c.sha_file(iso)!=ISO_SHA:raise ValueError('ISO original no autenticada')
 im=c.Image(iso);rec={p:(o,n) for p,o,n,_ in im.records()}
 start=im.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])
 members=c.members_from_dat(lzs_decompress(start,allow_overlap=False))
 buf=bytes(members['name.dat']);n,records=slots(buf)
 with master.open(encoding='utf-8-sig',newline='') as f:
  units=[r for r in csv.DictReader(f) if r['recurso']=='ISO_START/name.dat']
 off={x['offset']:x for x in records}
 missing=[u['unit_id'] for u in units if int(u['offset']) not in off]
 if missing:raise ValueError('unidades no alineadas con slots: '+str(missing[:5]))
 known={int(u['offset']) for u in units}
 counts=collections.Counter(x['clase'] for x in records)
 return dict(evidencia='A: ISO original auténtica; estructura de nombres, NO combinaciones jugables',
  iso_sha256=ISO_SHA,name_dat_sha256=c.sh(buf),bytes=len(buf),
  declarados_cabecera=n,slots_decodificados=len(records),
  slots_adicionales_tras_cabecera=len(records)-n,
  clases={str(k):v for k,v in sorted(counts.items())},
  unidades_manifiesto=len(units),slots_sin_unit_id=len(records)-len(known),
  encabezado_doble_coincidente=True,unidad_fuera_de_slot=0,
  advertencias=[
   'No inferir que el número de cabecera equivale a todos los slots decodificables',
   'Los tres códigos de clase NO demuestran su función gramatical',
   'No aprobar 58 fragmentos de generador hasta identificar concatenación/uso y validar en pantalla',
   'No exportar aquí cadenas del juego ni modificar bytes originales'],
  aprobaciones_editoriales_derivadas=0)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--iso',required=True,type=Path)
 p.add_argument('--informe',required=True,type=Path)
 a=p.parse_args();j=audit(a.iso);a.informe.parent.mkdir(parents=True,exist_ok=True)
 a.informe.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(j,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
