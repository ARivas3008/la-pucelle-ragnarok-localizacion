"""ROM-012: gate exacto para igualar el porcentaje editorial en integración binaria.

Evalúa SOLO informes de auditoría sobre ISO y cuatro EDAT auténticos. No
certifica PPSSPP, experiencia narrativa ni gráficos: son pruebas independientes.
"""
import argparse,json,sys
from pathlib import Path
ISO_BASE_SHA='4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5'
STATES=('TALK_BLOQUE_INSERTADO','SCRIPT_INSERTADO','CAMPO_COINCIDE_REVISION')
class CoberturaInvalida(ValueError):pass

def comprobar(cobertura,estado):
 editorial=estado['editorial_catalogo']
 grupos=int(editorial['revisados_editoriales_conocidos'])
 total_grupos=int(editorial['total_grupos_conocidos'])
 total=int(cobertura['unidades_total'])
 verificados=int(cobertura['unidades_insertadas_verificadas'])
 meta=(total*grupos+total_grupos-1)//total_grupos
 if cobertura.get('alcance')!='ISO_Y_CUATRO_DLC':
  raise CoberturaInvalida('Se exige auditoría completa ISO + cuatro DLC')
 if int(cobertura.get('unidades_alcance_auditado',-1))!=total:
  raise CoberturaInvalida('El denominador auditado no equivale al manifiesto')
 if cobertura.get('unidades_no_evaluadas_por_ausencia_dlc')!=0:
  raise CoberturaInvalida('Hay unidades DLC sin comprobar')
 original=cobertura.get('originales_autenticados') or {}
 if original.get('iso_sha256')!=ISO_BASE_SHA:
  raise CoberturaInvalida('La ISO original no coincide con la autenticada')
 hashes=original.get('dlc_sha256') or {}
 if set(hashes)!={f'DL_JP_{n:02d}.EDAT' for n in range(4)} or any(
  len(v)!=64 or any(x not in '0123456789abcdef' for x in v.lower()) for v in hashes.values()):
  raise CoberturaInvalida('Faltan hashes verificables de los cuatro EDAT')
 states=cobertura.get('estados') or {}
 if sum(int(x) for x in states.values())!=total or sum(int(states.get(s,0)) for s in STATES)!=verificados:
  raise CoberturaInvalida('Incoherencia entre categorías y numerador verificado')
 if len(cobertura.get('sha256',''))!=64 or not cobertura.get('recursos_compilados_releidos'):
  raise CoberturaInvalida('Falta SHA de candidata o diarios de recursos releídos')
 if verificados<meta:
  raise CoberturaInvalida(f'Faltan {meta-verificados} unidades: {verificados}/{total}; meta {meta}')
 return dict(resultado='UMBRAL_BINARIO_ALCANZADO',grupos_editoriales=f'{grupos}/{total_grupos}',
             unidades_verificadas=verificados,unidades_total=total,
             objetivo_minimo=meta,porcentaje_tecnico=round(100*verificados/total,2),
             nota='Solo cobertura binaria del manifiesto; no certificación visual ni funcional')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--cobertura',type=Path,required=True,help='cobertura_insercion_real.json de ISO y cuatro DLC')
 p.add_argument('--estado',type=Path,default=Path(__file__).resolve().parents[1]/'docs/seguimiento/estado.json')
 args=p.parse_args()
 try:
  result=comprobar(json.loads(args.cobertura.read_text(encoding='utf8')),
                    json.loads(args.estado.read_text(encoding='utf8')))
 except (CoberturaInvalida,KeyError,ValueError) as e:
  print('UMBRAL_NO_ALCANZADO: '+str(e),file=sys.stderr);return 2
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':sys.exit(main())
