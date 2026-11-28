from audit import *
import shutil,csv
# Pages follow source page boundaries; preserve speaker/voice/choice and external commands.
plan={
 ('SP/talk16_jp.dat',48672):['¡Claro que sí! ¡Voy a convertirme en la Doncella de la Luz!'],
 ('SP/talk16_jp.dat',69370):['Pero a ti te pega mucho más ser Señora Demonio que Doncella de la Luz...'],
 ('SP/talk16_jp.dat',97239):['¿Crees que voy a quedarme de brazos cruzados','y dejarte decir esas cosas?','¡Voy a convertirme en la Doncella de la Luz!'],
 ('SP/talk17_jp.dat',60307):['¿Será posible...? ¿¡La diosa Poitreene...!?'],
 ('SP/talk18_jp.dat',49669):['¡Hip...!','Prier, dijiste que llegarías a ser la Doncella de la Luz...'],
 ('SP/talk18_jp.dat',50110):['¡Hip...!','Prier, dijiste que llegarías a ser la Doncella de la Luz...'],
 ('SP/talk15_jp.dat',91878):['Así que...','¡No era una niña cualquiera...!'],
}
for off in (118051,118555,119326):plan['SP/talk18_jp.dat',off]=['Pero, si lo piensas bien, te pega más ser la Señora Demonio','que la Doncella de la Luz...']
for k,off in [('15',65259),('16',65924),('17',56559),('18',67044)]:plan[f'SP/talk{k}_jp.dat',off]=['...Sí. ¡Tienes razón, Prier...!']

def encode(t):
 rev={v:k for k,v in codes.items()};out=bytearray()
 for x in t:
  if x==' ':x='　'
  elif x==',':x='、'
  elif x=='.':x='。'
  elif 0x21<=ord(x)<=0x7e:x=chr(ord(x)+0xfee0)
  out.extend(rev[x] if x in rev else x.encode('cp932'))
 assert len(out)%2==0 and all(out[i]>=0x80 for i in range(0,len(out),2));return bytes(out)
def ix(v):
 if len(v)==1:return v[0]-31
 a,b=v;lead=a-0x81 if a<=0x9f else 31+a-0xe0;return 96+lead*192+b-0x40

def wrap(t):
 out=[];line=''
 for w in t.split():
  v=(line+' '+w).strip()
  if len(encode(v))>56:assert line;out.append(line);line=w
  else:line=v
 if line:out.append(line)
 assert len(out)<=3 and all(len(encode(x))<=56 for x in out);return out

def page_split(raw,r):
 pages=[]
 for t in r:
  if not pages or raw[prev['end']:t['offset']]==b'\0\2\1':pages.append([])
  pages[-1].append(decode(t['raw']));prev=t
 return pages

def replace(raw,edits):
 m=inspect(raw);base=m['base'];pos=base;parts=[raw[:base]];delta=0;shifts=[];ends=[];journal=[]
 starts={a for a,b,o in m['tokens']};ends_allowed={b for a,b,o in m['tokens']}
 for a,b,n in sorted(edits):
  assert a>=pos and a in starts and b in ends_allowed and not any(a<base+o<b for o in m['offsets']);parts.extend((raw[pos:a],n));journal.append((a+delta,n,raw[a:b]));delta+=len(n)-(b-a);ends.append(b-base);shifts.append(delta);pos=b
 parts.append(raw[pos:]);out=bytearray(b''.join(parts))
 for i,p in enumerate(m['offsets']):
  j=bisect_right(ends,p)-1;s.pack_into('<I',out,8+32*i,p+(shifts[j] if j>=0 else 0))
 check=inspect(out);assert check['n']==m['n'];assert all(raw[12+32*i:40+32*i]==out[12+32*i:40+32*i] for i in range(m['n']))
 restored=bytearray(out)
 for off,n,old in reversed(journal):assert restored[off:off+len(n)]==n;restored[off:off+len(n)]=old
 restored[:base]=raw[:base];assert restored==raw
 return bytes(out)

def controls(raw,m):return [raw[a:b] for a,b,o in m['tokens'] if o not in (1,2,0x14)]

def main():
 orig,op=inventory(SRC,P/'orig');new,np=inventory(DST,BASE/'ULJS00244');fnt=s.unpack('<11616H',np['ISO_START']['fontB.fnt']);fixes=[];changed={};found=set()
 names={(x['resource'],x['offset']) for x in json.loads((P/'all.json').read_text()) if 'Mayonnaise' in ' '.join(x['spanish'])};assert len(names)==68 and not names.intersection(plan)
 for k,raw in new.items():
  if not any(key[0]==k for key in set(plan)|names):continue
  a=orig[k];ma,mb=inspect(a),inspect(raw);edits=[];expected={};oldmap={}
  for r,q in align(k,a,raw,ma,mb):
   off=r[0]['offset'];oldmap[off]=[t['raw'] for t in q]
   if (k,off) in names:
    key=(k,off);found.add(key);assert not q[0]['choice'];pages=page_split(raw,q)
    # Exact byte substitution, no reflow or changes to other words or page breaks.
    st,en=q[0]['offset']-1,q[-1]['end']+1
    old=raw[st:en];data=old.replace(encode('Mayonnaise Harbor'),encode('Puerto Mayonesa')).replace(encode('Mayonnaise'),encode('Mayonesa'))
    assert data!=old and len(data)<len(old)
    pages=[[t.replace('Mayonnaise Harbor','Puerto Mayonesa').replace('Mayonnaise','Mayonesa') for t in page] for page in pages]
    assert all(len(encode(t))<=56 for page in pages for t in page)
    for t in ('Puerto Mayonesa','Mayonesa'):
     code=encode(t);assert all(code[i:i+2]==b'\x81\x40' or fnt[ix(code[i:i+2])] for i in range(0,len(code),2))
    edits.append((st,en,data));expected[off]=pages;fixes.append(dict(resource=k,offset_original=off,offset_rc037=q[0]['offset'],original=page_split(a,r),before=page_split(raw,q),after=pages,reason='Topónimo residual en inglés; se unifica con el cartel aprobado Puerto Mayonesa.'));continue
   if (k,off) not in plan:continue
   found.add((k,off));pages=[wrap(t) for t in plan[k,off]];assert len(pages)==len(page_split(a,r));assert not q[0]['choice'];assert all(t['raw'][i]>=0x80 for rr in (r,q) for t in rr for i in range(0,len(t['raw']),2));
   data=b'\2'.join(b''.join(b'\1'+encode(line)+b'\0' for line in page) for page in pages)
   for page in pages:
    for line in page:
     code=encode(line)
     assert all(code[i:i+2]==b'\x81\x40' or fnt[ix(code[i:i+2])] for i in range(0,len(code),2)),line
   edits.append((q[0]['offset']-1,q[-1]['end']+1,data));expected[off]=pages;fixes.append(dict(resource=k,offset_original=off,offset_rc037=q[0]['offset'],original=page_split(a,r),before=page_split(raw,q),after=pages,reason='Eliminación de repetición no presente en la fuente; separación de páginas original recuperada.'))
  out=replace(raw,edits);mc=inspect(out);assert len(out)<=286072 and len(out)<=len(raw);assert controls(raw,mb)==controls(out,mc)
  ar=list(align(k,a,out,ma,mc));assert len(ar)==len(ma['runs'])==len(oldmap)
  for r,q in ar:
   off=r[0]['offset'];assert (page_split(out,q)==expected[off] if off in expected else [t['raw'] for t in q]==oldmap[off]),(k,off)
  changed[k.split('/')[-1]]=out;print(k,len(edits),len(raw),len(out),flush=True)
 assert found==set(plan)|names
 # preserve member offsets, pad released space, change only member lengths and bytes in the edited ranges.
 pack=read(DST,SP);newpack=bytearray(pack);allowed=[]
 for i in range(s.unpack_from('<I',pack,12)[0]):
  pos=16+44*i;name,off,n,x=s.unpack_from('<32sIII',pack,pos);name=name.split(b'\0')[0].decode('ascii')
  if name not in changed:continue
  b=changed[name];assert len(b)<=n;newpack[off:off+n]=b.ljust(n,b'\0');s.pack_into('<I',newpack,pos+36,len(b));allowed.extend([(pos+36,pos+40),(off,off+n)])
 before,after=nis(pack),nis(newpack);assert set(before)==set(after) and all(after[k]==changed.get(k,before[k]) for k in before)
 cursor=0
 for lo,hi in sorted(allowed):assert pack[cursor:lo]==newpack[cursor:lo];cursor=hi
 assert pack[cursor:]==newpack[cursor:]
 dest=P/'RC038.iso';shutil.copyfile(DST,dest);off,n,_=iso(DST)[SP];assert n==len(newpack)
 with dest.open('r+b') as f:f.seek(off);f.write(newpack)
 assert iso(dest)==iso(DST) and read(dest,SP)==newpack
 with DST.open('rb') as f,dest.open('rb') as g:
  for lo,hi in [(0,off),(off+n,DST.stat().st_size)]:
   f.seek(lo);g.seek(lo)
   for _ in range(lo,hi,4*1024*1024):
    nn=min(hi-_,4*1024*1024);assert f.read(nn)==g.read(nn)
 (P/'fixes.json').write_text(json.dumps(fixes,ensure_ascii=False,indent=2));print('verified',len(fixes),len(changed),flush=True)
if __name__=='__main__':main()
