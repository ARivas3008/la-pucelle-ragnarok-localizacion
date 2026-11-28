import sys,csv,json,hashlib,collections
from pathlib import Path
sys.path.insert(0,'/tmp/rc38');from audit import *
B=Path('/tmp/rc41rev6/RC041_rev6.iso');D=Path('/tmp/rc41rev6/ULJS00244');P=Path('/mnt/data');sha=lambda b: h.sha256(b).hexdigest()
a=nis(read(B,'/PSP_GAME/USRDIR/ANMPACK.DAT')); bg=nis(read(B,'/PSP_GAME/USRDIR/BGPACK.DAT'))
for r in csv.DictReader(open('/tmp/rc41qa/graficos_aprobados_verificados.csv',encoding='utf-8-sig')):
 d=(bg if r['resource'].endswith('.txp') else a)[r['resource']]; assert sha(d[int(r['offset']):int(r['offset'])+int(r['size'])])==r['expected_sha256'],r
print('Intro, 19 signs, Map exact',flush=True)
eboot=read(B,'/PSP_GAME/SYSDIR/EBOOT.BIN');assert sha(eboot)==json.load(open(P/'QA_RC040.json'))['eboot_after'];print('87 menu changes exact EBOOT',flush=True)
talk,packs=inventory(B,D);prev,pp=inventory(Path('/tmp/rc38/RC038.iso'),Path('/tmp/rc38/replay38/JUEGO_PARA_PPSSPP_RC038/ULJS00244'));changes=[];residual=[]
for k,a in prev.items():
 b=talk[k];ma,mb=inspect(a),inspect(b);assert len(ma['runs'])==len(mb['runs']);n=0
 for r,q in align(k,a,b,ma,mb):
  n+=1
  if lines(r)!=lines(q): changes.append([k,r[0]['entry'],lines(r),lines(q)])
  t=' '.join(lines(q));
  if re.search('Re[- ]?Action|When you purify|Now Loading|Game Over|Map Clear',t,re.I):residual.append([k,q[0]['entry'],t])
 print(k,n,len(mb['runs']),flush=True)
print('changed vs RC038',len(changes),'residual',len(residual));print(residual[:40]);Path('/tmp/lp_reintegracion/changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2));Path('/tmp/lp_reintegracion/residual.json').write_text(json.dumps(residual,ensure_ascii=False,indent=2))
for k,m in packs.items():print(k,[(x,sha(m[x])==sha(pp[k][x])) for x in m if 'fontb' in x.lower()])
