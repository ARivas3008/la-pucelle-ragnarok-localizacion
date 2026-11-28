import struct as s,json,hashlib,re,zlib,sys,os,collections
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import iso,read,inventory,inspect,align,lines,decode,nis,lzs,dat
P=Path('/tmp/lapucelle_beta1'); O=Path('/tmp/rc38/orig'); B=P/'JUEGO_PARA_PPSSPP_RC041_REV6'; M=Path('/mnt/data'); A=O/'La_Pucelle_Ragnarok_v1.1.2.iso'; C=B/'La_Pucelle_Ragnarok_ES_RC041_REV6.iso'; E=M/'LaPucelle_Parcheador_RC041_REV6_GUI_Nativo.exe';Q=json.loads((M/'QA_RC041_REV6.json').read_text());D=B/'ULJS00244'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
checks={};rows=[]
for x in Q['outputs']:
 name=x['name'];a=A if name=='ISO' else O/name;b=C if name=='ISO' else D/name
 h1,h2=sha(a),sha(b);assert h1==x['source_sha256'] and h2==x['target_sha256'];rows.append(dict(name=name,source_sha256=h1,target_sha256=h2,size=b.stat().st_size,status='PASS'))
assert sha(E)==Q['windows_exe_sha256'];raw=E.read_bytes();pe=s.unpack_from('<I',raw,60)[0];assert raw[pe:pe+4]==b'PE\0\0';checks['exe']={'sha256':sha(E),'machine':hex(s.unpack_from('<H',raw,pe+4)[0]),'subsystem':s.unpack_from('<H',raw,pe+24+68)[0]}
found={};expected={v:k for k,v in Q['embedded_streams_verified'].items()}
for m in re.finditer(b'\x1f\x8b\x08',raw):
 i=m.start()
 try:
  z=zlib.decompressobj(31)
  if z.decompress(raw[i:i+65536],8)!=b'LPGUI001':continue
  z=zlib.decompressobj(31);z.decompress(raw[i:]);assert z.eof;n=len(raw)-i-len(z.unused_data);h=hashlib.sha256(raw[i:i+n]).hexdigest()
  if h in expected:found[expected[h]]=h
 except zlib.error:continue
assert len(found)==5;checks['embedded_streams']=found
orig,new=iso(A),iso(C);assert set(orig)==set(new)
def get_sfo(p):
 b=read(p,'/PSP_GAME/PARAM.SFO');assert b[:4]==b'\0PSF';ko,vo,n=s.unpack_from('<III',b,8);out={}
 for i in range(n):
  k,fmt,l,m,off=s.unpack_from('<HHIII',b,20+16*i);name=b[ko+k:b.index(0,ko+k)].decode();v=b[vo+off:vo+off+l];out[name]=v.rstrip(b'\0').decode('utf8','replace') if fmt==0x204 else s.unpack('<I',v)[0] if fmt==0x404 and l==4 else v.hex()
 return out
p=get_sfo(C);assert p==get_sfo(A) and p['DISC_ID']=='ULJS00244';checks['param_sfo']=p
for path,tree in [(A,orig),(C,new)]:
 with path.open('rb') as f:
  f.seek(32768);pvd=f.read(2048);assert pvd[:7]==b'\x01CD001\x01';v=s.unpack_from('<I',pvd,80)[0];assert v==s.unpack_from('>I',pvd,84)[0];assert v*2048<=path.stat().st_size
  for k,(o,n,r) in tree.items():
   assert o+n<=path.stat().st_size,(k,o,n);f.seek(r);e=f.read(34);assert s.unpack_from('>I',e,6)[0]*2048==o and s.unpack_from('>I',e,14)[0]==n
  checks[path.name]={'entries':len(tree),'volume_sectors':v,'size':path.stat().st_size}
checks['relocated_entries']=[k for k in new if new[k][0]!=orig[k][0]];checks['resized_entries']=[k for k in new if new[k][1]!=orig[k][1]]
print('ISO, SFO, hashes, streams passed',flush=True)
a,pa=inventory(A,O);b,pb=inventory(C,D);assert set(a)==set(b);stats=[];candidates=[]
# Flag, do not translate blindly: exact unmodified multiword English lines or Japanese characters in parsed strings.
for k,x in a.items():
 y=b[k];ma,mb=inspect(x),inspect(y);aligned=list(align(k,x,y,ma,mb));stats.append(dict(resource=k,original_runs=len(ma['runs']),patched_runs=len(mb['runs']),aligned=len(aligned),lines=sum(map(len,mb['runs']))));
 for r,q in aligned:
  origl=lines(r);es=lines(q)
  for t in es:
   if re.search(r'[\u3041-\u30ff\u3400-\u9fff]',t) or (t in origl and len(re.findall(r'[A-Za-z]{2,}',t))>=4):
    candidates.append({'resource':k,'entry':q[0]['entry'],'offset':q[0]['offset'],'source':' | '.join(origl),'target':' | '.join(es),'candidate':t})
print('TALK',len(stats),sum(t['patched_runs'] for t in stats),sum(t['aligned'] for t in stats),'candidates',len(candidates),flush=True)
report=dict(version='RC041 REV6',emulator_required='PPSSPP 1.20.4',runtime_executed=False,savestates_generated=0,checks=checks,outputs=rows,talk=stats,heuristic_candidates=len(candidates),limitations=['No PPSSPP instalado; descarga bloqueada por red/DNS.','No prueba de GUI Windows ni ejecución de juego.','Candidatos heurísticos no equivalen a fallos confirmados.'])
(P/'qa'/'QA_BETA01.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(P/'qa'/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2))
