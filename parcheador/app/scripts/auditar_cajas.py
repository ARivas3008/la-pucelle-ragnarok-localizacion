"""Audita almacenamiento de intervenciones 0x00 0x01 del original PSP.

Es un informe sobre bytes y bits de cadenas en archivo, NO mide ancho de
caracteres en píxeles ni da permiso para desplazar tablas de punteros.
"""
import argparse,csv,collections,json
from pathlib import Path
from construir_parche import Image,members_from_dat,match_source,cadenas_dialogo,DATA
from nis_formats import nispack,lzs_decompress

def run(iso_path,outdir):
 image=Image(Path(iso_path))
 recs={p:(off,length) for p,off,length,_ in image.records()}
 s=nispack(image.read(*recs['/PSP_GAME/USRDIR/SCRIPTPACK.DAT']))
 start=members_from_dat(lzs_decompress(image.read(*recs['/PSP_GAME/USRDIR/START_JP.LZS'])))
 buffers={**{f'ISO_START/{k}':v for k,v in start.items()},**{f'ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/{f["name"]}':bytearray(f['content']) for f in s}}
 manifest=list(csv.DictReader(DATA.open(encoding='utf-8-sig',newline='')))
 chains,ids,orphans=cadenas_dialogo(manifest,buffers)
 rows=[]
 for c in chains:
  caps=[]
  for u in c:
   style,b=match_source(buffers[u['recurso']],int(u['offset']),u['original'])
   caps.append(len(b) if b is not None else None)
  rows.append({'recurso':c[0]['recurso'],'unit_ids':','.join(x['unit_id'] for x in c),
               'grupo_ids':','.join(dict.fromkeys(x['grupo_id'] for x in c)),
               'lineas_del_script':len(c),'bytes_por_linea':','.join(str(n) for n in caps),
               'bytes_totales':sum(n or 0 for n in caps),
               'bits_totales':sum(n or 0 for n in caps)*8,
               'origen_verificado':all(n is not None for n in caps)})
 outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
 with (outdir/'capacidad_dialogos.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
 resumen={'intervenciones':len(chains),'distribucion_lineas':dict(collections.Counter(len(x) for x in chains)),
          'unidades_encadenadas':len(ids),'unidades_en_cadenas_incompletas':len(orphans),
          'nota':'Bits de almacenamiento, no cantidad de caracteres/pixeles visibles. No se amplían punteros.'}
 (outdir/'capacidad_dialogos.json').write_text(json.dumps(resumen,indent=2,ensure_ascii=False),encoding='utf-8')
 return resumen

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--iso',required=True);parser.add_argument('--salida',required=True)
 a=parser.parse_args();print(json.dumps(run(a.iso,a.salida),indent=2,ensure_ascii=False))
