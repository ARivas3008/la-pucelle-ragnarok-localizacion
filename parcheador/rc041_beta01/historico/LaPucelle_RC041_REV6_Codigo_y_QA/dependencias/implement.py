import sys,struct as s,hashlib as h,json,shutil,gzip,csv,collections,re
from pathlib import Path
import numpy as np
sys.path.insert(0,'/tmp/rc38')
from audit import *
from fix import encode,replace,controls
P=Path('/tmp/rc41'); old=Path('/tmp/rc40/RC040.iso'); dest=P/'RC041.iso'; dlcold=Path('/tmp/rc40/replay/JUEGO_PARA_PPSSPP_RC040/ULJS00244'); dlcnew=P/'ULJS00244';dlcnew.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
base_manifest=json.loads(Path('/tmp/rc40/gui/patches/manifest.json').read_text());assert sha(old)==base_manifest['specs'][0]['target_sha256']
orig,op=inventory(SRC,Path('/tmp/rc38/orig'));before,packs=inventory(old,dlcold)
changes=[];updates={};srcword=encode('Calamidad');target=encode('Calamity')
for k,b in before.items():
 if srcword not in b:continue
 a=orig[k];ma,mb=inspect(a),inspect(b);edits=[];expected={}
 for r,q in align(k,a,b,ma,mb):
  for t in q:
   if srcword not in t['raw']:continue
   assert 'Calamity' in ' '.join(lines(r));v=t['raw'].replace(srcword,target);assert len(v)<len(t['raw']) and len(v)<=56
   edits.append((t['offset']-1,t['end']+1,b'\1'+v+b'\0'));expected[t['offset']]=v
   changes.append(dict(resource=k,offset=t['offset'],source=' '.join(lines(r)),before=decode(t['raw']),after=decode(v)))
 out=replace(b,edits);mc=inspect(out);assert controls(b,mb)==controls(out,mc);assert len(out)<len(b);assert len(mc['runs'])==len(mb['runs'])
 for r,q in zip(mb['runs'],mc['runs']):
  assert len(r)==len(q)
  for t,u in zip(r,q):assert u['raw']==expected.get(t['offset'],t['raw'])
 assert srcword not in out;updates[k.split('/')[-1]]=out
assert len(changes)==7
pack=read(old,SP);newpack=bytearray(pack)
for i in range(s.unpack_from('<I',pack,12)[0]):
 pos=16+44*i;name,off,n,x=s.unpack_from('<32sIII',pack,pos);name=name.split(b'\0')[0].decode('ascii')
 if name in updates:
  b=updates[name];assert len(b)<=n;newpack[off:off+n]=b.ljust(n,b'\0');s.pack_into('<I',newpack,pos+36,len(b))
assert all(v==updates.get(k,nis(pack)[k]) for k,v in nis(newpack).items())
# Modify only literal/backreference tokens affected by fixed-width replacements. All other original compressed tokens retained.
def patch_lzs(blob,raw,new):
 assert len(raw)==len(new);assert lzs(blob)==raw
 marker=blob[12];i=16;p=0;out=bytearray(blob[:16]);rewritten=0
 while i<len(blob):
  st=i;op=blob[i];i+=1
  if op!=marker:n=1;ok=new[p]==op
  else:
   d=blob[i];i+=1
   if d==marker:n=1;ok=new[p]==marker
   else:
    d-=d>marker;n=blob[i];i+=1;assert d>0 and d<=p and n>0
    ok=new[p:p+n]==new[p-d:p-d+n]
  if ok:out.extend(blob[st:i])
  else:
   v=new[p:p+n];out.extend(v.replace(bytes([marker]),bytes([marker,marker])));rewritten+=1
  p+=n
 assert p==len(raw);s.pack_into('<I',out,8,len(out)-4);assert lzs(out)==new
 return bytes(out),rewritten
# Table slots: name at 8296 and 17766, descriptions at +22. All same across versions.
def kis_fix(k,blob):
 raw=lzs(blob);n=s.unpack_from('<I',raw)[0];base=16+32*n;prev=0
 for i in range(n):
  end=s.unpack_from('<I',raw,16+32*i)[0];name=raw[20+32*i:48+32*i].split(b'\0')[0]
  if name==b'kis.dat':offset=base+prev;break
  prev=end
 else:raise ValueError('kis missing')
 table=dat(raw)['kis.dat'];b=bytearray(table)
 # Exact original slots located from Japanese and English table copies. Pad to original field width.
 for off,size,text in [(8296,21,'Bastón oscuro'),(8317,59,'Imbuido del poder de Calamity.'),(17768,21,'Anillo de Calamity'),(17789,59,'Imbuido del poder de Calamity.')]:
  oldstr=bytes(b[off:off+size]).split(b'\0')[0]
  # Verify field boundary (all bytes after terminator zero), no binary stats.
  assert oldstr and not any(b[off+len(oldstr):off+size]),(k,off,b[off:off+size].hex())
  enc=bytes([0]) # encode ASCII + extended font
  rev={v:t for t,v in codes.items()};enc=b''.join(rev[ch] if ch in rev else ch.encode('cp932') for ch in text)
  assert len(enc)<size and decode(enc)==text
  if oldstr==enc:continue
  changes.append(dict(resource=k+'/kis.dat',offset=off,source=decode(oldstr),before=decode(oldstr),after=text));b[off:off+size]=enc.ljust(size,b'\0')
 new=raw[:offset]+bytes(b)+raw[offset+len(b):];assert len(new)==len(raw)
 assert all(v== (bytes(b) if name=='kis.dat' else dat(raw)[name]) for name,v in dat(new).items())
 out,nt=patch_lzs(blob,raw,new);print(k,len(blob),len(out),nt,flush=True);return out
start=kis_fix('ISO_START',read(old,ST))
# Preserve existing ISO extents when possible. Only change size in directory.
shutil.copyfile(old,dest);off,n,rec=iso(old)[ST];nextoff=iso(old)[SP][0];assert off+n<=nextoff and off+len(start)<=nextoff
with dest.open('r+b') as f:
 f.seek(off);f.write(start);f.write(b'\0'*max(0,n-len(start)));f.seek(rec+10);f.write(s.pack('<I',len(start))+s.pack('>I',len(start)));off2,n2,_=iso(old)[SP];f.seek(off2);f.write(newpack)
assert read(dest,ST)==start and read(dest,SP)==newpack
for f in sorted(dlcold.glob('*.EDAT')):
 b=f.read_bytes();name,blob=next(iter(nis(b).items()));assert len(nis(b))==1 and b[2048:]==blob
 v=kis_fix(f.name,blob);header=bytearray(b[:2048]);s.pack_into('<I',header,0x34,len(v));result=bytes(header)+v;assert nis(result)[name]==v;(dlcnew/f.name).write_bytes(result)
# Cross-check all talk and tables, other ISO members unchanged.
final,fp=inventory(dest,dlcnew);assert all(v==updates.get(k.split('/')[-1],before[k]) if k.startswith('SP/') else v==before[k] for k,v in final.items());assert all(all(v==packs[k][n] for n,v in members.items() if n!='kis.dat') for k,members in fp.items())
for k,members in fp.items():
 v=members['kis.dat'];assert b'Calamity' in v and 'カラミティー'.encode('cp932') not in v and b'Filled with the power of Calamity' not in v
assert all(srcword not in v for v in final.values());assert all(iso(old)[k]==iso(dest)[k] for k in iso(old) if k!=ST)
# Verify all outside changed extents identical.
for k,(a,n,r) in iso(old).items():
 if k in (SP,ST) or k.endswith('/') or not n:continue
 # directories contain updated size, compare only actual files via naming
 if '.' not in k.split('/')[-1]:continue
 assert read(old,k)==read(dest,k),k
print('changes',len(changes),flush=True)
shutil.copytree('/tmp/rc40/gui',P/'gui',dirs_exist_ok=True);patch=P/'gui/patches';m=base_manifest;m['version']='RC041-GUI-NATIVO';m['scope']='RC040 + Calamity unificado en diálogos y objetos de ISO y DLC; QA visual pendiente'
for spec in m['specs']:
 name=spec['name'];a=SRC if name=='ISO' else Path('/tmp/rc38/orig')/name;b=dest if name=='ISO' else dlcnew/name
 assert sha(a)==spec['source_sha256']
 with a.open('rb') as f,b.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as out:
  out.write(b'LPGUI001');o=0
  while True:
   x=f.read(65536);y=g.read(65536)
   if not y:break
   x=x[:len(y)].ljust(len(y),b'\0')
   if x!=y:out.write(s.pack('<QI',o,len(y)));out.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
   o+=len(y)
  out.write(s.pack('<Q',2**64-1))
 spec.update(target_sha256=sha(b),target_size=b.stat().st_size);print('delta',name,flush=True)
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
for f in (P/'gui').glob('*.go'):f.write_text(f.read_text().replace('RC040','RC041'))
report=dict(version='RC041',canonical='Calamity',dialogue_changes=7,object_fields_changed=len(changes)-7,changes=changes,all_other_talk_and_table_members_identical=True,outputs=m['specs'],limitations=['No se ha ejecutado Windows ni PPSSPP.','La apertura gráfica se conserva de RC040, sin volver a modificarla.','No se han revisado posibles variantes en imágenes no identificadas ni actualizado GitHub.'])
(P/'QA_RC041.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (P/'RC041_Calamity.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(changes[0]));w.writeheader();w.writerows(changes)
