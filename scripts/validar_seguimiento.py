"""Comprueba inventarios contra el checkout actual; no modifica datos."""
from pathlib import Path
import csv,json,collections,hashlib
R=Path(__file__).resolve().parents[1]; P=R/"docs/seguimiento"
def load(x): return json.loads((P/x).read_text(encoding="utf-8"))
def main():
 t=load("inventario_textos.json");g=load("inventario_graficos.json");s=load("estado.json")
 assert "hymt2" not in s, "HY-MT2 no debe figurar como indicador activo"
 assert s["exclusiones_del_alcance"]["hymt2_pendientes"]=="excluido"
 relay=(P/"prompts/SIGUIENTE_RELEVO.md").read_text(encoding="utf-8")
 for token in ("14. OBLIGACIÓN RECURSIVA", "14.8.", "NO TERMINES UNA EJECUCIÓN", "HY-MT2", "Traducción", "Gráficos", "Romhacking", "Betatesting"):
  assert token in relay, f"Relevo incompleto: {token}"
 ids=set();cnt=collections.Counter()
 assert len(t["corpus"])==15
 for c in t["corpus"]:
  with (R/c["ruta_revision"]).open(encoding="utf-8-sig",newline="") as f: actual={x["grupo_id"]:x["estado"] for x in csv.DictReader(f)}
  idx={str(i):st for st,k in [("revisado","revisados"),("requiere_investigacion","requieren_investigacion")] for i in c[k]}
  assert len(idx)==len(c["revisados"])+len(c["requieren_investigacion"]) and idx==actual,c["numero"]
  assert not ids.intersection(idx)
  ids.update(idx);cnt.update(idx.values())
 assert len(ids)==t["resumen_corpus"]["total"]==s["revision_corpus"]["total"]
 assert cnt["revisado"]==s["revision_corpus"]["revisados"] and cnt["requiere_investigacion"]==s["revision_corpus"]["requieren_investigacion"]
 with (R/t["fuentes"]["manifiesto"]).open(encoding="utf-8-sig",newline="") as f: m=list(csv.DictReader(f))
 d={int(x["unit_id"]):x for x in m}; expected={i for i,x in d.items() if x["seccion"]=="00_textos_en_imagenes"}
 assert len(m)==len(d)==26258 and expected=={x["unit_id"] for x in g["unidades"]} and len(expected)==62
 for x in g["unidades"]:
  assert d[x["unit_id"]]["grupo_id"]==str(x["grupo_id"]) and d[x["unit_id"]]["recurso"]==x["recurso"],x["id"]
 central=t["centrales"]
 with (R/central["fuente"]).open(encoding="utf-8-sig",newline="") as fp:
  actual_central={x["grupo_id"]:(x["estado"],x["es_revisado"]) for x in csv.DictReader(fp)}
 raw_central=(R/central["fuente"]).read_bytes()
 central_blob=hashlib.sha1(b"blob "+str(len(raw_central)).encode()+b"\0"+raw_central).hexdigest()
 assert central["sha_revision"]==central_blob, "El inventario no apunta al CSV central vigente"
 assert len(actual_central)==central["total"]==509
 pending={str(x) for x in central["grupo_ids_pendientes"]}
 reviewed={str(x) for x in central["grupo_ids_revisados"]}
 assert len(pending)==central["estados"]["pendiente"] and len(reviewed)==central["estados"]["revisado"]
 assert pending.isdisjoint(reviewed) and set(actual_central)==pending|reviewed
 assert not ids.intersection(actual_central), "Grupo central duplicado"
 assert all(actual_central[i][0]=="pendiente" and not actual_central[i][1].strip() for i in pending)
 assert all(actual_central[i][0]=="revisado" and actual_central[i][1].strip() for i in reviewed)
 assert s["grupos_centrales"]["pendientes"]==len(pending)
 assert s["grupos_centrales"]["revisados"]==len(reviewed)
 assert s["editorial_catalogo"]["pendientes_minimos"]==cnt["requiere_investigacion"]+len(pending)
 assert s["editorial_catalogo"]["revisados_editoriales_conocidos"]==cnt["revisado"]+len(reviewed)
 assert t["resumen_editorial_ampliado"]["pendientes_minimos_conocidos"]==s["editorial_catalogo"]["pendientes_minimos"]
 print(json.dumps({"ok":True,"grupos":len(ids),"unidades":len(m),"graficos":len(expected)}))
if __name__=="__main__":main()
