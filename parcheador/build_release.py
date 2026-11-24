#!/usr/bin/env python3
"""Build reproducible GUI patcher from repository source (no game assets)."""
from __future__ import annotations
import argparse, io, os, subprocess, shutil, tarfile, gzip, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MASTER=ROOT.parent/'data'/'maestros'/'04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv'
VERSION='0.19.0-integracion'


def make_resources(manifest:Path, packer:Path, dest:Path):
    if not manifest.is_file() or not packer.is_file():
        raise FileNotFoundError('Falta el manifiesto o el ejecutable de compresión Windows')
    entries={}
    for path in sorted((ROOT/'app').rglob('*')):
        if not path.is_file():continue
        rel=path.relative_to(ROOT/'app').as_posix()
        if path.suffix in ('.pyc','.pyo') or '__pycache__' in rel.split('/'):
            continue
        if rel.startswith('tests/') or rel in ('datos/mapa_26258_unidades.csv','scripts/nis_lzs_pack','scripts/nis_lzs_pack.exe'):
            continue
        entries[rel]=path.read_bytes()
    # v0.16 incorpora el motor de eventos sin romper la CLI histórica v0.13.
    # La estructura relativa es necesaria para los imports de v0.14.
    # El reubicador importa construir_parche.py desde app/scripts; este
    # importa segmentacion, atlas_ui_es, subtitulos_script e integracion_v013.
    # Empaquetar SOLO cuatro módulos impedía ejecutar v0.16 en Windows.
    # Duplicamos el conjunto completo de scripts bajo app/scripts.
    for old_rel in sorted(k for k in entries if k.startswith('scripts/') and k.endswith('.py')):
        entries['app/'+old_rel]=entries[old_rel]
    for rel in ('investigacion/v0.10/contenedores.py',
                'investigacion/v0.10/iso_reubicar.py',
                'investigacion/v0.12/reubicador_anclas_v012.py',
                'investigacion/v0.14/integrar_scripts_v014.py'):
        entries[rel]=(ROOT/rel).read_bytes()
    # Informe editorial de 4507 unidades, sin binarios comerciales.
    entries['datos/estado_unificado_66.csv']=(ROOT/'informes/estado_unificado_66.csv').read_bytes()
    entries['datos/mapa_26258_unidades.csv']=manifest.read_bytes()
    entries['datos/CENT017_NAME_DAT_17_NO_INVENTARIADOS.csv']=(ROOT.parent/'data/control/CENT017_NAME_DAT_17_NO_INVENTARIADOS.csv').read_bytes()
    editorial = {}
    for n in range(1,16):
        rel=f'corpus/{n:02d}/revision.csv'
        payload=(ROOT.parent/rel).read_bytes()
        entries[rel]=payload
        editorial[rel]=hashlib.sha256(payload).hexdigest()
    rel='data/preexistentes/509_revision_central.csv'
    payload=(ROOT.parent/rel).read_bytes()
    entries[rel]=payload
    editorial[rel]=hashlib.sha256(payload).hexdigest()
    entries['datos/fuentes_editoriales.json']=json.dumps({
        'version':VERSION, 'snapshot_main':None,
        'sha256':editorial},ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')
    entries['scripts/nis_lzs_pack.exe']=packer.read_bytes()
    with dest.open('wb') as outf:
        # Buffered compression is deterministic: fixed timestamps and names.
        with gzip.GzipFile(fileobj=outf,mode='wb',mtime=0,filename='') as gz:
            with tarfile.open(fileobj=gz,mode='w|') as tf:
                for rel,data in sorted(entries.items()):
                    t=tarfile.TarInfo(rel);t.size=len(data);t.mtime=0;t.mode=0o644
                    t.uid=t.gid=0;t.uname=t.gname=''
                    tf.addfile(t,io.BytesIO(data))
    return {'version':VERSION,'assets':len(entries),
            'manifest_sha256':hashlib.sha256(entries['datos/mapa_26258_unidades.csv']).hexdigest(),
            'packed_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--packer-exe',type=Path,required=True,help='nis_lzs_pack.exe compilado desde scripts/nis_lzs_pack.cpp')
    a.add_argument('--manifest',type=Path,default=MASTER)
    a.add_argument('--out',type=Path,default=ROOT/'dist'/f'LaPucelle_Parcheador_ES_GUI_v{VERSION}.exe')
    a.add_argument('--no-go',action='store_true',help='Sólo crea resources.tar.gz')
    x=a.parse_args()
    x.out.parent.mkdir(parents=True,exist_ok=True)
    print(make_resources(x.manifest,x.packer_exe,ROOT/'resources.tar.gz'))
    if not x.no_go:
        env=os.environ.copy();env['GOOS']='windows';env['GOARCH']='amd64';env['CGO_ENABLED']='0'
        subprocess.run(['go','build','-trimpath','-ldflags=-s -w -H=windowsgui','-o',str(x.out),'main.go'],cwd=ROOT,env=env,check=True)
        print('EXE SHA256',hashlib.sha256(x.out.read_bytes()).hexdigest(),x.out)

if __name__=='__main__':main()
