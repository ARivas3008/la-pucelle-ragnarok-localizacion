import sys,zipfile,csv,io,struct as s,json
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
_,orig=inventory(SRC,Path('/tmp/rc38/orig'));_,cur=inventory(Path('/tmp/rc41closures/RC041_rev3.iso'),Path('/tmp/rc41qa/ULJS00244'))
z=zipfile.ZipFile('/mnt/data/LaPucelle_Proyecto_15_Corpus_GitHub_ChatGPT.zip');n=next(n for n in z.namelist() if '04_MANIFIESTO' in n);man=list(csv.DictReader(io.TextIOWrapper(z.open(n),encoding='utf-8-sig')));rows=[]
for r in man:
 if r['recurso']!='DLC_00/script00.dat':continue
 a=orig['DLC_00']['script00.dat'];off=int(r['offset']);x=a[off:].split(b'\0')[0];pattern=bytes([0x32,len(x)+1])+x+b'\0';assert a[off-2:off+len(x)+1]==pattern,(off,r['original'])
 for k in ['DLC_00','DLC_01','DLC_02','DLC_03']:
  b=cur[k]['script00.dat'];cnt=s.unpack_from('<I',b)[0];body=4+8*cnt;ptrs=s.unpack_from(f'<{cnt}I',b,4);assert ptrs[0]==0 and all(a<=b for a,b in zip(ptrs,ptrs[1:])) and ptrs[-1]<=len(b)-body
  for m in re.finditer(re.escape(pattern),b):
   o=m.start()+2;refs=[p+body-o for p in ptrs if o<=p+body<o+len(x)+1];rows.append(dict(package=k,offset=o,reference_offset=off,original=decode(x),raw=x.hex(),cap=len(x),interior=[v for v in refs if 0<v<len(x)]));print(k,off,o,len(x),refs,repr(decode(x)))
Path('/tmp/rc41text/script_candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('rows',len(rows))
