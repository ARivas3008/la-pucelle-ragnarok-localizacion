import sys,json,re,struct as s
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
p=Path('/tmp/rc41text');a=nis(read(SRC,SP));b=nis(read(p/'RC041_rev4.iso',SP));rows=json.loads((p/'scriptpack_residual.json').read_text())['matches']
for r in rows:
 name=r['resource'];x=a[name][r['offset_source']:].split(b'\0')[0];pat=bytes([0x32,len(x)+1])+x+b'\0';raw=b[name];n=s.unpack_from('<I',raw)[0];body=4+8*n;ptr=s.unpack_from(f'<{n}I',raw,4);assert ptr[0]==0 and list(ptr)==sorted(ptr)
 for m in re.finditer(re.escape(pat),raw):
  o=m.start()+2;refs=[q+body-o for q in ptr if o<=q+body<=o+len(x)];print(name,o,len(x),refs,repr(decode(x)))
  if name in ('script05.dat','script07.dat','script15.dat','script18.dat'):
   for match in re.finditer(b'\x32(.)',raw[max(body,o-160):o+180],re.S):
    q=max(body,o-160)+match.start();l=raw[q+1];z=raw[q+2:q+1+l];
    if 1<l<100 and len(z)==l-1 and b'\0' not in z and raw[q+1+l]==0:print('  ',q+2,repr(decode(z)))
