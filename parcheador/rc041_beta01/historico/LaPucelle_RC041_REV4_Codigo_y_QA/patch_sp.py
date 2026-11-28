import sys,struct as s,json,re,gzip,hashlib as h,csv,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'/tmp/rc38');from audit import *
p=Path('/tmp/rc41text');dest=p/'RC041_rev4.iso';pack=read(dest,SP);old=nis(pack);new=dict(old);source=nis(read(SRC,SP));rows=json.loads((p/'scriptpack_residual.json').read_text())['matches'];rev={v:k for k,v in codes.items()}
def enc(t):
 safe=''.join(chr(ord(ch)+0xfee0) if 0x21<=ord(ch)<0x2e else ch for ch in t);return b''.join(rev[ch] if ch in rev else ch.encode('cp932') for ch in safe)
translations=['Esa noche','vi a Prier llorando a solas.','Debía de pensar en nuestros','padres fallecidos.','Prier intenta parecer fuerte,','pero...','Creo que por eso no quiere hablar','de ellos. No quería','parecer débil ante mí...','No sabía qué decirle. Me quedé allí','mirando las estrellas...','Entonces','¡Despierta!','Jamás imaginé','Sí...','Creía que solo','gastaba bromas inofensivas.',None,'Así que...']
assert len(rows)==len(translations)
edits=collections.defaultdict(list);journal=[];kept=[]
for r,t in zip(rows,translations):
 name=r['resource'];x=source[name][r['offset_source']:].split(b'\0')[0];pat=bytes([0x32,len(x)+1])+x+b'\0'
 matches=list(re.finditer(re.escape(pat),old[name]));assert len(matches)==r['count']
 for m in matches:
  o=m.start()+2
  if t is None:kept.append(dict(resource=name,offset=o,original=decode(x),reason='Nombre de la compañía NIS'));continue
  edits[name].append((o,x,t))
# Another English line visibly adjacent to repeated Awaken commands.
name='script07.dat';o=1956;x=old[name][o:].split(b'\0')[0];assert decode(x).strip()=='───I am you.';edits[name].append((o,x,'───Yo soy tú.'))
for name,items in edits.items():
 raw=old[name];n=s.unpack_from('<I',raw)[0];body=4+8*n;ptr=s.unpack_from(f'<{n}I',raw,4);assert list(ptr)==sorted(ptr) and ptr[0]==0
 pos=body;data=bytearray(raw[:body]);moves=[]
 for o,x,t in sorted(items):
  assert raw[o-2:o+len(x)+1]==bytes([0x32,len(x)+1])+x+b'\0';assert not any(o<q+body<o+len(x) for q in ptr);assert o-2>=pos
  y=enc(t);assert decode(y)==t,(decode(y),t);assert len(y)<=64
  if len(y)<=len(x):y=y.ljust(len(x),b' ')
  data.extend(raw[pos:o-1]);data.append(len(y)+1);new_o=len(data);data.extend(y+b'\0');pos=o+len(x)+1;moves.append((o,len(x),len(y),new_o));journal.append(dict(package='ISO_SCRIPTPACK',table=name,offset=o,original=decode(x),after=t,hex_before=x.hex(),hex_after=y.hex(),slot=len(x)))
 data.extend(raw[pos:]);
 for i,q in enumerate(ptr):
  absq=body+q;delta=0
  for o,l,k,no in moves:
   if absq>=o+l:delta+=k-l
  s.pack_into('<I',data,4+4*i,q+delta)
 assert data[4+4*n:body]==raw[4+4*n:body]
 # Reverse every edit and restore pointer table, compare exact original bytes.
 restored=bytearray(data)
 for o,l,k,no in reversed(moves):restored[no-1:no+k+1]=raw[o-1:o+l+1]
 restored[:body]=raw[:body];assert restored==raw
 new[name]=bytes(data);print(name,len(raw),len(data),len(items),flush=True)
# preserve original NIS member offsets and all other members, using existing alignment padding.
repacked=bytearray(pack);n=s.unpack_from('<I',pack,12)[0];entries=[(i,*s.unpack_from('<32sIII',pack,16+44*i)) for i in range(n)];entries.sort(key=lambda x:x[2])
for j,(i,nm,o,z,flag) in enumerate(entries):
 name=nm.split(b'\0')[0].decode('cp932');v=new[name];limit=entries[j+1][2] if j+1<len(entries) else len(pack);assert len(v)<=limit-o;assert not any(pack[o+z:o+len(v)])
 if v!=old[name]:repacked[o:o+len(v)]=v;s.pack_into('<I',repacked,16+44*i+36,len(v))
assert nis(repacked)==new and len(repacked)==len(pack)
with dest.open('r+b') as f:f.seek(iso(dest)[SP][0]);f.write(repacked)
assert nis(read(dest,SP))==new
# regenerate ISO patch only
patch=p/'gui/patches';m=json.loads((patch/'manifest.json').read_text());spec=next(s for s in m['specs'] if s['name']=='ISO')
with SRC.open('rb') as f,dest.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as out:
 out.write(b'LPGUI001');o=0
 while True:
  x=f.read(65536);y=g.read(65536)
  if not y:break
  x=x[:len(y)].ljust(len(y),b'\0')
  if x!=y:out.write(s.pack('<QI',o,len(y)));out.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
  o+=len(y)
 out.write(s.pack('<Q',2**64-1))
with dest.open('rb') as f:spec['target_sha256']=h.file_digest(f,'sha256').hexdigest()
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));r=json.loads((p/'report.json').read_text());r['outputs']=m['specs'];r['all_other_ISO_files_unchanged']=False;r['only_ISO_START_and_SCRIPTPACK_changed']=True;r['other_SCRIPTPACK_members_unchanged']=True;r['script_changes']+=len(journal);r['script_by_package']['ISO_SCRIPTPACK']=len(journal);r['script_fixed_length']=False;r['script_indices_unchanged']=False;r['script_SCRIPTPACK_reversible']=True;r['scriptpack_edits']=len(journal);r['scriptpack_preserved_branding']=kept;r['total_text_changes']+=len(journal);r['limitations'].append('Reubicaciones 0x32 y rótulos abreviados pendientes de validación visual; revisión de 481 anclas no es una búsqueda exhaustiva de todos los scripts.')
with (p/'RC041_REV4_Scripts.csv').open('a',encoding='utf-8',newline='') as f:csv.DictWriter(f,fieldnames=list(journal[0])).writerows(journal)
(p/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('DONE',len(journal),r['total_text_changes'],flush=True)
