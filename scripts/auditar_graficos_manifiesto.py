"""Inventario estructural de los TXP del manifiesto, sin asumir swizzle.

Distingue 16 bancos CLUT y alturas parciales. No extrae ni publica imágenes.
"""
import argparse,csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"parcheador/app/scripts"))
from nis_formats import lzs_decompress,nispack
from auditar_corazon_original import dat_members
from verificar_iso_aislamiento import inventory

def txp_structure(blob):
    if len(blob)<16:raise ValueError("Cabecera TXP truncada")
    w,h,colors,reserved,palette,banks,one,two=struct.unpack_from("<8H",blob)
    if not (0<w<=4096 and 0<h<=4096 and colors in (16,256) and palette==colors and banks in (1,16) and one==two==1):
        raise ValueError("Formato TXP no reconocido")
    bpp=4 if colors==16 else 8
    start=16+colors*banks*4
    if w*h*bpp%8 or len(blob)!=start+w*h*bpp//8:
        raise ValueError("Tamaño TXP discordante")
    return {"ancho":w,"alto":h,"bpp":bpp,"bancos_clut":banks,"colores":colors,
            "bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest(),
            "sha256_clut":hashlib.sha256(blob[16:start]).hexdigest(),
            "altura_multiplo_8":h%8==0,"decodificador_un_banco_bloques_completos_aplicable":banks==1 and h%8==0 and (w*bpp//8)%16==0}

def audit(iso,manifest,sha):
    with Path(iso).open("rb") as f:
        if hashlib.file_digest(f,"sha256").hexdigest()!=sha.lower():raise ValueError("ISO fuente incorrecta")
        files,_=inventory(iso)
        def read(name):
            off,size=files["PSP_GAME/USRDIR/"+name];f.seek(off);return f.read(size)
        bg={x["name"]:x["content"] for x in nispack(read("BGPACK.DAT"))}
        start=dat_members(lzs_decompress(read("START_JP.LZS")))
    with Path(manifest).open(encoding="utf-8-sig",newline="") as f:
        entries=[]
        for row in csv.DictReader(f):
            if row["seccion"]!="00_textos_en_imagenes":continue
            resource=row["recurso"];name=resource.rsplit("/",1)[-1]
            if resource.startswith("ISO_START/"):blob=start[name]
            elif resource.startswith("ISO/PSP_GAME/USRDIR/BGPACK.DAT/"):blob=bg[name]
            else:raise ValueError("Origen gráfico desconocido: "+resource)
            entries.append({"unit_id":int(row["unit_id"]),"grupo_id":int(row["grupo_id"]),
                            "recurso":resource,**txp_structure(blob)})
    if len(entries)!=62 or len({e["unit_id"] for e in entries})!=62:raise ValueError("Manifiesto gráfico inesperado")
    return {"unidades":entries,"archivos_distintos":len({e["recurso"] for e in entries}),
            "certificados_ppsspp":0,"nota":"Solo estructura de originales; no acredita rectángulos, decodificación de bancos múltiples ni traducción gráfica."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso",required=True,type=Path)
    p.add_argument("--manifiesto",required=True,type=Path)
    p.add_argument("--sha-iso",required=True)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();a.out.write_text(json.dumps(audit(a.iso,a.manifiesto,a.sha_iso),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
