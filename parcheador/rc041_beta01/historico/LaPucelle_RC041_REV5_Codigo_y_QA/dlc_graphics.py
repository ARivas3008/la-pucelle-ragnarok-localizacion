from view import *
import hashlib
_,packs=inventory(B,D);n='sys6.txp';b=packs['DLC_00'][n];assert all(packs[f'DLC_{i:02}'][n]==b for i in range(4));a,p,off,w,h0=txp(b);before=a.copy();v,p2,_,w2,h2=txp((P/'assets'/n).read_bytes());assert (w,h0)==(w2,h2)
rects=[(6,69,58,82),(201,29,253,46),(45,141,216,170),(4,172,161,187),(4,190,161,205),(4,208,161,223),(4,226,161,242),(8,38,25,47),(8,48,25,57),(8,58,25,67),(76,38,95,47),(116,38,135,47),(0,244,17,253)]
allowed=np.zeros_like(a,dtype=bool)
for x,y,X,Y in rects:
 colors=p2[v[y:Y,x:X]].astype('int32');flat=colors.reshape(-1,4);q=p.astype('int32');idx=np.argmin(((flat[:,None,:]-q[None,:,:])**2).sum(axis=2),axis=1).astype('u1').reshape(Y-y,X-x);a[y:Y,x:X]=idx;allowed[y:Y,x:X]=True
assert np.array_equal(a[~allowed],before[~allowed]);out=enc(b,a);assert out[:off]==b[:off] and len(out)==len(b) and np.array_equal(txp(out)[0],a)
(P/'assets'/'DLC_sys6.txp').write_bytes(out);image(out).save(P/'DLC_sys6.new.png');r=json.loads((P/'graphics.json').read_text());r.append(dict(resource='DLC_00–03/sys6.txp',regions=rects,before=hashlib.sha256(b).hexdigest(),after=hashlib.sha256(out).hexdigest(),pixels=int((a!=before).sum())));(P/'graphics.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
