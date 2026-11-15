#!/usr/bin/env python3
"""Audita que una localización NO altere texturas de interfaz por accidente.

No edita ni distribuye ISO/DLC. El informe comprueba bytes y contenedores,
no demuestra ejecución visual correcta en PPSSPP.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"app"/"scripts"))
from construir_parche import Image,members_from_dat
from nis_formats import lzs_decompress,nispack
from fuentes_es import get_tile,unpack_pixels

LZS="/PSP_GAME/USRDIR/START_JP.LZS"
EBOOT="/PSP_GAME/SYSDIR/EBOOT.BIN"
class AuditoriaError(ValueError): pass

def sha(x):return hashlib.sha256(x).hexdigest()
def named_bytes(iso_path,p):
    img=Image(iso_path)
    entries={name:(off,n) for name,off,n,_ in img.records()}
    if p not in entries:raise AuditoriaError(f"No se encontró {p}")
    return img.read(*entries[p])

def from_iso(path):
    return members_from_dat(lzs_decompress(named_bytes(path,LZS)))

def from_dlc(path):
    data=Path(path).read_bytes()
    entries=nispack(data)
    if len(entries)!=1 or entries[0]["name"].lower()!="start_jp.lzs":
        raise AuditoriaError(f"DLC no reconocido: {path}")
    return members_from_dat(lzs_decompress(entries[0]["content"]))

def compare_members(a,b,label,allow_atlas=False):
    problems=[];checks=[]
    for name,old in a.items():
        if name not in b:
            problems.append({"recurso":label+"/"+name,"incidencia":"FALTA_MIEMBRO"})
            continue
        new=bytes(b[name]);old=bytes(old)
        if name.lower().endswith(".txp") and name not in ("FontB0000.txp","FontB0001.txp"):
            if old!=new and not (allow_atlas and name in ("sys3.txp","sys4.txp")):
                problems.append({"recurso":label+"/"+name,"incidencia":"TEXTURA_UI_CAMBIADA_SIN_AUTORIZACION","sha_anterior":sha(old),"sha_nuevo":sha(new)})
            else:
                checks.append({"recurso":label+"/"+name,"integridad":old==new})
    extra=set(b)-set(a)
    if extra:
        problems.append({"recurso":label,"incidencia":"MIEMBROS_EXTRA", "nombres":sorted(extra)})
    for name in ("FontB0000.txp","FontB0001.txp"):
        if name not in a or name not in b:
            problems.append({"recurso":label+"/"+name,"incidencia":"FALTA_FUENTE"})
            continue
        old,new=bytes(a[name]),bytes(b[name])
        if len(old)!=len(new) or old[:1040]!=new[:1040]:
            problems.append({"recurso":label+"/"+name,"incidencia":"CAMBIO_CABECERA_O_CLUT_FONTB"})
        elif old!=new:
            checks.append({"recurso":label+"/"+name,"integridad":True,
                           "nota":"Se modificaron píxeles fontB, cabecera y CLUT preservadas"})
    if "fontB.fnt" in a and "fontB.fnt" in b and all(
        n in a and n in b for n in ("FontB0000.txp","FontB0001.txp")):
        oldmap=bytes(a["fontB.fnt"])
        if len(oldmap)==23232 and len(b["fontB.fnt"])==23232:
            glyphs=struct.unpack("<11616H",oldmap)
            maxi=max(glyphs[1:])
            try:
                oldpix=[unpack_pixels(bytes(a[n])) for n in ("FontB0000.txp","FontB0001.txp")]
                newpix=[unpack_pixels(bytes(b[n])) for n in ("FontB0000.txp","FontB0001.txp")]
                # Píxeles de TODOS los GID originales deben ser bit idénticos.
                modified=[gid for gid in range(1,maxi+1)
                          if get_tile(oldpix,gid)!=get_tile(newpix,gid)]
                if modified:
                    problems.append({"recurso":label+"/fontB","incidencia":"GLIFOS_ORIGINALES_MODIFICADOS",
                                     "muestra_gid":modified[:30],"total":len(modified)})
                else:
                    checks.append({"recurso":label+"/fontB","integridad":True,
                                   "nota":f"{maxi} GID originales preservados"})
            except Exception as exc:
                problems.append({"recurso":label+"/fontB","incidencia":"ERROR_DECODIFICANDO_FONT",
                                 "detalle":str(exc)})
        else:
            problems.append({"recurso":label+"/fontB.fnt","incidencia":"TAMANO_TABLA_CAMBIADO"})
    return checks,problems

def audit(original_iso,patched_iso,dlc_original=None,dlc_patched=None,
          preserve_eboot=False,allow_atlas=False):
    problems=[];checks=[]
    old=from_iso(original_iso);new=from_iso(patched_iso)
    ok,bad=compare_members(old,new,"ISO_START",allow_atlas)
    checks+=ok;problems+=bad
    eb_old=named_bytes(original_iso,EBOOT);eb_new=named_bytes(patched_iso,EBOOT)
    eb_changes=sum(x!=y for x,y in zip(eb_old,eb_new))
    if len(eb_old)!=len(eb_new) or preserve_eboot and eb_old!=eb_new:
        problems.append({"recurso":"EBOOT.BIN","incidencia":"EBOOT_CAMBIADO_EN_PRUEBA_DE_AISLAMIENTO",
                         "bytes_distintos":eb_changes})
    else:
        checks.append({"recurso":"EBOOT.BIN","integridad":eb_old==eb_new,
                       "bytes_distintos":eb_changes})
    if bool(dlc_original)!=bool(dlc_patched):
        raise AuditoriaError("Se deben proporcionar AMBAS carpetas DLC o ninguna")
    if dlc_original:
        for n in range(4):
            fname=f"DL_JP_{n:02d}.EDAT"
            a=from_dlc(Path(dlc_original)/fname)
            b=from_dlc(Path(dlc_patched)/fname)
            ok,bad=compare_members(a,b,f"DLC_{n:02d}",allow_atlas)
            checks+=ok;problems+=bad
    return {
        "ISO_original":str(original_iso),"ISO_parcheada":str(patched_iso),
        "estado":"INVESTIGAR_DIFERENCIAS" if problems else "SIN_CAMBIOS_GRAFICOS_NO_AUTORIZADOS",
        "comprobaciones":checks,"problemas":problems,
        "advertencia":"La comprobación binaria NO demuestra que desaparezcan los glitches en PPSSPP; comparar original y parche con idéntica configuración."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path,required=True)
    p.add_argument("--iso-parcheada",type=Path,required=True)
    p.add_argument("--dlc-original",type=Path)
    p.add_argument("--dlc-parcheado",type=Path)
    p.add_argument("--conservar-eboot",action="store_true")
    p.add_argument("--atlas-ui",action="store_true")
    p.add_argument("--informe",type=Path,required=True)
    args=p.parse_args()
    try:
        obj=audit(args.iso_original,args.iso_parcheada,args.dlc_original,args.dlc_parcheado,
                  args.conservar_eboot,args.atlas_ui)
        args.informe.parent.mkdir(parents=True,exist_ok=True)
        args.informe.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"Estado: {obj['estado']}; problemas={len(obj['problemas'])}; informe={args.informe}")
        return 1 if obj["problemas"] else 0
    except (OSError,ValueError,KeyError,IndexError) as exc:
        print("NO SE PUDO AUDITAR:",exc,file=sys.stderr)
        return 2

if __name__=="__main__":
    sys.exit(main())
