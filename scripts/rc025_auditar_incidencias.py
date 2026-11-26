#!/usr/bin/env python3
"""RC025: auditoría reproducible de los cinco fallos visuales de RC024.
No modifica ISO ni EDAT. --reparar-tutorial produce un miembro local solo
si la identificación por entrada y tramo es inequívoca y conserva controles.
Los resultados son evidencia estática, no una captura de PPSSPP.
"""
import argparse, csv, hashlib, json, re, struct, sys, unicodedata
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
for p in sorted((ROOT/'parcheador/investigacion').glob('v*')):
    sys.path.insert(0, str(p))
sys.path.insert(0, str(ROOT/'parcheador/app/scripts'))
from construir_parche import Image, members_from_dat, sha_file
from nis_formats import nispack, lzs_decompress
from formato_talk import inspect, replace
from recompilar_talk import runs, fit_slots, canon
from fuentes_es import decode_es, CODIGOS, index_sjis, unpack_pixels, get_tile, missing_render_glyphs

ORIGINAL='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
RC024='fc2c8b08f29ef8a0eb4b09b89010496fb382ef96a0976b87b75e75623646aece'
SOURCE='When you purify a dark portal, you damage enemies standing on the energy flowing from it.'
TARGET='Al purificar un portal oscuro, dañas a los enemigos que estén sobre la corriente de energía que sale de él.'
MARKERS=('When you purify a dark','悪魔の胃袋','MAP CLEAR!!','MAP CLEAR','STAGE CLEAR','GAME OVER','PLAYER TURN','ENEMY TURN','Panza del Diablo')
FONT_MEMBERS=('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')
def sha(b): return hashlib.sha256(b).hexdigest()
def read_iso(path):
    iso=Image(path)
    idx={n:(o,s) for n,o,s,_ in iso.records()}
    def get(name): return iso.read(*idx['/PSP_GAME/USRDIR/'+name])
    def pack(name): return {it['name']:it['content'] for it in nispack(get(name))}
    return iso,idx,get,pack
def start(raw): return members_from_dat(lzs_decompress(raw))
def decoded(b):
    # Separar variables de dos bytes; no tratarlas como letras.
    try: return unicodedata.normalize('NFKC',decode_es(b))
    except (UnicodeError,ValueError): return None
def entries(raw):
    meta=inspect(raw)
    by={}
    for t in meta['strings']:
        s=decoded(t['raw'])
        by.setdefault(t['entry'],[]).append((t,s))
    return meta,by
def eid(raw,n):
    return struct.unpack_from('<I',raw,12+32*n)[0]
def row_signature(raw,meta,n):
    # ID y condiciones, no offset.
    return raw[12+32*n:40+32*n]
def audit_talk(name,a,b):
    ma,ea=entries(a); mb,eb=entries(b)
    if ma['n']!=mb['n'] or any(row_signature(a,ma,i)!=row_signature(b,mb,i) for i in range(ma['n'])):
        raise ValueError('IDs/condiciones distintos '+name)
    result=[]
    for i,items in eb.items():
        original=Counter(s for _,s in ea.get(i,[]) if s and re.search(r'[A-Za-z\u3040-\u30ff\u3400-\u9fff]',s))
        for t,s in items:
            if not s: continue
            if original[s]:
                original[s]-=1
                result.append(dict(resource=name,entry=i,id=eid(b,i),offset=t['offset'],choice=bool(t.get('choice')),text=s,kind='COINCIDENCIA_ORIGINAL_REVISAR'))
    return result
def find_bytes(name,raw):
    for marker in MARKERS:
        variants=set()
        for enc in ('cp932','utf-8','utf-16le'):
            try: variants.add(marker.encode(enc))
            except UnicodeError: pass
        if marker.isascii():
            wide=''.join('\u3000' if c==' ' else chr(ord(c)+0xfee0) if '!'<=c<='~' else c for c in marker)
            variants.add(wide.encode('cp932'))
        for v in variants:
            pos=0
            while True:
                off=raw.find(v,pos)
                if off<0:break
                yield dict(resource=name,offset=off,marker=marker,bytes=v.hex())
                pos=off+len(v)
def font_audit(name,members):
    if not all(n in members for n in FONT_MEMBERS):
        raise ValueError('Fuente incompleta '+name)
    fnt=struct.unpack('<11616H',members['fontB.fnt'])
    ftd=struct.unpack('<11616H',members['fontB.ftd'])
    pix=[unpack_pixels(members[n]) for n in FONT_MEMBERS[2:]]
    def tile(code):
        ix=index_sjis(code); gid=fnt[ix]
        if not gid: return dict(gid=0,metric=ftd[ix],mask=[])
        t=get_tile(pix,gid)
        return dict(gid=gid,metric=ftd[ix],mask=[''.join('#' if v else '.' for v in row) for row in t])
    result={}
    for char in '¿¡áéíóúÁÉÍÓÚñÑüÜ«»':
        result[char]=tile(CODIGOS[char])
    for char in '？?！!':
        result[char]=tile(char.encode('cp932'))
    return dict(resource=name,glyphs=result)
def chapter_audit(original,candidate):
    result=[]
    for n in list(range(1,13))+list(range(15,19)):
        name=f'at{n:02d}.txp'
        a,b=original[name],candidate[name]
        # Comparar cabeceras y los últimos bytes sin asumir que equivalen
        # a la última fila: el swizzle de PSP requiere decodificación.
        result.append(dict(resource=name,original_sha=sha(a),candidate_sha=sha(b),
            original_size=len(a),candidate_size=len(b),header_equal=a[:16]==b[:16],
            last_256_bytes_different=sum(x!=y for x,y in zip(a[-256:],b[-256:])),
            state='REQUIERE_DECODIFICACION_TEX Y COMPARACION_VISUAL'))
    return result
def repair_tutorial(original,candidate,font):
    # Anclar el tramo entero en la fuente, no un substring arbitrario.
    mo=inspect(original); mc=inspect(candidate)
    source_runs=[r for r in runs(original,mo)
                 if canon(' '.join(decoded(t['raw']) or '' for t in r))==canon(SOURCE)]
    if len(source_runs)!=1:raise ValueError('Tramo original no inequívoco')
    source=source_runs[0]; i=source[0]['entry']
    if mo['n']!=mc['n'] or row_signature(original,mo,i)!=row_signature(candidate,mc,i):
        raise ValueError('Entrada/condiciones distintas')
    targets=[r for r in runs(candidate,mc) if r[0]['entry']==i and
             any(canon(decoded(t['raw']) or '').startswith(canon('When you purify a dark')) for t in r)]
    if len(targets)!=1:raise ValueError('Tramo candidato no inequívoco')
    target=targets[0]
    # Se exige igual número de slots que el original y que el tramo esté
    # delimitado por idénticos controles internos. Cualquier diferencia se
    # deriva a revisión manual; no se suprime ni se duplica una caja.
    if len(source)!=len(target):raise ValueError('Slots distintos; requiere revisión manual')
    def gap(raw,rr):return [raw[x['end']:y['offset']] for x,y in zip(rr,rr[1:])]
    if gap(original,source)!=gap(candidate,target):raise ValueError('Controles internos distintos')
    # Probar que el candidato no añadió texto ajeno al comienzo/final del
    # segmento: aceptar solo líneas ya presentes en la fuente o fragmentos
    # de la traducción canónica; las otras adaptaciones requieren revisión.
    orig_lines={canon(decoded(t['raw']) or '') for t in source}
    translated=canon(TARGET)
    for t in target:
        v=canon(decoded(t['raw']) or '')
        if not v or (v not in orig_lines and v not in translated):
            raise ValueError('Fragmento candidato no reconocido; revisar manualmente')
    lines,enc,_=fit_slots(TARGET,target)
    if missing_render_glyphs(TARGET,font):raise ValueError('Glifos ausentes')
    edits=[(t['offset']-1,t['end']+1,b'\1'+enc(line)+b'\0') for t,line in zip(target,lines)]
    out,journal=replace(candidate,edits)
    if len(out)>286072:raise ValueError('Búfer TALK excedido')
    return out,dict(entry=i,lines=lines,journal=journal,sha256=sha(out))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--rc024',type=Path,required=True)
    p.add_argument('--dlc-original',type=Path)
    p.add_argument('--dlc-rc024',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--reparar-tutorial',action='store_true')
    a=p.parse_args()
    if sha_file(a.original)!=ORIGINAL or sha_file(a.rc024)!=RC024:
        raise ValueError('SHA-256 original o RC024 no coincide')
    if bool(a.dlc_original)!=bool(a.dlc_rc024):raise ValueError('Se requieren ambas carpetas DLC')
    a.out.mkdir(parents=True,exist_ok=False)
    oi,ox,og,op=read_iso(a.original); ci,cx,cg,cp=read_iso(a.rc024)
    os,cs=start(og('START_JP.LZS')),start(cg('START_JP.LZS'))
    ot,ct=op('SCRIPTPACK.DAT'),cp('SCRIPTPACK.DAT')
    residues=[]; hits=[]; fonts=[]; resources=[]
    def audit_members(prefix,old,new):
        for name in sorted(new):
            r=prefix+'/'+name
            if name.lower().startswith('talk') and name.lower().endswith('.dat'):
                residues.extend(audit_talk(r,old[name],new[name]))
                resources.append(r)
            hits.extend(find_bytes(r,new[name]))
    audit_members('ISO_START',os,cs)
    audit_members('SCRIPTPACK.DAT',ot,ct)
    fonts.append(font_audit('ISO_START',cs))
    if a.dlc_original:
        for n in range(4):
            file=f'DL_JP_{n:02d}.EDAT'
            old=nispack((a.dlc_original/file).read_bytes())
            new=nispack((a.dlc_rc024/file).read_bytes())
            if len(old)!=1 or len(new)!=1:raise ValueError('EDAT inesperado')
            om,nm=start(old[0]['content']),start(new[0]['content'])
            audit_members(f'DLC_{n:02d}',om,nm)
            fonts.append(font_audit(f'DLC_{n:02d}',nm))
    for n in ('BGPACK.DAT','ANMPACK.DAT','MAPPACK.DAT'):
        for name,raw in cp(n).items():
            hits.extend(find_bytes(n+'/'+name,raw))
    eb='/PSP_GAME/SYSDIR/EBOOT.BIN'
    hits.extend(find_bytes(eb,ci.read(*cx[eb])))
    chapter=chapter_audit(op('BGPACK.DAT'),cp('BGPACK.DAT'))
    for filename,data,fields in [
        ('coincidencias_originales.csv',residues,['resource','entry','id','offset','choice','text','kind']),
        ('anclas_busqueda.csv',hits,['resource','offset','marker','bytes'])]:
        with (a.out/filename).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    report=dict(iso_sha=RC024,resources_talk=resources,coincidencias_originales=len(residues),
        coincidencias_por_recurso=dict(Counter(x['resource'] for x in residues)),
        anclas=len(hits),fonts=fonts,chapters=chapter,ppsspp=False,
        warning='Coincidencias candidatas, no errores confirmados; no incluye OCR de gráficos ni datos LZS anidados.')
    if a.reparar_tutorial:
        try:
            member,journal=repair_tutorial(ot['talk01_jp.dat'],ct['talk01_jp.dat'],cs)
            (a.out/'talk01_jp.dat').write_bytes(member);report['tutorial']=journal
        except (ValueError,KeyError) as e:report['tutorial']={'estado':'RECHAZADO','motivo':str(e)}
    (a.out/'informe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('fonts','chapters','tutorial')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
