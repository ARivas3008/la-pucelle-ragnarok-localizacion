"""Auditoría de solo lectura de BGPACK.DAT dentro de ISO9660 original de PSP.

No extrae ni publica materiales comerciales. Pruebas sintéticas != PPSSPP.
"""
import argparse
import collections
import hashlib
import json
import struct
from pathlib import Path

BLOCK=2048
ENTRY=44

def parse_bgpack(raw):
    if len(raw)<16 or raw[:8]!=b'NISPACK\0':
        raise ValueError('Cabecera NISPACK incorrecta')
    n=struct.unpack_from('<I',raw,12)[0]
    if not 0<n<100000 or 16+n*ENTRY>len(raw):
        raise ValueError('Tabla NISPACK inválida')
    members=[]
    names=set()
    for i in range(n):
        pos=16+i*ENTRY
        name_bytes=raw[pos:pos+32].split(b'\0',1)[0]
        if not name_bytes or b'/' in name_bytes or b'\\' in name_bytes:
            raise ValueError('Nombre inválido')
        name=name_bytes.decode('ascii')
        offset,size,metadata=struct.unpack_from('<III',raw,pos+32)
        if name in names or not size or offset<16+n*ENTRY or offset%BLOCK or offset+size>len(raw):
            raise ValueError('Miembro duplicado o fuera de límites')
        names.add(name)
        members.append(dict(name=name,offset=offset,size=size,metadata_u32=metadata))
    order=sorted(members,key=lambda item:item['offset'])
    if any(a['offset']+a['size']>b['offset'] for a,b in zip(order,order[1:])):
        raise ValueError('Miembros solapados')
    return members

def _directory(f,lba,size):
    f.seek(lba*BLOCK)
    data=f.read(size)
    p=0
    while p<len(data):
        length=data[p]
        if not length:
            p=(p//BLOCK+1)*BLOCK
            continue
        if length<34 or p+length>len(data):
            raise ValueError('Directorio ISO9660 truncado')
        row=data[p:p+length]
        p+=length
        name=row[33:33+row[32]].decode('ascii')
        if name in ('\x00','\x01'):
            continue
        yield name.split(';')[0],int.from_bytes(row[2:6],'little'),int.from_bytes(row[10:14],'little'),bool(row[25]&2)

def read_bgpack(iso_path):
    with Path(iso_path).open('rb') as f:
        f.seek(16*BLOCK)
        pvd=f.read(BLOCK)
        if pvd[:7]!=b'\x01CD001\x01':
            raise ValueError('No es volumen ISO9660 primario')
        root=pvd[156:190]
        stack=[('',int.from_bytes(root[2:6],'little'),int.from_bytes(root[10:14],'little'))]
        visited=set()
        while stack:
            parent,lba,size=stack.pop()
            if (lba,size) in visited:
                continue
            visited.add((lba,size))
            for name,child_lba,child_size,is_dir in _directory(f,lba,size):
                path='/'.join(x for x in (parent,name) if x)
                if is_dir:
                    stack.append((path,child_lba,child_size))
                elif path=='PSP_GAME/USRDIR/BGPACK.DAT':
                    f.seek(child_lba*BLOCK)
                    data=f.read(child_size)
                    if len(data)!=child_size:
                        raise ValueError('BGPACK truncado')
                    return data,dict(path=path,lba=child_lba,size=child_size)
    raise ValueError('No se encontró BGPACK.DAT')

def audit(iso,expect_iso_sha256=None):
    p=Path(iso)
    with p.open('rb') as f:
        sha=hashlib.file_digest(f,'sha256').hexdigest()
    if expect_iso_sha256 and sha.lower()!=expect_iso_sha256.lower():
        raise ValueError('SHA256 de ISO inesperado')
    raw,locator=read_bgpack(p)
    members=parse_bgpack(raw)
    txp=[]
    for x in members:
        if x['name'].lower().endswith('.txp'):
            item={key:x[key] for key in ('name','offset','size')}
            item['sha256']=hashlib.sha256(raw[x['offset']:x['offset']+x['size']]).hexdigest()
            txp.append(item)
    return {'clase':'A: ISO original auténtica, sin modificar',
            'no_certifica':['textos rasterizados','inserción','PPSSPP'],
            'iso_sha256':sha,'iso_bytes':p.stat().st_size,
            'bgpack':dict(locator,sha256=hashlib.sha256(raw).hexdigest()),
            'miembros':len(members),
            'tipos':dict(collections.Counter(x['name'].rsplit('.',1)[-1].lower() for x in members)),
            'texturas_txp':txp}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso',required=True,type=Path)
    p.add_argument('--expect-iso-sha256')
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    content=json.dumps(audit(args.iso,args.expect_iso_sha256),ensure_ascii=False,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding='utf-8')
    else:
        print(content)

if __name__=='__main__':
    main()
