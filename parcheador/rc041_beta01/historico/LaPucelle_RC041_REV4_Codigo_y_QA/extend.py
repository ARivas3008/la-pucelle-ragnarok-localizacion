import json,re,collections as c
from pathlib import Path
p=Path('/tmp/rc41text');fields=json.loads((p/'fields.json').read_text());old=json.loads((p/'fields_initial.json').read_text());plan=json.loads((p/'plan.json').read_text());keys={(r['package'],r['table'],r['offset']) for r in old};lookup={(r['package'],r['table'],r['row'],r['rel']):r for r in fields};key=lambda r:(r['package'],r['table'],r['offset']);pp={key(r):r for r in plan};jp=re.compile('[\u3040-\u30ff\u3400-\u9fff\ufffd]')
# adjust previously planned map fields to correctly proven capacity 30, and normalization errors.
for r in plan:
 if r['table']=='mapinfo.dat':r['cap']=30
 if r['target']=='N.º 1':r['target']='Número 1'
# exact original string map within same table and field from already translated fields and planned corrections.
bytext=c.defaultdict(set)
for r in fields:
 t=pp.get(key(r),{}).get('target',r['actual'])
 if t and not jp.search(t) and (t!=r['original'] or r['table']=='char.dat'):bytext[(r['table'],r['rel'],r['original'])].add(t)
name={293:'A veces',294:'Bastante',295:'De vuelta',296:'De golpe',297:'Alboroto',298:'De todos',299:'Súper',300:'Ya tarde',302:'Más bien',303:'Quizá',304:'Adrede',305:'En secreto',306:'En secreto'}
mdesc={'状態変化を回復します':'Cura cualquier estado alterado.','相手の急所を狙い撃ち!':'¡Ataca los puntos vitales del rival!','強烈な跳び蹴りで相手を爆砕!':'¡Destroza al rival con una patada voladora!','大地を揺るがす二段蹴りで相手を粉砕!':'Destroza al rival con una doble patada sísmica.','聖なるバトンを超速回転させ,相手にぶつける':'Ataque giratorio con un bastón sagrado.','聖なるバトンをフルスイングして超ダメージ':'Gran daño con un golpe de bastón sagrado.','ヌシの子を召喚して,範囲内にいる者を攻撃':'Invoca a la cría del Señor y ataca en el área.','この華麗なシリさばきを見るがいいッス!!':'¡Mira qué elegante movimiento de trasero, dood!','□ボタンを連打しても連射はできないッス!!':'¡Pulsar □ repetidamente no permite disparar, dood!'}
for r in fields:
 if key(r) in keys or not(r['same'] or r['japanese'] or r['invalid']):continue
 t,i,rel,src=r['table'],r['row'],r['rel'],r['original'];y=None;m='traducción directa'
 if t=='mapinfo.dat':
  if not jp.search(src):continue
  ref=lookup.get(('DLC_00',t,i,rel),{});base=lookup.get(('ISO_START',t,i,rel),{})
  if ref.get('original')==src and not jp.search(ref.get('actual','')) and ref.get('actual'):y=ref['actual'];m='mismo mapa japonés, traducción DLC00'
  elif src=='深闇の心':y='Corazón de oscuridad profunda'
  elif base.get('actual') and not jp.search(base['actual']):y=base['actual'];m='nombre equivalente en juego base'
 elif t=='name.dat':y=name.get(i)
 elif t=='magic.dat':
  if rel==40:y=mdesc.get(src)
  if src=='ヒップアタック!':y='Ataque de trasero'
  elif src=='プリニー連射!':y='Ráfaga Prinny'
  m2=re.fullmatch('(フロン|プリニー|コルネット|ラズベリル|ロザリンド|アサギ)特殊(\d+)(の説明)?',src)
  if m2:
   ch={'フロン':'Flonne','プリニー':'Prinny','コルネット':'Cornet','ラズベリル':'Raspberyl','ロザリンド':'Rozalin','アサギ':'Asagi'}[m2[1]];y=f'Especial de {ch} {m2[2]}' if not m2[3] else f'Descripción del especial {m2[2]} de {ch}.'
   if len(y)>21 and rel==18:y=f'Especial {ch} {m2[2]}'
  if not y and len(bytext[(t,rel,src)])==1:y=next(iter(bytext[(t,rel,src)]));m='cadena japonesa idéntica'
 if y and y!=r['actual']:plan.append(dict(r,target=y,method=m))
 else:print('UNRESOLVED',r['package'],t,i,src,r['actual'])
(p/'plan.json').write_text(json.dumps(plan,ensure_ascii=False));print('total plan',len(plan),c.Counter(r['package'] for r in plan))
