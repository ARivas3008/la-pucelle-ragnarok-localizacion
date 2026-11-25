#!/usr/bin/env python3
"""Auditoría de solo lectura: originales y cuatro EDAT piloto ROM-026."""
import argparse,csv,hashlib,json,struct,unicodedata
from pathlib import Path
from collections import Counter,defaultdict

PROFILES={'char.dat':(200,{0:24}),'name.dat':(16,{4:12}),'magic.dat':(116,{18:23,41:57}),'mapinfo.dat':(96,{12:28}),'com.dat':(92,{0:23,23:49}),'kis.dat':(148,{0:21,21:57}),'ritem.dat':(92,{4:13,17:43}),'skill.dat':(94,{16:21,37:57})}
FONT={'fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp'}
ICONS=set('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳')
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(s):return unicodedata.normalize('NFKC',s).strip(' \u3000')
def ids(spec):
 out=[]
 for r in spec.split(','):
  a,*b=map(int,r.split('-'));out.extend(range(a,(b[0] if b else a)+1))
 if len(set(out))!=len(out):raise ValueError('IDs repetidos')
 return {str(x) for x in out}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def unpack_edat(b):
 require(b[:8]==b'NISPACK\0' and struct.unpack_from('<II',b,8)==(0,1),'NISPACK inválido')
 name,o,n,_=struct.unpack_from('<32sIII',b,16);require(name.rstrip(b'\0')==b'start_jp.lzs' and o==2048 and o+n==len(b),'Directorio EDAT inválido')
 d=b[o:];ext,size,compressed,marker=struct.unpack_from('<4sIIB',d);require(ext==b'dat\0' and compressed+4==len(d) and 0<size<=256*1024*1024,'LZS inválido')
 out=bytearray();i=16;refs=0
 while len(out)<size:
  x=d[i];i+=1
  if x!=marker:out.append(x);continue
  dist=d[i];i+=1
  if dist==marker:out.append(dist);continue
  count=d[i];i+=1;dist-=dist>marker
  require(0<count<=dist<=len(out) and len(out)+count<=size,'Referencia LZS inválida o solapada');out.extend(out[-dist:len(out)-dist+count]);refs+=1
 require(len(out)==size and i==len(d),'Longitud LZS inválida')
 raw=bytes(out);count=struct.unpack_from('<I',raw)[0];require(count==36,'Cantidad DAT inválida');base=16+32*count;last=base;mm={}
 for i in range(count):
  pos=16+32*i;end=base+struct.unpack_from('<I',raw,pos)[0];name=raw[pos+4:pos+32].split(b'\0')[0].decode('cp932');require(last<=end<=len(raw) and name not in mm,'Miembro DAT inválido');mm[name]=raw[last:end];last=end
 require(last==len(raw),'DAT incompleto');return raw,mm,refs

def glyph_index(p):
 if len(p)==1:return p[0]-31
 a,b=p;return 96+((a-0x81) if a<=0x9f else 31+a-0xe0)*192+b-0x40

def verificar(manifest,proof,original_dir,pilot_dir):
 selected=ids(proof['ids_previos'])|ids(proof['ids_nuevos']);require(len(selected)==1457,'Selección inválida')
 rows=[r for r in manifest if r['recurso'].startswith('DLC_')];require(len(rows)==3537,'Manifiesto DLC distinto');rows=[r for r in rows if r['unit_id'] in selected];require(len(rows)==len(selected),'IDs no encontrados')
 result={}
 for i in range(4):
  key=f'DLC_{i:02}';name=f'DL_JP_{i:02}';old=(original_dir/(name+'.EDAT')).read_bytes();new=(pilot_dir/(name+'_rom026.EDAT')).read_bytes();ref=proof['packs'][key]
  require(sha(old)==ref['original_sha256'] and sha(new)==ref['edat_sha256'],'SHA EDAT distinto: '+key)
  a,orig,_=unpack_edat(old);b,cur,refs=unpack_edat(new);require(a[:16+36*32]==b[:16+36*32],'Directorio DAT alterado');require(old[:0x34]==new[:0x34] and old[0x38:2048]==new[0x38:2048],'Metadatos NISPACK alterados');require(sha(b)==ref['dat_sha256'],'SHA DAT distinto')
  require(orig.keys()==cur.keys(),'Miembros DAT distintos');intervals=defaultdict(list);counts=Counter();font=struct.unpack('<11616H',cur['fontB.fnt'])
  for r in rows:
   if not r['recurso'].startswith(key+'/'):continue
   n=r['recurso'].split('/')[-1];o=int(r['offset']);stride,starts=PROFILES[n];cap=starts.get((o-8)%stride);require(cap is not None and o+cap<=len(orig[n]),'Reserva inválida: '+r['unit_id']);before=orig[n][o:o+cap];after=cur[n][o:o+cap];x=before.index(0);y=after.index(0);require(x>0 and y>0 and not any(before[x:]) and not any(after[y:]),'Relleno inválido');source=before[:x].decode('cp932');require(norm(source)==norm(r['original']),'Fuente distinta: '+r['unit_id'])
   if source[0] in ICONS:require(before[:2]==after[:2],'Prefijo alterado');counts['prefijos']+=1
   j=0
   while j<y:
    k=1 if after[j]<0x80 or 0xa1<=after[j]<=0xdf else 2;p=after[j:j+k];j+=k;idx=glyph_index(p);require(p in (b' ',b'\x81\x40') or 0<idx<len(font) and font[idx]>0,'Glifo ausente')
   intervals[n].append((o,o+cap));counts['resueltos']+=1;counts['coinciden' if before==after else 'cambios']+=1
  for n,rr in intervals.items():
   last=0
   for start,end in sorted(rr):require(start>=last and orig[n][last:start]==cur[n][last:start],'Solapamiento o bytes exteriores alterados');last=end
   require(orig[n][last:]==cur[n][last:],'Bytes finales alterados');counts['bytes_exteriores']+=len(orig[n])-sum(e-s for s,e in rr)
   require(sha(cur[n])==proof['tablas'][key+'/'+n],'SHA tabla distinto')
  for n in orig:
   require(len(orig[n])==len(cur[n]),'Tamaño miembro alterado')
   if n not in intervals and n not in FONT:require(orig[n]==cur[n],'Recurso ajeno alterado')
  counts['intactos']=sum(orig[n]==cur[n] for n in orig);counts['refs']=refs;result[key]=dict(counts)
 require(sum(x['resueltos'] for x in result.values())==1457,'Cobertura inválida');return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originales',type=Path,required=True);p.add_argument('--pilotos',type=Path,required=True);p.add_argument('--manifiesto',type=Path,required=True);p.add_argument('--prueba',type=Path,required=True);a=p.parse_args();rows=list(csv.DictReader(a.manifiesto.open(encoding='utf-8-sig',newline='')));proof=json.loads(a.prueba.read_text(encoding='utf8'));print(json.dumps(verificar(rows,proof,a.originales,a.pilotos),indent=2))
if __name__=='__main__':main()
