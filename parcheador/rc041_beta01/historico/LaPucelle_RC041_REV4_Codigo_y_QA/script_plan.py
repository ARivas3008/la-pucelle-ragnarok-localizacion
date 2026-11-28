import sys,json,struct as s,re
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
p=Path('/tmp/rc41text');_,cur=inventory(Path('/tmp/rc41closures/RC041_rev3.iso'),Path('/tmp/rc41qa/ULJS00244'));rows=json.loads((p/'script_candidates.json').read_text());
# In the repository, script 0x32 consumes two-byte punctuation <0x2e, except space.
# Preserve original lengths and padding; no relocation of bytecode or indexes.
texts={881921:'Cargando el fondo.',881944:'Comprueba la conexión.',881973:'Tras comprobarlo, pulsa ○.',882022:'Cargando...',882043:'Espera un momento.',882343:'Carga completada.',886819:'Indicador sin configurar.',896633:'Y así, mi hermana Prier',896663:'fue reina del Mundo Oscuro.',896739:'Quería ser Doncella de la Luz,',896777:'¡y se hizo Señora Demonio! Qué ironía...',896869:'¿Será también voluntad de la',896909:'diosa Poitreene...?',897261:'Es la historia de la futura Señora Demonio:',901033:'La Pucelle: Ragnarok',901182:'Una joven sometería a los reyes demonios',901236:'y sería la Gran Señora Demonio',901428:'¿Continuará?'}
for r in rows:
 if r['reference_offset']==897315:
  if r['package']=='DLC_00':t='Relato de Prier.'
  else:t='la joven Prier.' if r['offset']<900000 else 'Unificadora.'
 else:t=texts[r['reference_offset']]
 r['target']=t
# Other exact strings not in initial inventory, confirmed by opcode and no interior pointers.
for k in ('DLC_00','DLC_01','DLC_02','DLC_03'):
 b=cur[k]['script00.dat'];n=s.unpack_from('<I',b)[0];body=4+8*n;ptr=s.unpack_from(f'<{n}I',b,4)
 for src in ('物語は語り継がれ、そして伝説となる───','物語は語り継がれゆき、そして伝説となる───'):
  # compare decoded source since comma may be Japanese or fullwidth.
  for i in range(896000,min(len(b)-66,905000)):
   if b[i]!=0x32 or not 8<b[i+1]<65:continue
   x=b[i+2:i+1+b[i+1]]
   if b[i+b[i+1]+1]!=0 or decode(x)!=src.replace('、',','):continue
   off=i+2;refs=[v+body-off for v in ptr if off<v+body<off+len(x)];assert not refs
   rows.append(dict(package=k,offset=off,reference_offset=-1,original=decode(x),raw=x.hex(),cap=len(x),interior=[],target='El relato perdurará y será leyenda.'))
# shorter variants when glyph bytes exceed original field.
rev={v:k for k,v in codes.items()}
def enc(t):
 safe=''.join(chr(ord(c)+0xfee0) if 0x21<=ord(c)<0x2e else c for c in t)
 return b''.join(rev[x] if x in rev else x.encode('cp932') for x in safe)
for r in rows:
 if len(enc(r['target']))>r['cap']:print('LONG',r['reference_offset'],r['cap'],len(enc(r['target'])),r['target'])
print('total',len(rows));(p/'script_plan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
