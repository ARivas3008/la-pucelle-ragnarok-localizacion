from view import *
from fix import encode,replace,controls,page_split,wrap
import csv,collections
orig,_=inventory(SRC,Path('/tmp/rc38/orig'));cur,packs=inventory(B,D)
updates={};log=[];skipped=[];target='caldo de setas';pattern=re.compile(r'Kinoko Jiru',re.I)
for k,raw in cur.items():
 m=inspect(raw);a=orig[k];ma=inspect(a);edits=[];exp={};beforemap={}
 for r,q in align(k,a,raw,ma,m):
  pages=page_split(raw,q);beforemap[r[0]['offset']]=[t['raw'] for t in q]
  full=' '.join(' '.join(p) for p in pages)
  if not pattern.search(full):continue
  if not k.startswith('SP/') or q[0]['choice'] or any(t['raw'][i]<0x80 for t in q for i in range(0,len(t['raw']),2)):
   skipped.append((k,r[0]['offset'],full,'control or outside SP'));continue
  res=[]
  for page in pages:
   t=' '.join(page);v=pattern.sub(lambda x:('Caldo de setas' if x.start()==0 or t[max(0,x.start()-1):x.start()] in ('«','“') else target),t)
   if t==v:res.append(page);continue
   try:res.append(wrap(v))
   except AssertionError:
    skipped.append((k,r[0]['offset'],t,'page capacity'));break
  else:
   if pattern.search(' '.join(' '.join(p) for p in res)):
    if k=='SP/talk04_jp.dat' and r[0]['offset']==78620:
     res=[wrap('¡Menos mal que hemos conseguido el caldo de setas!'),wrap('¡Ahora podremos salvar al niño!')]
    else:
     skipped.append((k,r[0]['offset'],full,'split across page'));continue
   data=b'\2'.join(b''.join(b'\1'+encode(line)+b'\0' for line in p) for p in res)
   edits.append((q[0]['offset']-1,q[-1]['end']+1,data));exp[r[0]['offset']]=res
   log.append(dict(resource=k,source_offset=r[0]['offset'],current_offset=q[0]['offset'],original=' | '.join(lines(r)),before=' | '.join(' / '.join(p) for p in pages),after=' | '.join(' / '.join(p) for p in res)))
 if not edits:continue
 b=replace(raw,edits);mb=inspect(b);assert controls(raw,m)==controls(b,mb);ar=list(align(k,a,b,ma,mb));assert len(ar)==len(beforemap)==len(ma['runs']);
 for r,q in ar:
  o=r[0]['offset'];assert (page_split(b,q)==exp[o] if o in exp else [t['raw'] for t in q]==beforemap[o]),(k,o)
 updates[k.split('/')[-1]]=b;print(k,len(edits),len(b)-len(raw),flush=True)
# Normalize all identified fixed table fields, preserve every other byte.
rev={v:k for k,v in codes.items()};defenc=lambda t:b''.join(rev[x] if x in rev else x.encode('cp932') for x in t)
packupdates={};tablelog=[]
for k,m in packs.items():
 for name,slots in [('kis.dat',[(22208,21)]),('magic.dat',[(16846,22),(16868,56),(20674,22),(20696,56)])]:
  b=bytearray(m[name]);
  for o,cap in slots:
   old=bytes(b[o:o+cap]);lead=len(old)-len(old.lstrip(b'\0'));x=old[lead:].split(b'\0')[0];# description fields may have nontext icon prefix, retain it
   prefix=b''
   if name=='magic.dat' and cap==56 and x.startswith(b'\x87'):prefix=x[:2];x=x[2:]
   t=decode(x)
   if not pattern.search(t):continue
   v=pattern.sub(lambda q:'Caldo de setas' if cap<=22 or q.start()==0 else 'caldo de setas',t);e=defenc(v);new=(b'\0'*lead+prefix+e).ljust(cap,b'\0');assert len(new)==cap and len(e)+lead+len(prefix)<cap and not any(old[lead+len(prefix)+len(x):]),(k,name,o,old.hex());b[o:o+cap]=new;tablelog.append(dict(resource=k+'/'+name,offset=o,before=t,after=v))
  if b!=m[name]:packupdates.setdefault(k,{})[name]=bytes(b)
(P/'text_changes.json').write_text(json.dumps(log,ensure_ascii=False,indent=2));(P/'table_changes.json').write_text(json.dumps(tablelog,ensure_ascii=False,indent=2));(P/'text_skips.json').write_text(json.dumps(skipped,ensure_ascii=False,indent=2));(P/'text_members').mkdir(exist_ok=True)
for n,b in updates.items():(P/'text_members'/n).write_bytes(b)
for k,m in packupdates.items():
 for n,b in m.items():(P/'text_members'/(k+'__'+n)).write_bytes(b)
print('dialogue',len(log),'tables',len(tablelog),'skips',len(skipped),skipped,flush=True)
