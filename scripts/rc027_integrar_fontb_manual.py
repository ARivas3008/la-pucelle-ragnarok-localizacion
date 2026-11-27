#!/usr/bin/env python3
"""Aplicar los assets manuales a un START_JP.LZS RC024 ya extendido."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'parcheador/app/scripts'))
from fontb_manual import apply_manual
from nis_formats import lzs_decompress
from rc026_reparar_start import compress

def repair(raw):
    count=struct.unpack_from('<I',raw)[0];base=16+count*32;pos=base;idx={}
    if not 0<count<=2000 or base>len(raw):raise ValueError('DAT inválido')
    for i in range(count):
        off=16+i*32;end=base+struct.unpack_from('<I',raw,off)[0]
        name=raw[off+4:off+32].split(b'\0',1)[0].decode('cp932')
        if name in idx or not pos<=end<=len(raw):raise ValueError('DAT inválido: '+name)
        idx[name]=(pos,end);pos=end
    if pos!=len(raw):raise ValueError('DAT incompleto')
    names=('fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp')
    m={n:raw[idx[n][0]:idx[n][1]] for n in names}
    proof=apply_manual(m);out=bytearray(raw)
    for n in names[2:]:
        lo,hi=idx[n]
        if len(m[n])!=hi-lo:raise ValueError('Tamaño alterado')
        out[lo:hi]=m[n]
    for n,(lo,hi) in idx.items():
        if n not in names[2:] and out[lo:hi]!=raw[lo:hi]:raise ValueError('Cambio ajeno')
    if out[:base]!=raw[:base]:raise ValueError('Directorio alterado')
    return bytes(out),proof
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--start',type=Path,required=True)
    a.add_argument('--salida',type=Path,required=True)
    args=a.parse_args()
    original=args.start.read_bytes()
    raw,report=repair(lzs_decompress(original))
    patched=compress(raw,original)
    args.salida.mkdir(parents=True,exist_ok=False)
    (args.salida/'START_JP.LZS').write_bytes(patched)
    report.update(original_sha256=hashlib.sha256(original).hexdigest(),
                  candidate_sha256=hashlib.sha256(patched).hexdigest(),iso_integrada=False)
    (args.salida/'informe.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
