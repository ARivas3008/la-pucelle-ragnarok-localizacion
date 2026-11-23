"""Cliente local HY-MT2: guarda original, contexto, parámetros y respuesta sin aprobarla a ciegas."""
from pathlib import Path
import json,urllib.request,hashlib,time,argparse,unicodedata
B=Path(__file__).resolve().parent
GLOSSARY='プリエ = Prier; キュロット = Culotte; アルエット = Alouette; エクレール = Éclair; オマール = Homard; クロワ = Croix; サラド = Salade; Father Salade = padre Salade; 悪魔の胃袋 = Panza del Diablo; ローゼンクイーン = Rosenqueen; プリカ = prica; 光の聖女 = Doncella de la Luz; 闇の王子 = Príncipe Oscuro; 油を売る / 油売って = perder el tiempo (idiom). Preserve character names and variable markers such as A1, A2, %s and %d exactly. Keep unfinished sentences unfinished; do not invent their ending. Use Spanish opening question and exclamation marks.'
def prompt(source,context=''):
 return ('Background information:\nThis is dialogue or a menu from La Pucelle Ragnarok, a humorous fantasy tactical RPG. Translate into natural Spanish suitable for a game. Use tú for companions and usted when a character respectfully addresses the priest. Do not add explanations, notes, speaker names or events absent from the source.\nGlossary: '+GLOSSARY+'\nScene context (do not translate this section):\n'+context+'\n\nTranslate the following segment into Spanish, without any additional explanation.\n\nSource text:\n'+source)
def translate(source,context=''):
 p=prompt(source,context)
 payload=dict(messages=[dict(role='user',content=p)],temperature=0.7,top_p=0.6,top_k=20,repeat_penalty=1.05,max_tokens=1024,seed=42,stream=False)
 req=urllib.request.Request('http://127.0.0.1:8766/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 begin=time.monotonic()
 with urllib.request.urlopen(req,timeout=600) as r:response=json.load(r)
 out=response['choices'][0]
 return dict(original=source,contexto=context,prompt=p,respuesta=out['message']['content'].strip(),fin=out['finish_reason'],segundos=round(time.monotonic()-begin,2),uso=response.get('usage'),modelo='Hy-MT2-1.8B-Q8_0',revision='a0c709d9fac510f2c807aa3af52872340dc37a4a',estado='pendiente_revision')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--muestra',action='store_true');ap.add_argument('--limite',type=int,default=0);a=ap.parse_args()
 if a.limite:
  queue=json.loads((B/'informes/cola_hymt2.json').read_text(encoding='utf8'))
  folder=B/'hymt2_borradores';folder.mkdir(exist_ok=True)
  done=0
  for row in queue:
   target=folder/(row['id']+'.json')
   if target.exists():continue
   context=('Menu selection: keep the translation short. ' if row['opcion'] else 'Dialogue. ')+'Adjacent lines in the same event:\n'+'\n'.join(row['contexto'])
   out=translate(row['original'],context);out['id']=row['id'];out['apariciones']=row['apariciones']
   target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
   done+=1
   print(json.dumps(dict(numero=done,id=row['id'],fin=out['fin'],segundos=out['segundos']),ensure_ascii=False),flush=True)
   if done>=a.limite:break
 if a.muestra:
  pending=json.loads((B/'informes/dialogos_pendientes.json').read_text(encoding='utf8'))
  sample=[pending[i] for i in (3,4,5)]
  results=[]
  for row in sample:
   source=unicodedata.normalize('NFKC',' '.join(row['original']))
   out=translate(source,'Location: town NPC conversation. Resource '+row['recurso']+', event '+str(row['entry_id'])+'.')
   results.append(out);print(json.dumps(out,ensure_ascii=False),flush=True)
   (B/'informes/hymt2_muestra.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
