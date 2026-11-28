import struct as s,unicodedata as u,re,collections as c,json,hashlib as h
from pathlib import Path
from bisect import bisect_right
P=Path('/tmp/rc38'); BASE=P/'replay/JUEGO_PARA_PPSSPP_RC037'; SRC=P/'orig/La_Pucelle_Ragnarok_v1.1.2.iso'; DST=BASE/'La_Pucelle_Ragnarok_ES_RC037.iso'
def iso(path):
 f=path.open('rb');f.seek(32768);p=f.read(2048);out={}
 def rec(b):return s.unpack_from('<I',b,2)[0]*2048,s.unpack_from('<I',b,10)[0],b[25]&2
 def walk(b,prefix,base):
  off,n,_=rec(b);f.seek(off);raw=f.read(n);i=0
  while i<n:
   l=raw[i]
   if not l:i=(i//2048+1)*2048;continue
   x=raw[i:i+l];name=x[33:33+x[32]].split(b';')[0].decode('ascii');a,z,d=rec(x)
   if name not in ('\0','\1'):
    key=prefix+'/'+name;out[key]=(a,z,off+i)
    if d:walk(x,key,off+i)
   i+=l
 walk(p[156:], '',0);f.close();return out
SP='/PSP_GAME/USRDIR/SCRIPTPACK.DAT'; ST='/PSP_GAME/USRDIR/START_JP.LZS'
def read(path,key):
 a,n,_=iso(path)[key]
 with path.open('rb') as f:f.seek(a);return f.read(n)
def nis(raw):
 assert raw[:8]==b'NISPACK\0';assert s.unpack_from('<I',raw,8)[0]==0
 return {name.split(b'\0')[0].decode('cp932'):raw[off:off+n] for name,off,n,x in (s.unpack_from('<32sIII',raw,16+44*i) for i in range(s.unpack_from('<I',raw,12)[0]))}
def lzs(b):
 ext,n,z,m=s.unpack_from('<4sIIB',b);assert z+4==len(b);out=bytearray();i=16
 while i<len(b):
  op=b[i];i+=1
  if op!=m:out.append(op);continue
  d=b[i];i+=1
  if d==m:out.append(m);continue
  d-=d>m;k=b[i];i+=1
  if k<=d:out.extend(out[-d:len(out)-d+k])
  else:
   for _ in range(k):out.append(out[-d])
 assert len(out)==n;return bytes(out)
def dat(raw):
 n=s.unpack_from('<I',raw)[0];base=16+32*n;pos=base;out={}
 for i in range(n):
  end=base+s.unpack_from('<I',raw,16+32*i)[0];name=raw[20+32*i:48+32*i].split(b'\0')[0].decode('cp932');out[name]=raw[pos:end];pos=end
 assert pos==len(raw);return out
EXTRAS='áéíóúÁÉÍÓÚñÑüÜ¿¡«»àèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöÄËÏÖŸçÇōūŌŪºª©†♀♂–—‘’“”';EXTRAS=''.join(dict.fromkeys(EXTRAS));codes={bytes([0xf0,k]):v for k,v in zip(list(range(0x40,0x7f))+list(range(0x80,0xfd)),EXTRAS)}
def decode(raw):
 i=0;out=[]
 while i<len(raw):
  n=1 if raw[i]<128 or 0xa1<=raw[i]<=0xdf else 2;v=raw[i:i+n];out.append(codes.get(v) or v.decode('cp932','replace'));i+=n
 return u.normalize('NFKC',''.join(out)).replace('、',',').replace('。','.')
def canon(x):return re.sub(r'\s+','',x).casefold()
def inspect(raw):
 n,n2=s.unpack_from('<II',raw);base=8+32*n;assert n==n2 and 0<n<10000
 offsets=[s.unpack_from('<I',raw,8+32*i)[0] for i in range(n)];assert offsets==sorted(offsets) and offsets[0]==0
 args={5:2,6:2,7:2,9:2,10:2,11:3,12:3,0xc9:1,0x14:1};pos=base;strings=[];tokens=[]
 def st(a,b,choice):strings.append(dict(offset=a,end=b,raw=raw[a:b],entry=bisect_right(offsets,a-base)-1,choice=choice))
 while pos<len(raw):
  start=pos;op=raw[pos];pos+=1
  if op==0x14:
   count=raw[pos];pos+=1
   for _ in range(count):
    mark=raw.index(1,pos);end=raw.index(0,mark+1);st(mark+1,end,True);tokens.append((mark,end+1,1));pos=end+1
   pos=raw.index(0xfd,pos)+1
  elif op==1:
   end=raw.index(0,pos);st(pos,end,False);pos=end+1
  else:pos+=args.get(op,0)
  assert pos<=len(raw);tokens.append((start,pos,op))
 starts={a-base for a,b,op in tokens};assert all(x in starts or x==len(raw)-base for x in offsets)
 runs=[]
 for t in strings:
  if not t['raw']:continue
  if runs:
   prev=runs[-1][-1]
   if not t['choice'] and not prev['choice'] and t['entry']==prev['entry'] and raw[prev['end']:t['offset']] in (b'\0\1',b'\0\2\1'):runs[-1].append(t);continue
  runs.append([t])
 return dict(n=n,base=base,offsets=offsets,tokens=tokens,runs=runs)
def inventory(path,dlc):
 out={'SP/'+k:v for k,v in nis(read(path,SP)).items() if k.startswith('talk')};packs={'ISO_START':dat(lzs(read(path,ST)))}
 for i in range(4):packs[f'DLC_{i:02}']=dat(lzs(next(iter(nis((dlc/f'DL_JP_{i:02}.EDAT').read_bytes()).values()))))
 out.update({k+'/'+n:v for k,m in packs.items() for n,v in m.items() if n.startswith('talk')});return out,packs

def align(k,a,b,ma,mb):
 aa=c.defaultdict(list);bb=c.defaultdict(list)
 for r in ma['runs']:aa[r[0]['entry']].append(r)
 for r in mb['runs']:bb[r[0]['entry']].append(r)
 def signature(raw,meta,i,rr):
  lo=meta['base']+meta['offsets'][i];hi=meta['base']+meta['offsets'][i+1] if i+1<meta['n'] else len(raw)
  # use per-entry 02 tokens only
  intervals=[(x,y) for x,y,op in meta['tokens'] if op==2 and lo<=x<hi]
  def gap(l,h):
   z=bytearray(raw[l:h]);
   for x,y in reversed(intervals):
    if l<=x<y<=h:del z[x-l:y-l]
   return bytes(z).rstrip(b'\0') if h==len(raw) else bytes(z)
  pos=lo;g=[]
  for r in rr:
   x,y=r[0]['offset']-1,r[-1]['end']+1;g.append(gap(pos,x));pos=y
  g.append(gap(pos,hi));return g
 for i,rr in aa.items():
  qq=bb[i]
  if len(rr)!=len(qq) or ma['n']!=mb['n'] or a[12+32*i:40+32*i]!=b[12+32*i:40+32*i] or [r[0]['choice'] for r in rr]!=[q[0]['choice'] for q in qq] or signature(a,ma,i,rr)!=signature(b,mb,i,qq):continue
  yield from zip(rr,qq)
def lines(r):return [decode(t['raw']) for t in r]
if __name__=='__main__':
 orig,op=inventory(SRC,P/'orig');new,np=inventory(DST,BASE/'ULJS00244');print('packs',len(orig),len(new),flush=True)
 rows=[];stats=c.Counter()
 for k,a in orig.items():
  b=new[k];ma,mb=inspect(a),inspect(b);stats['original_runs']+=len(ma['runs']);stats['new_runs']+=len(mb['runs']);stats['new_lines']+=sum(map(len,mb['runs']));
  for r,q in align(k,a,b,ma,mb):
   stats['aligned']+=1;rows.append(dict(resource=k,offset=r[0]['offset'],current=q[0]['offset'],entry=r[0]['entry'],choice=r[0]['choice'],original=lines(r),spanish=lines(q)))
  print(k,len(ma['runs']),len(mb['runs']),flush=True)
 (P/'all.json').write_text(json.dumps(rows,ensure_ascii=False));print(stats,flush=True)
