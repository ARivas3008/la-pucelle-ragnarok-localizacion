#!/usr/bin/env python3
"""RC026: preparar START_JP.LZS corregido sin modificar la ISO original.
Compresión portable Python, sin referencias solapadas.
No certifica renderizado en PPSSPP.
"""
import argparse, hashlib, json, struct, sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'parcheador/app/scripts'))
from fuentes_es import repair_inverted_punctuation
from nis_formats import lzs_header,lzs_decompress,nispack

def sha(b):return hashlib.sha256(b).hexdigest()

def compress(raw,original):
    h=lzs_header(original);marker=h['marker']
    # Ventana de 254 bytes: distancia codificada como 1..255 saltando marker.
    maxdist=254 if marker<255 else 254
    # Limitar memoria al historial vivo, no a las cadenas de todo el archivo.
    table={};history=deque();out=bytearray();i=0
    def remember(p):
        if p+3>len(raw):return
        key=raw[p:p+3]
        table.setdefault(key,deque()).append(p);history.append((p,key))
    def prune(p):
        while history and p-history[0][0]>maxdist:
            q,key=history.popleft();d=table[key];assert d.popleft()==q
            if not d:del table[key]
    while i<len(raw):
        prune(i);best=0;distance=0
        for q in reversed(table.get(raw[i:i+3],())):
            dist=i-q;limit=min(255,dist,len(raw)-i)
            if limit<=best:continue
            n=3
            while n<limit and raw[q+n]==raw[i+n]:n+=1
            if n>best and n<=limit:
                best=n;distance=dist
            if best>=min(255,maxdist,len(raw)-i):break
        if best>=4:
            token=distance+(distance>=marker)
            if token==marker or token>255:raise ValueError('Distancia no representable')
            out.extend((marker,token,best));step=best
        else:
            b=raw[i];out.append(b)
            if b==marker:out.append(b)
            step=1
        for p in range(i,i+step):remember(p);prune(p)
        i+=step
    result=struct.pack('<4sIIB3s',h['ext'],len(raw),len(out)+12,marker,h['reserved'])+out
    if lzs_decompress(result,allow_overlap=False)!=raw:
        raise ValueError('LZS no reversible')
    return result

def repair(raw):
    # START contiene un DAT de offsets acumulados, no NISPACK. Preservar directorio.
    count=struct.unpack_from('<I',raw)[0];base=16+count*32;pos=base;idx={}
    if not 0<count<=2000 or base>len(raw):raise ValueError('DAT inválido')
    for i in range(count):
        off=16+i*32;end=base+struct.unpack_from('<I',raw,off)[0]
        name=raw[off+4:off+32].split(b'\0',1)[0].decode('cp932')
        if name in idx or not pos<=end<=len(raw):raise ValueError('DAT inválido: '+name)
        idx[name]=(pos,end);pos=end
    if pos!=len(raw):raise ValueError('DAT incompleto')
    names=('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')
    m={n:raw[idx[n][0]:idx[n][1]] for n in names}
    journal=repair_inverted_punctuation(m)
    out=bytearray(raw)
    for n in names:
        lo,hi=idx[n]
        if len(m[n])!=hi-lo:raise ValueError('Tamaño alterado')
        out[lo:hi]=m[n]
    for n,(lo,hi) in idx.items():
        if n not in names[2:] and out[lo:hi]!=raw[lo:hi]:raise ValueError('Miembro ajeno modificado')
    if out[:base]!=raw[:base]:raise ValueError('Directorio modificado')
    return bytes(out),journal

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    a.salida.mkdir(parents=True,exist_ok=False)
    original=a.start.read_bytes();raw=lzs_decompress(original)
    candidate,journal=repair(raw)
    lzs=compress(candidate,original)
    (a.salida/'START_JP.LZS').write_bytes(lzs)
    (a.salida/'informe.json').write_text(json.dumps(dict(journal,original_sha=sha(original),candidate_sha=sha(lzs),
            original_size=len(original),candidate_size=len(lzs),raw_sha=sha(candidate),iso_integrada=False),indent=2,ensure_ascii=False))
if __name__=='__main__':main()
