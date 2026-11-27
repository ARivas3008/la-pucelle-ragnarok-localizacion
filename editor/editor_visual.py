#!/usr/bin/env python3
"""Editor visual local (HTML sin conexión). Exporta TALK, refluye solo zonas seguras.
SCRIPTPACK editable; START y DLC de consulta. No ejecutado sobre ISO auténtica aquí.
"""
import argparse,csv,hashlib,json,os,re,shutil,struct,sys,unicodedata,webbrowser
from pathlib import Path
from editor_dialogos import (check,sha,sha_file,read_at,iso_index,dat_members,
    load_iso,variables,decode_line,wide,encode_line,CHUNK)
from formato_talk import inspect,replace
from fuentes_es import (encode_es,decode_es,CODIGOS,index_sjis,unpack_pixels,get_tile,
    missing_render_glyphs,META_COUNT)
from nis_formats import nispack,lzs_decompress
from paginacion_talk import paginate_text

def label(b):
    s=decode_line(b)
    # NFKC changes fullwidth Latin but may change non-Latin symbols;
    # only reverse the exact transformations of our encoder.
    return ''.join(' ' if c=='　' else ',' if c=='、' else '.' if c=='。'
       else chr(ord(c)-0xfee0) if 0xff01<=ord(c)<=0xff5e else c for c in s)

def blocks(raw):
    m=inspect(raw);groups=[];cur=[]
    for t in sorted(m['strings'],key=lambda z:z['offset']):
        if cur:
            prev=cur[-1];sep=raw[prev['end']:t['offset']]
            if prev.get('choice') or t.get('choice') or not prev['raw'] or not t['raw'] or prev['entry']!=t['entry'] or sep not in (b'\0\1',b'\0\2\1'):
                groups.append(cur);cur=[]
        cur.append(t)
    if cur:groups.append(cur)
    byentry={}
    for r in groups:byentry.setdefault(r[0]['entry'],[]).append(r)
    result=[]
    for run in groups:
        a=run[0]['offset']-1;b=run[-1]['end']+1;entry=run[0]['entry']
        pages=[[]];editable=True;reason=''
        try:
            for i,t in enumerate(run):
                if i and raw[run[i-1]['end']:t['offset']]==b'\0\2\1':pages.append([])
                pages[-1].append(label(t['raw']))
            if any(t.get('choice') or not t['raw'] for t in run):
                editable=False;reason='Opción o línea vacía'
            if any(variables(t['raw']) for t in run):
                editable=False;reason='Variable dinámica: requiere revisión específica'
        except (ValueError,UnicodeError):
            pages=[['[CONTROL NO INTERPRETADO]']];editable=False;reason='Codificación no interpretada'
        # Changes in number of rows/pages require a clear boundary on BOTH sides.
        others=byentry[entry];idx=next(i for i,x in enumerate(others) if x is run)
        def clear(lo,hi):
            return any(lo<=x and y<=hi and op in (2,3) for x,y,op in m['tokens'])
        reflow=editable and (idx==0 or clear(others[idx-1][-1]['end']+1,a)) and (idx==len(others)-1 or clear(b,others[idx+1][0]['offset']-1))
        if m['unknown']:reflow=False
        if any(a<m['base']+p<b for p in m['offsets']):editable=reflow=False;reason='Puntero interior'
        result.append(dict(offset=a,fin=b,entrada=entry,id_dialogo=struct.unpack_from('<I',raw,12+32*entry)[0],
            sha_antes=sha(raw[a:b]),paginas=pages,editable=editable,reflujo=reflow,motivo=reason))
    return result

def export_font(font,out):
    fnt=struct.unpack('<11616H',font['fontB.fnt']);ftd=struct.unpack('<11616H',font['fontB.ftd'])
    pix=[unpack_pixels(font[n]) for n in ('FontB0000.txp','FontB0001.txp')]
    chars=''.join(dict.fromkeys(' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?¿¡«»"\'-–—…()[]%&+*/=áéíóúÁÉÍÓÚñÑüÜ€$@#'))
    result=[]
    for c in chars:
        try:
            code=encode_es(wide(c));idx=index_sjis(code);gid=fnt[idx];metric=ftd[idx]
            bbox=None
            if gid:
                t=get_tile(pix,gid);pts=[(x,y) for y,row in enumerate(t) for x,v in enumerate(row) if v]
                if pts:bbox=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts)+1,max(y for x,y in pts)+1]
            result.append(dict(signo=c if c!=' ' else '[ESPACIO]',codigo=code.hex().upper(),bytes=len(code),pares=len(code)//2,gid=gid,ftd_hex=f'{metric:04X}',bbox=bbox,ancho_tinta_px=bbox[2]-bbox[0] if bbox else 0))
        except (ValueError,UnicodeError):result.append(dict(signo=c,codigo='NO SOPORTADO'))
    with (out/'valores_signos.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['signo','codigo','bytes','pares','gid','ftd_hex','bbox','ancho_tinta_px']);w.writeheader();w.writerows(result)
    return result

def export_iso(iso,out,dlc=None,open_browser=True):
    check(not out.exists(),'Carpeta ya existente')
    off,pack,font=load_iso(iso)
    with iso.open('rb') as f:
        idx=iso_index(f);start=dat_members(lzs_decompress(read_at(f,*idx['/PSP_GAME/USRDIR/START_JP.LZS'])))
    resources=[];warnings=[]
    def add(scope,name,raw,editable):
        if not re.fullmatch(r'talk\d+(?:_jp)?\.dat',name,re.I):return
        try:
            records=blocks(raw)
            for r in records:
                r.update(scope=scope,recurso=name)
                if not editable:r.update(editable=False,reflujo=False,motivo='Solo lectura: contenedor distinto de SCRIPTPACK')
            resources.extend(records)
        except (ValueError,UnicodeError,struct.error) as e:warnings.append(dict(recurso=scope+'/'+name,error=str(e)))
    for r in nispack(pack):add('ISO_SCRIPTPACK',r['name'],r['content'],True)
    for n,r in start.items():add('ISO_START',n,r,False)
    if dlc:
        for i in range(4):
            try:
                ed=nispack((dlc/f'DL_JP_{i:02d}.EDAT').read_bytes());check(len(ed)==1,'EDAT inesperado')
                for n,r in dat_members(lzs_decompress(ed[0]['content'])).items():add(f'DLC_{i:02d}',n,r,False)
            except (ValueError,OSError,KeyError) as e:warnings.append(dict(recurso=f'DLC_{i:02d}',error=str(e)))
    check(resources,'No hay diálogos exportables')
    out.mkdir(parents=True)
    digest=sha_file(iso)
    font_info=export_font(font,out)
    data=dict(iso_sha256=digest,pack_sha256=sha(pack),registros=resources,advertencias=warnings,font=font_info)
    # Embedded JSON must not close a script tag, even when source text contains markup.
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    template=Path(__file__).with_name('visor.html').read_text(encoding='utf8')
    (out/'EDITOR.html').write_text(template.replace('/*DATA*/null',payload),encoding='utf8')
    with (out/'DIALOGOS_FISICOS.txt').open('w',encoding='utf8') as f:
        old=None
        for r in resources:
            key=(r['scope'],r['recurso'])
            if key!=old:f.write('\n=== '+ '/'.join(key)+' ===\n\n');old=key
            f.write(f"[Entrada {r['id_dialogo']} | {r['offset']}]\n")
            f.write('\n\n'.join('\n'.join(p) for p in r['paginas'])+'\n\n')
    (out/'origen.json').write_text(json.dumps(dict(iso_sha256=digest,pack_sha256=sha(pack),registros=len(resources),advertencias=warnings),ensure_ascii=False,indent=2),encoding='utf8')
    print('Intervenciones exportadas:',len(resources),'Advertencias:',len(warnings))
    if open_browser:webbrowser.open((out/'EDITOR.html').resolve().as_uri())

def apply_iso(iso,patch,out):
    check(not out.exists() and out.resolve()!=iso.resolve(),'Salida existente o igual a origen')
    log=out.with_suffix(out.suffix+'.json');check(not log.exists(),'Informe existente')
    changes=json.loads(patch.read_text(encoding='utf8'))
    check(changes['iso_sha256']==sha_file(iso),'La ISO no coincide con la exportada')
    off,pack,font=load_iso(iso);check(changes['pack_sha256']==sha(pack),'Pack diferente')
    members=nispack(pack);names={r['name']:i for i,r in enumerate(members)}
    check(len(names)==len(members),'Miembros duplicados')
    endian='>' if struct.unpack_from('<I',pack,8)[0]==1 else '<'
    order=sorted(members,key=lambda r:r['offset']);prev=16+44*len(order);limits={}
    for i,r in enumerate(order):
        check(prev<=r['offset']<=r['offset']+r['size']<=len(pack),'Miembros solapados')
        limits[r['name']]=order[i+1]['offset'] if i+1<len(order) else len(pack)
        prev=r['offset']+r['size']
    by={}
    for c in changes['cambios']:
        check(c['scope']=='ISO_SCRIPTPACK','Recurso solo lectura')
        by.setdefault(c['recurso'],[]).append(c)
    check(by,'No hay cambios')
    newpack=bytearray(pack);reports=[]
    for name,ed in by.items():
        item=members[names[name]];raw=item['content'];meta=inspect(raw)
        allowed={r['offset']:r for r in blocks(raw)};intervals=[];seen=set()
        for c in ed:
            a=c['offset'];check(a not in seen and a in allowed,'Ancla duplicada o ausente');seen.add(a)
            r=allowed[a];check(r['editable'] and c['sha_antes']==r['sha_antes'],'Bloque no editable o cambiado')
            pages=c['paginas'];old=r['paginas']
            check(isinstance(pages,list) and 1<=len(pages)<=64,'Páginas inválidas')
            check(all(isinstance(p,list) and 1<=len(p)<=3 for p in pages),'Máximo tres líneas por cuadro')
            structure=[len(p) for p in pages]==[len(p) for p in old]
            check(structure or (r['reflujo'] and c.get('aprobar_reflujo') is True),'Cambio de distribución no autorizado')
            # Editable blocks never contain dynamic variables. Encoding still validates installed font.
            encoded=[]
            for p in pages:
                lines=[]
                for line in p:
                    check(isinstance(line,str) and line==line.strip(),'Texto con espacios exteriores')
                    lines.append(b'\1'+encode_line(line,b'',font)+b'\0')
                encoded.append(b''.join(lines))
            replacement=b'\2'.join(encoded)
            if replacement!=raw[a:r['fin']]:intervals.append((a,r['fin'],replacement))
        if not intervals:continue
        result,journal=replace(raw,intervals)
        check(len(result)<=286072,'Búfer TALK excedido')
        # All non-01/02 controls must remain byte-identical.
        def sig(b):return [(op,b[a:z]) for a,z,op in inspect(b)['tokens'] if op not in (1,2)]
        check(sig(raw)==sig(result),'Control ajeno modificado')
        lo=item['offset'];oldend=lo+len(raw);end=lo+len(result)
        check(end<=limits[name] and (end<=oldend or not any(pack[oldend:end])),'No cabe en hueco NISPACK: '+name)
        newpack[lo:max(end,oldend)]=result+b'\0'*max(0,oldend-end)
        struct.pack_into(endian+'I',newpack,16+44*names[name]+36,len(result))
        reports.append(dict(recurso=name,sha256=sha(result),ediciones=journal))
    check(reports,'Sin cambios efectivos')
    hashes={r['recurso']:r['sha256'] for r in reports}
    for a,b in zip(members,nispack(newpack)):
        check(a['name']==b['name'] and a['offset']==b['offset'] and a['unknown']==b['unknown'],'Directorio modificado')
        check(sha(b['content'])==hashes.get(a['name'],sha(a['content'])),'Miembro alterado')
    check(len(newpack)==len(pack),'Tamaño de pack distinto')
    tmp=out.with_name(out.name+'.part');check(not tmp.exists(),'Temporal existente')
    try:
        with iso.open('rb') as f,tmp.open('xb') as g:shutil.copyfileobj(f,g,CHUNK)
        with tmp.open('r+b') as f:f.seek(off);f.write(newpack)
        with iso.open('rb') as a,tmp.open('rb') as b:
            check(read_at(b,off,len(newpack))==newpack,'Relectura incorrecta')
            for lo,hi in ((0,off),(off+len(pack),iso.stat().st_size)):
                for pos in range(lo,hi,CHUNK):
                    n=min(CHUNK,hi-pos);check(read_at(a,pos,n)==read_at(b,pos,n),'Cambios fuera del pack')
        digest=sha_file(tmp);os.replace(tmp,out)
        log.write_text(json.dumps(dict(iso_sha256=digest,recursos=reports,ppsspp=False),ensure_ascii=False,indent=2),encoding='utf8')
        print('ISO creada:',out)
    finally:
        if tmp.exists():tmp.unlink()

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    e=s.add_parser('exportar');e.add_argument('iso',type=Path);e.add_argument('carpeta',type=Path);e.add_argument('--dlc',type=Path);e.add_argument('--sin-abrir',action='store_true')
    a=s.add_parser('insertar');a.add_argument('iso',type=Path);a.add_argument('cambios',type=Path);a.add_argument('salida',type=Path)
    x=p.parse_args()
    if x.cmd=='exportar':export_iso(x.iso,x.carpeta,x.dlc,not x.sin_abrir)
    else:apply_iso(x.iso,x.cambios,x.salida)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,UnicodeError,struct.error) as e:raise SystemExit('ERROR: '+str(e))
