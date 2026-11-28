import sys,struct as s,hashlib as h,json,shutil,gzip,csv,collections,re
from pathlib import Path
import numpy as np
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/rc41text');old=Path('/tmp/rc41closures/RC041_rev3.iso');dest=P/'RC041_rev4.iso';dlcold=Path('/tmp/rc41qa/ULJS00244');dlcnew=P/'ULJS00244';dlcnew.mkdir(exist_ok=True)
# Load scan definitions without performing a second scan.
exec((P/'scan.py').read_text().split('layouts=')[1].split('rows=[]')[0].join(['layouts=','']))
def enc(t):
 rev={v:k for k,v in codes.items()};v=b''.join(rev[x] if x in rev else x.encode('cp932') for x in t);assert decode(v)==t,(t,decode(v));return v
def sha(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
oldtalk,current=inventory(old,dlcold);expected={k:dict(m) for k,m in current.items()};changes=[];skips=[];plan=json.loads((P/'plan.json').read_text());keys=set()
for r in plan:
 k,name,o,cap,rel=r['package'],r['table'],r['offset'],r['cap'],r['rel'];b=expected[k][name];field=b[o:o+cap];a=parse(field,name,rel);assert a and a[2]==r['actual'] and a[0]==r['lead'],r;lead,raw,text=a
 if (k,name,o) in keys:raise ValueError('duplicate')
 keys.add((k,name,o))
 try:
  y=enc(r['target']);assert len(y)+lead<cap,('capacity',len(y),lead,cap)
  # ASCII control bytes are preserved; an incomplete multibyte glyph is not a control.
  assert [z for z in raw if z<32]==[z for z in y if z<32],('control',raw.hex(),y.hex())
  if name=='char.dat' and '\ufffd' in text:assert raw.startswith(b'Nosferatu') and len(raw)==10,raw.hex()
  assert not any(field[lead+len(raw):]),field.hex()
  new=field[:lead]+y+b'\0'*(cap-lead-len(y));assert len(new)==cap and parse(new,name,rel)[2]==r['target']
  if new==field:continue
  expected[k][name]=b[:o]+new+b[o+cap:];changes.append(dict(package=k,table=name,row=r['row'],offset=o,original=r['original'],before=text,after=r['target'],method=r['method'],slot=cap,hex_before=field.hex(),hex_after=new.hex()))
 except (ValueError,AssertionError,UnicodeError) as e:skips.append(dict(r,reason=str(e)))
print('changes',len(changes),'skipped',len(skips),collections.Counter(x['package'] for x in changes),flush=True)
for r in skips:print('SKIP',r['package'],r['table'],r['row'],r['rel'],r['actual'],r['target'],r['reason'],flush=True)
# Fixed-length script commands, exact source bytes and no interior references.
scriptchanges=[];scriptplan=json.loads((P/'script_plan.json').read_text());seen=set()
for r in scriptplan:
 k=r['package'];o=r['offset'];b=expected[k]['script00.dat'];x=bytes.fromhex(r['raw']);cap=r['cap'];assert len(x)==cap and b[o-2:o+cap+1]==bytes([0x32,cap+1])+x+b'\0';assert (k,o) not in seen;seen.add((k,o));n=s.unpack_from('<I',b)[0];body=4+8*n;ptr=s.unpack_from(f'<{n}I',b,4);assert not any(o<q+body<o+cap for q in ptr)
 safe=''.join(chr(ord(ch)+0xfee0) if 0x21<=ord(ch)<0x2e else ch for ch in r['target']);rev={v:a for a,v in codes.items()};y=b''.join(rev[ch] if ch in rev else ch.encode('cp932') for ch in safe);assert len(y)<=cap,(r,len(y));y=y.ljust(cap,b' ');assert b'\0' not in y and decode(y).strip()==r['target'];expected[k]['script00.dat']=b[:o]+y+b[o+cap:];scriptchanges.append(dict(package=k,table='script00.dat',offset=o,original=r['original'],after=r['target'],hex_before=x.hex(),hex_after=y.hex(),slot=cap))
for k in current:
 a=current[k]['script00.dat'];b=expected[k]['script00.dat'];n=s.unpack_from('<I',a)[0];body=4+8*n;assert len(a)==len(b) and a[:body]==b[:body];allowed=set(i for r in scriptchanges if r['package']==k for i in range(r['offset'],r['offset']+r['slot']));assert all(i in allowed for i,(x,y) in enumerate(zip(a,b)) if x!=y)
with (P/'RC041_REV4_Scripts.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(scriptchanges[0]));w.writeheader();w.writerows(scriptchanges)
print('script fixed',len(scriptchanges),flush=True)

# Use previous validated compressor; keep original token where still valid.
exec(Path('/tmp/rc41/implement.py').read_text().split('def patch_lzs(blob,raw,new):')[1].split('# Table slots:')[0].join(['def patch_lzs(blob,raw,new):','']))
def transform(k,blob):
 raw=lzs(blob);n=s.unpack_from('<I',raw)[0];base=16+32*n;pos=base;b=bytearray(raw)
 for i in range(n):
  end=base+s.unpack_from('<I',raw,16+32*i)[0];name=raw[20+32*i:48+32*i].split(b'\0')[0].decode('cp932');v=expected[k][name];assert len(v)==end-pos;b[pos:end]=v;pos=end
 assert pos==len(raw);out,nt=patch_lzs(blob,raw,bytes(b));assert dat(lzs(out))==expected[k];print(k,len(blob),len(out),nt,flush=True);return out
start=transform('ISO_START',read(old,ST));shutil.copyfile(old,dest);off,n,rec=iso(old)[ST]
with dest.open('r+b') as f:
 # START is already relocated at end of REV3. Check existing extent is last and append only if necessary.
 f.seek(0,2);eof=f.tell();assert off+n<=eof
 other=[(a,z,k) for k,(a,z,_) in iso(old).items() if k!=ST and a>=off and z>0];assert not other,other
 f.seek(off);f.write(start);f.write(b'\0'*((-len(start))%2048));size=f.tell();f.truncate();assert size%2048==0
 f.seek(16*2048+80);f.write(s.pack('<I',size//2048)+s.pack('>I',size//2048));f.seek(rec+10);f.write(s.pack('<I',len(start))+s.pack('>I',len(start)))
assert read(dest,ST)==start
for i,f in enumerate(sorted(dlcold.glob('*.EDAT'))):
 b=f.read_bytes();name,blob=next(iter(nis(b).items()));assert len(nis(b))==1 and b[2048:]==blob
 v=transform(f'DLC_{i:02}',blob);header=bytearray(b[:2048]);s.pack_into('<I',header,0x34,len(v));result=bytes(header)+v;assert nis(result)[name]==v;(dlcnew/f.name).write_bytes(result)
newtalk,final=inventory(dest,dlcnew);assert oldtalk==newtalk and final==expected
for k in iso(old):
 if k!=ST and '.' in k.split('/')[-1]:assert read(old,k)==read(dest,k),k
for name,rows in [('RC041_REV4_Correcciones.csv',changes),('RC041_REV4_Rechazos.json',skips)]:
 if name.endswith('.json'):(P/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 else:
  with (P/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Recalculate audited coverage based on exact before and after fields, not bar lengths.
fields=json.loads((P/'fields.json').read_text());changed={(r['package'],r['table'],r['offset']) for r in changes};left=[r for r in fields if (r['same'] or r['japanese'] or r['invalid']) and (r['package'],r['table'],r['offset']) not in changed];(P/'residual.json').write_text(json.dumps(left,ensure_ascii=False,indent=2))
shutil.copytree('/tmp/rc41closures/gui',P/'gui',dirs_exist_ok=True);patch=P/'gui/patches';m=json.loads((patch/'manifest.json').read_text());m['version']='RC041-REV4-GUI-NATIVO';m['scope']='RC041 REV3 + traducción de tablas ISO/DLC y scripts 0x32; QA visual pendiente'
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
 spec.update(target_sha256=sha(b),target_size=b.stat().st_size)
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));report=dict(version='RC041 REV4',base_sha256=sha(old),fields_audited=len(fields),candidates=len([r for r in fields if r['same'] or r['japanese'] or r['invalid']]),changes=len(changes),skips=len(skips),by_package=dict(collections.Counter(x['package'] for x in changes)),remaining_flags=len(left),remaining_JP=sum(r['japanese'] for r in left),remaining_invalid=sum(r['invalid'] for r in left),all_TALK_unchanged=True,all_other_ISO_files_unchanged=True,outputs=m['specs'],ppsspp=False,windows_gui=False,limitations=['Auditoría limitada a campos válidos de ocho tablas; otros campos y recursos no certificados.','Traducciones nuevas o reutilizadas requieren revisión contextual y visual.','Los nombres propios legítimos se conservan.','No publicado en GitHub.'])
report.update(script_changes=len(scriptchanges),script_by_package=dict(collections.Counter(x['package'] for x in scriptchanges)),script_fixed_length=True,script_indices_unchanged=True,total_text_changes=len(changes)+len(scriptchanges));(P/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for f in (P/'gui').glob('*.go'):f.write_text(f.read_text().replace('RC041_REV3','RC041_REV4'))
print('DONE',report,flush=True)
