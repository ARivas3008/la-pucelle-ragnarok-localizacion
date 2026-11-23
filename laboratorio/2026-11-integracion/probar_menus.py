from pathlib import Path
import sys,csv,json,hashlib
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as c
source=c.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso')
records={p:(o,n) for p,o,n,_ in source.records()}
off,length=records['/PSP_GAME/SYSDIR/EBOOT.BIN'];original=source.read(off,length);data=bytearray(original)
with c.DATA.open(encoding='utf-8-sig',newline='') as f:manifest=list(csv.DictReader(f))
reviews,_,_=c.read_reviews(B/'fuente',False)
changed,rejected=c.sustituir_eboot_ascii(data,manifest,reviews,c.leer_refinamientos(),c.cargar_menus_centrales(),True)
allowed=set()
for uid,(a,b,pos) in changed.items():
 end=original.index(b'\0',pos);allowed.update(range(pos,end))
assert len(data)==len(original)
assert all(i in allowed for i,(a,b) in enumerate(zip(original,data)) if a!=b)
dest=B/'prueba_integrada/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'
target=c.Image(dest);rec={p:(o,n) for p,o,n,_ in target.records()}
assert rec['/PSP_GAME/SYSDIR/EBOOT.BIN']==(off,length)
with dest.open('r+b') as f:f.seek(off);f.write(data)
(B/'informes/prueba_menus.json').write_text(json.dumps(dict(cambios=changed,rechazos=rejected,
 sha256_eboot=hashlib.sha256(data).hexdigest(),fuera_de_textos_identico=True),ensure_ascii=False,indent=2),encoding='utf-8')
print('Menús insertados:',len(changed),'rechazados:',rejected)
