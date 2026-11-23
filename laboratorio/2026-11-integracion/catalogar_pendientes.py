from pathlib import Path
import csv,json,collections,unicodedata
B=Path(__file__).resolve().parent;R=B.parent
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
manifest=rows(B/'fuente/data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv')
groups=collections.defaultdict(list)
for r in manifest:groups[r['grupo_id']].append(r)
central=rows(R/'01_GitHub_main/data/preexistentes/509_revision_central.csv')
reviews=[r for n in range(1,16) for r in rows(B/f'fuente/corpus/{n:02d}/revision.csv')]
canon=lambda s:' '.join(unicodedata.normalize('NFKC',s).split())
byorig=collections.defaultdict(list)
for r in reviews:
 if r['estado']=='revisado':
  original=' '.join(u['original'] for u in groups[r['grupo_id']])
  byorig[canon(original)].append(r)
output=[]
for r in central+[r for r in reviews if r['estado']!='revisado']:
 units=groups[r['grupo_id']]; original=' '.join(u['original'] for u in units)
 matches=byorig.get(canon(original),[])
 output.append(dict(grupo_id=r['grupo_id'],estado=r['estado'],recurso=units[0]['recurso'],original=original,
  es_actual=r['es_revisado'],borrador=units[0]['es_grupo_corregido'],
  coincidencias=[dict(grupo_id=m['grupo_id'],es=m['es_revisado']) for m in matches]))
(B/'informes/pendientes_editoriales.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print('Pendientes',len(output),'con original coincidente',sum(bool(r['coincidencias']) for r in output))
print(json.dumps(output[:30],ensure_ascii=False,indent=1))
