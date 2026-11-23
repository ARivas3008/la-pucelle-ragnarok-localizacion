from pathlib import Path
import json,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from recompilar_talk import wrap
def guardar_lote(numero,inicio,fin,correcciones):
 queue=json.loads((B/'informes/cola_hymt2.json').read_text(encoding='utf8'));out=[]
 for i in range(inicio,fin):
  row=queue[i];draft=json.loads((B/'hymt2_borradores'/(row['id']+'.json')).read_text(encoding='utf8'))
  assert draft['fin']=='stop'
  es=correcciones.get(i,draft['respuesta']).replace('…','...').replace('。','.').replace('、',',')
  if row['opcion']:assert len(wrap(es))==1
  else:wrap(es)
  out.append(dict(id=row['id'],original=row['original'],es=es,estado='revisado',procedencia='HY-MT2 local + cotejo editorial de fuente, contexto y glosario',corregido=es!=draft['respuesta'],apariciones=row['apariciones']))
 (B/f'hymt2_revisados/lote{numero:03d}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 print('Lote',numero,'revisados',len(out),'corregidos',sum(r['corregido'] for r in out))
