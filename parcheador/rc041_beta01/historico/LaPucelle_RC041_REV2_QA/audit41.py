import sys,json,csv,re
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
P=Path('/tmp/rc41qa');T=Path('/tmp/rc41/RC041.iso');D=Path('/tmp/rc41/ULJS00244')
def sha(x):return h.sha256(x).hexdigest()
def fsha(p):
 with p.open('rb') as f:return h.file_digest(f,'sha256').hexdigest()
def write(name,rows):
 if not rows:return
 with (P/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
orig,op=inventory(SRC,Path('/tmp/rc38/orig'));new,np=inventory(T,D);stats=c.Counter();res=[];unch=[];unmatched=[];over=[];jap=[];bad=[]
for k,a in orig.items():
 b=new[k];ma,mb=inspect(a),inspect(b);pairs=list(align(k,a,b,ma,mb));got={q[0]['offset'] for r,q in pairs};counts=c.Counter(original=len(ma['runs']),actual=len(mb['runs']),aligned=len(pairs),lines=sum(map(len,mb['runs'])),entries=mb['n'],unmatched=len(mb['runs'])-len(got))
 for r,q in pairs:
  src=' '.join(lines(r));es=' '.join(lines(q));row=dict(resource=k,offset=q[0]['offset'],entry=q[0]['entry'],original=src,actual=es)
  if canon(src)==canon(es) and any(x.isalpha() for x in src):unch.append(row);counts['unchanged_alpha']+=1
  if re.search('[\u3040-\u30ff\u3400-\u9fff]',es):jap.append(row);counts['japanese_candidates']+=1
 for q in mb['runs']:
  if q[0]['offset'] not in got:unmatched.append(dict(resource=k,offset=q[0]['offset'],entry=q[0]['entry'],actual=' '.join(lines(q))))
  for t in q:
   if len(t['raw'])>56:over.append(dict(resource=k,offset=t['offset'],entry=t['entry'],bytes=len(t['raw']),actual=decode(t['raw'])))
   if '�' in decode(t['raw']):bad.append(dict(resource=k,offset=t['offset'],entry=t['entry'],actual=decode(t['raw'])))
 stats.update(counts);res.append(dict(resource=k,**{x:counts[x] for x in ['original','actual','aligned','lines','entries','unmatched','unchanged_alpha','japanese_candidates']}))
write('talk_recursos.csv',res);write('talk_identicos.csv',unch);write('talk_sin_alinear.csv',unmatched);write('talk_japones.csv',jap);write('talk_lineas_largas.csv',over);write('talk_codificacion.csv',bad)
print('TALK',stats,'long',len(over),'bad',len(bad),flush=True)
graphics=[];hashes={}
for n in ['ANMPACK.DAT','BGPACK.DAT','MAPPACK.DAT']:
 k='/PSP_GAME/USRDIR/'+n;a=nis(read(SRC,k));b=nis(read(T,k));print(n,len(a),len(b),flush=True);assert a.keys()==b.keys()
 for name,v in b.items():graphics.append(dict(resource=n+'/'+name,original_sha256=sha(a[name]),rc041_sha256=sha(v),changed=a[name]!=v,original_bytes=len(a[name]),current_bytes=len(v)));hashes[name]=sha(v)
for k,m in np.items():
 for n,v in m.items():
  if n.endswith(('.fnt','.txp','.tm2','.png','.anm')) or 'font' in n.lower():graphics.append(dict(resource=k+'/'+n,original_sha256=sha(op[k][n]),rc041_sha256=sha(v),changed=op[k][n]!=v,original_bytes=len(op[k][n]),current_bytes=len(v)))
write('graficos_inventario.csv',graphics);known=json.load(open('/mnt/data/QA_RC033_GUI.json'))['carteles'];checks=[dict(resource=x['member'],expected=x['sha256'],actual=hashes.get(x['member']),match=x['sha256']==hashes.get(x['member'])) for x in known];v=fsha(Path('/mnt/data/wmap_03_Mapa_pulido.txp'));checks.append(dict(resource='wmap_03.txp',expected=v,actual=hashes.get('wmap_03.txp'),match=v==hashes.get('wmap_03.txp')));write('graficos_aprobados.csv',checks);print('graphics',len(graphics),'changed',sum(x['changed'] for x in graphics),'checks',sum(x['match'] for x in checks),len(checks),flush=True)
m=json.load(open('/tmp/rc41/gui/patches/manifest.json'));checks2=[]
for x in m['specs']:
 p=T if x['name']=='ISO' else D/x['name'];a=SRC if x['name']=='ISO' else Path('/tmp/rc38/orig')/x['name'];checks2.append(dict(name=x['name'],original_match=fsha(a)==x['source_sha256'],target_match=fsha(p)==x['target_sha256'],size_match=p.stat().st_size==x['target_size']))
print('files',checks2,flush=True)
(P/'summary.json').write_text(json.dumps(dict(talk=dict(stats),long_lines=len(over),decode_candidates=len(bad),graphics_total=len(graphics),graphics_changed=sum(x['changed'] for x in graphics),known_graphic_checks=checks,hashes=checks2),ensure_ascii=False,indent=2))
