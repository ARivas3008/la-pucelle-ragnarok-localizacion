from pathlib import Path
import csv,json,re
B=Path(__file__).resolve().parent
fixed={'12934':'Enfermería','12935':'Cuarto de Salade','136':'Cuarto de Salade','13926':'Panza del Diablo'}
fixed.update({'1754':'Esta joven sería conocida como «Prier, Señora Demonio»:','1757':'Esta joven sometería a todos los grandes señores demonio',
 '3308':'Como nosotros, es hermana de la orden de La Pucelle.',
 '3476':'como chivos expiatorios o traidores y los juzgaban.',
 '3581':'Esta es la historia de Prier, que sería conocida como',
 '3715':'Desde entonces, cesaron los rumores sobre el Príncipe',
 '14531':'quería ser Doncella de la Luz y fue Gran Señora Demonio.'})
changes=[];suspects=[]
for path in sorted((B/'fuente/corpus').glob('*/revision.csv')):
 with path.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 dirty=False
 for row in rows:
  old=row['es_revisado'];new=fixed.get(row['grupo_id'],old)
  for before,after in [('del Estómago del Diablo','de la Panza del Diablo'),('al Estómago del Diablo','a la Panza del Diablo'),('el Estómago del Diablo','la Panza del Diablo'),('El Estómago del Diablo','La Panza del Diablo'),('Estómago del Diablo','Panza del Diablo'),('Panza diabla','Panza del Diablo')]:
   new=new.replace(before,after)
  if new!=old:
   row['es_revisado']=new;dirty=True
   changes.append(dict(corpus=path.parent.name,grupo_id=row['grupo_id'],antes=old,despues=new,motivo='Terminología y límites visuales: capturas del usuario'))
  for match in re.finditer(r'\b([\wáéíóúñ]+)(?:\s+|\s*,\s*)\1\b',new,re.I):
   suspects.append(dict(corpus=path.parent.name,grupo_id=row['grupo_id'],coincidencia=match.group(),texto=new,estado='Revisar: puede ser repetición expresiva legítima'))
 if dirty:
  with path.open('w',encoding='utf-8-sig',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
target=B/'informes/correcciones_terminologia.json'
if changes:
 previous=json.loads(target.read_text(encoding='utf-8')) if target.exists() else []
 target.write_text(json.dumps(previous+changes,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'informes/repeticiones_corpus_para_cotejo.json').write_text(json.dumps(suspects,ensure_ascii=False,indent=2),encoding='utf-8')
print('Cambios editoriales',len(changes),'repeticiones que requieren contexto',len(suspects))
