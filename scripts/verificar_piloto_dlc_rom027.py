#!/usr/bin/env python3
"""Relectura ROM-027: recompila exclusivamente bloques completos de origen exacto.
No escribe originales ni candidatos. Los hashes de ROM-026 y del corpus son obligatorios.
"""
import argparse,csv,hashlib,json,struct,unicodedata
from bisect import bisect_right
from collections import Counter,defaultdict
from pathlib import Path
from verificar_piloto_dlc_rom026 import unpack_edat,verificar as verificar_base,ids,require,sha,norm,glyph_index,FONT

EXTRAS=''.join(dict.fromkeys('áéíóúÁÉÍÓÚñÑüÜ¿¡«»àèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöÄËÏÖŸçÇōūŌŪºª©†♀♂–—‘’“”'))
CODES={c:bytes([0xf0,t]) for c,t in zip(EXTRAS,[*range(0x40,0x7f),*range(0x80,0xfd)])}

def inspect(raw):
 n,n2=struct.unpack_from('<II',raw);base=8+32*n
 require(0<n<10000 and n==n2 and base<=len(raw),'Índice TALK inválido')
 offsets=[struct.unpack_from('<I',raw,8+32*i)[0] for i in range(n)]
 require(offsets[0]==0 and offsets==sorted(offsets) and offsets[-1]<=len(raw)-base,'Offsets TALK inválidos')
 args={5:2,6:2,7:2,9:2,10:2,11:3,12:3,0xc9:1,0x14:1};pos=base;strings=[];tokens=[]
 while pos<len(raw):
  start=pos;op=raw[pos];pos+=1
  if op==0x14:
   count=raw[pos];pos+=1
   for _ in range(count):
    mark=raw.find(b'\x01',pos);require(mark>=0,'Opción sin marcador');end=raw.find(b'\0',mark+1);require(end>=0,'Opción sin terminador');strings.append(dict(offset=mark+1,end=end,raw=raw[mark+1:end],entry=bisect_right(offsets,mark-base)-1,choice=True));tokens.append((mark,end+1,1));pos=end+1
   tail=raw.find(b'\xfd',pos);require(tail>=0,'Selector sin terminador');pos=tail+1
  elif op==1:
   end=raw.find(b'\0',pos);require(end>=0,'Texto sin terminador');strings.append(dict(offset=pos,end=end,raw=raw[pos:end],entry=bisect_right(offsets,pos-base)-1));pos=end+1
  else:
   require(op in args or op in (0,2,3,0xfa,0xfd,0xfe,0xff),'Opcode desconocido');pos+=args.get(op,0)
  require(pos<=len(raw),'Argumento fuera de TALK');tokens.append((start,pos,op))
 starts={a-base for a,b,op in tokens};require(all(x in starts or x==len(raw)-base for x in offsets),'Entrada no apunta a opcode')
 return dict(n=n,base=base,offsets=offsets,strings=strings,tokens=tokens)

def runs(raw,meta):
 out=[]
 for t in sorted(meta['strings'],key=lambda x:x['offset']):
  if not t['raw']:continue
  if out:
   p=out[-1][-1]
   if not t.get('choice') and not p.get('choice') and t['entry']==p['entry'] and raw[p['end']:t['offset']] in (b'\0\1',b'\0\2\1'):
    out[-1].append(t);continue
  out.append([t])
 return out

def encode(text):
 wide=''.join('　' if c==' ' else '、' if c==',' else '。' if c=='.' else chr(ord(c)+0xfee0) if 0x21<=ord(c)<=0x7e else c for c in text)
 data=b''.join(CODES[c] if c in CODES else c.encode('cp932') for c in wide)
 require(len(data)%2==0 and all(x>=0x80 for x in data[::2]),'Ancho TALK inválido')
 return data

def wrap(text):
 require(text.strip()==text and text and not any(c in text for c in '\0\n\r\t') and '  ' not in text,'Espaciado o control editorial')
 lines=[];line=''
 for word in text.split(' '):
  require(len(encode(word))<=56,'Palabra excede 28 glifos');candidate=(line+' '+word) if line else word
  if len(encode(candidate))>56:lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 require(' '.join(lines)==text,'Texto alterado por reflujo');return lines

def compile_selected(raw,res,rows,selected,reviews,font):
 meta=inspect(raw);by={int(r['offset']):r for r in rows if r['recurso']==res};groups=defaultdict(set)
 for r in rows:
  if r['recurso']==res:groups[r['grupo_id']].add(r['unit_id'])
 edits=[];seen=set();fnt=struct.unpack('<11616H',font)
 for seq in runs(raw,meta):
  rr=[by.get(t['offset']) for t in seq];target=[r for r in rr if r and r['unit_id'] in selected]
  if not target:continue
  require(len(target)==len(seq),'Bloque parcial seleccionado');gids=list(dict.fromkeys(r['grupo_id'] for r in target));units=[r['unit_id'] for r in target];require(not seen.intersection(units),'Unidad repetida')
  require(all(groups[g]=={r['unit_id'] for r in target if r['grupo_id']==g} for g in gids),'Grupo partido por controles')
  for r,t in zip(target,seq):
   require(norm(r['original'])==norm(t['raw'].decode('cp932')),'Fuente literal distinta')
   require(len(t['raw'])%2==0 and all(x>=0x80 for x in t['raw'][::2]),'Variable/control no admitido')
  text=' '.join(reviews[g] for g in gids);source=''.join(r['original'] for r in target)
  require(all(source.count(c)==text.count(c) for c in '□△○×◯♪♫★☆¥'),'Símbolo funcional alterado')
  lines=wrap(text);choice=bool(seq[0].get('choice'));require(not choice or len(lines)==1,'Opción de varias líneas')
  off=seq[0]['offset'];previous=[x for x in meta['strings'] if x['entry']==seq[0]['entry'] and x['end']<off-1]
  if previous and not choice:
   last=max(previous,key=lambda t:t['end']);between=[op for a,b,op in meta['tokens'] if a>last['end'] and b<=off-1];require(any(op in (2,3) for op in between),'No consta reinicio de caja')
  new=bytearray()
  for i,line in enumerate(lines):
   d=encode(line);require(all(d[q:q+2]==b'\x81\x40' or 0<glyph_index(d[q:q+2])<len(fnt) and fnt[glyph_index(d[q:q+2])] for q in range(0,len(d),2)),'Glifo no asignado')
   if i and i%3==0:new+=b'\2'
   new+=b'\1'+d+b'\0'
  a=off-1;b=seq[-1]['end']+1;edits.append((a,b,bytes(new),units,gids,sha(text.encode()),len(lines)));seen.update(units)
 require(seen=={r['unit_id'] for r in by.values() if r['unit_id'] in selected},'Unidades sin compilación')
 base=meta['base'];parts=[raw[:base]];pos=base;delta=0;ends=[];shifts=[];journal=[];starts={a for a,b,op in meta['tokens']};lasts={b for a,b,op in meta['tokens']}
 for a,b,new,units,gids,h,lines in sorted(edits):
  require(a>=pos and a in starts and b in lasts and not any(a<base+p<b for p in meta['offsets']),'Límites de edición inválidos');parts.extend([raw[pos:a],new]);journal.append((a,a+delta,raw[a:b],new,units,gids,h,lines));delta+=len(new)-(b-a);ends.append(b-base);shifts.append(delta);pos=b
 parts.append(raw[pos:]);out=bytearray(b''.join(parts))
 for i,p in enumerate(meta['offsets']):
  q=bisect_right(ends,p)-1;struct.pack_into('<I',out,8+i*32,p+(shifts[q] if q>=0 else 0))
 check=inspect(out);require(meta['n']==check['n'],'Cantidad de entradas modificada')
 require(sum(bool(t.get('choice')) for t in meta['strings'])==sum(bool(t.get('choice')) for t in check['strings']),'Cantidad de opciones modificada')
 require(all(raw[12+32*i:40+32*i]==out[12+32*i:40+32*i] for i in range(meta['n'])),'Metadatos de entrada modificados')
 restored=bytearray(out)
 for _,off,old,new,*_ in reversed(journal):
  require(restored[off:off+len(new)]==new,'Destino inválido');restored[off:off+len(new)]=old
 restored[:base]=raw[:base];require(restored==raw,'Reversión no exacta')
 def controls(m,r):return [(op,r[a:b]) for a,b,op in m['tokens'] if op not in (1,2,0x14)]
 require(controls(meta,raw)==controls(check,bytes(out)),'Control no textual modificado')
 return bytes(out),journal,check

def read_reviews(repo,tsv):
 result={}
 if tsv:
  for p in tsv:
   for line in p.read_text(encoding='utf8').splitlines():
    gid,text=line.split('\t',1);require(gid not in result,'Grupo repetido');result[gid]=text
 else:
  paths=[repo/'corpus'/f'{n:02d}'/'revision.csv' for n in range(1,16)]+[repo/'data/preexistentes/509_revision_central.csv']
  for p in paths:
   for r in csv.DictReader(p.open(encoding='utf-8-sig',newline='')):
    if r['estado']=='revisado':require(r['grupo_id'] not in result,'Grupo repetido');result[r['grupo_id']]=r['es_revisado']
 return result

def verify(rows,reviews,proof,proof26,orig_dir,base_dir,pilot_dir):
 verificar_base(rows,proof26,orig_dir,base_dir)
 selected=ids(proof['ids_dialogos']);fixed=ids(proof26['ids_previos'])|ids(proof26['ids_nuevos']);require(len(selected)==1276 and not selected&fixed and len(fixed)==1457,'Inventario alterado')
 chosen=[r for r in rows if r['unit_id'] in selected];gids={r['grupo_id'] for r in chosen};require(len(chosen)==1276 and len(gids)==926 and gids<=reviews.keys(),'Revisiones incompletas')
 require(sha(''.join(g+'\t'+reviews[g]+'\n' for g in sorted(gids,key=int)).encode())==proof['revisiones_sha256'],'Revisiones distintas del piloto')
 result={};digest=[]
 for i in range(4):
  key=f'DLC_{i:02}';name=f'DL_JP_{i:02}';orig=(orig_dir/(name+'.EDAT')).read_bytes();base=(base_dir/(name+'_rom026.EDAT')).read_bytes();pilot=(pilot_dir/(name+'_rom027.EDAT')).read_bytes();ref=proof['packs'][key]
  a,om,_=unpack_edat(orig);b,bm,_=unpack_edat(base);c,cm,refs=unpack_edat(pilot)
  require(sha(pilot)==ref['edat_sha256'] and sha(c)==ref['dat_sha256'],'SHA ROM-027 distinto');require(orig[:0x34]==pilot[:0x34] and orig[0x38:2048]==pilot[0x38:2048],'Metadatos EDAT distintos');require(om.keys()==bm.keys()==cm.keys(),'Miembros distintos')
  require(all(bm[n]==cm[n] for n in bm if n!='talk00.dat' and n not in FONT),'Campos previos alterados')
  require(bm['talk00.dat']==om['talk00.dat'],'Base TALK modificada')
  for n in ('fontB.fnt','fontB.ftd'):
   old=struct.unpack('<11616H',bm[n]);new=struct.unpack('<11616H',cm[n]);allowed={glyph_index(CODES[ch]) for ch in '«»'};require(all(old[j]==new[j] for j in range(len(old)) if j not in allowed),'Mapeo anterior alterado')
   for ch,gid in [('«',2433),('»',2434)]:require(old[glyph_index(CODES[ch])]==0 and new[glyph_index(CODES[ch])]==(gid if n.endswith('.fnt') else 257),'Gaiji incorrecto')
  require(bm['FontB0000.txp']==cm['FontB0000.txp'],'Atlas anterior modificado')
  # Only the expected 14x14 tiles may change in page 1, checked by the exact swizzle byte positions.
  permitted=set()
  for gid in (2433,2434):
   k=gid%1296;x=k%36*14;y=k//36*14
   for v in range(y,y+14):
    for u in range(x,x+14):permitted.add(1040+((v//8)*16+(u//32))*128+(v%8)*16+(u%32)//2)
  require(len(bm['FontB0001.txp'])==len(cm['FontB0001.txp']) and all(x==y or j in permitted for j,(x,y) in enumerate(zip(bm['FontB0001.txp'],cm['FontB0001.txp']))),'Atlas fuera de gaiji modificado')
  expected,journal,meta=compile_selected(om['talk00.dat'],key+'/talk00.dat',rows,selected,reviews,cm['fontB.fnt'])
  require(expected==cm['talk00.dat'] and sha(expected)==ref['talk_sha256'],'TALK final distinto de revisión');require(len(expected)<286072,'TALK excede límite conservador')
  count=sum(len(j[4]) for j in journal);require(count==ref['dialogos'] and len(journal)==ref['bloques'],'Cobertura distinta')
  digest.extend((key+'/talk00.dat',a0,b0,h,','.join(units)) for a0,b0,old,new,units,gs,h,ls in journal)
  result[key]=dict(dialogos=count,bloques=len(journal),entradas=meta['n'],opciones=sum(bool(t.get('choice')) for t in meta['strings']),referencias_lzs=refs,miembros_intactos=sum(om[n]==cm[n] for n in om))
 require(sha(''.join('\t'.join(map(str,x))+'\n' for x in digest).encode())==proof['diario_sha256'],'Diario no coincide')
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originales',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--pilotos',type=Path,required=True);p.add_argument('--manifiesto',type=Path,required=True);p.add_argument('--prueba',type=Path,required=True);p.add_argument('--prueba-base',type=Path,required=True);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--revisiones-tsv',nargs='+',type=Path);a=p.parse_args()
 rows=list(csv.DictReader(a.manifiesto.open(encoding='utf-8-sig',newline='')));require(len(rows)==26258,'Manifiesto distinto');proof=json.loads(a.prueba.read_text());proof26=json.loads(a.prueba_base.read_text());reviews=read_reviews(a.repo,a.revisiones_tsv);result=verify(rows,reviews,proof,proof26,a.originales,a.base,a.pilotos);print(json.dumps(result,indent=2));print('2733/3537 (77.27%); validación binaria, no PPSSPP')
if __name__=='__main__':main()
