"""Inspeccion y descompresion sin efectos sobre originales, compatible con Scarlet NISLZS.
NIS LZS: [ext4][raw_u32_le][compressed_u32_le][marker_u8][3 reserved][tokens...].
NISPACK: [NISPACK\\0][byte-order flag][nfiles][name32,offset,size,unk32]*.
"""
from pathlib import Path
import struct

def lzs_header(data):
 if len(data)<16:raise ValueError('LZS demasiado corto')
 ext,uncompressed,compressed,marker,*other=struct.unpack_from('<4sIIB3B',data)
 if compressed+4!=len(data):
  raise ValueError(f'LZS longitud no coincide: header+4={compressed+4} real={len(data)}')
 if uncompressed>256*1024*1024:raise ValueError('LZS mayor de 256 MiB')
 return {'ext':ext,'raw_size':uncompressed,'compressed_size':compressed,'marker':marker,'reserved':bytes(other)}

def lzs_decompress(data):
 h=lzs_header(data)
 raw=bytearray(h['raw_size'])
 marker=h['marker'];i=16;j=0
 end=len(data)
 while j<h['raw_size']:
  if i>=end:raise ValueError(f'LZS truncado i={i},j={j}')
  op=data[i];i+=1
  if op!=marker:
   raw[j]=op;j+=1
  else:
   if i>=end:raise ValueError('LZS sin distancia')
   distance=data[i];i+=1
   if distance==marker:
    raw[j]=marker;j+=1
   else:
    if i>=end:raise ValueError('LZS sin longitud')
    if distance>marker:distance-=1
    n=data[i];i+=1
    if n>h['raw_size']-j or distance>j:
     raise ValueError(f'LZS referencia invalida output={j} distance={distance} n={n}')
    if not distance:raise ValueError('LZS distancia cero')
    for k in range(n):raw[j+k]=raw[j-distance+k]
    j+=n
 if i!=end:raise ValueError(f'LZS sobran {end-i} bytes después de descomprimir')
 return bytes(raw)

def nispack(data):
 if data[:8]!=b'NISPACK\x00':raise ValueError('No es NISPACK')
 endian_flag=struct.unpack_from('<I',data,8)[0]
 if endian_flag not in (0,1):raise ValueError('Bandera endianness desconocida')
 endian='>' if endian_flag==1 else '<'
 count=struct.unpack_from(endian+'I',data,12)[0]
 if count>5000:raise ValueError('Demasiados archivos')
 items=[]
 for n in range(count):
  o=16+n*44
  name,offset,size,unknown=struct.unpack_from(endian+'32sIII',data,o)
  name=name.split(b'\x00')[0].decode('cp932','replace')
  if offset+size>len(data):raise ValueError('Offset o tamaño NISPACK fuera de archivo')
  items.append({'name':name,'offset':offset,'size':size,'unknown':unknown,'content':data[offset:offset+size]})
 return items

if __name__=='__main__':
 import hashlib,collections,time
 a=Path('/mnt/data/START_JP.LZS').read_bytes()
 print('ISO start',lzs_header(a),flush=True)
 start=time.time()
 raw=lzs_decompress(a)
 print('ISO decoded',len(raw),'SHA256',hashlib.sha256(raw).hexdigest(),'took',round(time.time()-start,2),'s',flush=True)
 Path('/mnt/data/start_jp_raw.dat').write_bytes(raw)
 files=nispack(raw)
 print('NISPACK inner',len(files))
 for x in files:
  print(x['name'],x['offset'],x['size'],hex(x['unknown']))
 Path('/mnt/data/start_extracted').mkdir(exist_ok=True)
 for x in files:
  Path('/mnt/data/start_extracted',x['name']).write_bytes(x['content'])
