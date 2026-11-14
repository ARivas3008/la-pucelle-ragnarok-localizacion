#!/usr/bin/env python3
"""Evita que un PR de revisión cambie los archivos de cualquier otro corpus."""
import argparse,subprocess,re,sys
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--head',required=True);a=p.parse_args()
m=re.fullmatch(r'revision/corpus-(\d{2})',a.head)
if not m:
    print('PR de coordinación: sin restricción de carpeta corpus. QA principal sigue vigente.');sys.exit(0)
code=m.group(1)
if not 1<=int(code)<=15:sys.exit('Número de corpus fuera de rango')
changed=subprocess.check_output(['git','diff','--name-only',f'{a.base}...HEAD'],text=True).splitlines()
allowed=f'corpus/{code}/revision.csv'
wrong=[f for f in changed if f!=allowed]
if wrong or not changed:
    print('ERROR: un PR de corpus debe modificar exactamente',allowed,'y nada más. Cambios:',changed)
    sys.exit(1)
print('Cambios autorizados:',changed)
