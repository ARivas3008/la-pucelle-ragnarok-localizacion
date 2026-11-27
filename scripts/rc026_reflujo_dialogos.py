#!/usr/bin/env python3
"""Auditar cuadros sobrantes de TALK YA traducido (RC024 o posterior).
No elimina automáticamente una pausa narrativa. Un 02 interno solo se
retira con aprobación explícita del candidato y ancla SHA256 exacta.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'parcheador/app/scripts'))
from formato_talk import inspect,replace
from fuentes_es import decode_es
from paginacion_talk import paginate_words

SPACE=b'\x81\x40'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)

def text_words(data):
    # Mantener los pares originales; no decodificar y recodificar el español.
    # Las variables dinámicas quedan fuera de esta primera fase: su expansión
    # visual puede exceder el espacio aunque los dos bytes quepan.
    need(data and len(data)%2==0,'Ancho impar o cadena vacía')
    words=[];word=bytearray()
    for i in range(0,len(data),2):
        p=data[i:i+2]
        need(p[0]>=0x80,'Control/variable dinámica: revisar aparte')
        if p==SPACE:
            need(word,'Espacios estructurados: revisar aparte')
            words.append(bytes(word));word.clear()
        else:word.extend(p)
    need(word,'Espacio final: revisar aparte')
    words.append(bytes(word))
    # Validar codificación, sin cambiar un solo par.
    for w in words:decode_es(w)
    return words

def group_runs(raw,meta):
    groups=[];current=[]
    for t in sorted(meta['strings'],key=lambda t:t['offset']):
        if t.get('choice') or not t['raw']:
            if current:groups.append(current);current=[]
            continue
        if current:
            last=current[-1]
            if t['entry']!=last['entry'] or raw[last['end']:t['offset']] not in (b'\0\1',b'\0\2\1'):
                groups.append(current);current=[]
        current.append(t)
    if current:groups.append(current)
    return groups

def clear_between(meta,lo,hi):
    return any(lo<=a and b<=hi and op in (2,3) for a,b,op in meta['tokens'])

def isolated(meta,run):
    a,b=run[0],run[-1]
    same=[t for t in meta['strings'] if t['entry']==a['entry']]
    prior=[t for t in same if t['end']<a['offset']]
    after=[t for t in same if t['offset']>b['end']]
    if prior and not clear_between(meta,prior[-1]['end']+1,a['offset']-1):return False
    if after and not clear_between(meta,b['end']+1,after[0]['offset']-1):return False
    return True

def layout_stats(pages):
    return dict(cuadros=len(pages),lineas=sum(map(len,pages)),
                cuadros_una_palabra=sum(sum(len(l) for l in p)==1 for p in pages),
                cuadros_una_linea=sum(len(p)==1 for p in pages),
                lineas_una_palabra=sum(len(l)==1 for p in pages for l in p))
def display(pages):
    return [[decode_es(SPACE.join(line)) for line in p] for p in pages]

def candidates(raw):
    meta=inspect(raw);out=[];skipped=[]
    for run in group_runs(raw,meta):
        if len(run)<2:continue
        a,b=run[0]['offset']-1,run[-1]['end']+1
        try:
            need(isolated(meta,run),'Límite de cuadro no inequívoco; revisar con contexto')
            old=[[]];flat=[]
            for i,t in enumerate(run):
                if i and raw[run[i-1]['end']:t['offset']]==b'\0\2\1':old.append([])
                words=text_words(t['raw'])
                # Un corte tras guion o antes de cierre de puntuación puede
                # representar una palabra partida. No reconstruir por intuición.
                if flat:
                    last=decode_es(flat[-1]);first=decode_es(words[0])
                    need(not last.endswith(('-', '－','‐','–','—','¿','¡','（','(')) and
                         not first.startswith((',', '.', '，','。','、','？','！','?', '!',')','）',':',';')),
                         'Unión ambigua de palabras/puntuación')
                flat.extend(words);old[-1].append(words)
            pages=paginate_words(flat,[len(w)//2 for w in flat])
            stats0,stats1=layout_stats(old),layout_stats(pages)
            keys=('cuadros','lineas','cuadros_una_palabra','cuadros_una_linea','lineas_una_palabra')
            if tuple(stats1[k] for k in keys)>=tuple(stats0[k] for k in keys):continue
            new=b'\2'.join(b''.join(b'\1'+SPACE.join(line)+b'\0' for line in p) for p in pages)
            need(tuple(w for p in pages for l in p for w in l)==tuple(flat),'Contenido perdido')
            entry=run[0]['entry']
            out.append(dict(entrada=entry,id_dialogo=struct.unpack_from('<I',raw,12+32*entry)[0],
                 offset=a,fin=b,sha_antes=sha(raw[a:b]),sha_despues=sha(new),
                 antes=display(old),despues=display(pages),
                 metricas_antes=stats0,metricas_despues=stats1,aprobado=False,
                 revisar='Confirmar mismo hablante, contexto y que los 02 internos no sean pausas intencionales',
                 new_hex=new.hex()))
        except (ValueError,UnicodeError) as e:
            skipped.append(dict(offset=a,entrada=run[0]['entry'],motivo=str(e)))
    return out,skipped

def audit(raw):
    c,s=candidates(raw)
    # El hex nuevo se reconstruye al aplicar; el informe es solo revisión.
    return dict(sha256_origen=sha(raw),candidatos=[{k:v for k,v in r.items() if k!='new_hex'} for r in c],
                omitidos=s,ppsspp=False)

def control_signature(raw,meta):
    # 01 y 02 son los únicos opcodes que se permiten cambiar DENTRO de
    # los intervalos aprobados. Los selectores 14 incluyen sus propios bytes.
    return [(op,raw[a:b]) for a,b,op in meta['tokens'] if op not in (1,2)]

def apply(raw,approval):
    need(approval['sha256_origen']==sha(raw),'SHA origen distinto')
    current,_=candidates(raw)
    by={r['offset']:r for r in current};edits=[];seen=set();accepted=[]
    for r in approval['candidatos']:
        if r.get('aprobado') is not True:continue
        off=r['offset'];need(off not in seen and off in by,'Aprobación repetida o ancla inexistente')
        seen.add(off);c=by[off]
        need(all(r.get(k)==c[k] for k in ('entrada','id_dialogo','fin','sha_antes','sha_despues')),'Ancla o destino distinto')
        edits.append((off,c['fin'],bytes.fromhex(c['new_hex'])))
        accepted.append({k:v for k,v in c.items() if k!='new_hex'})
    need(edits,'No hay candidatos aprobados')
    result,journal=replace(raw,edits)
    need(len(result)<=286072,'Búfer TALK excedido')
    need(control_signature(raw,inspect(raw))==control_signature(result,inspect(result)),'Control ajeno alterado')
    return result,dict(sha256_origen=sha(raw),sha256_salida=sha(result),aplicados=accepted,
                       diario=journal,ppsspp=False)

def audit_iso(iso,dlc,out):
    from construir_parche import Image,members_from_dat
    from nis_formats import nispack,lzs_decompress
    img=Image(iso);idx={n:(o,s) for n,o,s,_ in img.records()}
    def read(name):return img.read(*idx['/PSP_GAME/USRDIR/'+name])
    resources=[]
    for r in nispack(read('SCRIPTPACK.DAT')):
        if r['name'].lower().startswith('talk') and r['name'].lower().endswith('.dat'):
            resources.append(('ISO_SCRIPTPACK',r['name'],r['content']))
    start=members_from_dat(lzs_decompress(read('START_JP.LZS')))
    for n,raw in start.items():
        if n.lower().startswith('talk') and n.lower().endswith('.dat'):resources.append(('ISO_START',n,bytes(raw)))
    if dlc:
        for i in range(4):
            items=nispack((dlc/f'DL_JP_{i:02d}.EDAT').read_bytes())
            need(len(items)==1,'EDAT no reconocido')
            for n,raw in members_from_dat(lzs_decompress(items[0]['content'])).items():
                if n.lower().startswith('talk') and n.lower().endswith('.dat'):
                    resources.append((f'DLC_{i:02d}',n,bytes(raw)))
    out.mkdir(parents=True,exist_ok=False);summary=[]
    for folder,n,raw in resources:
        need(Path(n).name==n,'Nombre de miembro inseguro')
        d=out/folder;d.mkdir(exist_ok=True)
        try:
            r=audit(raw);(d/(n+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
            (d/n).write_bytes(raw)
            summary.append(dict(recurso=folder+'/'+n,candidatos=len(r['candidatos']),
                                omitidos=len(r['omitidos']),
                                cuadros_posibles=sum(c['metricas_antes']['cuadros']-c['metricas_despues']['cuadros'] for c in r['candidatos'])))
        except (ValueError,UnicodeError) as e:summary.append(dict(recurso=folder+'/'+n,error=str(e)))
    (out/'resumen.json').write_text(json.dumps(dict(recursos=summary,aplicados=0,ppsspp=False),ensure_ascii=False,indent=2),encoding='utf8')
    print('Recursos auditados:',len(summary))

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('auditar');a.add_argument('talk',type=Path);a.add_argument('informe',type=Path)
    b=s.add_parser('aplicar');b.add_argument('talk',type=Path);b.add_argument('informe',type=Path);b.add_argument('salida',type=Path)
    c=s.add_parser('auditar-iso');c.add_argument('--iso',type=Path,required=True);c.add_argument('--dlc',type=Path);c.add_argument('--salida',type=Path,required=True)
    x=p.parse_args()
    if x.cmd=='auditar-iso':audit_iso(x.iso,x.dlc,x.salida);return
    raw=x.talk.read_bytes()
    if x.cmd=='auditar':
        with x.informe.open('x',encoding='utf8') as f:json.dump(audit(raw),f,ensure_ascii=False,indent=2)
    else:
        result,report=apply(raw,json.loads(x.informe.read_text(encoding='utf8')))
        log=x.salida.with_suffix(x.salida.suffix+'.json')
        need(not x.salida.exists() and not log.exists(),'Salida existente')
        with x.salida.open('xb') as f:f.write(result)
        with log.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
if __name__=='__main__':main()
