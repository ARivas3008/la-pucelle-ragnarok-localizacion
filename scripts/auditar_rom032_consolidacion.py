#!/usr/bin/env python3
"""ROM-032: comprobar el inventario consolidado y las evidencias previas.
No certifica una nueva ISO/EDAT ni sustituye auditar_entrega.py.
"""
import json,hashlib
from pathlib import Path
from auditar_rom030_agregado import audit,require
ROOT=Path(__file__).resolve().parents[1]
def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
    path=ROOT/'docs/seguimiento/informes/ROM-032_consolidacion_conservadora.json'
    proof=json.loads(path.read_text(encoding='utf8'))
    entries=proof['blobs_evidencias']
    require(len(entries)==len({e['ruta'] for e in entries}),'Evidencias repetidas')
    for item in entries:
        target=(ROOT/item['ruta']).resolve()
        require(target.is_relative_to(ROOT) and target.is_file(),'Evidencia ausente: '+item['ruta'])
        require(blob_sha(target.read_bytes())==item['blob'],'Evidencia histórica modificada: '+item['ruta'])
    a,_=audit(ROOT)
    p=proof['contabilidad']
    require(a['historica']==p['integral_historica'],'Base histórica distinta')
    require(a['validas']==p['validas'],'Denominador distinto')
    require(a['agregada_sin_adaptaciones_eboot']==p['agregada_sin_190_eboot'],'Agregada estricta distinta')
    require(a['agregada_con_adaptaciones_eboot_historicas']==p['agregada_con_190_eboot'],'Agregada ampliada distinta')
    require(a['pendientes_con_adaptaciones_eboot_historicas']==p['pendientes']==sum(proof['pendientes'].values()),'Pendientes distintos')
    require(p['agregada_con_190_eboot']+p['pendientes']==p['validas'],'Inventario no cierra')
    st=json.loads((ROOT/'docs/seguimiento/estado.json').read_text(encoding='utf8'))
    require(all(st['rom032'][k]==v for k,v in p.items()),'Estado consolidado distinto')
    require(not proof['candidata_integral'] and not proof['ppsspp'],'Esta evidencia no certifica candidata')
    print(json.dumps({'ok':True,'evidencias':len(entries),'cobertura_agregada':p['agregada_con_190_eboot'],'validas':p['validas'],'pendientes':p['pendientes'],'candidata_integral':False},ensure_ascii=False))
if __name__=='__main__':main()
