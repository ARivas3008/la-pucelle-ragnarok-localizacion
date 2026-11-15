# Estado editorial observado en `main` — 15 de noviembre de 2026

**Método:** se leyeron directamente los quince `corpus/NN/revision.csv` de `main`, se analizaron sus filas CSV conservando campos entrecomillados y se contabilizó la columna `estado`. Esta tabla es una **instantánea**; ninguna fila se cambió para obtenerla.

| Corpus | Grupos | `revisado` | `requiere_investigacion` |
|---:|---:|---:|---:|
| 01 | 1001 | 1001 | 0 |
| 02 | 1058 | 972 | 86 |
| 03 | 949 | 949 | 0 |
| 04 | 997 | 997 | 0 |
| 05 | 1000 | 987 | 13 |
| 06 | 968 | 947 | 21 |
| 07 | 974 | 938 | 36 |
| 08 | 1006 | 1000 | 6 |
| 09 | 1058 | 1013 | 45 |
| 10 | 1000 | 991 | 9 |
| 11 | 1000 | 928 | 72 |
| 12 | 1003 | 1003 | 0 |
| 13 | 947 | 947 | 0 |
| 14 | 1055 | 1055 | 0 |
| 15 | 1000 | 999 | 1 |
| **Total** | **15 016** | **14 727 (98,1 %)** | **289 (1,9 %)** |

Otros **509** grupos centrales se gestionan fuera de los quince CSV, en `data/preexistentes/509_revision_central.csv`. Estos 509 no se suman a la columna `revisado` ni se consideran pendientes editoriales automáticamente sin revisar sus estados individuales.

## Por qué no es un 100 % de la localización

- `revisado` es una **marca de la hoja editorial**, no prueba de que el texto se haya reinsertado ni de que el revisor haya validado todos los matices del japonés en tiempo de juego.
- Hay **289 grupos** que requieren investigación; sus estados no deben elevarse automáticamente ni sustituirse por texto MTL.
- El manifiesto físico es de **26 258 unidades**, no de 15 016: un grupo puede contener varias unidades y los recursos gráficos no siguen la misma regla binaria.
- El informe de scripts **492/503** es solo una subfamilia, con 3 reubicaciones experimentales sin PPSSPP y 11 casos aún bloqueados. No sumar contadores de ámbitos superpuestos.
- Quedan conflictos de campos fijos, EBOOT, texturas, fuentes/anchuras, escenas introductorias, continuaciones talk y QA visual de ISO y cuatro DLC.

## Próxima puerta de calidad reproducible

1. Resolver los 289 grupos con investigación y auditar los 509 centrales contra fuente/contexto.
2. Construir los CSV revisados y validar ID, fuente, controles, ancho y SHA del maestro.
3. Ejecutar la fase conservadora y registrar por `unit_id` el resultado técnico sobre ISO + DLC en copia.
4. Instrumentar las 15 referencias CP932 antes de aprobar los 3 ensayos; corregir 11 casos por semántica real.
5. Registrar prueba en PPSSPP de cada escena, menús, HUD, guardado, DLC y finales. Solo entonces computar el porcentaje final.

Este documento describe estados públicos observables, no modifica el trabajo de los traductores.
