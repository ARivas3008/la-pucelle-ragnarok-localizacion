from pathlib import Path
import sys,csv,json,re,hashlib
B=Path(__file__).resolve().parent;R=B.parent
sys.path.insert(0,str(B/'fuente/parcheador/app/scripts'))
import construir_parche as c
from fuentes_es import encode_es
i=c.Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');rec={p:(o,n) for p,o,n,_ in i.records()}
b=i.read(*rec['/PSP_GAME/SYSDIR/EBOOT.BIN'])
manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')))
occupied=[]
for row in manifest:
 if row['recurso'].endswith('EBOOT.BIN'):
  off=int(row['offset']);end=b.find(b'\0',off);occupied.append((off,end))
menus=c.cargar_menus_centrales()
menus.update(json.loads((B/'menus_adicionales_contextuales.json').read_text(encoding='utf-8')))
menus.update({'Cursor Mode   Ａ':'Modo cursor   A','Cursor Mode   Ｂ':'Modo cursor   B',
 'Save':'Guardar','Time':'Tiempo','Quit':'Salir','Skills':'Hab.','Equip':'Equip',
 'Items':'Obj.','And':'y','Super full':'Muy lleno','Survey':'Encuesta',
 'Are you sure?':'¿Seguro?', 'Mt. Tarte':'Monte Tarte','Watercress Castle':'Cast. Berros',
 'HP':'PV','SP':'PE','Del.':'Borr','Pause':'Pausa',
 '%dSpecific items will power up':'%dPotencia ciertos objetos'})
patches=[];candidates=[];unchanged=[]
for m in re.finditer(rb'[^\x00]+\x00',b):
 off=m.start();raw=m.group()[:-1];end=off+len(raw)
 if not 699836<=off<893796 or len(raw)>180 or len(raw)<2:continue
 if any(off<z and end>a for a,z in occupied):continue
 # Tres límites de string cotejados en la tabla de UI; los bytes previos
 # pertenecen al campo anterior y se conservan literalmente.
 if off in (782787,783463,783495):off+=1;raw=raw[1:]
 try:source=raw.decode('cp932')
 except UnicodeError:continue
 if any(ord(ch)<32 for ch in source):continue
 src=source.rstrip(' \u3000');prefix='';dest=menus.get(src)
 if dest is None:
  while src and src[0] in '○×□△◇◆　／':prefix+=src[0];src=src[1:]
  dest=menus.get(src)
 if source in ('×Quit','／×Quit'):dest='Sal.'
 if source=='○Wear＆Buy':dest='Compra/e.'
 if dest is not None:
  target=prefix+dest
  encoded=encode_es(target)
  if len(encoded)<=len(raw):
   format_tokens=lambda t:re.findall(r'%[-+ #0]*\d*(?:\.\d+)?[diuoxXfFeEgGcs%]',t)
   assert format_tokens(source)==format_tokens(target),(source,target)
   encoded=encoded.ljust(len(raw),b' ')
   if encoded!=raw:
    patches.append(dict(id=f'EBOOT_EXTRA_{off}',offset=off,original=source,es=target,
      antes_hex=raw.hex(),despues_hex=encoded.hex(),origen='Coincidencia literal de etiqueta contextual o revisión de UI'))
   else:unchanged.append(dict(offset=off,original=source))
  else:candidates.append(dict(offset=off,original=source,es=target,motivo='No cabe en campo'))
 elif source in ('La Pucelle','Eclair','Satan','English','user_main'):unchanged.append(dict(offset=off,original=source))
 elif re.search(r'[A-Za-z]{3}',source) and 763000<off<795000 and not re.search(r'\.dat|\.txp|\.lzs|\.km2|\.KM2|\.mp[dp]|std::|not found|scriptPack|setenablesave',source):
  candidates.append(dict(offset=off,original=source,es='',motivo='Revisar contexto fuera del corpus'))
result=dict(original_sha256=hashlib.sha256(b).hexdigest(),size=len(b),patches=patches)
(B/'fuente/parcheador/app/datos/menus_fuera_corpus.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(B/'informes/menus_fuera_corpus_pendientes.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf-8')
print('Adicionales:',len(patches),'ya iguales:',len(unchanged),'pendientes:',len(candidates))
print(json.dumps(candidates,ensure_ascii=False,indent=1))
