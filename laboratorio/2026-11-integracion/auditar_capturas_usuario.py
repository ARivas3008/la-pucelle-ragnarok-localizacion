from pathlib import Path
import csv,json,sys,re,unicodedata
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as c
from nis_formats import nispack,lzs_decompress
from fuentes_es import decode_es
terms=['Church','Devils Stomach','Buy','Total Purica','Infirmary','Office','MAP CLEAR','Fight','Player Turn','Enemy Turn','Flow','Element']
iso=c.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in iso.records()}
eb=iso.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN'])
for term in terms:
 for m in re.finditer(re.escape(term.encode()),eb):
  off=m.start();a=eb.rfind(b'\0',max(0,off-40),off)+1;b=eb.find(b'\0',off);end=(b+4)//4*4
  print('EBOOT',off,repr(eb[a:b].decode('cp932',errors='replace')),eb[b:end].hex())
disc=c.Image(B/'prueba_dialogos/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso');rr={p:(o,n) for p,o,n,_ in disc.records()}
pack=nispack(disc.read(*rr['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']))
raw=next(x['content'] for x in pack if x['name']=='script01.dat')
for phrase in [b'Aunque llevamos',b'No solo nos']:
 off=raw.find(phrase);end=raw.find(b'\0',off)
 print('SCRIPT',off,decode_es(raw[off:end]),raw[off-2:end+10].hex())
rows=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')))
for term in ['The basics of combat','Purification','Item Record','Infirmary','Office','Yes','Now let us review','Watching that thing','In the name of','The foundation']:
 found=[r for r in rows if term.lower() in unicodedata.normalize('NFKC',r['original']).lower()]
 print('CORPUS',term,len(found),[(r['unit_id'],r['grupo_id'],r['recurso'],r['original']) for r in found[:6]])
