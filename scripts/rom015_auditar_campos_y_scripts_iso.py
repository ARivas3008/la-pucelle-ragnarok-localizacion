"""ROM-015: confirmar 2091 campos y 485 textos script contra la ISO original.

 python scripts/rom015_auditar_campos_y_scripts_iso.py --iso ORIGINAL.iso --informe censo.json

No modifica la ISO ni exporta textos protegidos. El resultado certifica
identidad de ORIGEN, nunca las inserciones españolas o el funcionamiento PSP.
"""
import argparse,collections,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'parcheador/app/scripts'))
import construir_parche as c
from nis_formats import lzs_decompress,nispack
from recompilar_talk import canon
ISO_SHA='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
MANIFEST=ROOT/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv'
def cotejar_cadena(buf,offset,original):
 """Contrasta una cadena CP932 completa desde su offset, sin alterar bytes."""
 if offset<0 or offset>=len(buf):return 'OFFSET_FUERA'
 end=buf.find(b'\0',offset,min(len(buf),offset+4096))
 if end<0:return 'SIN_TERMINADOR'
 if end==offset:return 'CADENA_VACIA'
 try:physical=bytes(buf[offset:end]).decode('cp932')
 except UnicodeError:return 'CP932_INVALIDO'
 return 'COINCIDE' if canon(physical)==canon(original) else 'CONTENIDO_DISTINTO'
def auditar(iso,manifest=MANIFEST):
 if c.sha_file(iso)!=ISO_SHA:raise ValueError('ISO original no autenticada')
 im=c.Image(iso);rec={p:(o,n) for p,o,n,_ in im.records()}
 prefix='/PSP_GAME/USRDIR/'
 start=lzs_decompress(im.read(*rec[prefix+'START_JP.LZS']),allow_overlap=False)
 buffers={'ISO_START/'+name:bytes(data) for name,data in c.members_from_dat(start).items()}
 scriptpack=im.read(*rec[prefix+'SCRIPTPACK.DAT'])
 buffers.update({'ISO'+prefix+'SCRIPTPACK.DAT/'+e['name']:e['content'] for e in nispack(scriptpack)})
 buffers['ISO/PSP_GAME/SYSDIR/EBOOT.BIN']=im.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN'])
 with manifest.open(encoding='utf-8-sig',newline='') as stream:
  rows=list(csv.DictReader(stream))
 counts=collections.Counter();byres=collections.defaultdict(collections.Counter);failed=[]
 for row in rows:
  res=row['recurso']
  if not res.startswith('ISO') or '/talk' in res or res.endswith('.txp'):continue
  kind='SCRIPT' if '/script' in res else 'CAMPO'
  raw=buffers.get(res)
  state='RECURSO_AUSENTE' if raw is None else cotejar_cadena(raw,int(row['offset']),row['original'])
  counts[kind]+=1;counts[kind+'_'+state]+=1
  byres[res][state]+=1
  if state!='COINCIDE':
   failed.append(dict(unit_id=row['unit_id'],recurso=res,offset=row['offset'],motivo=state))
 if counts['CAMPO']!=2091 or counts['SCRIPT']!=485:
  raise ValueError('Denominadores ISO textuales cambiados: '+str(dict(counts)))
 if failed:raise ValueError(f'{len(failed)} discordancias de origen: '+str(failed[:6]))
 return dict(fecha='2026-11-24',evidencia='A ISO original autenticada; NO insercion ni PPSSPP',
   iso_original_sha256=ISO_SHA,scriptpack_original_sha256=c.sh(scriptpack),
   unidades_campos_cotejadas=2091,unidades_script_cotejadas=485,
   unidades_talk_iso_remitidas_a_rom013=20083,unidades_textuales_iso_total=22659,
   graficos_iso_fuera_del_cotejo_textual=62,unidades_iso_catalogo=22721,
   estados=dict(counts),por_recurso={res:dict(states) for res,states in byres.items()},
   unidades_nuevas_insertadas_y_verificadas=0,
   observacion='Los 22659 cotejos confirman byte de origen e identidad textual, no la traducción insertada')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--iso',type=Path,required=True)
 p.add_argument('--informe',type=Path,required=True)
 a=p.parse_args();j=auditar(a.iso);a.informe.parent.mkdir(parents=True,exist_ok=True)
 a.informe.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(j['estados'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
