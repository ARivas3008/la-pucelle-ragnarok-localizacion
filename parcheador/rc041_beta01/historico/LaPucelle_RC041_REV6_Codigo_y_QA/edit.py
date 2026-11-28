import sys, json, hashlib, collections
from pathlib import Path
sys.path.insert(0,'/tmp/rc41rev5');from graphics import *
P=Path('/tmp/rc41rev6'); B=Path('/tmp/rc41rev5/RC041_rev5.iso'); D=Path('/tmp/rc41rev5/ULJS00244');A=P/'assets'; A.mkdir(exist_ok=True)
_,packs=inventory(B,D);bg=nis(read(B,'/PSP_GAME/USRDIR/BGPACK.DAT'))
# Original split label: two strips x=38..95 and x=2..59; joined in game. Preserve surrounding frame.
b=packs['ISO_START']['sys7.txp'];a,p,off,w,hh=txp(b);old=a.copy();regions=[(38,6,96,25),(2,38,60,57)]
strips=[a[y:Y,x:X].copy() for x,y,X,Y in regions];joined=np.concatenate(strips,axis=1);rgb=p[joined][:,:,:3];mask=np.isin(joined,[2,4,14,15]).astype('u1')*255
# Limit to inscription zone; fill ink by interpolation from gold plate, preserving non-ink pixels.
mask=cv2.dilate(mask,np.ones((3,3),np.uint8));rest=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA);q=quant(rest,p);joined[mask>0]=q[mask>0]
g=glyph('¡Reacción!',112,16,21,IT);canvas=np.zeros(joined.shape,dtype='u1');y=(canvas.shape[0]-g.shape[0])//2;x=(canvas.shape[1]-g.shape[1])//2;canvas[y:y+g.shape[0],x:x+g.shape[1]]=g
strong=canvas>=90;stroke=cv2.dilate(strong.astype('u1'),np.ones((3,3),np.uint8))>0;joined[stroke]=2;joined[strong]=15
for i,(x,y,X,Y) in enumerate(regions):a[y:Y,x:X]=joined[:,i*58:(i+1)*58]
new=enc(b,a);assert new[:off]==b[:off] and len(new)==len(b);assert np.array_equal(txp(new)[0],a);allowed=np.zeros_like(a,dtype=bool)
for x,y,X,Y in regions:allowed[y:Y,x:X]=True
assert np.array_equal(a[~allowed],old[~allowed]);(A/'sys7.txp').write_bytes(new)
# Chapter 2 follows the native Japanese chapter ending, not the different English localization.
orig=nis(read(SRC,'/PSP_GAME/USRDIR/BGPACK.DAT'))['at16.txp'];T[16]='Fragmentos del corazón';v=chapter(orig,16);(A/'at16.txp').write_bytes(v)
# compare actual atlases and joined inscription
sheet=Image.new('RGB',(990,510),(35,35,35));dr=ImageDraw.Draw(sheet)
for j,(label,q1,q2) in enumerate([('Re-Action!! / ¡Reacción!',b,new),('Capítulo adicional 2',bg['at16.txp'],v)]):
 for i,x in enumerate((q1,q2)):
  im=image(x);im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST) if j==0 else im;xx=i*495+7;yy=20+j*270;dr.text((xx,yy-16),label+' | '+('Antes' if i==0 else 'Después'),fill='white');sheet.paste(im,(xx,yy),im)
sheet.save('/mnt/data/RC041_REV6_Graficos_comparacion.png')
print('edited',int((old!=a).sum()),'pixels; title',int((txp(bg['at16.txp'])[0]!=txp(v)[0]).sum()))
# catalogue all stand-alone TXP in BG and START packs, contact sheets for visual checking
items={f'BG/{n}':b for n,b in bg.items() if n.lower().endswith('.txp')};items.update({k+'/'+n:b for k,m in packs.items() for n,b in m.items() if n.lower().endswith('.txp') and 'font' not in n.lower()});seen={};records=[]
for n,b in items.items():
 digest=hashlib.sha256(b).hexdigest();records.append(dict(resource=n,sha256=digest,size=len(b),duplicate_of=seen.get(digest,'')));seen.setdefault(digest,n)
unique=[(n,items[n]) for n in seen.values()];print('TXP',len(items),'unique',len(unique));(P/'texture_inventory.json').write_text(json.dumps(records,indent=2))
for start in range(0,len(unique),36):
 sheet=Image.new('RGB',(1200,6*170),(45,45,48));dr=ImageDraw.Draw(sheet)
 for i,(n,b) in enumerate(unique[start:start+36]):
  x=i%6*200;y=i//6*170;dr.text((x+2,y+2),n,fill='white')
  try:im=image(b);im.thumbnail((195,148));sheet.paste(im,(x+2,y+18),im)
  except Exception as e:dr.text((x+2,y+30),str(e)[:24],fill='orange')
 sheet.save(P/f'contact_{start}.png')
