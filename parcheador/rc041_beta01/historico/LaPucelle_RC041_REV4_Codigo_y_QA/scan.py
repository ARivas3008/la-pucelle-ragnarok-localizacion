import sys,struct as s, re,collections as c,csv,json
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
p=Path('/tmp/rc41text');base=Path('/tmp/rc41closures/RC041_rev3.iso');dlc=Path('/tmp/rc41qa/ULJS00244');_,orig=inventory(SRC,Path('/tmp/rc38/orig'));_,cur=inventory(base,dlc)
layouts={'kis.dat':(148,[(0,21),(21,59)]),'magic.dat':(116,[(18,22),(40,56)]),'skill.dat':(94,[(16,21),(37,57)]),'mapinfo.dat':(96,[(12,30)]),'char.dat':(200,[(0,24)]),'ritem.dat':(92,[(4,13),(17,59)]),'name.dat':(16,[(4,12)]),'com.dat':(92,[(0,23),(23,57)])}
jp=re.compile('[\u3040-\u30ff\u3400-\u9fff]')
def parse(field,name,rel):
 lead=len(field)-len(field.lstrip(b'\0'));t=field[lead:].split(b'\0')[0]
 if not t or lead>2 or any(field[lead+len(t):]):return None
 if name=='magic.dat' and rel==40 and t.startswith(b'\x87'):lead+=2;t=t[2:]
 return (lead,t,decode(t))
rows=[]
for k,m in orig.items():
 for name,(stride,slots) in layouts.items():
  src=m[name];dst=cur[k][name];n=((len(src)-8)//stride if name in ('magic.dat','name.dat') else s.unpack_from('<I',src)[0]);assert len(src)==len(dst)
  for i in range(n):
   for rel,cap in slots:
    o=8+i*stride+rel;a=src[o:o+cap];b=dst[o:o+cap];aa=parse(a,name,rel);bb=parse(b,name,rel)
    if not aa or not bb or not any(x.isalpha() for x in aa[2]):continue
    rows.append(dict(package=k,table=name,row=i,rel=rel,offset=o,cap=cap,original=aa[2],actual=bb[2],same=a==b,japanese=bool(jp.search(bb[2])),invalid='\ufffd' in bb[2],lead=bb[0]))
(p/'fields.json').write_text(json.dumps(rows,ensure_ascii=False));print('fields',len(rows));print('unchanged or JP',c.Counter((r['package'],r['table']) for r in rows if r['same'] or r['japanese']));
for k in orig:
 print('\n',k)
 for name in layouts:
  rr=[r for r in rows if r['package']==k and r['table']==name];bad=[r for r in rr if r['same'] or r['japanese'] or r['invalid']];print(name,len(rr),len(bad),len(set(r['actual'] for r in bad)))
  if k in ('ISO_START','DLC_00'):print(' | '.join(dict.fromkeys(r['actual'] for r in bad))[:8000])
