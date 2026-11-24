"""ROM-013: censo de cadenas/runs de ISO auténtica, sin escribir binarios.

Ejemplo:
 python scripts/rom013_auditar_talk_original.py --iso ORIGINAL.iso --informe informe.json

El archivo original y los textos del juego permanecen locales. Solo se exportan
conteos y hashes. No cuenta unidades insertadas ni pruebas PPSSPP.
"""
import argparse,collections,csv,hashlib,json,sys,unicodedata,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'parcheador/app/scripts'))
from construir_parche import Image,members_from_dat,sha_file,sh
from nis_formats import lzs_decompress,nispack
from formato_talk import inspect
from recompilar_talk import runs

ISO_SHA='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
MANIFEST=ROOT/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv'
def canon(s):
 return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('、',',').replace('。','.'))
def audit(iso,manifest=MANIFEST):
 if sha_file(iso)!=ISO_SHA:raise ValueError('La ISO no coincide con el original autenticado')
 im=Image(iso);index={n:(o,size) for n,o,size,_ in im.records()}
 prefix='/PSP_GAME/USRDIR/'
 start=lzs_decompress(im.read(*index[prefix+'START_JP.LZS']),allow_overlap=False)
 start_files=members_from_dat(start)
 scriptpack=im.read(*index[prefix+'SCRIPTPACK.DAT'])
 script_files={e['name']:e['content'] for e in nispack(scriptpack)}
 data={'ISO_START/'+name:bytes(raw) for name,raw in start_files.items() if name.startswith('talk')}
 data.update({'ISO'+prefix+'SCRIPTPACK.DAT/'+name:raw
              for name,raw in script_files.items() if name.startswith('talk') and name.endswith('_jp.dat')})
 with manifest.open(encoding='utf-8-sig',newline='') as stream:
  rows=list(csv.DictReader(stream))
 refs=collections.defaultdict(list)
 for row in rows:
  if row['recurso'] in data:refs[row['recurso']].append(row)
 summary=[];total=collections.Counter();mismatches=[]
 for resource,blob in sorted(data.items()):
  meta=inspect(blob);physical=runs(blob,meta)
  strings={item['offset']:item['raw'] for item in meta['strings']}
  mapped=set()
  for row in refs[resource]:
   offset=int(row['offset'])
   raw=strings.get(offset)
   try:correct=(raw is not None and canon(raw.decode('cp932'))==canon(row['original']))
   except UnicodeError:correct=False
   if not correct:mismatches.append({'unit_id':row['unit_id'],'recurso':resource,'offset':offset})
   else:mapped.add(offset)
  buckets=collections.Counter()
  for block in physical:
   n=sum(item['offset'] in mapped for item in block)
   state='total_mapeado' if n==len(block) else 'mixto' if n else 'sin_mapeo'
   buckets[state]+=1
  missing=sum(item['offset'] not in mapped for item in meta['strings'])
  stats=dict(resource=resource,sha256=sh(blob),strings=len(meta['strings']),
             runs=len(physical),units_manifest=len(refs[resource]),
             units_ok=len(refs[resource])-sum(x['recurso']==resource for x in mismatches),
             sin_id_en_manifiesto=missing,bloques=dict(buckets))
  summary.append(stats)
  total['recursos']+=1;total['cadenas']+=stats['strings']
  total['runs']+=stats['runs'];total['unidades']+=len(refs[resource])
  total['cadenas_sin_id']+=missing
  for state,n in buckets.items():total[state]+=n
 if mismatches:raise ValueError(f'{len(mismatches)} unidades del manifiesto difieren del original: {mismatches[:5]}')
 if total['unidades']!=20083:raise ValueError('Censo talk ISO distinto de los 20083 originales esperados')
 return dict(fecha='2026-11-24',tipo='A ISO original auténtica; NO inserción/PPSSPP',
             iso_original_sha256=ISO_SHA,scriptpack_sha256=sh(scriptpack),
             unidades_verificadas_como_origen=20083,
             unidades_insertadas_nuevas_certificadas=0,resumen=dict(total),
             recursos=summary,advertencias=[
               'Los 20083 cotejos confirman el origen, no que esté traducido en una ISO candidata',
               'Los runs mixtos son objetivos de investigación; no unidades insertadas',
               'No incluye los cuatro DLC ni certificación de PPSSPP'])
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--iso',type=Path,required=True)
 p.add_argument('--informe',type=Path,required=True)
 a=p.parse_args();r=audit(a.iso)
 a.informe.parent.mkdir(parents=True,exist_ok=True)
 a.informe.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(r['resumen'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
