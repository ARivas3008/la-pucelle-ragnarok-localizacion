"""Repartición conservadora de un diálogo en varias cajas sin mover punteros.

NO es resegmentación semántica certificada: propone/reparte palabras cuando la
traducción y el origen caben en las cajas existentes y todas las fuentes coinciden.
"""
import re
from math import inf
from fuentes_es import encode_es, FontError

class SegmentacionError(ValueError): pass

def repartir(texto,capacidades,encoder=encode_es):
    if not capacidades or any(x<1 for x in capacidades):raise SegmentacionError('capacidades inválidas')
    if any(c in texto for c in ('\n','\r','\x00','\t')):raise SegmentacionError('control de párrafo/caja: segmentación manual')
    if re.search(r'\{[^}]*\}|%[sd]|<[^>]+>',texto):raise SegmentacionError('variables o códigos de control sin parser de cajas')
    if texto!=texto.strip() or '  ' in texto:raise SegmentacionError('espacios estructurados: requieren cotejo manual')
    words=texto.split(' ')
    n=len(words);m=len(capacidades)
    if n<m:raise SegmentacionError('menos palabras que unidades físicas')
    if n>300 or m>60:raise SegmentacionError('exceso de complejidad; cotejo manual')
    # Cachea tokens en bytes sin perder tildes (gaiji de dos bytes).
    enc=[]
    for w in words:
        if not w:raise SegmentacionError('palabra vacía')
        try:enc.append(encoder(w))
        except FontError as e:raise SegmentacionError(str(e)) from e
    lengths=[len(x) for x in enc]
    pref=[0]
    for x in lengths:pref.append(pref[-1]+x)
    # El espacio puede ocupar uno o dos bytes según el estilo normal/ancho.
    try:separator_len=len(encoder(' '))
    except (FontError,UnicodeError) as e:raise SegmentacionError(str(e)) from e
    def used(i,j):return pref[j]-pref[i]+(j-i-1)*separator_len
    # Si la suma de las capacidades es insuficiente, no sirve recortar palabras.
    if used(0,n)>sum(capacidades):raise SegmentacionError('traducción supera la capacidad total de bytes')
    goal=[(sum(capacidades[:i+1])/sum(capacidades))*n for i in range(m)]
    dp={(0,0):(0,[])}
    for i,cap in enumerate(capacidades):
        nxt={}
        for (old_i,k),(score,prev) in dp.items():
            if old_i!=i:continue
            maxj=n-(m-i-1)
            for j in range(k+1,maxj+1):
                size=used(k,j)
                if size>cap:break
                seg=' '.join(words[k:j])
                punctuation_bonus=-0.3 if seg.endswith(('.','!','?','…','—',':',';')) else 0
                split_penalty=abs(j-goal[i])/(max(1,n))*3
                whitespace_waste=(cap-size)/cap
                cost=score+split_penalty+whitespace_waste*0.4+punctuation_bonus
                state=(i+1,j)
                if state not in nxt or cost<nxt[state][0]:nxt[state]=(cost,prev+[seg])
        dp=nxt
    if (m,n) not in dp:raise SegmentacionError('no hay cortes en límites de palabra que quepan en todas las cajas')
    chunks=dp[m,n][1]
    if ' '.join(chunks)!=texto:raise SegmentacionError('la reconstrucción de la cadena cambió')
    for chunk,cap in zip(chunks,capacidades):
        if len(encoder(chunk))>cap:raise SegmentacionError('longitud incorrecta')
    return chunks
