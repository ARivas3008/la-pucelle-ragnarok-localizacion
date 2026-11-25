#!/usr/bin/env python3
"""Audit the eight fixed ISO tables against original bytes and insertion journal.
No commercial assets are written. Run from a complete repository checkout.
"""
import argparse,csv,hashlib,json,sys
from collections import Counter
from pathlib import Path

TABLES={'name.dat':290,'char.dat':152,'mapinfo.dat':100,'com.dat':148,'skill.dat':113,'kis.dat':277,'ritem.dat':214,'magic.dat':538}
PREFIXES=(b'\x87\x40',b'\x87\x41',b'\x87\x42')

def verificar_tabla(original,current,rows,journal,pending):
    expected={str(r['unit_id']):r for r in rows}
    if len(expected)!=len(rows):raise ValueError('IDs duplicados en manifiesto')
    done={str(r['unit_id']):r for r in journal};blocked={str(r['unit_id']):r for r in pending}
    if len(done)!=len(journal) or len(blocked)!=len(pending) or done.keys()&blocked.keys() or done.keys()|blocked.keys()!=expected.keys():
        raise ValueError('Diario incompleto, duplicado o ajeno al manifiesto')
    if len(original)!=len(current):raise ValueError('Tamaño de tabla modificado')
    intervals=[];counts=Counter();prefixes=Counter()
    for uid,j in done.items():
        row=expected[uid];off=int(j['offset']);cap=int(j['capacidad'])
        if any(str(row[k])!=str(j[k]) for k in ('unit_id','grupo_id','recurso','offset')):raise ValueError('Ancla del diario distinta: '+uid)
        if off<0 or cap<1 or off+cap>len(original):raise ValueError('Reserva fuera del archivo: '+uid)
        old=bytes.fromhex(j['antes_hex']);new=bytes.fromhex(j['despues_hex'])
        if len(old)!=cap or len(new)!=cap or old!=original[off:off+cap] or new!=current[off:off+cap]:raise ValueError('Relectura física distinta: '+uid)
        pos=new.find(b'\0')
        if pos<1 or any(new[pos:]):raise ValueError('Falta terminador o relleno cero: '+uid)
        if old[:2] in PREFIXES:
            if new[:2]!=old[:2]:raise ValueError('Prefijo funcional cambiado: '+uid)
            prefixes[old[:2].hex()]+=1
        intervals.append((off,off+cap));counts['coincidencias' if old==new else 'compactas' if j.get('adaptacion_compacta') else 'completas']+=1
    last=0
    for off,end in sorted(intervals):
        if off<last:raise ValueError('Reservas solapadas')
        if original[last:off]!=current[last:off]:raise ValueError('Datos ajenos al diario modificados')
        last=end
    if original[last:]!=current[last:]:raise ValueError('Datos finales ajenos al diario modificados')
    return dict(total=len(rows),resueltos=len(done),pendientes=len(blocked),completas=counts['completas'],compactas=counts['compactas'],coincidencias=counts['coincidencias'],prefijos=dict(prefixes),bytes_exteriores=len(original)-sum(e-o for o,e in intervals),sha256_destino=hashlib.sha256(current).hexdigest())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--iso',type=Path,required=True);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--informe',type=Path,required=True);p.add_argument('--recomprimir',action='store_true');p.add_argument('--estricto',action='store_true');a=p.parse_args()
    root=a.repo.resolve();sys.path.insert(0,str(root/'parcheador/app/scripts'))
    import construir_parche as c
    from integracion_total import verificar_iso_base
    from campos_revisados import aplicar
    from fuentes_es import add_spanish_fonts
    from nis_formats import lzs_decompress
    from revisiones_coordinadas import merge_central
    iso_sha=verificar_iso_base(a.iso);image=c.Image(a.iso);rec={p:(o,n) for p,o,n,_ in image.records()}
    blob=image.read(*rec['/PSP_GAME/USRDIR/START_JP.LZS'])
    if c.sh(blob)!=c.SHA_ISO_START:raise ValueError('START original no autenticado')
    raw=lzs_decompress(blob,allow_overlap=False);original=c.members_from_dat(raw);current={k:bytearray(v) for k,v in original.items()}
    manifest=list(csv.DictReader(c.DATA.open(encoding='utf-8-sig',newline='')));reviews,checks,states=c.read_reviews(root,False);reviews,checks,states=merge_central(root,reviews,manifest,checks,states)
    selection=[r for r in manifest if r['recurso'].startswith('ISO_START/') and r['recurso'].split('/')[-1] in TABLES]
    ids={r['unit_id']:r for r in selection}
    if len(ids)!=sum(TABLES.values()) or len(selection)!=len(ids):raise ValueError('Inventario ISO de tablas distinto')
    font=add_spanish_fonts(current);result=aplicar('ISO_START',original,current,selection,reviews);tables={}
    for name,count in TABLES.items():
        res='ISO_START/'+name;rows=[r for r in selection if r['recurso']==res]
        if len(rows)!=count:raise ValueError('Inventario distinto: '+name)
        journal=[j for j in result['aplicados'] if j['unit_id'] in ids and ids[j['unit_id']]['recurso']==res];pending=[j for j in result['pendientes'] if j['unit_id'] in ids and ids[j['unit_id']]['recurso']==res]
        tables[name]=verificar_tabla(original[name],current[name],rows,journal,pending)
    allowed=set(TABLES)|{'fontB.fnt','fontB.ftd','FontB0000.txp','FontB0001.txp'}
    if set(current)!=set(original) or any(current[n]!=original[n] for n in original if n not in allowed):raise ValueError('Recursos ajenos modificados')
    out=dict(iso_original_sha256=iso_sha,tablas=tables,total=sum(TABLES.values()),resueltos=sum(x['resueltos'] for x in tables.values()),pendientes=result['pendientes'],fuentes=font,corpus_sha256=checks,ppsspp=False)
    if a.recomprimir:
        new=c.replace_dat_members(raw,current);packed=c.cpack(new,blob,'ISO_START');assert lzs_decompress(packed,allow_overlap=False)==new;out['recompresion']={'bytes':len(packed),'sha256':c.sh(packed),'dat_sha256':c.sh(new)}
    a.informe.parent.mkdir(parents=True,exist_ok=True);a.informe.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['resueltos'],'/',out['total'])
    if a.estricto and out['resueltos']!=out['total']:raise SystemExit(1)

if __name__=='__main__':main()
