"""Comprueba inventarios contra el checkout actual; no modifica datos."""
from pathlib import Path
import csv,json,collections
R=Path(__file__).resolve().parents[1]; P=R/"docs/seguimiento"
def load(x): return json.loads((P/x).read_text(encoding="utf-8"))
def main():
 t=load("inventario_textos.json");g=load("inventario_graficos.json");s=load("estado.json")
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
 assert len(actual_central)==central["total"]==509
 assert set(actual_central)=={str(x) for x in central["grupo_ids_pendientes"]}
 assert not ids.intersection(actual_central), "Grupo central duplicado"
 assert all(st=="pendiente" and not es.strip() for st,es in actual_central.values())
 assert s["grupos_centrales"]["pendientes"]==len(actual_central)
 assert s["editorial_catalogo"]["pendientes_minimos"]==cnt["requiere_investigacion"]+len(actual_central)
 print(json.dumps({"ok":True,"grupos":len(ids),"unidades":len(m),"graficos":len(expected)}))
if __name__=="__main__":main()
