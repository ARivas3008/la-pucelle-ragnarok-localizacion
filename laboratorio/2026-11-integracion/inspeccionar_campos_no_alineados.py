from pathlib import Path
import json,csv,sys
B=Path(__file__).resolve().parent
exec((B/'planificar_todos_dialogos.py').read_text(encoding='utf8').split('manifest=')[0])
from campos_fijos import PERFILES
rows=json.loads((B/'informes/campos_pendientes_plan.json').read_text(encoding='utf8'))
for r in rows:
 if r['capacidad_bytes'] is not None:continue
 key,name=r['recurso'].split('/');raw=fonts[key][name];off=int(r['offset'])
 print(json.dumps(dict(uid=r['unit_id'],recurso=r['recurso'],offset=off,original=r['original'],bytes=bytes(raw[max(0,off-12):off+64]).hex(),campos=[dict(inicio=c.comienzo,resto=(off-c.header)%c.stride,cap=c.longitud) for c in PERFILES[name]]),ensure_ascii=False),flush=True)
