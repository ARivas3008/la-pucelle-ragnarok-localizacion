#!/usr/bin/env python3
"""Editor manual conservador: ISO PSP > SCRIPTPACK.DAT > talkXX_jp.dat.
Solo dialogos normales. Conserva entradas, controles, variables y sectores.
Python 3.10+; sin paquetes externos. No modificar ISO original.
"""
import argparse,csv,hashlib,json,os,re,shutil,struct,sys,unicodedata
from pathlib import Path
from formato_talk import inspect,replace
from fuentes_es import encode_es,decode_es,missing_render_glyphs
from nis_formats import nispack,lzs_decompress

CHUNK=4*1024*1024
COLS=['recurso','entrada','id_dialogo','offset','tipo','original_hex','texto_actual','nuevo_texto']
def check(c,m):
    if not c:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(CHUNK),b''):h.update(b)
    return h.hexdigest()
def read_at(f,off,n):
    f.seek(off);b=f.read(n);check(len(b)==n,'Lectura truncada');return b
def iso_index(f):
    p=read_at(f,16*2048,2048)
    check(p[:7]==b'\x01CD001\x01','No es ISO9660 PSP sin comprimir')
    root=p[156:190]
    def info(r):
        check(len(r)>=34 and 33+r[32]<=len(r),'Registro ISO truncado')
        o,n=struct.unpack_from('<I',r,2)[0]*2048,struct.unpack_from('<I',r,10)[0]
        check(o==struct.unpack_from('>I',r,6)[0]*2048 and n==struct.unpack_from('>I',r,14)[0],'ISO endian incoherente')
        return o,n
    index={}
    def visit(r,prefix,ancestors):
        o,n=info(r);check(o not in ancestors,'Ciclo ISO')
        check(n<=16*1024*1024,'Directorio demasiado grande')
        d=read_at(f,o,n);i=0
        while i<n:
            k=d[i]
            if not k:i=(i//2048+1)*2048;continue
            check(i+k<=n,'Registro ISO truncado')
            row=d[i:i+k];i+=k
            a,b=info(row);name=row[33:33+row[32]]
            if name in (b'\0',b'\1'):continue
            name=name.decode('ascii').split(';')[0]
            path=prefix+'/'+name
            check(path not in index,'Ruta ISO duplicada')
            index[path]=(a,b)
            if row[25]&2:visit(row,path,ancestors|{o})
    visit(root,'',set())
    return index
def dat_members(raw):
    check(len(raw)>=16,'DAT corto')
    n=struct.unpack_from('<I',raw)[0];base=16+32*n;pos=base
    check(0<n<=2000 and base<=len(raw),'DAT invalido')
    m={}
    for i in range(n):
        off=16+32*i;end=base+struct.unpack_from('<I',raw,off)[0]
        name=raw[off+4:off+32].split(b'\0',1)[0].decode('cp932')
        check(name not in m and pos<=end<=len(raw),'DAT invalido')
        m[name]=raw[pos:end];pos=end
    check(pos==len(raw),'DAT incompleto');return m
def load_iso(path):
    with open(path,'rb') as f:
        idx=iso_index(f)
        off,size=idx['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']
        pack=read_at(f,off,size)
        start=read_at(f,*idx['/PSP_GAME/USRDIR/START_JP.LZS'])
    font=dat_members(lzs_decompress(start))
    return off,pack,font
def variables(b):
    check(len(b)%2==0,'Texto TALK de ancho impar')
    result=[]
    for i in range(0,len(b),2):
        pair=b[i:i+2]
        if pair[0]>=0x80:continue
        check(pair[0]==65 and 48<=pair[1]<=57,'Control de texto desconocido')
        result.append(pair.decode('ascii'))
    return tuple(result)
def decode_line(b):
    variables(b);return ''.join(decode_es(b[i:i+2]) for i in range(0,len(b),2))
VAR=re.compile(r'(?<![A-Za-z0-9])A[0-9](?![A-Za-z0-9])')
def wide(s):
    return ''.join('　' if c==' ' else '、' if c==',' else '。' if c=='.' else chr(ord(c)+0xfee0) if 0x21<=ord(c)<=0x7e else c for c in s)
def encode_line(s,old,font):
    check(s and not any(ord(c)<32 for c in s),'Texto vacio o control no admitido')
    expected=variables(old);parts=[];pos=0;visible=[]
    if expected:
        for match in VAR.finditer(s):
            t=wide(s[pos:match.start()]);parts.append(encode_es(t));visible.append(t)
            parts.append(match.group().encode('ascii'));pos=match.end()
    t=wide(s[pos:]);parts.append(encode_es(t));visible.append(t)
    data=b''.join(parts)
    check(variables(data)==expected,'Variables A0..A9 diferentes')
    check(len(data)<=56,'Maximo conservador: 28 pares por linea')
    check(not missing_render_glyphs(''.join(visible),font),'La fuente instalada no contiene algun glifo')
    return data
def rows_for(pack):
    result=[];warnings=[]
    for item in nispack(pack):
        name=item['name']
        if not re.fullmatch(r'talk\d+_jp\.dat',name,re.I):continue
        raw=item['content']
        try:meta=inspect(raw)
        except ValueError as e:
            warnings.append({'recurso':name,'error':str(e)});continue
        for t in meta['strings']:
            kind='OPCION_NO_EDITAR' if t.get('choice') else 'DIALOGO'
            try:s=decode_line(t['raw'])
            except (ValueError,UnicodeError):
                s='[CONTROL NO INTERPRETADO]';kind='NO_EDITAR'
            result.append(dict(recurso=name,entrada=str(t['entry']),
                id_dialogo=str(struct.unpack_from('<I',raw,12+32*t['entry'])[0]),
                offset=str(t['offset']),tipo=kind,original_hex=t['raw'].hex(),
                texto_actual=unicodedata.normalize('NFKC',s),nuevo_texto=''))
    return result,warnings
def export(iso,out):
    check(not out.exists(),'La carpeta ya existe')
    _,pack,_=load_iso(iso);rows,warnings=rows_for(pack)
    check(rows,'No se encontraron dialogos')
    out.mkdir(parents=True)
    with (out/'dialogos.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=COLS);w.writeheader();w.writerows(rows)
    (out/'origen.json').write_text(json.dumps(dict(iso_sha256=sha_file(iso),pack_sha256=sha(pack),filas=len(rows),advertencias=warnings),ensure_ascii=False,indent=2),encoding='utf8')
    print('Exportadas',len(rows),'lineas. Advertencias:',len(warnings))
def stripped(raw,meta):
    # Conserva todos los bytes de control, incluidos marcadores y terminadores.
    parts=[];pos=meta['base']
    for t in sorted(meta['strings'],key=lambda z:z['offset']):
        check(t['offset']>=pos,'Texto solapado')
        parts.append(raw[pos:t['offset']]);pos=t['end']
    parts.append(raw[pos:]);return b''.join(parts)
def edit_pack(pack,changes,font):
    members=nispack(pack)
    endian='>' if struct.unpack_from('<I',pack,8)[0]==1 else '<'
    names={x['name']:i for i,x in enumerate(members)}
    check(len(names)==len(members),'NISPACK con nombres duplicados')
    ordered=sorted(members,key=lambda x:x['offset'])
    limits={}
    prev=16+44*len(members)
    for i,x in enumerate(ordered):
        lo=x['offset'];end=lo+x['size']
        check(prev<=lo<=end<=len(pack),'NISPACK solapado')
        limits[x['name']]=ordered[i+1]['offset'] if i+1<len(ordered) else len(pack)
        prev=end
    out=bytearray(pack);journal=[]
    for name,rows in changes.items():
        item=members[names[name]];old=item['content'];meta=inspect(old)
        by={t['offset']:t for t in meta['strings']};edits=[]
        for row in rows:
            t=by[int(row['offset'])]
            check(not t.get('choice'),'Opcion no editable en este modo')
            b=encode_line(row['nuevo_texto'],t['raw'],font)
            edits.append((t['offset']-1,t['end']+1,b'\1'+b+b'\0'))
        new,j=replace(old,edits);newmeta=inspect(new)
        check(len(newmeta['strings'])==len(meta['strings']),'Numero de lineas distinto')
        check(stripped(old,meta)==stripped(new,newmeta),'Controles modificados')
        check(len(new)<=286072,'Limite conservador de buffer TALK excedido')
        lo=item['offset'];oldend=lo+len(old);newend=lo+len(new)
        check(newend<=limits[name],'No cabe en su hueco NISPACK: '+name+'; acorta el texto')
        check(newend<=oldend or not any(pack[oldend:newend]),'Hueco no vacio')
        out[lo:max(oldend,newend)]=new+b'\0'*max(0,oldend-newend)
        struct.pack_into(endian+'I',out,16+44*names[name]+36,len(new))
        journal.append(dict(recurso=name,lineas=len(edits),tamano_anterior=len(old),tamano_nuevo=len(new),sha256=sha(new),ediciones=j))
    reread=nispack(out)
    for a,b in zip(members,reread):
        check(a['name']==b['name'] and a['offset']==b['offset'] and a['unknown']==b['unknown'],'Directorio alterado')
        if a['name'] not in changes:check(a['content']==b['content'],'Miembro ajeno alterado')
        else:check(sha(b['content'])==next(j['sha256'] for j in journal if j['recurso']==a['name']),'Relectura incorrecta')
    check(len(out)==len(pack),'Pack cambio de tamano')
    return out,journal
def apply(iso,folder,out):
    check(not out.exists() and out.resolve()!=iso.resolve(),'Salida existente o igual al original')
    report=out.with_suffix(out.suffix+'.json')
    check(not report.exists(),'Informe ya existe')
    fingerprint=json.loads((folder/'origen.json').read_text(encoding='utf8'))
    check(sha_file(iso)==fingerprint['iso_sha256'],'Selecciona la misma ISO que exportaste')
    off,pack,font=load_iso(iso)
    check(sha(pack)==fingerprint['pack_sha256'],'SCRIPTPACK distinto')
    actual,_=rows_for(pack)
    with (folder/'dialogos.csv').open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);check(reader.fieldnames==COLS,'Columnas alteradas');rows=list(reader)
    check(len(rows)==len(actual)==fingerprint['filas'],'Filas alteradas')
    changes={}
    for a,b in zip(actual,rows):
        check(all(b.get(k)==a[k] for k in COLS[:-1]),'Cambiaste columna protegida u orden: '+a['recurso']+' '+a['offset'])
        if b['nuevo_texto'] and b['nuevo_texto']!=a['texto_actual']:
            check(a['tipo']=='DIALOGO','Fila no editable')
            changes.setdefault(a['recurso'],[]).append(b)
    check(changes,'No hay cambios en nuevo_texto')
    new,journal=edit_pack(pack,changes,font)
    tmp=out.with_name(out.name+'.part');check(not tmp.exists(),'Temporal existente')
    try:
        with iso.open('rb') as src,tmp.open('xb') as dst:shutil.copyfileobj(src,dst,CHUNK)
        with tmp.open('r+b') as f:f.seek(off);f.write(new)
        with iso.open('rb') as a,tmp.open('rb') as b:
            check(read_at(b,off,len(new))==new,'Relectura pack incorrecta')
            for lo,hi in ((0,off),(off+len(pack),iso.stat().st_size)):
                for pos in range(lo,hi,CHUNK):
                    n=min(CHUNK,hi-pos)
                    check(read_at(a,pos,n)==read_at(b,pos,n),'Cambios fuera del pack')
        check(tmp.stat().st_size==iso.stat().st_size,'Tamano ISO alterado')
        digest=sha_file(tmp)
        os.replace(tmp,out)
        with report.open('x',encoding='utf8') as f:
            json.dump(dict(iso_sha256=digest,origen_sha256=fingerprint['iso_sha256'],recursos=journal,ppsspp=False),f,ensure_ascii=False,indent=2)
        print('ISO creada:',out,'SHA256:',digest)
    finally:
        if tmp.exists():tmp.unlink()
def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    e=sub.add_parser('exportar');e.add_argument('iso',type=Path);e.add_argument('carpeta',type=Path)
    a=sub.add_parser('insertar');a.add_argument('iso',type=Path);a.add_argument('carpeta',type=Path);a.add_argument('salida',type=Path)
    x=p.parse_args()
    if x.cmd=='exportar':export(x.iso,x.carpeta)
    else:apply(x.iso,x.carpeta,x.salida)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,UnicodeError,struct.error) as e:raise SystemExit('ERROR: '+str(e))
