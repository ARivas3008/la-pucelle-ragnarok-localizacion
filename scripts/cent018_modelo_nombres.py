"""CENT-018 — modelo estructural del ensamblador de nombres de La Pucelle PSP.

El EBOOT de la ISO original concatena los campos con strcpy/strcat y exige
strlen <=16 bytes: clase1 nombre+fragmento; clase2 fragmento+nombre;
clase3 ambos sentidos con probabilidad comparable.

No escribe ISO/DLC, no decide traducciones y no simula calidad visual.
"""
import argparse,csv,json
from pathlib import Path

class CombinacionInvalida(ValueError):pass
SLOT_TEXT_BYTES=12
MAX_NAME_BYTES=16
CLASS_SUFFIX=1
CLASS_PREFIX=2
CLASS_EITHER=3

def codificar(texto):
 if not isinstance(texto,str) or not texto or '\x00' in texto:
  raise CombinacionInvalida("Nombre vacío o con NUL")
 try:return texto.encode('cp932')
 except UnicodeError as ex:raise CombinacionInvalida('Nombre no codificable en CP932') from ex

def comprobar_slot(fragmento):
 encoded=codificar(fragmento)
 # El slot reserva 12 bytes incluyendo terminador NUL.
 if len(encoded)>=SLOT_TEXT_BYTES:
  raise CombinacionInvalida('Fragmento excede 11 bytes útiles del slot fijo')
 return encoded

def combinar(base,fragmento,clase,sentido=None):
 if clase not in (1,2,3):raise CombinacionInvalida('Clase name.dat inválida')
 base_raw=codificar(base)
 frag_raw=comprobar_slot(fragmento)
 if clase==3:
  if sentido not in (1,2):
   raise CombinacionInvalida('Clase 3 exige modelar cada sentido de manera explícita')
  actual=sentido
 else:
  if sentido is not None and sentido!=clase:
   raise CombinacionInvalida('Sentido contradictorio con clase original')
  actual=clase
 result=base_raw+frag_raw if actual==1 else frag_raw+base_raw
 if len(result)>MAX_NAME_BYTES:
  raise CombinacionInvalida('Nombre generado excede 16 bytes, el motor reintentaría')
 return result.decode('cp932')

def evaluar(propuestas,bases):
 """Recibe (ID, clase, fragmento ES) y comprueba todas las bases propuestas."""
 records=[]
 for gid,clase,texto in propuestas:
  positions=(1,2) if clase==3 else (clase,)
  ok=0;rejected=0;samples=[]
  for base in bases:
   for pos in positions:
    try:
     result=combinar(base,texto,clase,pos)
     ok+=1
     if len(samples)<4:samples.append(result)
    except CombinacionInvalida:
     rejected+=1
  records.append(dict(id=gid,clase=clase,propuesta=texto,
                      combinaciones_validas=ok,combinaciones_rechazadas=rejected,
                      ejemplos=samples,certificado_visual=False))
 return records

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--propuestas',type=Path,required=True,
                help='CSV con id,clase,es_propuesta; no aprobará nada automáticamente')
 p.add_argument('--bases',nargs='+',required=True,help='Nombres base de prueba')
 p.add_argument('--informe',type=Path,required=True)
 a=p.parse_args()
 with a.propuestas.open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f)
  cols=set(r.fieldnames or [])
  if {'grupo_id','clase_mips','es_propuesta'}.issubset(cols):
   idkey='grupo_id';classkey='clase_mips'
  elif {'id','clase','es_propuesta'}.issubset(cols):
   idkey='id';classkey='clase'
  else:p.error('Faltan columnas id/clase o grupo_id/clase_mips y es_propuesta')
  inp=[(row[idkey],int(row[classkey]),row['es_propuesta']) for row in r if row['es_propuesta'].strip()]
 result={'evidencia':'B: simulación con algoritmo MIPS auténtico; no PPSSPP',
         'limite_slot_bytes_con_nul':SLOT_TEXT_BYTES,'limite_nombre_bytes':MAX_NAME_BYTES,
         'bases_de_prueba':a.bases,'conteo_propuestas':len(inp),
         'simulaciones':evaluar(inp,a.bases),'aprobaciones_editoriales':0}
 a.informe.parent.mkdir(parents=True,exist_ok=True)
 a.informe.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Simulados',len(inp),'fragmentos; sin aprobaciones automáticas')
if __name__=='__main__':main()
