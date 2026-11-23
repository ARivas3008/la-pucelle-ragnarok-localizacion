from pathlib import Path
import sys,csv,json,collections
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as core
from nis_formats import nispack,lzs_decompress
from fuentes_es import add_spanish_fonts
from formato_talk import inspect
from recompilar_talk import catalog,compile_one
iso=core.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in iso.records()}
buffers={};fonts={}
for it in nispack(iso.read(*rec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])):
 if it['name'].startswith('talk'):buffers['ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+it['name']]=it['content']
for key,data in [('ISO_START',iso.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS']))]+[(f'DLC_{i:02d}',nispack((R/f'ULJS00244/ULJS00244/DL_JP_{i:02d}.EDAT').read_bytes())[0]['content']) for i in range(4)]:
 members=core.members_from_dat(lzs_decompress(data));add_spanish_fonts(members);fonts[key]=members
 for name,data in members.items():
  if name.startswith('talk'):buffers[key+'/'+name]=bytes(data)
manifest=list(csv.DictReader(core.DATA.open(encoding='utf-8-sig',newline='')))
reviews,_,_=core.read_reviews(B/'fuente',False)
metas={res:inspect(raw) for res,raw in buffers.items()}
segments=json.loads((B/'fuente/parcheador/app/datos/segmentos_talk_revisados.json').read_text(encoding='utf-8'))
extra=B/'fuente/parcheador/app/datos/segmentos_hymt2_aprobados.json'
if extra.is_file():segments+=json.loads(extra.read_text(encoding='utf8'))
trie,rejected=catalog(manifest,reviews,buffers,metas,segments=segments)
applied=[];pending=[];sizes=[]
outdir=B/'dialogos_compilados';outdir.mkdir(exist_ok=True)
for res,raw in buffers.items():
 key='ISO_START' if res.startswith('ISO/') else res.split('/')[0]
 out,ok,bad,journal=compile_one(res,raw,metas[res],trie,fonts[key]);applied+=ok;pending+=bad
 target=outdir/(res.replace('/','__'));target.write_bytes(out)
 (outdir/(target.name+'.json')).write_text(json.dumps(journal,ensure_ascii=False),encoding='utf-8')
 sizes.append(dict(recurso=res,original=len(raw),nuevo=len(out),bloques_aplicados=len(ok),bloques_pendientes=len(bad)))
 print(sizes[-1],flush=True)
for name,data in [('dialogos_aplicados',applied),('dialogos_pendientes',pending),('grupos_no_catalogados',rejected),('tamanos_dialogos',sizes)]:
 (B/f'informes/{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Resumen',dict(bloques_aplicados=len(applied),bloques_pendientes=len(pending),grupos_aplicados=len({g for a in applied for g in a['grupos']}),grupos_sin_catalogar=len(rejected),motivos=dict(collections.Counter(p['motivo'] for p in pending))))
