#!/usr/bin/env python3
"""ROM-030: reconciliación de inventario por unit_id. No abre ISO ni certifica juego."""
import argparse,csv,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GOOD={'CAMPO_COINCIDE_REVISION','SCRIPT_INSERTADO','TALK_BLOQUE_INSERTADO','SIN_CAMBIO_COINCIDE_REVISION'}
TABLES={'name.dat','char.dat','mapinfo.dat','com.dat','skill.dat','kis.dat','ritem.dat','magic.dat'}
CONTROL=re.compile(r'%(?:[-+ #0]*\d*(?:\.\d+)?)?[diuoxXfFeEgGcs%]|\{[^}]*\}|<[^>]*>|\\[rn]')
def require(condition,msg):
    if not condition:raise ValueError(msg)
def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def expand(spec):
    out=[]
    for field in spec.split(','):
        a,*b=map(int,field.split('-'));out.extend(range(a,(b[0] if b else a)+1))
    require(len(out)==len(set(out)),'IDs repetidos')
    return set(out)
def distinct(*sets):
    result=set()
    for x in sets:
        require(not result&x,'Pilotos con IDs solapados');result.update(x)
    return result
def audit(root=ROOT):
    root=Path(root);d=root/'docs/seguimiento/informes'
    load=lambda name:json.loads((d/name).read_text(encoding='utf8'))
    rows=csvrows(root/'docs/informes/cobertura_v0.19.0.csv')
    manifest=csvrows(root/'data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv')
    require(len(rows)==len(manifest)==26258,'Tamaño de inventario distinto')
    byid={int(x['unit_id']):x for x in manifest}
    require(len(byid)==26258 and {int(x['unit_id']) for x in rows}==set(byid),'IDs históricos distintos')
    for row in rows:
        m=byid[int(row['unit_id'])]
        require(all(m[k]==row[k] for k in ('grupo_id','recurso','offset','original')),'Ancla histórica distinta: '+row['unit_id'])
    p=load('ROM-026_dlc_piloto.json');q=load('ROM-027_dlc_piloto.json');s=load('ROM-028_dlc_piloto.json');t=load('ROM-029_dlc_piloto.json')
    fixed=distinct(expand(p['ids_previos']),expand(p['ids_nuevos']))
    dialogue=expand(q['ids_dialogos']);extra=set(s['ids_nuevos']);require(len(extra)==len(s['ids_nuevos']),'IDs ROM028 repetidos')
    dlc=distinct(fixed,dialogue,extra,{t['extra_id']})
    require((len(fixed),len(dialogue),len(extra),len(dlc))==(1457,1276,802,3536),'Inventario DLC distinto')
    all_dlc={i for i,m in byid.items() if m['recurso'].startswith('DLC_')}
    require(all_dlc-dlc=={1630} and not dlc-all_dlc,'Cierre DLC no exacto')
    require(all(byid[i]['recurso'].split('/')[-1] in TABLES for i in fixed),'ROM026 no son tablas')
    require(all('/talk' in byid[i]['recurso'] for i in dialogue),'ROM027 no son TALK')
    require(t['non_text']['unit_id']==1630 and byid[1630]['recurso']=='DLC_00/ritem.dat','Exclusión no textual distinta')
    tabs={i for i,m in byid.items() if m['recurso'].startswith('ISO_START/') and m['recurso'].rsplit('/',1)[-1] in TABLES}
    require(len(tabs)==1832,'Inventario tablas ISO distinto')
    historical={int(x['unit_id']) for x in rows if x['estado'] in GOOD-{'SIN_CAMBIO_COINCIDE_REVISION'}}
    same={int(x['unit_id']) for x in rows if x['estado']=='SIN_CAMBIO_COINCIDE_REVISION'}
    solved=(historical|same|dlc|tabs)-{1630}
    require(len(historical)==21805 and len(solved)==22997,'Contabilidad no reproducible')
    missing=set(byid)-solved-{1630}
    eboot=load('ROM-030_eboot_cotejo.json')
    menu=csvrows(root/'parcheador/app/datos/menu_eboot_contextual.csv')
    menu_map={x['original']:x['es'] for x in menu}
    require(len(menu_map)==len(menu),'Original de menú repetido')
    historic_byid={int(x['unit_id']):x for x in rows}
    ids=set();stable=set();changed=set()
    for x in eboot:
        uid=x['unit_id'];r=historic_byid[uid]
        require(uid in missing and uid not in ids,'Rótulo duplicado o fuera de pendientes')
        require(r['recurso'].endswith('EBOOT.BIN') and r['offset']==str(x['offset']) and r['original']==x['original'],'Ancla EBOOT distinta')
        require(r['texto_actual_campo'].strip()==x['adaptacion_historica'],'Adaptación histórica distinta')
        require(menu_map.get(x['original'])==x['adaptacion_actual'],'Adaptación de motor distinta')
        require(CONTROL.findall(x['original'])==CONTROL.findall(x['adaptacion_historica'])==CONTROL.findall(x['adaptacion_actual']),'Variables EBOOT distintas')
        ids.add(uid)
        (stable if x['adaptacion_actual']==x['adaptacion_historica'] else changed).add(uid)
    require(len(ids)==192 and len(stable)==190 and changed=={3774,3778},'Cotejo de EBOOT distinto')
    require(menu_map['Move Speed  Fast']!=menu_map['Move Speed  Blitz'] and menu_map['Text Speed  Fast']!=menu_map['Text Speed  Blitz'],'Ajustes duplicados')
    resources=defaultdict(list)
    for i in sorted(missing):
        resources[byid[i]['recurso']].append(i)
    result={'historica':len(historical),'agregada_sin_adaptaciones_eboot':len(solved),'agregada_con_adaptaciones_eboot_historicas':len(solved|stable),'validas':len(byid)-1,'pendientes':len(missing),'pendientes_con_adaptaciones_eboot_historicas':len(missing-stable),'cotejos_eboot':len(ids),'eboot_relectura_pendiente':sorted(changed),'recursos_pendientes':{k:len(v) for k,v in resources.items()},'candidata_integral':False,'ppsspp':False}
    return result,resources
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--salida',type=Path);a=p.parse_args()
    result,resources=audit(a.repo)
    if a.salida:
        a.salida.mkdir(parents=True,exist_ok=True)
        (a.salida/'pendientes_rom030.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2),encoding='utf8')
        (a.salida/'resumen_rom030.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
