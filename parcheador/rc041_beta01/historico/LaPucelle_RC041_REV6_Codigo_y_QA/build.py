import sys
sys.path.insert(0,"/tmp/rc41rev5")
from view import *
P=Path("/tmp/rc41rev6");B=Path("/tmp/rc41rev5/RC041_rev5.iso");D=Path("/tmp/rc41rev5/ULJS00244")
import shutil,gzip,hashlib as H,csv,collections
base=B;dest=P/'RC041_rev6.iso';dlcnew=P/'ULJS00244';dlcnew.mkdir(exist_ok=True);assets=P/'assets';textmembers=P/'text_members';origdlc=Path('/tmp/rc38/orig');BG='/PSP_GAME/USRDIR/BGPACK.DAT'
def sha(p):
 with p.open('rb') as f:return H.file_digest(f,'sha256').hexdigest()
oldtalk,packs=inventory(base,D); expected={k:dict(m) for k,m in packs.items()};graphic_physical=[]
for k,m in expected.items():
 for n in ['sys2.txp','sys7.txp']:
  f=assets/('DLC_sys6.txp' if n=='sys6.txp' and k!='ISO_START' else n);v=f.read_bytes();assert len(v)==len(m[n]);assert m[n]!=v;assert txp(v)[2:]==txp(m[n])[2:];graphic_physical.append(k+'/'+n);m[n]=v
 for f in textmembers.glob(k+'__*'):
  n=f.name.split('__',1)[1];v=f.read_bytes();assert len(v)==len(m[n]);m[n]=v
# Replace same-sized background assets at exact NIS member positions.
def pack_replace(pack,repls,allow_growth=False):
 before=nis(pack);out=bytearray(pack);entries=sorted([(i,*s.unpack_from('<32sIII',pack,16+44*i)) for i in range(s.unpack_from('<I',pack,12)[0])],key=lambda e:e[2]);changed=[]
 for j,(i,nm,o,z,flag) in enumerate(entries):
  name=nm.split(b'\0')[0].decode('cp932');
  if name not in repls:continue
  v=repls[name];end=entries[j+1][2] if j+1<len(entries) else len(pack);assert len(v)<=end-o,(name,len(v),end-o);assert len(v)==z or allow_growth;assert not any(pack[o+z:o+len(v)]),(name,'padding nonzero')
  out[o:o+max(z,len(v))]=v.ljust(max(z,len(v)),b'\0');s.pack_into('<I',out,16+44*i+36,len(v));changed.append(name)
 assert set(changed)==set(repls) and nis(out)=={k:repls.get(k,v) for k,v in before.items()} and len(out)==len(pack);return bytes(out)
repls={f.name:f.read_bytes() for f in assets.glob('at*.txp')};assert len(repls)==1
bg=pack_replace(read(base,BG),repls);graphic_physical.extend('BGPACK.DAT/'+n for n in repls)
talkrepls={f.name:f.read_bytes() for f in textmembers.glob('talk*.dat')};sp=pack_replace(read(base,SP),talkrepls,True);print('bg and sp members',len(repls),len(talkrepls),flush=True)
exec(Path('/tmp/rc41/implement.py').read_text().split('def patch_lzs(blob,raw,new):')[1].split('# Table slots:')[0].join(['def patch_lzs(blob,raw,new):','']))
def transform(k,blob):
 raw=lzs(blob);n=s.unpack_from('<I',raw)[0];base=16+32*n;pos=base;b=bytearray(raw)
 for i in range(n):
  end=base+s.unpack_from('<I',raw,16+32*i)[0];name=raw[20+32*i:48+32*i].split(b'\0')[0].decode('cp932');v=expected[k][name];assert len(v)==end-pos;b[pos:end]=v;pos=end
 assert pos==len(raw);out,nt=patch_lzs(blob,raw,bytes(b));assert dat(lzs(out))==expected[k];print(k,len(blob),len(out),nt,flush=True);return out
start=transform('ISO_START',read(base,ST));shutil.copyfile(base,dest);idx=iso(base);off,n,rec=idx[ST]
with dest.open('r+b') as f:
 assert not [k for k,(a,z,_) in idx.items() if k!=ST and a>=off and z>0]
 f.seek(off);f.write(start);f.write(b'\0'*((-len(start))%2048));size=f.tell();f.truncate();f.seek(16*2048+80);f.write(s.pack('<I',size//2048)+s.pack('>I',size//2048));f.seek(rec+10);f.write(s.pack('<I',len(start))+s.pack('>I',len(start)))
 for k,v in [(BG,bg),(SP,sp)]:
  a,z,_=idx[k];assert len(v)==z;f.seek(a);f.write(v)
for i,f in enumerate(sorted(D.glob('*.EDAT'))):
 b=f.read_bytes();name,blob=next(iter(nis(b).items()));assert len(nis(b))==1 and b[2048:]==blob
 v=transform(f'DLC_{i:02}',blob);header=bytearray(b[:2048]);s.pack_into('<I',header,0x34,len(v));result=bytes(header)+v;assert nis(result)[name]==v;(dlcnew/f.name).write_bytes(result)
newtalk,new=inventory(dest,dlcnew);assert new==expected;assert all(v==talkrepls.get(k.split('/')[-1],oldtalk[k]) if k.startswith('SP/') else v==oldtalk[k] for k,v in newtalk.items());assert all(iso(base)[k]==iso(dest)[k] for k in idx if k!=ST);assert nis(read(dest,BG))==nis(bg);assert read(dest,SP)==sp
for k in idx:
 if k not in (ST,BG,SP) and '.' in k.split('/')[-1]:assert read(base,k)==read(dest,k),k
# Verify each prior closure by hash and exact bytes.
for q in json.loads(Path('/tmp/rc41closures/closures.json').read_text()):
 with dest.open('rb') as f:f.seek(q['offset']);assert H.sha256(f.read(q['size'])).hexdigest()==q['new_sha256']
# Scan all TALK runs in final output for residual terminology, including crossed lines.
remaining=[];runs_total=0
for k,b in newtalk.items():
 m=inspect(b);runs_total+=len(m['runs'])
 for r in m['runs']:
  text=' '.join(lines(r));
  if re.search('Kinoko Jiru',text,re.I):remaining.append((k,r[0]['offset'],text))
assert not remaining,remaining
for k,m in new.items():
 for n in ('kis.dat','magic.dat','ritem.dat','name.dat','skill.dat'):
  assert not re.search(rb'kinoko jiru',m[n],re.I),(k,n)
print('verified',runs_total,'runs, 22 previous closures,',len(graphic_physical),'graphics',flush=True)
shutil.copytree('/tmp/rc41rev5/gui',P/'gui',dirs_exist_ok=True);patch=P/'gui/patches';m=json.loads((patch/'manifest.json').read_text());m['version']='RC041-REV6-GUI-NATIVO';m['scope']='RC041 REV5 + Reacción, Omitir, título capítulo adicional 2 armonizado; QA visual pendiente'
for spec in m['specs']:
 name=spec['name'];a=SRC if name=='ISO' else origdlc/name;b=dest if name=='ISO' else dlcnew/name;assert sha(a)==spec['source_sha256']
 with a.open('rb') as f,b.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as out:
  out.write(b'LPGUI001');o=0
  while True:
   x=f.read(65536);y=g.read(65536)
   if not y:break
   x=x[:len(y)].ljust(len(y),b'\0')
   if x!=y:out.write(s.pack('<QI',o,len(y)));out.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
   o+=len(y)
  out.write(s.pack('<Q',2**64-1))
 spec.update(target_sha256=sha(b),target_size=b.stat().st_size)
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));report=dict(version='RC041 REV6',base_sha256=sha(base),dialogue_runs_reread=runs_total,kinoko_jiru_residual=len(remaining),graphics_physical=len(graphic_physical),graphics_resources=graphic_physical,closures_preserved=22,nonaffected_iso_files_identical=True,outputs=m['specs'],ppsspp=False,windows_gui=False,limitations=['Re-Action!! y スキップ reconstruidos sobre atlas original, pendientes de prueba de UV/legibilidad.', 'Capítulo adicional 2 armonizado con el cierre japonés ココロノカケラ.', 'Inventario de texturas independientes BGPACK/START no es exhaustivo de texturas internas ANMPACK, KM2, otros contenedores ni videos.', 'Revisión semántica y PPSSPP pendientes; no publicado en GitHub.'])
(P/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for f in (P/'gui').glob('*.go'):f.write_text(f.read_text().replace('RC041_REV5','RC041_REV6'))
print('BUILD READY',flush=True)
