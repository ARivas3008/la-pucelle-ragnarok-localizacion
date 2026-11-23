from pathlib import Path
import sys,csv,json
B=Path(__file__).resolve().parent;R=B.parent
sys.path[:0]=[str(B/'fuente/parcheador/app/scripts'),str(B/'fuente/parcheador/investigacion/v0.14')]
import construir_parche as c
from nis_formats import nispack
from integrar_scripts_v014 import originals,load_rows,plan
cache=B/'recursos_base';cache.mkdir(exist_ok=True)
base=B/'prueba_scripts_corregidos/La_Pucelle_Ragnarok_ES_SCRIPT_V014_EXPERIMENTAL.iso'
for member in ['START_JP.LZS','SCRIPTPACK.DAT']:
 path=cache/member
 if not path.exists():
  image=c.Image(base);rec={p:(o,n) for p,o,n,_ in image.records()}
  path.write_bytes(image.read(*rec['/PSP_GAME/USRDIR/'+member]))
for num in range(4):
 target=cache/f'DLC_{num:02d}.lzs'
 if not target.exists():
  source_dlc=R/f'10_Trabajo_v0181/salida_v0183/DL_JP_{num:02d}_ES_PRELIMINAR.EDAT'
  target.write_bytes(nispack(source_dlc.read_bytes())[0]['content'])
source,ctx=originals(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso',R/'ULJS00244/ULJS00244')
rows=load_rows(c.DATA,B/'fuente/parcheador/informes/estado_unificado_66.csv',B/'fuente')
changed,report,stats=plan(rows,source,'conservador')
folder=B/'scripts_compilados';folder.mkdir(exist_ok=True)
for res,data in changed.items():
 (folder/(res.replace('/','__'))).write_bytes(data['raw'])
 (folder/(res.replace('/','__')+'.json')).write_text(json.dumps(data['journal']),encoding='utf-8')
print(dict(stats),'recursos',len(changed))
(B/'informes/scripts_signos_seguridad.json').write_text(json.dumps(dict(estados=dict(stats),reporte=report),ensure_ascii=False,indent=2),encoding='utf-8')
