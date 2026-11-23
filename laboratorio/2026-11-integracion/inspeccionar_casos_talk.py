from pathlib import Path
import sys,csv,struct
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from construir_parche import Image,DATA,members_from_dat
from nis_formats import nispack,lzs_decompress
from formato_talk import inspect
iso=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in iso.records()}
raw=next(x['content'] for x in nispack(iso.read(*rec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'])) if x['name']=='talk01_jp.dat')
info=inspect(raw)
for a,b,op in [(a,b,op) for a,b,op in info['tokens'] if op==0x82][:5]:
 print('DESCONOCIDO',a,raw[a-14:a+32].hex(),repr(raw[a-14:a+32].decode('cp932',errors='replace')))
rows=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')))
for uid in ['4974','5252','6363']:
 r=next(r for r in rows if r['unit_id']==uid);off=int(r['offset'])
 print('UNIDAD',uid,off,r['original'],raw[off-16:off+60].hex(),repr(raw[off-16:off+60].decode('cp932',errors='replace')))
for k in range(7,9):
 a=info['base']+info['offsets'][k];b=info['base']+info['offsets'][k+1]
 print('entrada',k,raw[a:b].hex())
