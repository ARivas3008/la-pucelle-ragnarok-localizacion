from pathlib import Path
import sys,struct,json,re,collections
B=Path(__file__).resolve().parent;R=B.parent
sys.path[:0]=[str(B/'herramientas/python'),str(B/'fuente/parcheador/app/scripts')]
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
from construir_parche import Image,members_from_dat
from nis_formats import nispack,lzs_decompress
i=Image(R/'La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso');records={p:(o,n) for p,o,n,_ in i.records()}
data=i.read(*records['/PSP_GAME/SYSDIR/EBOOT.BIN'])
text_offset=84;text_addr=142622720;text_size=694808;bias=text_addr-text_offset
md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);md.skipdata=True
ins=list(md.disasm(data[text_offset:text_offset+text_size],text_addr))
strings={}
for m in re.finditer(rb'(?:talk|script)%?[^\x00]{0,24}\.dat\x00',data):
 strings[m.start()+bias]=m.group()[:-1].decode('cp932')
print('Cadenas',[(hex(a),s) for a,s in strings.items()])
refs=[]
for index,inst in enumerate(ins):
 if inst.mnemonic!='lui':continue
 reg,imm=inst.op_str.split(', ');hi=int(imm,0)<<16
 for nxt in ins[index+1:index+12]:
  if nxt.mnemonic not in ('addiu','ori'):continue
  ops=nxt.op_str.split(', ')
  if len(ops)!=3 or ops[1]!=reg:continue
  value=(hi+int(ops[2],0))&0xffffffff if nxt.mnemonic=='addiu' else hi|int(ops[2],0)
  if value in strings:refs.append((index,value,strings[value]))
lines=[]
for ix,addr,name in refs:
 lines.append(f'\nREF {name} @ {addr:08x}\n')
 for inst in ins[max(0,ix-18):ix+40]:lines.append(f'{inst.address:08x}  {inst.mnemonic:8} {inst.op_str}')
(B/'informes/referencias_motor.asm').write_text('\n'.join(lines),encoding='utf-8')
(B/'informes/eboot.asm').write_text('\n'.join(f'{it.address:08x}  {it.mnemonic:8} {it.op_str}' for it in ins),encoding='utf-8')
print('Referencias',len(refs),'instrucciones',len(ins))
members=members_from_dat(lzs_decompress(i.read(*records['/PSP_GAME/USRDIR/START_JP.LZS'])))
raw=members['script00.dat'];n=struct.unpack_from('<I',raw)[0];ptr=struct.unpack_from(f'<{n}I',raw,4)
print('script00',len(raw),'n',n,'base',4+4*n,'último',ptr[-1],'primeros',ptr[:30])
print('body inicio',raw[4+4*n:4+4*n+160].hex())
