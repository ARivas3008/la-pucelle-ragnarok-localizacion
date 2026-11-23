"""Cobertura sobre bytes releídos de ISO/EDAT; nunca cuenta IDs de catálogo reutilizados."""
from pathlib import Path
import csv,json,sys,hashlib,collections,bisect,unicodedata,argparse,datetime
B=Path(__file__).resolve().parents[1];R=B
sys.path.insert(0,str(R/'parcheador/app/scripts'))
import construir_parche as c
from nis_formats import nispack,lzs_decompress
from fuentes_es import decode_es
from recompilar_talk import canon
def load(iso,dlc):
 im=c.Image(iso);rec={p:(o,n) for p,o,n,_ in im.records()};buf={}
 for key,blob in [('ISO_START',im.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS']))]+[(f'DLC_{n:02d}',nispack((dlc/f'DL_JP_{n:02d}.EDAT').read_bytes())[0]['content']) for n in range(4)]:
  for name,data in c.members_from_dat(lzs_decompress(blob,allow_overlap=False)).items():buf[key+'/'+name]=bytes(data)
 for pack in ('SCRIPTPACK.DAT','BGPACK.DAT'):
  path='/PSP_GAME/USRDIR/'+pack
  if path in rec:
   for item in nispack(im.read(*rec[path])):buf['ISO'+path+'/'+item['name']]=item['content']
 buf['ISO/PSP_GAME/SYSDIR/EBOOT.BIN']=im.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN'])
 return buf
ap=argparse.ArgumentParser();ap.add_argument('--entrega',type=Path,required=True);ap.add_argument('--iso-original',type=Path,required=True);ap.add_argument('--dlc-original',type=Path,required=True);args=ap.parse_args()
reportdir=args.entrega/'informes' if args.entrega else B/'informes'
dest=args.entrega/'JUEGO_PARA_PPSSPP/La_Pucelle_Ragnarok_ES.iso' if args.entrega else B/'prueba_correcciones/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'
actual=load(dest,dest.parent/'ULJS00244')
original=load(args.iso_original,args.dlc_original)
manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')))
reviews,_,_=c.read_reviews(R,False)
intervals={};script_units=set();proof=[]
for folder in ('dialogos_compilados','scripts_compilados'):
 suffix='.talk.json' if folder=='dialogos_compilados' else '.script.json'
 files=reportdir.glob('*'+suffix) if args.entrega else (B/folder).glob('*.json')
 for f in sorted(files):
  res=f.name[:-len(suffix) if args.entrega else -5].replace('__','/')
  j=json.loads(f.read_text(encoding='utf8'))
  if args.entrega:
   if folder=='dialogos_compilados':
    from formato_talk import replace
    edits=[(e['offset_original'],e['offset_original']+len(bytes.fromhex(e['antes_hex'])),bytes.fromhex(e['despues_hex'])) for e in j]
    built,roundtrip=replace(original[res],edits);assert roundtrip==j
   else:
    size=len(original[res])+(j['ediciones'][-1]['delta_after'] if j['ediciones'] else 0)
    built=actual[res][:size];assert c.sh(built)==j['sha256_modificado']
  else:built=f.with_suffix('').read_bytes()
  # DAT no registra tamaño lógico: el lector incluye hasta 15 ceros de alineación.
  padding=actual[res][len(built):]
  assert actual[res][:len(built)]==built and (not padding or (len(padding)<16 and not any(padding) and len(actual[res])%16==0)), 'La ISO no contiene el recurso compilado: '+res
  if folder=='dialogos_compilados':
   ints=[]
   for e in j:
    off=e['offset_original'];new=e['offset_nuevo'];old=bytes.fromhex(e['antes_hex']);after=bytes.fromhex(e['despues_hex'])
    assert original[res][off:off+len(old)]==old
    assert actual[res][new:new+len(after)]==after
    ints.append((off,off+len(old)))
   intervals[res]=sorted(ints)
  else:
   assert hashlib.sha256(original[res]).hexdigest()==j['sha256_original']
   for e in j['ediciones']:
    new=e['new_offset'];after=bytes.fromhex(e['despues_hex'])
    assert actual[res][new:new+len(after)]==after
    script_units.add(e['unit_id'])
  proof.append(dict(recurso=res,sha256=hashlib.sha256(built).hexdigest()))
def cstring(b,off):
 end=b.find(b'\0',off)
 return b[off:end] if end>=off else b''
result=[]
for row in manifest:
 res=row['recurso'];off=int(row['offset']) if row['offset'].isdigit() else -1;uid=row['unit_id'];name=res.split('/')[-1]
 state='SIN_VERIFICAR';text='';rev=reviews.get(row['grupo_id'],{}).get('es_revisado','')
 if res in intervals:
  ints=intervals[res];i=bisect.bisect_right(ints,(off,10**12))-1
  state='TALK_BLOQUE_INSERTADO' if i>=0 and ints[i][0]<=off<ints[i][1] else 'TALK_PENDIENTE'
 elif uid in script_units:state='SCRIPT_INSERTADO'
 elif name.startswith('script'):state='SCRIPT_PENDIENTE'
 elif name.endswith('.txp'):state='GRAFICO_PENDIENTE_REVISION_VISUAL'
 elif res in actual and res in original and off>=0:
  before=cstring(original[res],off);after=cstring(actual[res],off)
  try:text=decode_es(after)
  except UnicodeError:text=after.decode('cp932',errors='replace')
  if after!=before:
   state='CAMPO_COINCIDE_REVISION' if rev and canon(text)==canon(rev) else 'CAMPO_MODIFICADO_COTEJO_PENDIENTE'
  else:state='SIN_CAMBIO_COINCIDE_REVISION' if rev and canon(text)==canon(rev) else 'CAMPO_SIN_TRADUCIR'
 result.append(dict(unit_id=uid,grupo_id=row['grupo_id'],recurso=res,offset=row['offset'],estado=state,original=row['original'],es_revision=rev,texto_actual_campo=text))
counts=collections.Counter(r['estado'] for r in result)
verified=sum(counts[s] for s in ('TALK_BLOQUE_INSERTADO','SCRIPT_INSERTADO','CAMPO_COINCIDE_REVISION'))
summary=dict(fecha=datetime.date.today().isoformat(),iso=str(dest),sha256=c.sha_file(dest),unidades_total=len(result),unidades_insertadas_verificadas=verified,porcentaje_unidades_tecnicas=round(100*verified/len(result),2),estados=dict(counts),recursos_compilados_releidos=proof,
 advertencias=['Porcentaje de unidades técnicas del manifiesto, no porcentaje del juego ni calidad editorial.','Los bloques talk incluyen unidades físicas de destino; no se cuentan los IDs de los catálogos reutilizados.','Campos modificados con reducciones requieren cotejo antes de sumarlos.','Texturas pendientes de revisión visual; textos fuera del manifiesto se contabilizan aparte.','Esta comprobación binaria no sustituye la prueba en PPSSPP.'])
(reportdir/'cobertura_insercion_real.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
with (reportdir/'cobertura_insercion_real.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
print(json.dumps({k:v for k,v in summary.items() if k!='recursos_compilados_releidos'},ensure_ascii=False,indent=2),flush=True)
