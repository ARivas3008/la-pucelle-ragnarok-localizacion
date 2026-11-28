import sys,struct as s,shutil,json,gzip,hashlib as H, numpy as np
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
from fix import encode
P=Path('/tmp/lp_reintegracion');M=Path('/mnt/data');base=Path('/tmp/rc41rev6/RC041_rev6.iso');bd=Path('/tmp/rc41rev6/ULJS00244');dest=P/'BETA02.iso';dd=P/'ULJS00244';dd.mkdir(exist_ok=True);origd=Path('/tmp/rc38/orig');AN='/PSP_GAME/USRDIR/ANMPACK.DAT'
sha=lambda x:H.sha256(x).hexdigest()
def hf(p):
 with p.open('rb') as f:return H.file_digest(f,'sha256').hexdigest()
new=(P/'new.anm').read_bytes();old=(P/'beta.anm').read_bytes();pack=read(base,AN);a=bytearray(pack);entries=[s.unpack_from('<32sIII',pack,16+44*i) for i in range(s.unpack_from('<I',pack,12)[0])];_,o,n,_=next(x for x in entries if x[0].split(b'\0')[0]==b'anm3000.dat');assert n==len(new)==len(old) and pack[o:o+n]==old;a[o:o+n]=new
assert nis(a)=={k:new if k=='anm3000.dat' else v for k,v in nis(pack).items()};shutil.copyfile(base,dest);anmo=iso(base)[AN][0]
with dest.open('r+b') as f:f.seek(anmo+o);f.write(new)
EBOOT='/PSP_GAME/SYSDIR/EBOOT.BIN'
eboot_new=(P/'eboot_new.bin').read_bytes();eboot_old=read(base,EBOOT);eboff,ebsize,_=iso(base)[EBOOT];assert len(eboot_new)==ebsize and eboot_new[:0xd1478]==eboot_old[:0xd1478]
with dest.open('r+b') as f:f.seek(eboff);f.write(eboot_new)
assert read(dest,EBOOT)==eboot_new
assert iso(base)==iso(dest) and nis(read(dest,AN))['anm3000.dat']==new
# Keep fixed slots and exact controls while aligning the translated tutorial with the Spanish combat alert.
exec(Path('/tmp/rc41/implement.py').read_text().split('def patch_lzs(blob,raw,new):')[1].split('# Table slots:')[0].join(['def patch_lzs(blob,raw,new):','']))
logs=[]
for i,f in enumerate(sorted(bd.glob('*.EDAT'))):
 b=f.read_bytes();name,blob=next(iter(nis(b).items()));raw=lzs(blob);members=dat(raw);talk=members['talk00.dat'];x=bytearray(talk);m=inspect(talk)
 for r in m['runs']:
  for t in r:
   before=decode(t['raw']);after=before.replace('«Re-Action»','«¡Reacción!»').replace('Re-Action','reacción');after=after.replace('La reacción','La reacción')
   if before==after:continue
   if after.startswith('reacción'):after='R'+after[1:]
   enc=encode(after)
   if len(enc)>len(t['raw']):
    # Use capitalized label without exclamation if the existing line has no free slot.
    after=after.replace('«¡Reacción!»','«Reacción»');enc=encode(after)
   assert len(enc)<=len(t['raw']) and (len(t['raw'])-len(enc))%2==0
   # Reproduce same length and original pointers; any spare cell is a trailing blank.
   enc+=b'\x81\x40'*((len(t['raw'])-len(enc))//2);x[t['offset']:t['end']]=enc
   logs.append(dict(resource=f.name,entry=t['entry'],offset=t['offset'],before=before,after=after))
 assert len(x)==len(talk);m2=inspect(bytes(x));assert m['offsets']==m2['offsets'] and m['tokens']==m2['tokens'];assert not any('Re-Action' in ' '.join(lines(r)) for r in m2['runs'])
 # Replace exact DAT member, without changing length or any adjacent byte.
 count=s.unpack_from('<I',raw)[0];start=16+32*count;pos=start;z=bytearray(raw)
 for j in range(count):
  end=start+s.unpack_from('<I',raw,16+32*j)[0];nm=raw[20+32*j:48+32*j].split(b'\0')[0].decode('cp932')
  if nm=='talk00.dat':assert raw[pos:end]==talk;z[pos:end]=x
  pos=end
 assert dat(z)=={k:bytes(x) if k=='talk00.dat' else v for k,v in members.items()};v,_=patch_lzs(blob,raw,bytes(z));assert lzs(v)==z;head=bytearray(b[:2048]);s.pack_into('<I',head,0x34,len(v));assert b[2048:]==blob;newb=bytes(head)+v;assert nis(newb)[name]==v;(dd/f.name).write_bytes(newb)
print('DLC dialogue corrections',len(logs),flush=True);(P/'tutorial.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
# Verify all ISO files except ANMPACK byte-identical and only one ANM changed.
for k,(off,n,rec) in iso(base).items():
 if k not in (AN,EBOOT) and '.' in k.split('/')[-1]:assert read(base,k)==read(dest,k),k
assert sha(eboot_old)==json.load(open(M/'QA_RC040.json'))['eboot_after'];assert all(read(dest,EBOOT)[int(r.get('new_offset',r['offset']),16):int(r.get('new_offset',r['offset']),16)+len(bytes.fromhex(r.get('after_hex',r['after'])))]==bytes.fromhex(r.get('after_hex',r['after'])) for r in json.load(open(M/'QA_RC039.json'))['changes'])
# Rebuild five cumulative streams from user's verified inputs.
shutil.copytree('/tmp/lapucelle_beta1/gui',P/'gui',dirs_exist_ok=True);patch=P/'gui/patches';m=json.loads((patch/'manifest.json').read_text());m['version']='RC041-REV6-BETA02-GUI-NATIVO';m['scope']='BETA01 + introducción nativa corregida en textura real y legibilidad; tutorial DLC armonizado con Reacción; menús anteriores conservados y avisos de guardado traducidos'
for spec in m['specs']:
 name=spec['name'];a=SRC if name=='ISO' else origd/name;b=dest if name=='ISO' else dd/name;assert hf(a)==spec['source_sha256']
 with a.open('rb') as f,b.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as out:
  out.write(b'LPGUI001');o=0
  while True:
   x=f.read(65536);y=g.read(65536)
   if not y:break
   x=x[:len(y)].ljust(len(y),b'\0')
   if x!=y:out.write(s.pack('<QI',o,len(y)));out.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
   o+=len(y)
  out.write(s.pack('<Q',2**64-1))
 spec.update(target_sha256=hf(b),target_size=b.stat().st_size)
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));r=dict(version='RC041 REV6 BETA02',base_sha256=hf(base),intro_pairs=11,intro_pixel_offset=hex(0xc60),intro_old_sha=sha(old),intro_new_sha=sha(new),tutorial_lines_changed=len(logs),menu_previous_87_preserved=True,boot_menu_changes=11,all_other_iso_files_unchanged=True,all_other_ANM_members_unchanged=True,all_other_DLC_members_unchanged=True,outputs=m['specs'],limitations=['RC024 acumulativa original no disponible; no se certifica recuperación histórica exhaustiva.','Los antiguos menús se conservan binariamente; su visualización debe validarse en ejecución.','Sin certificación Windows ni hardware PSP.'])
(P/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
for f in (P/'gui').glob('*.go'):f.write_text(f.read_text().replace('RC041_REV6_BETA01','RC041_REV6_BETA02').replace('RC041 REV6 BETA01','RC041 REV6 BETA02'))
print('ready',flush=True)
