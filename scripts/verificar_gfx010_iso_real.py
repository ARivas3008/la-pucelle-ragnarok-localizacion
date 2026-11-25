"""Auditar ISO grafica frente a ISO PSP original sin exportar recursos protegidos."""
import argparse,hashlib,json,struct
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def iso_records(path):
 with path.open('rb') as f:
  f.seek(16*2048);p=f.read(2048)
  if p[1:6]!=b'CD001':raise ValueError('PVD ISO9660 inexistente')
  root=p[156:190];out={}
  def directory(lba,n,prefix):
   f.seek(lba*2048);raw=f.read(n);j=0
   while j<len(raw):
    size=raw[j]
    if size==0:j=(j//2048+1)*2048;continue
    rec=raw[j:j+size];j+=size
    if len(rec)<34:raise ValueError('Registro ISO9660 truncado')
    name=rec[33:33+rec[32]]
    if name in (bytes([0]),bytes([1])):continue
    name=name.decode('ascii').split(';')[0]
    off=struct.unpack_from('<I',rec,2)[0]*2048
    length=struct.unpack_from('<I',rec,10)[0]
    target=prefix+'/'+name
    if rec[25]&2:directory(off//2048,length,target)
    else:out[target]=(off,length)
  directory(struct.unpack_from('<I',root,2)[0],struct.unpack_from('<I',root,10)[0],'')
  return out
def members(blob):
 count=struct.unpack_from('<I',blob,12)[0]
 if count>10000:raise ValueError('BGPACK member count implausible')
 out={}
 for i in range(count):
  name,off,size,_=struct.unpack_from('<32sIII',blob,16+44*i)
  name=name.partition(b'\0')[0].decode('cp932')
  if name in out or off+size>len(blob):raise ValueError('BGPACK corrupto: '+name)
  out[name]=(off,size,blob[off:off+size])
 return out
def compare_outside(src,dst,start,length):
 count=0
 with src.open('rb') as a,dst.open('rb') as b:
  for lo,hi in ((0,start),(start+length,src.stat().st_size)):
   a.seek(lo);b.seek(lo);remaining=hi-lo
   while remaining:
    n=min(8<<20,remaining);s=a.read(n);t=b.read(n)
    if len(s)!=n or len(t)!=n:raise ValueError('Archivo truncado')
    count+=n
    if s!=t:raise ValueError('Alteracion fuera de BGPACK: '+str(lo))
    remaining-=n;lo+=n
 return count
def audit(original,pilot,manifest):
 ref=json.loads(manifest.read_text(encoding='utf-8'))
 if original.stat().st_size!=pilot.stat().st_size:raise ValueError('Tamanos ISO distintos')
 a=sha_file(original);b=sha_file(pilot)
 if a!=ref['iso_original_sha256']:raise ValueError('SHA original ajeno al manifiesto')
 if b!=ref['iso_piloto_sha256']:raise ValueError('SHA piloto ajeno al manifiesto')
 ra=iso_records(original);rb=iso_records(pilot)
 if ra!=rb:raise ValueError('Directorio ISO9660 modificado')
 key='/PSP_GAME/USRDIR/BGPACK.DAT';start,length=ra[key]
 with original.open('rb') as f:f.seek(start);before=f.read(length)
 with pilot.open('rb') as f:f.seek(start);after=f.read(length)
 if sha(before)!=ref['BGPACK_original_sha256'] or sha(after)!=ref['BGPACK_piloto_sha256']:
  raise ValueError('BGPACK hash inesperado')
 aa=members(before);bb=members(after)
 if aa.keys()!=bb.keys():raise ValueError('Miembros BGPACK modificados')
 changed=[];identical=0
 for name,(off,n,data) in aa.items():
  off2,n2,data2=bb[name]
  if (off,n)!=(off2,n2):raise ValueError('Offset o tamano cambiado: '+name)
  if data==data2:identical+=1;continue
  if name not in ref['assets']:raise ValueError('Cambio no autorizado: '+name)
  if sha(data)!=ref['assets'][name]['original_sha256'] or sha(data2)!=ref['assets'][name]['nuevo_sha256']:
   raise ValueError('TXP no reproducible: '+name)
  if data[:1040]!=data2[:1040]:raise ValueError('CLUT o cabecera alterada: '+name)
  changed.append(name)
 if set(changed)!=set(ref['assets']):raise ValueError('Faltan titulos editados')
 clean=compare_outside(original,pilot,start,length)
 return dict(evidencia='A ISO autentica + B reconstruccion estatica; no PPSSPP',
             iso_original_sha256=a,iso_piloto_sha256=b,
             bgpack_original_sha256=sha(before),bgpack_piloto_sha256=sha(after),
             miembros=len(aa),modificados=sorted(changed),miembros_intactos=identical,
             archivos_iso=len(ra),bytes_fuera_bgpack_cotejados=clean,
             fuera_bgpack_identico=True,ppsspp=False)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--original',type=Path,required=True)
 p.add_argument('--piloto',type=Path,required=True)
 p.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parents[1]/'docs/seguimiento/informes/GFX-007_capitulos_piloto.json')
 p.add_argument('--informe',type=Path,required=True)
 args=p.parse_args();result=audit(args.original,args.piloto,args.manifest)
 args.informe.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('AISLAMIENTO_GFX_VERIFICADO',len(result['modificados']),result['miembros_intactos'])
if __name__=='__main__':main()
