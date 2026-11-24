"""Cobertura sobre bytes releídos de ISO/EDAT; nunca cuenta IDs de catálogo reutilizados."""
from pathlib import Path
import csv,json,sys,hashlib,collections,bisect,unicodedata,argparse,datetime
B=Path(__file__).resolve().parents[1];R=B
sys.path.insert(0,str(R/'parcheador/app/scripts'))
import construir_parche as c
from nis_formats import nispack,lzs_decompress
from fuentes_es import decode_es
from recompilar_talk import canon
from revisiones_coordinadas import merge_central
from nis_formats import lzs_header
def load(iso,dlc=None):
 im=c.Image(iso);rec={p:(o,n) for p,o,n,_ in im.records()};buf={}
 packs=[('ISO_START',im.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS']))]
 if dlc is not None:
  for n in range(4):
   path=dlc/f'DL_JP_{n:02d}.EDAT'
   if not path.is_file():raise FileNotFoundError('Falta DLC original: '+str(path))
   parts=nispack(path.read_bytes())
   if not parts:
    raise ValueError('DLC sin recurso LZS: '+str(path))
   candidates=[]
   for part in parts:
    try:lzs_header(part['content']);candidates.append(part)
    except ValueError:pass
   if len(candidates)!=1:
    raise ValueError('DLC sin un único LZS validado: '+str(path))
   packs.append((f'DLC_{n:02d}',candidates[0]['content']))
 for key,blob in packs:
  for name,data in c.members_from_dat(lzs_decompress(blob,allow_overlap=False)).items():buf[key+'/'+name]=bytes(data)
 for pack in ('SCRIPTPACK.DAT','BGPACK.DAT'):
  path='/PSP_GAME/USRDIR/'+pack
  if path in rec:
   for item in nispack(im.read(*rec[path])):buf['ISO'+path+'/'+item['name']]=item['content']
 buf['ISO/PSP_GAME/SYSDIR/EBOOT.BIN']=im.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN'])
 return buf
def revisiones_completas(repo,manifest):
 """Combina 15016 revisiones distribuidas y 509 centrales sin inventar
 aprobaciones. Fallo cerrado si un ID falta, está duplicado o no es válido.
 """
 base,_,states=c.read_reviews(repo,False)
 merged,_,_=merge_central(repo,base,manifest,[],states,expected=509)
 if len(merged)!=15525:raise ValueError('Catálogo editorial incompleto para auditoría')
 return merged

ap=argparse.ArgumentParser();ap.add_argument('--entrega',type=Path,required=True);ap.add_argument('--iso-original',type=Path,required=True);ap.add_argument('--dlc-original',type=Path,help='Cuatro EDAT originales; omitir para auditoría ISO exclusivamente');args=ap.parse_args()
reportdir=args.entrega/'informes' if args.entrega else B/'informes'
dest=args.entrega/'JUEGO_PARA_PPSSPP/La_Pucelle_Ragnarok_ES.iso' if args.entrega else B/'prueba_correcciones/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'
if not dest.is_file():raise FileNotFoundError('No existe la ISO candidata: '+str(dest))
actual=load(dest,dest.parent/'ULJS00244' if args.dlc_original else None)
original=load(args.iso_original,args.dlc_original)
manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')))
reviews=revisiones_completas(R,manifest)
intervals={};script_units=set();proof=[]
for folder in ('dialogos_compilados','scripts_compilados'):
 suffix='.talk.json' if folder=='dialogos_compilados' else '.script.json'
 files=reportdir.glob('*'+suffix) if args.entrega else (B/folder).glob('*.json')
 for f in sorted(files):
  res=f.name[:-len(suffix) if args.entrega else -5].replace('__','/')
  if not args.dlc_original and res.startswith('DLC_'):
   continue  # Fuera del alcance de ISO sola; nunca atribuirle inserción
  if res not in original or res not in actual:
   raise ValueError('Informe de recurso no disponible en los originales/candidata: '+res)
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
 if not args.dlc_original and res.startswith('DLC_'):
  result.append(dict(unit_id=uid,grupo_id=row['grupo_id'],recurso=res,offset=row['offset'],estado='NO_EVALUADO_DLC_AUSENTE',original=row['original'],es_revision=rev,texto_actual_campo=''))
  continue
 if res in intervals:
  ints=intervals[res];i=bisect.bisect_right(ints,(off,10**12))-1
  state='TALK_BLOQUE_INSERTADO' if i>=0 and ints[i][0]<=off<ints[i][1] else 'TALK_PENDIENTE'
 elif uid in script_units:state='SCRIPT_INSERTADO'
 elif name.startswith('script'):state='SCRIPT_PENDIENTE'
 elif name.startswith('talk'):state='TALK_PENDIENTE'
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
sin_dlc=not bool(args.dlc_original)
alcance=len(result)-counts['NO_EVALUADO_DLC_AUSENTE']
if alcance<=0:raise ValueError('Auditoría sin unidades aplicables')
originales_autenticados=dict(iso_sha256=c.sha_file(args.iso_original),
 dlc_sha256={f'DL_JP_{n:02d}.EDAT':c.sha_file(args.dlc_original/f'DL_JP_{n:02d}.EDAT') for n in range(4)} if args.dlc_original else {})
summary=dict(fecha=datetime.date.today().isoformat(),iso=str(dest),sha256=c.sha_file(dest),
 originales_autenticados=originales_autenticados,
 alcance='ISO_SOLA' if sin_dlc else 'ISO_Y_CUATRO_DLC',unidades_total=len(result),
 unidades_alcance_auditado=alcance,unidades_no_evaluadas_por_ausencia_dlc=counts['NO_EVALUADO_DLC_AUSENTE'],
 unidades_insertadas_verificadas=verified,porcentaje_unidades_tecnicas=round(100*verified/alcance,2),
 porcentaje_sobre_catalogo_total=round(100*verified/len(result),2) if not sin_dlc else None,
 estados=dict(counts),recursos_compilados_releidos=proof,
 advertencias=['La cobertura es SOLO del alcance auditado y no certifica DLC ausentes ni el porcentaje del proyecto entero.',
 'Porcentaje de unidades técnicas del manifiesto auditado, no porcentaje del juego ni calidad editorial.','Los bloques talk incluyen unidades físicas de destino; no se cuentan los IDs de los catálogos reutilizados.','Campos modificados con reducciones requieren cotejo antes de sumarlos.','Texturas pendientes de revisión visual; textos fuera del manifiesto se contabilizan aparte.','Esta comprobación binaria no sustituye la prueba en PPSSPP.'])
(reportdir/('cobertura_iso_sola.json' if sin_dlc else 'cobertura_insercion_real.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
with (reportdir/('cobertura_iso_sola.csv' if sin_dlc else 'cobertura_insercion_real.csv')).open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
print(json.dumps({k:v for k,v in summary.items() if k!='recursos_compilados_releidos'},ensure_ascii=False,indent=2),flush=True)
