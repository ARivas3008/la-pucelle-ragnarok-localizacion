from view import *
import csv,zipfile,io,collections
z=zipfile.ZipFile('/mnt/data/LaPucelle_Proyecto_15_Corpus_GitHub_ChatGPT.zip'); rows=list(csv.DictReader(io.TextIOWrapper(z.open(next(x for x in z.namelist() if '04_MANIFIESTO' in x)),encoding='utf-8-sig')))
_,orig=inventory(SRC,Path('/tmp/rc38/orig'));_,cur=inventory(B,D)
a={k+'/'+n:v for k,m in orig.items() for n,v in m.items() if n.startswith('script')}; b={k+'/'+n:v for k,m in cur.items() for n,v in m.items() if n.startswith('script')};a.update({'ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+k:v for k,v in nis(read(SRC,SP)).items() if k.startswith('script')});b.update({'ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/'+k:v for k,v in nis(read(B,SP)).items() if k.startswith('script')}); found=[]
for r in rows:
 k=r['recurso'];o=int(r['offset']);
 if k not in a:continue
 raw=a[k];x=raw[o:].split(b'\0')[0]
 if not x or len(x)>64 or raw[o-2:o]!=bytes([50,len(x)+1]):continue
 pat=bytes([50,len(x)+1])+x+b'\0';matches=list(re.finditer(re.escape(pat),b[k]));
 if not matches:continue
 t=decode(x)
 if not re.search(r'[a-zA-Z]{2,}|[\u3040-\u9fff]',t):continue
 found.append(dict(resource=k,offset_source=o,original=t,target=r['es_grupo_corregido'],matches=[m.start()+2 for m in matches],raw=x.hex(),gid=r['grupo_id']))
(P/'text_candidates.json').write_text(json.dumps(found,ensure_ascii=False,indent=2));print(len(found));
for r in found:print(r['resource'].split('/')[-1],r['original'],'=>',r['target'],r['matches'])
