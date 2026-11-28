from view import *
from PIL import ImageFont,ImageFilter
import cv2,collections,hashlib
SER='/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf'; IT='/usr/share/fonts/truetype/noto/NotoSerif-BoldItalic.ttf'; SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; SB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
T={1:'Aprender el oficio',2:'La promesa de un niño',3:'Prier y Alouette',4:'Un problema gigantesco',5:'Un asunto peliagudo',6:'El viaje',7:'Un baile en el cielo',8:'Hacia una tierra inexplorada',9:'Recuerdos de Fátima',10:'El príncipe de las tinieblas',11:'La Doncella de la Luz',12:'Nace una leyenda',15:'Nace una Señora Demonio',16:'Señora Demonio',17:'La aparición de la desesperación',18:'Hermana de las tinieblas'}

def glyph(t,w,h,size,font=SER):
 for n in range(size,3,-1):
  f=ImageFont.truetype(font,n*4);bb=f.getbbox(t);im=Image.new('L',(bb[2]-bb[0]+8,bb[3]-bb[1]+8));ImageDraw.Draw(im).text((4-bb[0],4-bb[1]),t,font=f,fill=255);im=im.crop(im.getbbox());im=im.resize((max(1,round(im.width/4)),max(1,round(im.height/4))),Image.Resampling.LANCZOS)
  if im.width<=w and im.height<=h:return np.array(im)
 raise ValueError(t)
def quant(rgb,pal):
 # compare RGB only for opaque chapters; output exact original indexed palette
 flat=rgb.reshape(-1,3).astype('int32');p=pal[:,:3].astype('int32');out=[]
 for i in range(0,len(flat),2048):out.extend(np.argmin(((flat[i:i+2048,None]-p[None,:])**2).sum(axis=2),axis=1))
 return np.array(out,dtype='u1').reshape(rgb.shape[:2])

def chapter(b,i):
 a,p,off,w,h=txp(b);old=a.copy();rgb=p[a][:,:,:3];gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);mask=np.zeros_like(gray)
 # dark ink contrasts sharply against the gold or crimson background. Restrict to the two original text bands.
 for x,y,X,Y in [(166,40,315,71),(67,79,414,109)]:
  g=gray[y:Y,x:X];closed=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));contrast=closed.astype(int)-g.astype(int)
  thresh=23 if i<15 else 22; m=((contrast>thresh)&(g<(140 if i<15 else 104))).astype('u1')*255
  # include antialias edges while keeping the rest of the design
  m=cv2.dilate(m,np.ones((3,3),np.uint8));mask[y:Y,x:X]=m
 restored=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA);a[mask>0]=quant(restored,p)[mask>0]
 for t,cy,ww,hh,fs in [(f'Capítulo {i if i<15 else i-14}',53,166,28,27),(T[i],94,350,29,27)]:
  g=glyph(t,ww,hh,fs);x=(w-g.shape[1])//2;y=cy-g.shape[0]//2;alpha=g.astype(float)/255;region=p[a[y:y+g.shape[0],x:x+g.shape[1]]][:,:,:3].astype(float);ink=np.array([101,83,50] if i<15 else [50,19,12]);q=quant(np.round(region*(1-alpha[:,:,None])+ink*alpha[:,:,None]).astype('u1'),p);sub=a[y:y+g.shape[0],x:x+g.shape[1]];sub[g>5]=q[g>5]
 out=enc(b,a);assert len(out)==len(b) and out[:off]==b[:off] and np.array_equal(txp(out)[0],a);assert np.array_equal(a[:39],old[:39]) and np.array_equal(a[110:],old[110:]);return out

def ui(b,name):
 a,p,off,w,h=txp(b);before=a.copy();bounds=[]
 def mark(rect,t,kind,fs,font):
  x,y,X,Y=rect;rw,rh=X-x,Y-y;old=a[y:Y,x:X].copy();g=glyph(t,rw-2,rh-2,fs,font); xx=1;yy=(rh-g.shape[0])//2;sub=a[y:Y,x:X]
  if kind=='white':
   sub[:]=0;alpha=p[:,3].astype(int);vals=np.argmin(abs(g[:,:,None].astype(int)-alpha[None,None,:]),axis=-1).astype('u1');sub[yy:yy+g.shape[0],xx:xx+g.shape[1]]=vals
  elif kind=='paper':
   # replace dark ink with background sampled from same row, retain all other texture pixels
   for r in range(rh):
    m=sub[r]==46;choices=sub[r][~m];bg=collections.Counter(choices).most_common(1)[0][0] if len(choices) else 19;sub[r,m]=bg
   region=sub[yy:yy+g.shape[0],xx:xx+g.shape[1]];region[g>=100]=46
  elif kind=='flow':
   sub[:]=207;canvas=np.zeros((rh,rw),dtype='u1');canvas[yy:yy+g.shape[0],xx:xx+g.shape[1]]=g;strong=canvas>=100;stroke=cv2.dilate(strong.astype('u1'),np.ones((3,3),np.uint8))>0;sub[stroke]=210;sub[strong]=32
  elif kind=='bonus':
   sub[:]=0;canvas=np.zeros((rh,rw),dtype='u1');canvas[yy:yy+g.shape[0],xx:xx+g.shape[1]]=g;strong=canvas>=100;stroke=cv2.dilate(strong.astype('u1'),np.ones((3,3),np.uint8))>0;sub[stroke]=6;sub[strong]=15
  elif kind in ('stats','stats_transparent'):
   # Existing background is nearly uniform; clear only the ink rectangle.
   sub[:]=19 if kind=='stats' else 4;canvas=np.zeros((rh,rw),dtype='u1');canvas[yy:yy+g.shape[0],xx:xx+g.shape[1]]=g;strong=canvas>=100;stroke=cv2.dilate(strong.astype('u1'),np.ones((3,3),np.uint8))>0;sub[stroke]=59;sub[strong]=62
  elif kind=='stat_item':
   # Keep all original plaque borders, recolor only the yellow foreground.
   sub[sub==12]=1;sub[sub==8]=1;region=sub[yy:yy+g.shape[0],xx:xx+g.shape[1]];region[g>=100]=12
  else:raise ValueError(kind)
  bounds.append(dict(rect=rect,text=t,pixels=int((old!=sub).sum())))
 if name=='sys3.txp':
  for rect,t,fs in [((0,60,209,89),'FIN DE LA PARTIDA',33),((0,151,77,179),'VICTORIA',30),((78,151,192,179),'EMPATE',30),((0,181,94,209),'DERROTA',30),((95,181,250,209),'¡COMBATE!',30),((0,216,48,240),'turno',23)]:mark(rect,t,'white',fs,IT)
 if name=='sys6.txp':
  for rect,t in [((8,69,54,81),'Elemento'),((202,32,252,45),'Dirección'),((6,173,161,186),'Muestra interés'),((6,191,161,204),'Considera convertirse'),((6,209,161,222),'Probable conversión'),((6,227,161,241),'Se convertirá seguro')]:mark(rect,t,'paper',12,SANS)
  for rect,t in [((48,142,110,154),'Alcance:'),((118,142,139,154),'Cas.'),((79,157,158,169),'Turnos restantes'),((165,157,195,169),'Flujo')]:mark(rect,t,'flow',11,SB)
  for rect,t in [((8,38,25,47),'Nv'),((8,48,25,57),'PV'),((8,58,25,67),'PE'),((76,38,95,47),'Mov'),((116,38,135,47),'Sal')]:mark(rect,t,'stats',11,SB)
  mark((0,244,17,253),'PV','stats_transparent',11,SB)
 if name=='sys5.txp':
  for rect,t in [((0,60,90,79),'BONO+'),((0,83,44,104),'¡Golpe!')]:mark(rect,t,'bonus',22,IT)
 if name=='item.txp':
  for rect,t in [((1,100,26,108),'PV'),((33,100,58,108),'PE'),((65,100,95,108),'ATQ'),((33,116,63,124),'VEL'),((65,116,95,124),'PRE')]:mark(rect,t,'stat_item',11,SB)
 allowed=np.zeros_like(a,dtype=bool)
 for q in bounds:
  x,y,X,Y=q['rect'];allowed[y:Y,x:X]=True
 assert np.array_equal(a[~allowed],before[~allowed]);out=enc(b,a);assert out[:off]==b[:off] and len(out)==len(b) and np.array_equal(txp(out)[0],a);return out,bounds
if __name__=='__main__':
 bg=nis(read(B,'/PSP_GAME/USRDIR/BGPACK.DAT'));_,packs=inventory(B,D);assets=P/'assets';assets.mkdir(exist_ok=True);r=[]
 ims=[]
 for i,t in T.items():
  n=f'at{i:02}.txp';old=bg[n];new=chapter(old,i);(assets/n).write_bytes(new);r.append(dict(resource='BGPACK.DAT/'+n,title=t,pixels=int((txp(old)[0]!=txp(new)[0]).sum()),before=h.sha256(old).hexdigest(),after=h.sha256(new).hexdigest()));ims.append((n,image(old),image(new)))
 sheet=Image.new('RGB',(976,16*194),(35,35,35));d=ImageDraw.Draw(sheet)
 for i,(n,o,v) in enumerate(ims):
  y=i*194;d.text((8,y+3),n+' original',fill='white');d.text((496,y+3),n+' español',fill='white');sheet.paste(o,(4,y+20),o);sheet.paste(v,(492,y+20),v)
 sheet.save(P/'comparacion_titulos.png')
 for n in ['sys3.txp','sys5.txp','sys6.txp','item.txp']:
  old=packs['ISO_START'][n];new,rr=ui(old,n);(assets/n).write_bytes(new);r.append(dict(resource='ISO_START/'+n,regions=rr,before=h.sha256(old).hexdigest(),after=h.sha256(new).hexdigest()));image(new).save(P/(n+'.new.png'))
 (P/'graphics.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('assets',len(r),flush=True)
