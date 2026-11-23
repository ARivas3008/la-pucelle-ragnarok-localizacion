from pathlib import Path
import sys,struct,collections,json
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from construir_parche import Image
from nis_formats import nispack
i=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in i.records()}
files=nispack(i.read(*rec['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']))
for file in files:
 if file['name']!='talk01_jp.dat':continue
 b=file['content'];n=struct.unpack_from('<I',b)[0];base=8+32*n
 entries=[struct.unpack_from('<8I',b,8+32*k) for k in range(n)]
 print(file['name'],'size',len(b),'entries',n,'base',base)
 for j in range(8):print('Campo',j,'valores',collections.Counter(e[j] for e in entries).most_common(12))
 for k,e in enumerate(entries[:18]):
  start=base+e[0];end=base+entries[k+1][0] if k+1<n else len(b)
  print(k,e,'BYTES',b[start:end].hex(),'TEXTO',repr(b[start:end].decode('cp932',errors='replace')))
