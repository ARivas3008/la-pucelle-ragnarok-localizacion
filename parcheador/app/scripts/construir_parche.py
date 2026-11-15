#!/usr/bin/env python3
"""Parcheador experimental conservador La Pucelle Ragnarok PSP.
No promete una localización final: aplica sólo textos unitarios comprobables sin
cambiar offsets ni punteros, conserva el resto y emite un informe exhaustivo.
No distribuye juegos ni DLC. Usa únicamente archivos aportados por el propietario.
"""
import argparse,csv,hashlib,json,os,re,shutil,struct,subprocess,sys,tempfile,urllib.request,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from nis_formats import lzs_decompress,lzs_header,nispack
from fuentes_es import encode_es, FontError, add_spanish_fonts, CODIGOS, missing_render_glyphs, unpack_pixels, get_tile
from segmentacion import repartir, SegmentacionError
from atlas_ui_es import apply as aplicar_atlas_ui, validate as validar_atlas_ui, AtlasError
from subtitulos_script import aplicar as aplicar_subtitulos_script, CaptionError
from campos_fijos import capacidad_verificada, ampliar_campo, CampoError
from integracion_v013 import cargar_propuestas, ajustar_propuestas, aplicar as aplicar_reducciones_v013

ROOT=Path(__file__).resolve().parents[1]
MENU_CENTRAL=ROOT/'datos/menu_eboot_contextual.csv'
DATA=ROOT/'datos/mapa_26258_unidades.csv'
# En un checkout de GitHub no duplicar el manifiesto maestro (~12 MB).
if not DATA.is_file():
 DATA=ROOT.parents[1]/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv'
REDUCCIONES=ROOT/'datos/propuestas_reduccion_v012.csv'
AJUSTES_REDUCCIONES=ROOT/'datos/ajustes_reducciones_v013.csv'
REMOTE='https://raw.githubusercontent.com/ARivas3008/la-pucelle-ragnarok-localizacion/main/corpus/{:02d}/revision.csv'
SHA_ISO_START='22be383708fe5520cf9da7efa302a2502a9fca82727874b644ab64ad2d72620a'

class Fail(Exception):pass

def sh(b):return hashlib.sha256(b).hexdigest()

def sha_file(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while True:
   chunk=f.read(8*1024*1024)
   if not chunk:break
   h.update(chunk)
 return h.hexdigest()

def read_reviews(repo_dir, fetch):
 rev={}; counter=Counter();tmp=[]
 for n in range(1,16):
  file=Path(repo_dir)/'corpus'/f'{n:02d}'/'revision.csv' if repo_dir else None
  if file and file.exists():
   raw=file.read_bytes()
  elif fetch:
   u=REMOTE.format(n)
   try:
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'LaPucelle-Localizacion/1.0'}),timeout=30) as r:raw=r.read()
   except Exception as e:raise Fail(f'No se pudo obtener revisión {n:02d}: {e}. Usa --repo-directorio')
  else:raise Fail(f'Falta el corpus {n:02d}: usa --repo-directorio con checkout ACTUAL o --descargar-revisiones.')
  s=raw.decode('utf-8-sig').splitlines()
  reader=csv.DictReader(s)
  if not {'grupo_id','es_revisado','estado'}.issubset(reader.fieldnames or []):raise Fail(f'Cabeceras incorrectas corpus {n:02d}')
  for row in reader:
   gid=row['grupo_id']
   if gid in rev:raise Fail(f'ID duplicado en revisiones: {gid}')
   rev[gid]=row;counter[row['estado']]+=1
  tmp.append({'corpus':f'{n:02d}','sha256':sh(raw),'filas':len(s)-1})
 if len(rev)!=15016:raise Fail(f'Se esperaban 15016 grupos de revisión, llegaron {len(rev)}')
 return rev,tmp,counter

def dat_entries(raw):
 n=struct.unpack_from('<I',raw)[0]
 if n<1 or n>2000 or 16+n*32>len(raw):raise Fail('DAT índice inválido')
 base=16+n*32;pos=base;els=[]
 for i in range(n):
  x=16+i*32
  end=base+struct.unpack_from('<I',raw,x)[0]
  name=raw[x+4:x+32].split(b'\0',1)[0].decode('cp932','replace')
  if end<pos or end>len(raw):raise Fail(f'DAT longitud fuera de rango: {name}')
  els.append((name,pos,end));pos=end
 if pos!=len(raw):raise Fail('DAT no cubre el archivo completo')
 return els

def members_from_dat(raw):return {n:bytearray(raw[s:e]) for n,s,e in dat_entries(raw)}

def replace_dat_members(raw, members):
 b=bytearray(raw)
 for n,s,e in dat_entries(raw):
  if n not in members or len(members[n])!=e-s:raise Fail(f'Tamaño miembro DAT distinto: {n}')
  b[s:e]=members[n]
 return bytes(b)

def to_full(s):
 a=[]
 for c in s:
  o=ord(c)
  if c==' ':a.append('　')
  elif c==',':a.append('、')
  elif c=='.':a.append('。')
  elif 0x21<=o<=0x7e:a.append(chr(o+0xfee0))
  else:a.append(c)
 return ''.join(a)

def canonical_source(text):
 """Equivalencia solo de ancho Unicode; no inventa ni completa el original.

 Ejemplo verificado: HP Growth +1 (manifiesto) frente a HP Growth ＋１
 (bytes del juego). No convierte japonés, no elimina caracteres.
 """
 return unicodedata.normalize('NFKC',text)

def match_source(buf,off,orig):
 if off<0 or off>=len(buf) or not orig:return None,None
 # Método original rápido y más estricto.
 for style,s in [('normal',orig),('ancho',to_full(orig))]:
  try:t=s.encode('cp932')
  except UnicodeEncodeError:continue
  if len(t)>0 and buf[off:off+len(t)]==t and off+len(t)<len(buf) and buf[off+len(t)]==0:
   return style,t
 # Algunos textos del juego son MIXTOS, con letras ASCII y signos
 # japoneses de ancho completo. El manifiesto conserva su forma NFKC.
 # Aceptar únicamente si toda la cadena en ese offset coincide tras NFKC.
 end=buf.find(b'\x00',off,min(len(buf),off+2048))
 if end<off+1:return None,None
 raw=bytes(buf[off:end])
 try:decoded=raw.decode('cp932')
 except UnicodeError:return None,None
 if canonical_source(decoded).strip(' \u3000')!=canonical_source(orig).strip(' \u3000'):return None,None
 # Se guarda el ancho original solo si las LETRAS estaban en ancho completo;
 # si no, usar la codificación compacta normal para el texto de destino.
 alnum=[c for c in decoded if c.isascii() and c.isalnum()]
 wide_alnum=[c for c in decoded if ord(c) in range(0xFF10,0xFF5B) and c.isalnum()]
 style='ancho' if wide_alnum and not alnum else 'normal'
 return style,raw

def safe_encoding(text,style,length,drop_accents=False,fuentes_es=False):
 if '\r' in text or '\n' in text or '\x00' in text:raise Fail('saltos de línea o NUL: requieren controlador de cajas')
 if re.search(r'\{[^}]*\}|%[sd]|<[^>]+>',text):raise Fail('contiene controles no validados')
 if drop_accents:
  import unicodedata
  # ¡ y ¿ se eliminan sólo como modo preliminar explícito.
  text=unicodedata.normalize('NFD',text)
  text=''.join(c for c in text if unicodedata.category(c)!='Mn').replace('¿','').replace('¡','')
 if style=='ancho':text=to_full(text)
 try:b=encode_es(text) if fuentes_es else text.encode('cp932')
 except (UnicodeEncodeError,FontError) as e:raise Fail('caracteres sin codificar/fontB; '+str(e)) from e
 if len(b)>length:raise Fail(f'traducción {len(b)} bytes excede los {length} bytes disponibles')
 pad=length-len(b)
 if style=='ancho':
  b+=b' '*(pad%2)+('　'*(pad//2)).encode('cp932')
 else:b+=b' '*pad
 if len(b)!=length:raise Fail('error de relleno')
 return b


def es_revisado_para_parche(gid, review, refinamientos=None):
 """Permite microediciones editoriales contextualizadas con cotejo exacto.
 No altera el corpus remoto ni cambia estados; anota su aplicación por grupo.
 """
 text=review.get('es_revisado','')
 update=(refinamientos or {}).get(gid)
 if update and text==update['origen']:
  return update['ajuste']
 return text

def leer_refinamientos():
 path=ROOT/'datos/ajustes_contextuales.csv'
 if not path.is_file():return {}
 rows={}
 for r in csv.DictReader(path.open(encoding='utf-8-sig',newline='')):
  if not r['grupo_id'] or not r['origen'] or not r['ajuste']:
   raise Fail('Ajustes contextuales incompletos')
  rows[r['grupo_id']]=r
 return rows

def cadenas_dialogo(manifest, source_buffers):
 """Encuentra las intervenciones físicas por la estructura exacta del script.

 En talkXX_jp.dat una unidad textual empieza después del opcode 0x01;
 el separador 0x00 0x01 une dos líneas de LA MISMA intervención.
 Un nuevo opcode 0x02/0x03 implica otro diálogo o cambio de escena.
 Nunca agrupa por simple cercanía de offsets, que sería inseguro.
 """
 by_resource=defaultdict(dict)
 for r in manifest:
  res=r['recurso']
  if res not in source_buffers:continue
  if not re.search(r'(?:^|/)(?:talk\d+(?:_jp)?|script\d+)\.dat$',res,re.I):continue
  by_resource[res][int(r['offset'])]=r
 links={};orphan=set()
 for res,offsets in by_resource.items():
  buf=source_buffers[res]
  for off,row in offsets.items():
   if off<=0 or off>=len(buf) or buf[off-1]!=1:continue
   end=buf.find(b'\x00',off,min(len(buf),off+2048))
   if end<0 or end+2>=len(buf) or buf[end+1]!=1:continue
   after=end+2
   if after in offsets:
    links[(res,off)]=(res,after)
   else:
    orphan.add(row['unit_id'])
 incoming=set(links.values());chains=[];chain_ids=set()
 for start in links:
  if start in incoming:continue
  chain=[start]
  while chain[-1] in links:
   chain.append(links[chain[-1]])
  if len(chain)>=2:
   u=[by_resource[res][off] for res,off in chain]
   chains.append(u)
   chain_ids.update(x['unit_id'] for x in u)
 return chains,chain_ids,orphan

def planificar_intervenciones(manifest,source_buffers,group_units,reviews,investigacion,sin_fuentes_es,fuentes,refinamientos):
 """Aplica un mensaje entero o no aplica ninguna de sus líneas.
 Evita textos medio en español, medio en inglés como los vistos en PPSSPP.
 """
 chains,ids,orphan=cadenas_dialogo(manifest,source_buffers)
 solutions={};rejected={};revised={}
 for chain in chains:
  cids=[r['unit_id'] for r in chain]
  key=tuple(cids)
  try:
   gids=list(dict.fromkeys(r['grupo_id'] for r in chain))
   if any({x['unit_id'] for x in group_units[g]}-{r['unit_id'] for r in chain} for g in gids):
    raise SegmentacionError('Un grupo comparte fragmentos con otra intervención: requiere revisión manual')
   revs=[reviews.get(g) for g in gids]
   if any(not r for r in revs):raise SegmentacionError('Intervención con texto sin revisión central')
   if any(r['estado'] not in ('revisado','requiere_investigacion') for r in revs):
    raise SegmentacionError('Intervención con estado editorial pendiente')
   if not investigacion and any(r['estado']=='requiere_investigacion' for r in revs):
    raise SegmentacionError('Intervención con textos pendientes de investigación')
   spanish=[]
   for g,r in zip(gids,revs):
    t=es_revisado_para_parche(g,r,refinamientos)
    if not t.strip():raise SegmentacionError('Falta traducción de una línea')
    spanish.append(t)
   phrase=' '.join(spanish)
   desc=[]
   for u in chain:
    resource=u['recurso'];off=int(u['offset']);buf=source_buffers[resource]
    style,src=match_source(buf,off,u['original'])
    if not style or src is None:
     raise SegmentacionError('No coinciden todos los bytes originales del mensaje')
    desc.append((resource,off,style,len(src)))
   if len({x[2] for x in desc})!=1:raise SegmentacionError('Intervención con estilos de codificación mezclados')
   if any(rsc!=desc[0][0] for rsc,_,_,_ in desc):raise SegmentacionError('Intervención cruza recursos distintos')
   style=desc[0][2]
   enc=lambda t:encode_es(to_full(t) if style=='ancho' else t) if not sin_fuentes_es else (to_full(t) if style=='ancho' else t).encode('cp932')
   chunks=repartir(phrase,[x[3] for x in desc],encoder=enc)
   staged=[]
   for row,meta,chunk in zip(chain,desc,chunks):
    rsc,off,st,cap=meta
    text=to_full(chunk) if st=='ancho' else chunk
    pack='ISO_START' if rsc.startswith('ISO/') else rsc.split('/')[0]
    if not sin_fuentes_es and (missing:=missing_render_glyphs(text,fuentes[pack]['inner'])):
     raise SegmentacionError('Fuente sin glifos: '+repr(missing))
    b=safe_encoding(chunk,st,cap,fuentes_es=not sin_fuentes_es)
    staged.append((row['unit_id'],meta,chunk,b))
   for uid,meta,chunk,b in staged:solutions[uid]=(meta,chunk,b,key)
   for g,r in zip(gids,revs):
    if es_revisado_para_parche(g,r,refinamientos)!=r['es_revisado']:
     revised[g]=es_revisado_para_parche(g,r,refinamientos)
  except (Fail,SegmentacionError,UnicodeError,FontError) as e:
   for uid in cids:rejected[uid]=str(e)
 # Las cadenas con una unidad de destino que no figura en el manifiesto
 # tampoco pueden darse por traducidas a medias.
 for uid in orphan:rejected.setdefault(uid,'El script tiene una continuación fuera del mapa de unidades')
 return solutions,rejected,ids,revised

def planificar_paginados(manifest,source_buffers,group_units,reviews,investigacion,sin_fuentes_es,fuentes,refinamientos):
 """Traduce un grupo editorial distribuido entre cuadros 0x01/0x02/0x01.

 Reconoce SOLO delimitadores literales entre unidades del mismo grupo;
 nunca añade ni desplaza bytecode o punteros, ni fusiona hablantes diferentes.
 Si cualquiera de sus cajas falla, no modifica ninguna.
 """
 chains,_,_=cadenas_dialogo(manifest,source_buffers)
 solutions={}; rejected={}
 for gid,units in group_units.items():
  if len(units)<2:continue
  ordered=sorted(units,key=lambda x:int(x['offset']))
  res=ordered[0]['recurso']
  if not all(x['recurso']==res for x in ordered):continue
  if not re.search(r'(?:^|/)talk\d+(?:_jp)?\.dat$',res,re.I):continue
  if res not in source_buffers:continue
  buf=source_buffers[res]
  desc=[];boundary=[]
  for u in ordered:
   off=int(u['offset']);style,src=match_source(buf,off,u['original'])
   if not style or src is None or off<1 or buf[off-1]!=1:break
   desc.append((res,off,style,len(src)))
   boundary.append((off,off+len(src)))
  if len(desc)!=len(ordered):continue
  marks=[bytes(buf[end:nxt]) for (_,end),(nxt,_) in zip(boundary,boundary[1:])]
  if not marks or not all(x in (b'\x00\x01',b'\x00\x02\x01') for x in marks):continue
  if b'\x00\x02\x01' not in marks:continue
  members={u['unit_id'] for u in ordered}
  if any(members.intersection({x['unit_id'] for x in c}) and
         any(x['grupo_id']!=gid for x in c) for c in chains):continue
  try:
   rev=reviews.get(gid)
   if not rev or rev['estado'] not in ('revisado','requiere_investigacion'):
    raise SegmentacionError('Sin revisión editorial del grupo paginado')
   if rev['estado']=='requiere_investigacion' and not investigacion:
    raise SegmentacionError('Grupo paginado pendiente de investigación')
   phrase=es_revisado_para_parche(gid,rev,refinamientos)
   if not phrase.strip():raise SegmentacionError('Traducción vacía')
   styles={x[2] for x in desc}
   if len(styles)!=1:raise SegmentacionError('Estilos CP932 mezclados entre páginas')
   style=desc[0][2]
   enc=lambda t:encode_es(to_full(t) if style=='ancho' else t) if not sin_fuentes_es else (to_full(t) if style=='ancho' else t).encode('cp932')
   chunks=repartir(phrase,[x[3] for x in desc],encoder=enc)
   pack='ISO_START' if res.startswith('ISO_START/') else res.split('/')[0] if not res.startswith('ISO/') else 'ISO_START'
   staged=[]
   for u,meta,chunk in zip(ordered,desc,chunks):
    printable=to_full(chunk) if style=='ancho' else chunk
    if not sin_fuentes_es and (missing:=missing_render_glyphs(printable,fuentes[pack]['inner'])):
     raise SegmentacionError('Glifos no disponibles: '+repr(missing))
    encoded=safe_encoding(chunk,style,meta[3],fuentes_es=not sin_fuentes_es)
    staged.append((u['unit_id'],(meta,chunk,encoded,tuple(sorted(members)))))
   solutions.update(staged)
  except (Fail,SegmentacionError,FontError,UnicodeError) as exc:
   for u in ordered:rejected[u['unit_id']]=str(exc)
 return solutions,rejected


def cargar_menus_centrales():
 """Curaduría voluntaria de interfaz. No se confunde con los 15 corpus revisados."""
 with MENU_CENTRAL.open(encoding='utf-8-sig',newline='') as f:
  rows=list(csv.DictReader(f))
 out={}
 for r in rows:
  if not r['original'] or not r['es'] or r['original'] in out:
   raise Fail('Ajuste de menú vacío o duplicado')
  out[r['original']]=r['es']
 return out

def sustituir_eboot_ascii(eboot,manifest,reviews,refinamientos,menus_centrales=None):
 """Solo entradas ASCII completas con mismo bloque NUL y longitud fija.
 No altera secciones ELF, offsets, símbolos, código ni terminadores.
 El menú Start/Continue/Settings se conserva en su tabla original.
 """
 changes={};rejected={}
 for row in manifest:
  if row['recurso']!='ISO/PSP_GAME/SYSDIR/EBOOT.BIN':continue
  uid=row['unit_id'];gid=row['grupo_id'];off=int(row['offset'])
  r=reviews.get(gid)
  source=row['original']
  if source in (menus_centrales or {}):
   text=menus_centrales[source]
  elif r and r['estado']=='revisado':
   text=es_revisado_para_parche(gid,r,refinamientos)
  else:continue
  if not source.isascii() or not text.isascii() or not text.strip() or re.search(r'[%{}<>\\\r\n]',text+source):
   rejected[uid]='EBOOT: texto no ASCII o con controles; requiere ingeniería adicional'
   continue
  if off<0 or off>=len(eboot):rejected[uid]='EBOOT: offset fuera de rango';continue
  end=eboot.find(b'\x00',off,min(len(eboot),off+256))
  if end<off:rejected[uid]='EBOOT: cadena NUL no localizada';continue
  original=bytes(eboot[off:end])
  if original.rstrip(b' ')!=source.encode('ascii'):
   rejected[uid]='EBOOT: los bytes no corresponden exactamente a la fuente';continue
  if len(text)>len(original):
   rejected[uid]='EBOOT: el texto en español excede el campo original';continue
  data=text.encode('ascii').ljust(len(original),b' ')
  if data!=original:
   eboot[off:end]=data
   changes[uid]=(source,text,off)
 return changes,rejected

class Image:
 def __init__(self,path):
  self.path=Path(path)
  with self.path.open('rb') as f:
   f.seek(16*2048);p=f.read(2048)
   if p[1:6]!=b'CD001':raise Fail('ISO9660 inválido')
   self.root=p[156:]
 def records(self):
  with self.path.open('rb') as fp:
   def dec(rec):
    ext=struct.unpack_from('<I',rec,2)[0];ln=struct.unpack_from('<I',rec,10)[0]
    n=rec[32];name=rec[33:33+n].decode('ascii','replace').split(';')[0]
    return name,ext*2048,ln,bool(rec[25]&2)
   def rec(dirent,prefix):
    _,off,size,_=dec(dirent)
    fp.seek(off);d=fp.read(size);idx=0
    while idx<len(d):
     k=d[idx]
     if not k:idx=(idx//2048+1)*2048;continue
     ent=d[idx:idx+k];idx+=k
     name,pos,sz,isdir=dec(ent)
     if name in ('\x00','\x01'):continue
     path=prefix+'/'+name
     yield path,pos,sz,off+idx-k
     if isdir:yield from rec(ent,path)
   yield from rec(self.root,'')
 def read(self,off,length):
  with self.path.open('rb') as f:f.seek(off);return f.read(length)

def cpack(unc, original, folder):
    """Recompresión de NIS LZS con ayudante ya incluido (sin compilar C++)."""
    h = lzs_header(original)
    prebuilt = Path(__file__).parent / ('nis_lzs_pack.exe' if os.name == 'nt' else 'nis_lzs_pack')
    if not prebuilt.is_file():
        raise Fail('Falta el compresor incluido. Vuelve a extraer el parcheador EXE.')
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / 'uncompressed.dat').write_bytes(unc)
        command = [str(prebuilt), str(t / 'uncompressed.dat'), str(t / 'output.lzs'),
                   h['ext'].rstrip(b'\0').decode('ascii'), str(h['marker'])]
        cp = subprocess.run(command, capture_output=True, text=True, errors='replace')
        if cp.returncode:
            raise Fail('Error de compresión LZS: ' + (cp.stderr or cp.stdout)[:1000])
        out = (t / 'output.lzs').read_bytes()
        if lzs_decompress(out) != unc:
            raise Fail('La compresión no pasa la verificación reversible LZS')
        return out

def auditar_graficos(original_members,nuevo_members,atlas_ui=False):
 """Abortar si cambia un recurso gráfico distinto del atlas de fuente.
 También verifica que los glifos existentes no se reescribieron por error.
 """
 no_font=[]
 for name,old in original_members.items():
  if name not in nuevo_members:raise Fail('Recurso eliminado: '+name)
  new=nuevo_members[name]
  if len(old)!=len(new):raise Fail('Tamaño de recurso modificado: '+name)
  if name.lower().endswith('.txp') and name not in ('FontB0000.txp','FontB0001.txp'):
   if atlas_ui and name in ('sys3.txp','sys4.txp'):
    continue # exact diff verified below against SHA-pinned bitmap patches
   if old!=new:raise Fail('Textura no relacionada con fuente alterada: '+name)
   no_font.append(name)
 if all(n in original_members for n in ('fontB.fnt','FontB0000.txp','FontB0001.txp')):
  old_fnt=struct.unpack('<11616H',original_members['fontB.fnt'])
  oldmax=max(old_fnt[1:])
  for name in ('FontB0000.txp','FontB0001.txp'):
   if bytes(original_members[name][:1040])!=bytes(nuevo_members[name][:1040]):
    raise Fail('Cabecera o paleta de textura de fuentes alterada: '+name)
  orig=[unpack_pixels(bytes(original_members[n])) for n in ('FontB0000.txp','FontB0001.txp')]
  dest=[unpack_pixels(bytes(nuevo_members[n])) for n in ('FontB0000.txp','FontB0001.txp')]
  for gid in range(1,oldmax+1):
   if get_tile(orig,gid)!=get_tile(dest,gid):
    raise Fail(f'Glifo original sobrescrito en gid {gid}')
 if atlas_ui:
  try:validar_atlas_ui(original_members,nuevo_members)
  except AtlasError as e:raise Fail('Comprobación de atlas: '+str(e)) from e
 return {'texturas_no_fontB_preservadas':len(no_font), 'glifos_originales_preservados':oldmax,
         'paletas_y_cabeceras_preservadas':True}

def patch(args):
 if not args.iso and not args.dlc_directorio:
  raise Fail('Debes elegir al menos uno de estos objetivos: ISO o carpeta de DLC')
 original_iso=Path(args.iso) if args.iso else None
 if original_iso:
  if not original_iso.is_file():raise Fail('No existe la ISO original')
  if args.salida.resolve()==original_iso.resolve():raise Fail('Prohibido sobrescribir ISO original')
 packs={};recs={};scriptpack={};script_raw=None;scriptinfo=None;startinfo=None;iso=None;ebootinfo=None;eboot_raw=None
 if original_iso:
  iso=Image(original_iso);recs={p:(o,n,r) for p,o,n,r in iso.records()}
  startinfo=recs.get('/PSP_GAME/USRDIR/START_JP.LZS');scriptinfo=recs.get('/PSP_GAME/USRDIR/SCRIPTPACK.DAT')
  if not startinfo or not scriptinfo:raise Fail('ISO sin START_JP o SCRIPTPACK')
  start_lzs=iso.read(*startinfo[:2])
  if sh(start_lzs)!=SHA_ISO_START and not args.permitir_version_diferente:
   raise Fail(f'START_JP distinto del aportado y verificado, SHA256={sh(start_lzs)}')
  start_raw=lzs_decompress(start_lzs)
  packs['ISO_START']={'inner':members_from_dat(start_raw),'source_lzs':start_lzs,'source_raw':start_raw}
  script_raw=iso.read(*scriptinfo[:2])
  scriptpack={x['name']:bytearray(x['content']) for x in nispack(script_raw)}
  ebootinfo=recs.get('/PSP_GAME/SYSDIR/EBOOT.BIN')
  eboot_raw=bytearray(iso.read(*ebootinfo[:2])) if ebootinfo else None
 # Los EDAT originales solo se procesan si se ha solicitado la carpeta de DLC.
 edats={}
 if args.dlc_directorio:
  dlc_folder=Path(args.dlc_directorio)
  if not dlc_folder.is_dir():raise Fail('No existe la carpeta de los DLC')
  for n in range(4):
   p=dlc_folder/f'DL_JP_{n:02d}.EDAT'
   if not p.is_file():raise Fail(f'Falta el DLC {p}')
   data=p.read_bytes();l=nispack(data)
   if len(l)!=1 or l[0]['name'].lower()!='start_jp.lzs':raise Fail(f'DLC no reconocido: {p.name}')
   lzs=l[0]['content'];raw=lzs_decompress(lzs)
   key=f'DLC_{n:02d}'
   packs[key]={'inner':members_from_dat(raw),'source_lzs':lzs,'source_raw':raw}
   edats[key]=(p,data)
 # Texturas de interfaz opcionales: sólo diffs del atlas con SHA original exacto.
 texturas_ui={}
 if args.atlas_ui:
  for k,obj in packs.items():
   try:texturas_ui[k]=aplicar_atlas_ui(obj['inner'])
   except AtlasError as e:raise Fail(f'Atlas de interfaz {k}: {e}') from e
 # Antes de insertar español, insertar glifos privados en LAS CINCO fuentes.
 reporte_fuentes={}
 if not args.sin_fuentes_es:
  for k,obj in packs.items():
   try:reporte_fuentes[k]=add_spanish_fonts(obj['inner'])
   except FontError as e:raise Fail(f'No se pudieron preparar las fuentes para {k}: {e}') from e
 if args.solo_fuentes:
  reviews,revchecks,states={},[],Counter()
 else:
  reviews,revchecks,states=read_reviews(args.repo_directorio,args.descargar_revisiones)
 manifest=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')))
 group_units=defaultdict(list)
 for x in manifest:group_units[x['grupo_id']].append(x)
 source_buffers={}
 for key,obj in packs.items():
  for name,buf in obj['inner'].items():source_buffers[f'{key}/{name}']=buf
 for name,buf in scriptpack.items():source_buffers[f'ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/{name}']=buf
 # Rótulos narrativos del script original, no subtítulos rasterizados del vídeo.
 # Reemplazo exacto dentro del espacio existente; nunca toca Now Loading.
 reporte_script=[];alerta_script=None
 if original_iso and not args.solo_fuentes and not args.sin_subtitulos_script:
  try:
   corregido,reporte_script=aplicar_subtitulos_script(source_buffers['ISO_START/script00.dat'])
   source_buffers['ISO_START/script00.dat'][:]=corregido
  except CaptionError as exc:
   alerta_script=str(exc)  # No impide otros recursos; conservar script original.
 stats=Counter();result=[];patch_offsets=defaultdict(list)
 refinamientos=leer_refinamientos()
 eb_changes={};eb_rejected={}
 if eboot_raw is not None and not args.solo_fuentes:
  eb_changes,eb_rejected=sustituir_eboot_ascii(eboot_raw,manifest,reviews,refinamientos,cargar_menus_centrales())
 block_solutions={};block_rejected={};block_uids=set();editorial_changes={}
 if args.dialogos_atomicos and not args.solo_fuentes:
  block_solutions,block_rejected,block_uids,editorial_changes=planificar_intervenciones(
      manifest,source_buffers,group_units,reviews,args.incluir_investigacion,args.sin_fuentes_es,packs,refinamientos)
 # v0.17: admitir páginas adyacentes del MISMO grupo verificadas por
 # bytecode original, sin desplazar offsets ni cambiar el contenedor.
 paged_solutions,paged_rejected=planificar_paginados(
    manifest,source_buffers,group_units,reviews,args.incluir_investigacion,
    args.sin_fuentes_es,packs,refinamientos)
 for uid,sol in paged_solutions.items():
  block_solutions[uid]=sol
  block_rejected.pop(uid,None)
  block_uids.add(uid)
 seg_solutions={}

 seg_rejected={}
 if args.segmentar_conservador and not args.solo_fuentes:
  for gid,units in group_units.items():
   rev=reviews.get(gid)
   if any(x['unit_id'] in block_uids or x['unit_id'] in block_rejected for x in units):continue
   if len(units)<2 or not rev or rev['estado'] not in ('revisado','requiere_investigacion'):
    continue
   if rev['estado']=='requiere_investigacion' and not args.incluir_investigacion:continue
   if not rev.get('es_revisado','').strip():continue
   descriptors=[]
   for u in units:
    res=u['recurso'];buf=source_buffers.get(res)
    if buf is None:break
    off=int(u['offset']);style,src=match_source(buf,off,u['original'])
    if not style or not src:break
    descriptors.append((res,off,style,len(src)))
   if len(descriptors)!=len(units):continue
   try:
    # No repartir texto sobre recursos o estilos de codificación mezclados.
    if len({(x[0],x[2]) for x in descriptors})>1:continue
    # Calcular capacidad usando el mismo estilo de codificación final.
    style=descriptors[0][2]
    enc=lambda text: encode_es(to_full(text) if style=='ancho' else text) if not args.sin_fuentes_es else (to_full(text) if style=='ancho' else text).encode('cp932')
    chunks=repartir(es_revisado_para_parche(gid,rev,refinamientos),[x[3] for x in descriptors],encoder=enc)
    prepared=[]
    # Preparar TODAS las cajas de un grupo ANTES de escribir cualquiera.
    for u,desc,chunk in zip(units,descriptors,chunks):
     rsc,off,style,cap=desc
     display=to_full(chunk) if style=='ancho' else chunk
     if not args.sin_fuentes_es and missing_render_glyphs(display,packs[rsc.split('/')[0] if not rsc.startswith('ISO/') else 'ISO_START']['inner']):
      raise SegmentacionError('caracter sin glifo en el grupo')
     data=safe_encoding(chunk,style,cap,drop_accents=args.sin_tildes_preliminar,fuentes_es=not args.sin_fuentes_es)
     prepared.append((u['unit_id'],desc,chunk,data))
    for uid,desc,chunk,data in prepared:
     seg_solutions[uid]=(desc,chunk,data)
   except (SegmentacionError,FontError,Fail,UnicodeEncodeError) as e:
    # Una cadena demasiado larga no es un error de todo el parcheo.
    # No modificar ninguna caja del grupo cuando falla una sola.
    seg_rejected[gid]=str(e)
    continue
 for row in manifest:
  uid=row['unit_id'];gid=row['grupo_id'];res=row['recurso'];status='';reason='';newtext='';original=row['original']
  r=reviews.get(gid);units=group_units[gid]
  if res.startswith('ISO/') or res.startswith('ISO_START/'):
   outside=not original_iso
  elif res.startswith('DLC_'):
   outside=not args.dlc_directorio
  else:
   outside=False
  if outside:
   status='OMITIDO_FUERA_DE_ALCANCE';reason='El objetivo no se seleccionó en este parcheo (ISO o DLC)'
  elif args.solo_fuentes:
   status='OMITIDO_SOLO_FUENTES';reason='Modo de prueba de fuentes, sin texto de corpus'
  elif uid in eb_changes:
   status='APLICADO_EBOOT_ASCII';newtext=eb_changes[uid][1]
   reason='EBOOT: reemplazo ASCII de campo NUL exacto, sin mover offsets ni modificar código'
  elif uid in eb_rejected:
   status='BLOQUEADO_EBOOT';reason=eb_rejected[uid]
  elif uid in block_rejected:
   status='BLOQUEADO_BLOQUE_DIALOGO';reason='Intervención original conservada íntegra: '+block_rejected[uid]
  elif uid in block_solutions:
   (rsc,off,style,cap),newtext,target,chainkey=block_solutions[uid]
   occupied=(off,off+cap+1)
   if any(not (occupied[1]<=a or occupied[0]>=b) for a,b in patch_offsets[rsc]):
    status='COLISION';reason='Colisión con otra unidad; revisar bloque completo'
   else:
    source_buffers[rsc][off:off+cap]=target
    patch_offsets[rsc].append(occupied)
    status='APLICADO_PAGINA_ESTRUCTURAL' if uid in paged_solutions else 'APLICADO_BLOQUE_DIALOGO'
    reason='Intervención completa repartida entre cajas 0x01, sin mezclar idiomas'
  elif uid in seg_solutions:
   (rsc,off,style,cap),newtext,target=seg_solutions[uid]
   try:
    occupied=(off,off+cap+1)
    if any(not (occupied[1]<=a or occupied[0]>=b) for a,b in patch_offsets[rsc]):
     status='COLISION';reason='La caja se solapa con otra ya modificada'
    else:
     source_buffers[rsc][off:off+cap]=target
     patch_offsets[rsc].append(occupied)
     status='APLICADO_SEGMENTACION_PROPUESTA'
     reason='Corte por palabras y capacidad de bytes, requiere inspección de cajas y lectura en PPSSPP'
   except Fail as e:
    status='BLOQUEADO_SEGMENTACION';reason=str(e)
  elif not r:
   status='CENTRAL_SIN_REVISION';reason='Los 509 grupos de coordinación son externos al corpus revisado'
  elif len(units)!=1:
   if gid in seg_rejected:
    status='BLOQUEADO_SEGMENTACION';reason='No se modificó ninguna unidad de este grupo: '+seg_rejected[gid]
   else:
    status='RESEGMENTACION';reason=f'Grupo {gid} tiene {len(units)} unidades; distribución de bytes/controles no aprobada'
  elif r['estado'] not in ('revisado','requiere_investigacion'):
   status='NO_REVISADO';reason='Estado editorial '+r['estado']
  elif r['estado']=='requiere_investigacion' and not args.incluir_investigacion:
   status='INVESTIGACION';reason='Marcado requiere_investigacion en el repositorio'
  elif not (newtext:=es_revisado_para_parche(gid,r,refinamientos)).strip():
   status='SIN_TEXTO';reason='No hay español revisado'
  elif res not in source_buffers:
   status='RECURSO_NO_TEXTO';reason='Textura, EBOOT o archivo no mapeado para inserción de cadenas'
  else:
   buf=source_buffers[res];off=int(row['offset'])
   style,src=match_source(buf,off,original)
   if not style:
    status='NO_COINCIDE_FUENTE';reason='Bytes origen no verificables en offset exacto o sin NUL inmediatamente después'
   else:
    try:
     if not args.sin_fuentes_es and (missing:=missing_render_glyphs(to_full(newtext) if style=='ancho' else newtext,packs[res.split('/')[0] if not res.startswith('ISO/') else 'ISO_START']['inner'])):raise Fail('fontB no cubre: '+repr(missing))
     # Tablas de ancho fijo: nombres/descripciones pueden usar su padding cero.
     # Nunca se desplaza el resto del registro ni se modifican offsets.
     campo=capacidad_verificada(res,buf,off,len(src))
     expanded=False
     if campo is not None and not args.sin_tildes_preliminar:
      if any(c in newtext for c in ('\r','\n','\x00','\t')) or re.search(r'\{[^}]*\}|%[sd]|<[^>]+>',newtext):
       raise Fail('Controles especiales: campo fijo no autorizado')
      text_encoded=to_full(newtext) if style=='ancho' else newtext
      try:bytes_es=encode_es(text_encoded) if not args.sin_fuentes_es else text_encoded.encode('cp932')
      except (FontError,UnicodeError) as e:raise Fail(str(e)) from e
      if len(bytes_es)>len(src) and len(bytes_es)+1<=campo:
       try:target=ampliar_campo(bytes(buf[off:off+campo]),len(src),bytes_es,campo)
       except CampoError as e:raise Fail(str(e)) from e
       expanded=True
     if not expanded:
      target=safe_encoding(newtext,style,len(src),drop_accents=args.sin_tildes_preliminar,fuentes_es=not args.sin_fuentes_es)
     if target==src:
      status='SIN_CAMBIO';reason='Ya coincide con fuente'
     else:
      occupied=(off,off+len(target)+(0 if expanded else 1))
      if any(not (occupied[1]<=a or occupied[0]>=b) for a,b in patch_offsets[res]):
       status='COLISION';reason='Zona ya alterada por otra unidad'
      else:
       buf[off:off+len(target)]=target
       patch_offsets[res].append(occupied)
       if expanded:
        status='APLICADO_CAMPO_FIJO_PROVISIONAL' if r['estado']=='requiere_investigacion' else 'APLICADO_CAMPO_FIJO'
        reason=f'Campo reservado de {len(target)} bytes, con NUL y ceros: sin mover punteros'
       else:
        status='APLICADO_PROVISIONAL' if r['estado']=='requiere_investigacion' else 'APLICADO'
        reason='Cadena actualizada dentro de espacio y offset originales; comprobar visualmente'
    except Fail as e:
     status='BLOQUEADO_CODIFICACION_O_TAMANO';reason=str(e)
  stats[status]+=1
  result.append({'unit_id':uid,'grupo_id':gid,'recurso':res,'offset':row['offset'],'estado':status,'motivo':reason,'estado_editorial':r['estado'] if r else 'central','original':original,'es_revisado':newtext})
 # Integración opcional v0.13: solo unidades que el motor anterior no insertó.
 reporte_reducciones={'conteos':{},'detalles':[],'eboot_cambios':{}}
 if args.reducciones_verificadas and not args.solo_fuentes:
  if not REDUCCIONES.is_file():raise Fail('Falta el CSV versionado de reducciones v0.12')
  reporte_reducciones=aplicar_reducciones_v013(
      ajustar_propuestas(cargar_propuestas(REDUCCIONES),AJUSTES_REDUCCIONES),
      manifest,result,source_buffers,eboot_raw,
      patch_offsets,packs,match_source,reviews,fuentes_activas=not args.sin_fuentes_es)
  eb_changes.update(reporte_reducciones['eboot_cambios'])
  stats=Counter(r['estado'] for r in result)
 args.salida.mkdir(parents=True,exist_ok=True)
 with (args.salida/'reporte_por_unidad.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=result[0]);w.writeheader();w.writerows(result)
 summary={'advertencia':'PARCHE EXPERIMENTAL PARCIAL; NO CERTIFICA JUGABILIDAD NI REINSERCION TOTAL',
          'original_iso_sha256':sha_file(original_iso) if args.hash_iso and original_iso else '(no calculado/no seleccionado)',
          'objetivos':{'iso':bool(original_iso),'dlc':bool(edats)},
          'estado_revisiones':dict(states),'sha256_revisiones':revchecks,'unidades_por_estado':dict(stats),
          'cadenas_modificadas':sum(v for k,v in stats.items() if k.startswith('APLICADO')),
          'bloques_de_dialogo_procesados':len({v[3] for v in block_solutions.values()}),
          'grupos_paginados_estructurales':len({v[3] for v in paged_solutions.values()}),
          'unidades_paginadas_estructurales':len(paged_solutions),
          'bloques_bloqueados':len(set(block_rejected.values())),
          'ediciones_contextuales_aplicadas':editorial_changes,
          'menus_eboot_ascii_aplicados':len(eb_changes),
          'reducciones_v012':{'conteos':reporte_reducciones['conteos'], 'auditoria_editorial_pendiente':True},
          'campos_fijos_ampliados':stats['APLICADO_CAMPO_FIJO']+stats['APLICADO_CAMPO_FIJO_PROVISIONAL'],
          'rotulos_narrativos_script':reporte_script,
          'alerta_rotulos_script':alerta_script,
          'now_loading_modificado':False,
          'texturas_interfaz_localizadas':texturas_ui,
          'fuentes_es':{k:{'glifos_agregados':v['glifos_agregados'],'alias_ascii':v['alias_ascii'],'gid_final':v['gid_final']} for k,v in reporte_fuentes.items()},
          'cobertura_fuentes':{c:b.hex() for c,b in CODIGOS.items()} if reporte_fuentes else {},
          'total_unidades':len(result),'revisiones_pendientes':stats['INVESTIGACION'],
          'unidades_bloqueadas':sum(v for k,v in stats.items() if k.startswith('BLOQUEADO_')),
          'unidades_sin_resegmentar':stats['RESEGMENTACION']}
 (args.salida/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'estados':dict(stats),'output':str(args.salida)},ensure_ascii=False,indent=2))
 if args.solo_auditoria:return
 if summary['cadenas_modificadas']==0 and not reporte_fuentes:raise Fail('No se creó ningún juego modificado: cero cambios verificables')
 # Compresión y validación de START ISO y 4 DLC; no pasa a fase de escritura sin 5 recompressiones válidas.
 new_lzs={}
 summary['auditoria_grafica']={}
 for key,obj in packs.items():
  summary['auditoria_grafica'][key]=auditar_graficos(members_from_dat(obj['source_raw']),obj['inner'],atlas_ui=args.atlas_ui)
  candidate=replace_dat_members(obj['source_raw'],obj['inner'])
  new_lzs[key]=cpack(candidate,obj['source_lzs'],key)
  summary.setdefault('recompresion',{})[key]={'original':len(obj['source_lzs']),'nuevo':len(new_lzs[key]),'raw_sha256':sh(candidate)}
 if original_iso:
  start_off,start_len,_=startinfo
  nextstart=min([o for p,(o,_,_) in recs.items() if o>start_off] or [original_iso.stat().st_size])
  if len(new_lzs['ISO_START'])>nextstart-start_off:raise Fail(f'START excede espacio ISO: {len(new_lzs["ISO_START"])} > {nextstart-start_off}. No se escribió ISO.')
  temp=Path(str(args.salida/'La_Pucelle_Ragnarok_ES_PRELIMINAR.iso')+'.tmp')
  out_iso=args.salida/'La_Pucelle_Ragnarok_ES_PRELIMINAR.iso'
  try:
   shutil.copyfile(original_iso,temp)
   with temp.open('r+b') as f:
    f.seek(start_off);f.write(new_lzs['ISO_START']);f.write(b'\x00'*max(0,start_len-len(new_lzs['ISO_START'])))
    rec_off=startinfo[2]
    f.seek(rec_off+10);f.write(struct.pack('<I',len(new_lzs['ISO_START']))+struct.pack('>I',len(new_lzs['ISO_START'])))
    for file in nispack(script_raw):
     new=scriptpack[file['name']]
     if len(new)!=file['size']:raise Fail('Cambio peligroso de longitud scriptpack')
     f.seek(scriptinfo[0]+file['offset']);f.write(new)
    if eboot_raw is not None and eb_changes:
     f.seek(ebootinfo[0]);f.write(eboot_raw)
   os.replace(temp,out_iso)
  finally:
   if temp.exists():temp.unlink()
  verifyiso=Image(out_iso)
  rec2={p:(o,n,r) for p,o,n,r in verifyiso.records()}
  if sh(verifyiso.read(*rec2['/PSP_GAME/USRDIR/START_JP.LZS'][:2]))!=sh(new_lzs['ISO_START']):raise Fail('Error de verificación del START dentro de ISO nueva')
  if eb_changes and sh(verifyiso.read(*rec2['/PSP_GAME/SYSDIR/EBOOT.BIN'][:2])) != sh(eboot_raw):raise Fail('Error en verificación EBOOT de menús')
  sc2=verifyiso.read(*rec2['/PSP_GAME/USRDIR/SCRIPTPACK.DAT'][:2]);member2={x['name']:x['content'] for x in nispack(sc2)}
  if len(member2)!=len(scriptpack) or any(sh(member2.get(k,b''))!=sh(v) for k,v in scriptpack.items()):raise Fail('SCRIPTPACK no coincide tras empaquetado')
 for key,(p,data) in edats.items():
  out=args.salida/(p.stem+'_ES_PRELIMINAR.EDAT')
  # Original NISPACK header de 2048 bytes, único miembro con size en offset 0x34.
  buf=bytearray(data[:2048]);struct.pack_into('<I',buf,0x34,len(new_lzs[key]))
  out.write_bytes(bytes(buf)+new_lzs[key])
  check=nispack(out.read_bytes())
  if len(check)!=1 or lzs_decompress(check[0]['content'])!=replace_dat_members(packs[key]['source_raw'],packs[key]['inner']):raise Fail(f'No coincide DLC reconstruido {key}')
 (args.salida/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 print(('ISO y ' if original_iso else '')+('4 EDAT ' if edats else '')+'preliminares reconstruidos; NO aprobados para publicación/juego sin QA PPSSPP.')

def main():
 p=argparse.ArgumentParser(description='Auditar y reconstruir LOCALMENTE una ISO PSP y 4 DLC (experimental, fail-closed)')
 p.add_argument('--iso',type=Path,help='ISO opcional; no se exige en modo solo DLC')
 p.add_argument('--dlc-directorio',type=Path,help='Carpeta DLC opcional; no se exige en modo solo ISO')
 p.add_argument('--repo-directorio',type=Path,help='Checkout GitHub actualizado con 15 corpus revisados')
 p.add_argument('--descargar-revisiones',action='store_true',help='Obtener 15 archivos revision.csv públicos del main actual')
 p.add_argument('--salida',required=True,type=Path)
 p.add_argument('--solo-auditoria',action='store_true')
 p.add_argument('--incluir-investigacion',action='store_true',help='Permitir propuestas marcadas requiere_investigacion, como provisional')
 p.add_argument('--atlas-ui',action='store_true',help='Atlas de interfaz sys3/sys4 con original SHA256 verificado; vista previa recomendada')
 p.add_argument('--reducciones-verificadas',action='store_true',help='OPT-IN: abreviaciones v0.12 que pasan capacidad/bytes; todavía requieren QA editorial y visual')
 p.add_argument('--sin-subtitulos-script',action='store_true',help='No editar los cuatro rótulos narrativos identificados en script00.dat')
 p.add_argument('--solo-fuentes',action='store_true',help='Generar ISO y 4 DLC con fuentes extendidas; sin descargar revisiones ni sustituir diálogos')
 p.add_argument('--sin-fuentes-es',action='store_true',help='Desactiva extensión de fontB (no recomendado)')
 p.add_argument('--segmentar-conservador',action='store_true',help='Repartición por palabras solo fuera de bloques de discurso')
 p.add_argument('--dialogos-atomicos',action='store_true',help='Sin mezclar idiomas dentro de cada intervención de bytecode 0x01 (recomendado)')
 p.add_argument('--sin-tildes-preliminar',action='store_true',help='OPCIONAL: sustituir caracteres españoles no CP932; pérdida ortográfica')
 p.add_argument('--permitir-version-diferente',action='store_true')
 p.add_argument('--hash-iso',action='store_true')
 a=p.parse_args()
 if not (a.iso or a.dlc_directorio):p.error('selecciona --iso o --dlc-directorio (o ambos)')
 try:patch(a)
 except (Fail,ValueError,IndexError,UnicodeError) as e:print('BLOQUEADO:',e,file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
