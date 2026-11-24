"""Defensa adicional para candidatas ISO de tamaño y distribución FIJOS.

No admite reubicaciones ni crecimiento; para ellos usar verificar_iso_aislamiento
y auditar explícitamente las nuevas regiones. No es una prueba de PPSSPP.
"""
from pathlib import Path
import argparse,hashlib,json
from verificar_iso_aislamiento import inventory,verify,ISOIsolationError,BLOCK

def volume_info(path):
    path=Path(path)
    with path.open("rb") as f:
        f.seek(16*BLOCK)
        v=f.read(BLOCK)
    if v[:7]!=b"\x01CD001\x01":raise ISOIsolationError("PVD inválido")
    declared=int.from_bytes(v[80:84],"little")
    if declared!=int.from_bytes(v[84:88],"big"):
        raise ISOIsolationError("PVD: tamaño de volumen dual endian discordante")
    physical=path.stat().st_size//BLOCK
    return {"sectores_declarados_pvd":declared,"sectores_fisicos":physical,
            "diferencia_sectores":physical-declared,
            "pvd_sha256":hashlib.sha256(v).hexdigest()}

def compare_range(a,b,start,end):
    a.seek(start);b.seek(start)
    while start<end:
        n=min(1024*1024,end-start)
        x,y=a.read(n),b.read(n)
        if len(x)!=n or len(y)!=n or x!=y:
            raise ISOIsolationError(f"Bytes no autorizados distintos en intervalo {start}:{start+n}")
        start+=n

def verify_fixed(original,candidate,allowed=None,expected_sha=None):
    original,candidate=Path(original),Path(candidate)
    allowed={} if allowed is None else allowed
    if not isinstance(allowed,dict):raise ISOIsolationError("Autorizaciones inválidas")
    old,od=inventory(original);new,nd=inventory(candidate)
    if original.stat().st_size!=candidate.stat().st_size or old!=new or od!=nd:
        raise ISOIsolationError("Layout no fijo: usar auditoría para reubicación")
    report=verify(original,candidate,allowed,expected_sha)
    info=volume_info(original);target=volume_info(candidate)
    if info!=target:raise ISOIsolationError("PVD modificado")
    authorized=sorted((old[name][0],sum(old[name])) for name in allowed)
    cursor=0;checked=0
    with original.open("rb") as a,candidate.open("rb") as b:
        for start,end in authorized:
            compare_range(a,b,cursor,start);checked+=start-cursor;cursor=end
        compare_range(a,b,cursor,original.stat().st_size)
        checked+=original.stat().st_size-cursor
    return {**report,"modo":"layout_fijo","volumen_original":info,
            "bytes_fuera_de_recursos_autorizados_cotejados":checked,
            "nota":"Incluye PVD, tablas, directorios y huecos físicos. No acepta crecimiento ni reubicación; contenido interno autorizado y PPSSPP requieren QA independiente."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",required=True,type=Path)
    p.add_argument("--iso-candidata",required=True,type=Path)
    p.add_argument("--hash-original-iso",required=True)
    p.add_argument("--allow-json",type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    perms=json.loads(a.allow_json.read_text(encoding="utf-8")) if a.allow_json else {}
    r=verify_fixed(a.iso_original,a.iso_candidata,perms,a.hash_original_iso)
    out=json.dumps(r,ensure_ascii=False,indent=2)+"\n"
    if a.out:a.out.write_text(out,encoding="utf-8")
    else:print(out)
if __name__=="__main__":main()
