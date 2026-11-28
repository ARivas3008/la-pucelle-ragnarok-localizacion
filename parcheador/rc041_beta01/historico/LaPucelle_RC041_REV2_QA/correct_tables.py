import sys,struct as s,hashlib as h,json,shutil,gzip,csv,re,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/rc41qa');old=Path('/tmp/rc41/RC041.iso');dest=P/'RC041_rev2.iso';dlcold=Path('/tmp/rc41/ULJS00244');dlcnew=P/'ULJS00244';dlcnew.mkdir(exist_ok=True)
# Exact known source fields. No global substitution. Maintain glossary and controls.
plans={
'kis.dat':{
'A sword used by a famous hero':'Espada de un héroe famoso.', 'Has the elemental power of fire':'Posee el poder elemental del fuego.', 'Wind Staff':'Bastón de viento', 'Has the elemental power of wind':'Posee el poder elemental del viento.', 'Has the elemental power of ice':'Posee el poder elemental del hielo.', 'Has the elemental power of thunder':'Posee el poder elemental del rayo.', 'Has the elemental power of aid':'Posee el poder elemental de apoyo.', 'Has the elemental power of healing':'Posee el poder elemental de curación.', 'Has the elemental power of holiness':'Posee el poder elemental sagrado.', 'Makes it easier to make friends':'Facilita hacer amigos.', 'Once used by the great Polyansky':'Usada por el gran Polyansky.', 'Increases chances of hitting':'Aumenta la probabilidad de acertar.', 'Increases chance of hitting':'Aumenta la probabilidad de acertar.', 'Recovers HP':'Recupera HP.', 'Recovers SP':'Recupera SP.', **{'Makes it easier to increase '+x:'Facilita aumentar '+x+'.' for x in ('SP','ATK','DEF','INT','SPD','HIT','RES')}},
'magic.dat':{'Lightning Spear':'Lanza relámpago','A healing miracle':'Un milagro de curación.','The most advanced healing miracle':'El milagro de curación más avanzado.','Rail Gun':'Cañón de riel','A combined attack with Dark Eclair':'Ataque combinado con Éclair oscura.','A combined attack with Eclair':'Ataque combinado con Éclair.','Light and Dark':'Luz y oscuridad','Lightning Rod':'Pararrayos','Sword Throw':'Lanzamiento de espada','A cruel claw attack':'Un ataque de garras.','Judgement':'Juicio','Heals everyone':'Cura a todos.','Spirit Wave':'Onda espiritual','Battlecry':'Grito de guerra','Curse Roar':'Rugido maldito','Deals great damage to everyone':'Inflige mucho daño a todos.','Decrease defensive power':'Reduce la defensa.','Healing Roar':'Rugido curativo','Heal everyone':'Cura a todos.','Dark Wave':'Onda oscura','Thunder Crash':'Impacto de trueno','Heals target':'Cura al objetivo.',**{'A combination attack with '+x:'Ataque combinado con '+y+'.' for x,y in [('Homard','Homard'),('Alouette','Alouette'),('Prier','Prier'),('Culottes','Culotte'),('Yattanya','Yattanya'),('Eclair','Éclair'),('Salade','Salade'),('Croix','Croix'),('Dark Eclair','Éclair oscura'),('Flonne','Flonne')]},**{'Damage target with the power of '+x:'Daña al objetivo con el poder '+y+'.' for x,y in [('fire','del fuego'),('wind','del viento'),('ice','del hielo'),('lightning','del rayo'),('light','de la luz')]}},
'skill.dat':{'Allows critical hits':'Permite golpes críticos.','Attack strength temporarily up':'Aumenta temporalmente el ataque.','Enemy defense temporarily down':'Reduce temporalmente la defensa enemiga.','Defense temporarily up':'Aumenta temporalmente la defensa.','Magic defense temporarily up':'Aumenta temporalmente la defensa mágica.','Recovers HP':'Recupera PV.'},
'mapinfo.dat':{'Couscous Village':'Aldea Cuscús','Choux Fleurs Hill':'Colina Chou-Fleur','Mayonnaise Harbor':'Puerto Mayonesa','Saint Chapel':'Capilla Santa Doncella','Corridor of Darkness':'Pasillo de las tinieblas'},
'char.dat':{'Dark Eclair':'Éclair oscura','Dark Knight':'Caballero oscuro','Old Woman':'Anciana'},
'ritem.dat':{'Very strong':'Es muy fuerte.','Pot Lid':'Tapa de olla'}}
# Field positions proven by record layout. ritem only exact anchors below.
fields={'kis.dat':(148,{8:21,29:59}),'magic.dat':(116,{26:22,51:53}),'skill.dat':(94,{45:59}),'mapinfo.dat':(96,{20:64}),'char.dat':(100,{8:24})}
def enc(t):
 rev={v:k for k,v in codes.items()};v=b''.join(rev[x] if x in rev else x.encode('cp932') for x in t);assert decode(v)==t;return v
def cstr(b,o):return b[o:b.index(0,o)]
def sha(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
_,original=inventory(SRC,Path('/tmp/rc38/orig'));_,current=inventory(old,dlcold);expected={k:dict(m) for k,m in current.items()};changes=[];skipped=[];candidates=[]
for name,plan in plans.items():
 src=original['ISO_START'][name];cur=current['ISO_START'][name]
 if name=='ritem.dat': positions=[(6925,59),(9856,13),(9869,59)]
 else:
  stride,layout=fields[name];positions=[(o,cap) for mod,cap in layout.items() for o in range(mod,len(src)-cap+1,stride)]
 for o,cap in sorted(positions):
  x=cstr(src,o);key=x.decode('ascii','ignore').strip();target=plan.get(key)
  if target is None or x.strip()!=key.encode('ascii') or cstr(cur,o)!=x:continue
  if name=='magic.dat' and o%116==51:assert src[o-2]==0x87 and cur[o-2:o]==src[o-2:o]
  candidates.append((name,o,cap,key,target))
for name,o,cap,key,target in candidates:
 y=enc(target);jp=cstr(original['DLC_00'][name],o)
 if len(y)+1>cap:skipped.append(dict(resource=name,offset=o,source=key,target=target,reason='capacidad'));continue
 for k,tables in current.items():
  raw=expected[k][name];source=original[k][name];x=cstr(source,o);v=cstr(raw,o)
  if k!='ISO_START' and (x!=jp or not re.search('[\u3040-\u30ff\u3400-\u9fff]',decode(x))):continue
  if v!=x:continue # preserve already reviewed translations
  if name=='magic.dat' and o%116==51:
   if source[o-2]!=0x87 or raw[o-2:o]!=source[o-2:o]:skipped.append(dict(resource=k+'/'+name,offset=o,source=decode(x),target=target,reason='control previo distinto'));continue
  n=max(len(x),len(y))+1
  if n>cap or any(raw[o+len(v):o+n]) or any(source[o+len(x):o+n]):skipped.append(dict(resource=k+'/'+name,offset=o,source=decode(x),target=target,reason='relleno insuficiente'));continue
  assert raw[o:o+n]==source[o:o+n]
  b=raw[:o]+y.ljust(n,b'\0')+raw[o+n:];assert len(b)==len(raw) and cstr(b,o)==y
  expected[k][name]=b;changes.append(dict(resource=k+'/'+name,offset=o,original_en=key,original=decode(x),translation=target,bytes_slot=n))
# DLCs: reuse only Spanish fields already present in DLC 00, where the entire
# original Japanese record is byte-identical. Preserve each target's other fields.
layouts={'kis.dat':(148,[(0,21),(21,59)]),'magic.dat':(116,[(18,22),(40,56)]),'skill.dat':(94,[(16,21),(37,57)]),'mapinfo.dat':(96,[(12,32)]),'char.dat':(200,[(0,24)]),'ritem.dat':(92,[(4,13),(17,59)]),'name.dat':(16,[(4,12)]),'com.dat':(92,[(0,23),(23,57)])}
propagated=0
for name,(stride,slots) in layouts.items():
 src0=original['DLC_00'][name];es0=expected['DLC_00'][name];n0=s.unpack_from('<I',src0)[0];assert 8+n0*stride<=len(src0),(name,n0,len(src0))
 for i in range(n0):
  start=8+i*stride;orig_record=src0[start:start+stride]
  for rel,cap in slots:
   o=start+rel;srcfield=src0[o:o+cap];destfield=es0[o:o+cap]
   if srcfield==destfield:continue
   def valid_textfield(field):
    lead=len(field)-len(field.lstrip(b'\0'));t=field[lead:].split(b'\0')[0]
    if not t or lead>2 or any(field[lead+len(t):]):return None
    # Preserve leading magic-control pairs in source and destination.
    return lead,t
   a1,b1=valid_textfield(srcfield),valid_textfield(destfield)
   if a1 is None or b1 is None or a1[0]!=b1[0]:continue
   a2,b2=a1[1],b1[1]
   if name=='magic.dat' and rel==40 and a2.startswith(b'\x87'):
    if b2[:2]!=a2[:2]:continue
    a2,b2=a2[2:],b2[2:]
   src_text,dest_text=decode(a2),decode(b2)
   if not re.search('[\u3040-\u30ff\u3400-\u9fff]',src_text) or re.search('[\u3040-\u30ff\u3400-\u9fff\ufffd]',dest_text) or not any(x.isalpha() for x in dest_text):continue
   for k in ('DLC_01','DLC_02','DLC_03'):
    osrc=original[k][name];cur=expected[k][name]
    if osrc[start:start+stride]!=orig_record or cur[o:o+cap]!=srcfield:continue
    expected[k][name]=cur[:o]+destfield+cur[o+cap:]
    changes.append(dict(resource=k+'/'+name,offset=o,original_en='Referencia exacta DLC_00',original=src_text,translation=dest_text,bytes_slot=cap));propagated+=1
print('propagated exact Japanese source records',propagated,flush=True)

print('candidates',len(candidates),'edits',len(changes),'skipped',len(skipped),collections.Counter(x['resource'].split('/')[0] for x in changes),flush=True)
# Re-encode only LZS tokens whose source or backreference changed.
exec(Path('/tmp/rc41/implement.py').read_text().split('def patch_lzs(blob,raw,new):')[1].split('# Table slots:')[0].join(['def patch_lzs(blob,raw,new):','']))
def transform(k,blob):
 raw=lzs(blob);n=s.unpack_from('<I',raw)[0];base=16+32*n;pos=base;b=bytearray(raw)
 for i in range(n):
  end=base+s.unpack_from('<I',raw,16+32*i)[0];name=raw[20+32*i:48+32*i].split(b'\0')[0].decode('cp932');v=expected[k][name];assert len(v)==end-pos;b[pos:end]=v;pos=end
 assert pos==len(raw);out,nt=patch_lzs(blob,raw,bytes(b));assert dat(lzs(out))==expected[k];print(k,len(blob),len(out),nt,flush=True);return out
start=transform('ISO_START',read(old,ST));shutil.copyfile(old,dest);off,n,rec=iso(old)[ST];nextoff=iso(old)[SP][0]
with dest.open('r+b') as f:
 if off+max(n,len(start))>nextoff:
  f.seek(0,2);off=f.tell();assert off%2048==0;f.write(start);f.write(b'\0'*((-len(start))%2048));size=f.tell();assert size%2048==0
  f.seek(16*2048+80);f.write(s.pack('<I',size//2048)+s.pack('>I',size//2048));f.seek(rec+2);f.write(s.pack('<I',off//2048)+s.pack('>I',off//2048))
 else:
  f.seek(off);f.write(start);f.write(b'\0'*max(0,n-len(start)))
 f.seek(rec+10);f.write(s.pack('<I',len(start))+s.pack('>I',len(start)))
assert read(dest,ST)==start
for i,f in enumerate(sorted(dlcold.glob('*.EDAT'))):
 b=f.read_bytes();name,blob=next(iter(nis(b).items()));assert len(nis(b))==1 and b[2048:]==blob
 v=transform(f'DLC_{i:02}',blob);header=bytearray(b[:2048]);s.pack_into('<I',header,0x34,len(v));result=bytes(header)+v;assert nis(result)[name]==v;(dlcnew/f.name).write_bytes(result)
oldtalk,_=inventory(old,dlcold);newtalk,final=inventory(dest,dlcnew);assert oldtalk==newtalk and final==expected
for k in iso(old):
 if k!=ST and '.' in k.split('/')[-1]:assert read(old,k)==read(dest,k),k
for name,rows in [('correcciones_tablas.csv',changes),('rechazos_tablas.csv',skipped)]:
 if rows:
  with (P/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
shutil.copytree('/tmp/rc41/gui',P/'gui',dirs_exist_ok=True);patch=P/'gui/patches';m=json.loads((patch/'manifest.json').read_text());m['version']='RC041-REV2-GUI-NATIVO';m['scope']='RC041 + correcciones de tablas ISO/DLC con anclas verificadas; QA visual pendiente'
for spec in m['specs']:
 name=spec['name'];a=SRC if name=='ISO' else Path('/tmp/rc38/orig')/name;b=dest if name=='ISO' else dlcnew/name
 assert sha(a)==spec['source_sha256']
 with a.open('rb') as f,b.open('rb') as g,gzip.GzipFile(patch/spec['patch'],'wb',compresslevel=5,mtime=0) as out:
  out.write(b'LPGUI001');o=0
  while True:
   x=f.read(65536);y=g.read(65536)
   if not y:break
   x=x[:len(y)].ljust(len(y),b'\0')
   if x!=y:out.write(s.pack('<QI',o,len(y)));out.write(np.bitwise_xor(np.frombuffer(x,dtype='u1'),np.frombuffer(y,dtype='u1')).tobytes())
   o+=len(y)
  out.write(s.pack('<Q',2**64-1))
 spec.update(target_sha256=sha(b),target_size=b.stat().st_size)
(patch/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));report=dict(version='RC041-REV2',base_sha256=sha(old),changes=len(changes),propagated_exact_dlc_fields=propagated,candidates=len(candidates),skipped=len(skipped),by_package=dict(collections.Counter(x['resource'].split('/')[0] for x in changes)),all_other_tables_unchanged=True,all_TALK_unchanged=True,all_other_ISO_files_unchanged=True,outputs=m['specs'],ppsspp=False,windows_gui=False)
(P/'QA_RC041_rev2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(patch/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for f in (P/'gui').glob('*.go'):f.write_text(f.read_text().replace('RC041','RC041_REV2'))
print('DONE',report,flush=True)
