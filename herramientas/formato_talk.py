"""Intérprete talk contrastado con EBOOT 0x0884459c..0x08844c14.

Tabla: count,count,[offset,ID,condiciones: 24 bytes] * count.
El texto 0x01 se lee en pares; A0..A9 son variables, no ASCII literal.
Los saltos 0x0c usan IDs de diálogo de 24 bits, no offsets del cuerpo.
"""
import struct
from collections import Counter
from bisect import bisect_right

class TalkError(ValueError):pass

def inspect(raw):
 if len(raw)<40:raise TalkError('Talk truncado')
 n,n2=struct.unpack_from('<II',raw);base=8+32*n
 if not 0<n<10000 or n!=n2 or base>len(raw):raise TalkError('Tabla talk inválida')
 offsets=[struct.unpack_from('<I',raw,8+32*i)[0] for i in range(n)]
 if offsets[0]!=0 or offsets!=sorted(offsets) or offsets[-1]>len(raw)-base:raise TalkError('Índice talk inválido')
 args={5:2,6:2,7:2,9:2,10:2,11:3,12:3,0xc9:1,0x14:1}
 pos=base;strings=[];tokens=[];unknown=Counter()
 while pos<len(raw):
  start=pos;op=raw[pos];pos+=1
  if op==0x14:
   # El selector no ejecuta linealmente las ramas: busca N marcadores 01
   # y el terminador FD (EBOOT 0x08844a7c..0x08844b14). Un 14 01 entre
   # opciones no es una segunda instrucción de menú independiente.
   count=raw[pos];pos+=1
   for k in range(count):
    mark=raw.find(b'\x01',pos)
    if mark<0:raise TalkError('Opción sin marcador')
    end=raw.find(b'\0',mark+1)
    if end<0:raise TalkError('Opción sin terminador')
    strings.append(dict(offset=mark+1,end=end,raw=bytes(raw[mark+1:end]),entry=bisect_right(offsets,mark-base)-1,choice=True))
    tokens.append((mark,end+1,1));pos=end+1
   tail=raw.find(b'\xfd',pos)
   if tail<0:raise TalkError('Selector sin fin FD')
   pos=tail+1
  elif op==1:
   end=raw.find(b'\0',pos)
   if end<0:raise TalkError('String talk sin terminador')
   strings.append(dict(offset=pos,end=end,raw=bytes(raw[pos:end]),entry=bisect_right(offsets,pos-base)-1))
   pos=end+1
  else:
   pos+=args.get(op,0)
   if op not in args and op not in (0,2,3,0xfa,0xfd,0xfe,0xff):unknown[op]+=1
  if pos>len(raw):raise TalkError('Argumento talk fuera del recurso')
  tokens.append((start,pos,op))
 starts={a-base for a,b,op in tokens}
 bad=[x for x in offsets if x not in starts and x!=len(raw)-base]
 if bad:raise TalkError(f'{len(bad)} entradas no apuntan a opcodes: {bad[:5]}')
 return dict(n=n,base=base,offsets=offsets,strings=strings,tokens=tokens,unknown=dict(unknown))

def replace(raw,edits):
 """Sustituye intervalos de tokens completos y mueve solo la columna offset."""
 meta=inspect(raw);base=meta['base'];pos=base;delta=0;parts=[bytes(raw[:base])];ends=[];shifts=[];journal=[]
 starts={a for a,b,op in meta['tokens']};ends_allowed={b for a,b,op in meta['tokens']}
 for a,b,new in sorted(edits):
  if a<pos or a not in starts or b not in ends_allowed:raise TalkError('Edición no delimitada por opcodes')
  if any(a<base+p<b for p in meta['offsets']):raise TalkError('Entrada interior a la edición')
  parts.extend([bytes(raw[pos:a]),new]);newpos=a+delta
  delta+=len(new)-(b-a);ends.append(b-base);shifts.append(delta)
  journal.append(dict(offset_original=a,offset_nuevo=newpos,antes_hex=bytes(raw[a:b]).hex(),despues_hex=new.hex()))
  pos=b
 parts.append(bytes(raw[pos:]));out=bytearray(b''.join(parts))
 for i,p in enumerate(meta['offsets']):
  ix=bisect_right(ends,p)-1;shift=shifts[ix] if ix>=0 else 0
  struct.pack_into('<I',out,8+i*32,p+shift)
 check=inspect(out)
 assert check['n']==meta['n']
 for i in range(meta['n']):assert raw[12+32*i:40+32*i]==out[12+32*i:40+32*i]
 # Restauración independiente: se quita cada destino y se repone el original.
 restored=bytearray(out)
 for j in reversed(journal):
  a=j['offset_nuevo'];new=bytes.fromhex(j['despues_hex'])
  assert restored[a:a+len(new)]==new
  restored[a:a+len(new)]=bytes.fromhex(j['antes_hex'])
 restored[:base]=raw[:base]
 if restored!=raw:raise TalkError('Reversión no idéntica')
 return bytes(out),journal
