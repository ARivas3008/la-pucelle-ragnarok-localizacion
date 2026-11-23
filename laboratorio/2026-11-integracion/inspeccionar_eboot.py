import sys,struct,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
from construir_parche import Image
i=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');records={p:(o,n) for p,o,n,_ in i.records()}
data=i.read(*records['/PSP_GAME/SYSDIR/EBOOT.BIN'])
assert data[:6]==b'\x7fELF\x01\x01'
shoff=struct.unpack_from('<I',data,32)[0];ents,n,strings=struct.unpack_from('<3H',data,46)
sec=[struct.unpack_from('<10I',data,shoff+j*ents) for j in range(n)]
names=data[sec[strings][4]:sec[strings][4]+sec[strings][5]]
sections=[]
for s in sec:
 name=names[s[0]:].split(b'\0')[0].decode('ascii')
 sections.append(dict(name=name,flags=s[2],addr=s[3],offset=s[4],size=s[5]))
print('secciones',sections)
for needle in [b'Settings',b'Cursor Mode',b'Attack',b'Status']:
 print(needle,[(m.start(),next((s['name'] for s in sections if s['offset']<=m.start()<s['offset']+s['size']),None)) for m in re.finditer(re.escape(needle)+b'\0',data)])
(B/'informes/eboot_secciones.json').write_text(json.dumps(sections,indent=2),encoding='utf-8')
