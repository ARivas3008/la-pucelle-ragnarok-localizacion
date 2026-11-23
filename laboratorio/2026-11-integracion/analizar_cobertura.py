"""Solo lectura de originales y motor; escribe metadatos en informes."""
import collections,csv,json,struct,sys,unicodedata
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parent
SOURCE=ROOT/'10_Trabajo_v0181/fuente'
sys.path.insert(0,str(SOURCE/'parcheador/app/scripts'))
import construir_parche as core
from fuentes_es import add_spanish_fonts,index_sjis,encode_es
from nis_formats import lzs_decompress,nispack

def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def csvout(p,data):
 if not data:return
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

final=rows(ROOT/'10_Trabajo_v0181/informes/estado_final_v0183.csv')
manifest=rows(SOURCE/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv')
reviews,_,editorial=core.read_reviews(SOURCE,False)
central=rows(ROOT/'01_GitHub_main/data/preexistentes/509_revision_central.csv')
bygroup=collections.defaultdict(list)
for r in final:bygroup[r['grupo_id']].append(r)
completed=lambda r:r['estado_final'].startswith('APLICADO') or r['estado_final']=='SIN_CAMBIO'
group_states=collections.Counter('completo' if all(map(completed,v)) else 'parcial' if any(map(completed,v)) else 'sin_insercion' for v in bygroup.values())
causes=collections.Counter((r['estado_final'],r['motivo_final']) for r in final if not completed(r))
csvout(B/'informes/causas.csv',[dict(estado=s,motivo=m,unidades=n) for (s,m),n in causes.most_common()])
im=core.Image(ROOT/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso')
records={p:(o,n) for p,o,n,_ in im.records()}
packs={};buffers={}
raw=lzs_decompress(im.read(*records['/PSP_GAME/USRDIR/START_JP.LZS']))
packs['ISO_START']={'inner':core.members_from_dat(raw)}
for entry in nispack(im.read(*records['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])):
 buffers['ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+entry['name']]=bytearray(entry['content'])
for n in range(4):
 blob=(ROOT/f'ULJS00244/ULJS00244/DL_JP_{n:02d}.EDAT').read_bytes()
 packs[f'DLC_{n:02d}']={'inner':core.members_from_dat(lzs_decompress(nispack(blob)[0]['content']))}
for key,p in packs.items():
 add_spanish_fonts(p['inner'])
 for name,blob in p['inner'].items():buffers[key+'/'+name]=blob
metrics=[];p=packs['ISO_START']['inner']
fnt=struct.unpack('<11616H',p['fontB.fnt']);ftd=struct.unpack('<11616H',p['fontB.ftd'])
for c in 'AaMm iI.,éñ¿ＡａＭｍ　':
 ix=index_sjis(encode_es(c));metrics.append(dict(caracter=c,indice=ix,gid=fnt[ix],ftd=ftd[ix],ftd_hex=hex(ftd[ix])))
groups=collections.defaultdict(list)
for r in manifest:groups[r['grupo_id']].append(r)
sim=[]
for label,compact in [('original_ancho',False),('ascii_existente',True)]:
 saved=core.to_full
 if compact:core.to_full=lambda s:s
 try:
  solutions,rejected,_,_=core.planificar_intervenciones(manifest,buffers,groups,reviews,False,False,packs,core.leer_refinamientos())
  paged,paged_bad=core.planificar_paginados(manifest,buffers,groups,reviews,False,False,packs,core.leer_refinamientos())
  solutions.update(paged)
  for uid in paged:rejected.pop(uid,None)
  sim.append(dict(metodo=label,unidades_resueltas=len(solutions),bloqueadas=len(rejected),causas=dict(collections.Counter(rejected.values()))))
  csvout(B/f'informes/simulacion_{label}.csv',[dict(unit_id=u,estado='candidato',texto=v[1]) for u,v in solutions.items()])
 finally:core.to_full=saved
# Continuaciones enlazadas con opcode real 00 01, sin inventar IDs del maestro.
known=collections.defaultdict(dict)
for r in manifest:
 if '/talk' in r['recurso']:known[r['recurso']][int(r['offset'])]=r
extra=[];seen=set()
for res,offsets in known.items():
 raw=buffers[res]
 for off,r in sorted(offsets.items()):
  end=raw.find(b'\0',off,min(len(raw),off+2048))
  if end<0 or raw[end+1:end+2]!=b'\x01':continue
  cur=end+2
  while cur not in offsets and (res,cur) not in seen and raw[cur-1:cur]==b'\x01':
   stop=raw.find(b'\0',cur,min(len(raw),cur+2048))
   if stop<=cur:break
   seen.add((res,cur));txt=bytes(raw[cur:stop]).decode('cp932',errors='replace')
   extra.append(dict(recurso=res,offset=cur,unidad_previa=r['unit_id'],grupo_previo=r['grupo_id'],original=txt,bytes=stop-cur))
   if raw[stop+1:stop+2]!=b'\x01':break
   cur=stop+2
csvout(B/'informes/continuaciones_fuera_manifiesto.csv',extra)
result=dict(unidades=len(final),grupos=len(bygroup),estados_grupo=dict(group_states),estados_editoriales=dict(editorial),
 centrales=dict(collections.Counter(r['estado'] for r in central)),causas_unidades=[dict(estado=s,motivo=m,n=n) for (s,m),n in causes.most_common(15)],
 fuente_metricas=metrics,simulaciones=sim,continuaciones_fuera_manifiesto=len(extra),
 textos_distintos_fuera_manifiesto=len({unicodedata.normalize('NFKC',r['original']).strip() for r in extra}),
 atlas_deltas_disponible=(SOURCE/'parcheador/app/datos/atlas_deltas.json.z').is_file())
(B/'informes/diagnostico_cobertura.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
