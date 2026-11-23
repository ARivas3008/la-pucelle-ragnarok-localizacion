from pathlib import Path
import sys,csv,json,collections
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from construir_parche import Image,members_from_dat,DATA
from nis_formats import nispack,lzs_decompress
from formato_talk import inspect
iso=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in iso.records()}
buffers={}
for it in nispack(iso.read(*rec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])):
 if it['name'].startswith('talk'):buffers['ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+it['name']]=it['content']
for key,data in [('ISO_START',iso.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS']))]+[(f'DLC_{i:02d}',nispack((R/f'ULJS00244/ULJS00244/DL_JP_{i:02d}.EDAT').read_bytes())[0]['content']) for i in range(4)]:
 for name,data in members_from_dat(lzs_decompress(data)).items():
  if name.startswith('talk'):buffers[key+'/'+name]=bytes(data)
rows=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')));results=[]
for res,raw in buffers.items():
 try:
  info=inspect(raw);texts={t['offset']:t for t in info['strings']};wanted=[r for r in rows if r['recurso']==res]
  bad=[r['unit_id'] for r in wanted if int(r['offset']) not in texts]
  extras=[dict(offset=t['offset'],original=t['raw'].decode('cp932',errors='replace'),entry=t['entry']) for t in info['strings'] if t['offset'] not in {int(r['offset']) for r in wanted} and t['raw']]
  result=dict(recurso=res,entradas=info['n'],cadenas=len(texts),unidades=len(wanted),fuera_de_cadena=bad,
   opcodes_no_identificados=info['unknown'],impares=[t['offset'] for t in info['strings'] if len(t['raw'])%2],extras=extras)
 except ValueError as e:result=dict(recurso=res,error=str(e))
 results.append(result)
 print({k:v for k,v in result.items() if k not in ('extras','impares')},'extras',len(result.get('extras',[])),'impares',len(result.get('impares',[])))
(B/'informes/interprete_talk.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
