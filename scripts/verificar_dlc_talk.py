#!/usr/bin/env python3
"""Censo TALK de los cuatro DLC: solo lectura, no aprueba traducciones."""
import argparse,csv,hashlib,json,sys,unicodedata
from pathlib import Path
from collections import Counter,defaultdict

def norm(s):return unicodedata.normalize('NFKC',s).strip(' \u3000')
def line_key(s):return ''.join(unicodedata.normalize('NFKC',s).split())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dlc-directorio',required=True,type=Path)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--informe',required=True,type=Path)
    a=p.parse_args();sys.path.insert(0,str(a.repo.resolve()/'parcheador/app/scripts'))
    from dlc_originales import verificar_dlc_originales
    from nis_formats import nispack,lzs_decompress
    from construir_parche import members_from_dat,DATA
    from formato_talk import inspect
    from recompilar_talk import runs
    proof=verificar_dlc_originales(a.dlc_directorio)
    manifest=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')))
    assert len(manifest)==26258
    line_index=defaultdict(set);run_index=defaultdict(set);packs={};result={}
    for n in range(4):
        key=f'DLC_{n:02d}';data=(a.dlc_directorio/f'DL_JP_{n:02d}.EDAT').read_bytes()
        part=nispack(data)[0];members=members_from_dat(lzs_decompress(part['content'],allow_overlap=False))
        assert len(members)==36
        # Cotejo de todos los campos, scripts y TALK del manifiesto.
        selection=[r for r in manifest if r['recurso'].startswith(key+'/')]
        for row in selection:
            src=members[row['recurso'].split('/')[-1]];off=int(row['offset'])
            end=src.find(b'\0',off)
            if end<off or norm(src[off:end].decode('cp932'))!=norm(row['original']):
                raise ValueError('Ancla original distinta: '+row['unit_id'])
        raw=members['talk00.dat'];meta=inspect(raw)
        if meta['unknown']:raise ValueError('Opcode desconocido: '+key)
        rr=[r for r in selection if r['recurso']==key+'/talk00.dat']
        by={int(r['offset']):r for r in rr};ss={s['offset']:s for s in meta['strings']}
        if len(by)!=len(rr) or not by.keys()<=ss.keys():raise ValueError('Anclas TALK inválidas')
        run=runs(raw,meta);groups=defaultdict(list);counts=Counter()
        for r in rr:
            groups[r['grupo_id']].append(int(r['offset']))
        for item in meta['strings']:
            off=item['offset']
            if off in by:line_index[line_key(item['raw'].decode('cp932'))].add(by[off]['grupo_id'])
        for seq in run:
            k=sum(t['offset'] in by for t in seq)
            counts['bloque_completo_manifiesto' if k==len(seq) else 'bloque_parcial_manifiesto' if k else 'bloque_sin_ancla']+=1
            if k:counts['unidades_bloque_completo' if k==len(seq) else 'unidades_bloque_parcial']+=k
            if k==len(seq):
                run_index[tuple(t['raw'] for t in seq)].add(tuple(dict.fromkeys(by[t['offset']]['grupo_id'] for t in seq)))
        for gid,offs in groups.items():
            physical=[ss[o] for o in sorted(offs)]
            good=all(raw[x['end']:y['offset']] in (b'\0\1',b'\0\2\1') and x['entry']==y['entry'] for x,y in zip(physical,physical[1:]))
            counts['grupos_contiguos' if good else 'grupos_cruzan_controles']+=1
        result[key]=dict(sha256=hashlib.sha256(raw).hexdigest(),anclas_todos_recursos=len(selection),entradas=meta['n'],tokens=len(meta['tokens']),cadenas=len(meta['strings']),opciones=sum(bool(t.get('choice')) for t in meta['strings']),anclas_talk=len(rr),grupos=len(groups),bloques=len(run),estadisticas=dict(counts))
        packs[key]=(meta,by,run)
    for key,(meta,by,run) in packs.items():
        counts=Counter()
        for item in meta['strings']:
            if item['offset'] in by:counts['directas']+=1;continue
            m=line_index.get(line_key(item['raw'].decode('cp932')),set())
            counts['otra_linea_un_grupo' if len(m)==1 else 'otra_linea_varios_grupos' if m else 'otra_linea_sin_coincidencia']+=1
        for seq in run:
            if all(t['offset'] in by for t in seq):continue
            m=run_index.get(tuple(t['raw'] for t in seq),set())
            counts['bloque_exacto_un_grupo_tuple' if len(m)==1 else 'bloque_exacto_varios_group_tuples' if m else 'sin_bloque_exacto_completo']+=1
        result[key]['reutilizacion_candidata']=dict(counts)
    out=dict(originales=proof,recursos=result,ppsspp=False,advertencia='Coincidencias de origen, no traducciones insertadas ni autorización automática de reutilización.')
    a.informe.parent.mkdir(parents=True,exist_ok=True);a.informe.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
