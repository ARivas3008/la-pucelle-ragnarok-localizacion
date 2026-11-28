import sys,json,struct as s,hashlib as h
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/lp_reintegracion');base=Path('/tmp/rc41rev6/RC041_rev6.iso');key='/PSP_GAME/SYSDIR/EBOOT.BIN';a=read(base,key);b=bytearray(a)
plan=[(0xd1478,'Memory Stick not inserted','No hay Memory Stick'),(0xd1518,'Not enough free space on Memory Stick','Espacio libre insuficiente en Memory Stick'),(0xd1568,'Not enough space on Memory Stick','Espacio insuficiente en Memory Stick'),(0xd15dc,'Free space on Memory not enough','Espacio libre insuficiente'),(0xd1630,'Read necessary data for saving','Leyendo datos para guardar'),(0xd1658,'Please wait','Un momento'),(0xd1674,'Preparing for deletion','Preparando el borrado'),(0xd16a8,'Transfer data possible','Se pueden transferir datos'),(0xd16c4,'Finished saving','Datos guardados'),(0xd1748,'Please insert Memory Stick','Inserta la Memory Stick')]
rows=[]
# Only whole standalone, NUL-terminated exact source strings; preserve slot boundaries.
for off,old,new in plan:
 old=old.encode();new=new.encode();end=off+len(old);assert a[off:end]==old and a[end]==0
 while a[end]==0:end+=1
 assert len(new)<end-off;b[off:end]=new.ljust(end-off,b'\0');rows.append(dict(offset=hex(off),before=old.decode(),after=new.decode(),capacity=end-off))
o=0xd178c;old=b'Checking Memory Stick';new=b'Leyendo Memory Stick ';assert len(new)==len(old) and a[o:o+len(old)+2]==old+b'\x87\x4a';b[o:o+len(old)]=new;rows.append(dict(offset=hex(o),before=old.decode(),after=new.decode().strip(),capacity=len(old),trademark_preserved=True))
assert len(a)==len(b) and all(a[i]==b[i] for i in range(0xd1478)) and a[0xd17a1:]==b[0xd17a1:];(P/'eboot_new.bin').write_bytes(b);(P/'bootmenus.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('menus',len(rows))
