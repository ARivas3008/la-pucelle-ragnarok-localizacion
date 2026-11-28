from edit import *
b=packs['ISO_START']['sys2.txp'];a,p,off,w,hh=txp(b);before=a.copy();x,y,X,Y=0,60,20,67;sub=a[y:Y,x:X];sub[:]=0
# 3x5 pixel lettering, with a one-pixel dark shadow. Avoid triangle glyph above.
font={'O':['111','101','101','101','111'],'M':['101','111','111','101','101'],'I':['1']*5,'T':['111','010','010','010','010'],'R':['110','101','110','101','101']}
word='OMITIR';g=np.zeros((5,19),np.uint8);pos=0
for ch in word:
 c=np.array([[int(v) for v in line] for line in font[ch]],np.uint8);g[:,pos:pos+c.shape[1]]=c;pos+=c.shape[1]+1
assert pos-1==19
mask=np.zeros(sub.shape,np.uint8);mask[:5,:19]=g;stroke=cv2.dilate(mask,np.ones((3,3),np.uint8))>0;sub[stroke]=2;sub[mask>0]=14
out=enc(b,a);assert out[:off]==b[:off] and len(out)==len(b);assert np.array_equal(a[:60],before[:60]) and np.array_equal(a[67:],before[67:]) and np.array_equal(a[60:67,20:],before[60:67,20:]);(A/'sys2.txp').write_bytes(out)
# add actual comparison
im=Image.open('/mnt/data/RC041_REV6_Graficos_comparacion.png').convert('RGB');sheet=Image.new('RGB',(990,710),(35,35,35));sheet.paste(im,(0,0));dr=ImageDraw.Draw(sheet)
for i,raw in enumerate((b,out)):
 v=image(raw).crop((0,49,21,68)).resize((168,152),Image.Resampling.NEAREST);xx=i*495+7;dr.text((xx,528),'Saltar escena | '+('Antes' if i==0 else 'Después'),fill='white');sheet.paste(v,(xx,548),v)
sheet.save('/mnt/data/RC041_REV6_Graficos_comparacion.png')
