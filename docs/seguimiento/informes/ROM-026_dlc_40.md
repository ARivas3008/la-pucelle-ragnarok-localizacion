# ROM-026 — Meta 40% de inventario DLC superada en piloto privado

Fecha 24/11/2026 (Lima), base ROM-025 3511d585ec9bd78065e90806f398e3365ce78b18. Los seis workflows de la base concluyeron success. No se modifica main, corpus ni los originales. No se publican EDAT, DAT, fuentes ni ISO comerciales.

## Resultado de ejecución local
Se recuperaron 1633 revisiones vigentes de los corpus 01/02/13/14/15 (estado revisado), con cotejo FNV32 de grupos/texto UTF-8 ordenados: 365 sin diferencias respecto a entrada, 1036027082; lotes de diferencias 347/218/183/278/242, huellas 3231129543/3677670142/2398503952/3164169540/1845780451. Se excluyeron 26 unidades del piloto anterior ya incluidas en ese conjunto. De 1607 candidatas nuevas se verificaron 1243: 1242 sustituciones completas y una coincidencia original (ID 1277). Las otras 364 no se escribieron: 350 por exceso de bytes, 10 por glifos fuera del subconjunto actual, 4 por capacidad no autenticada. 3.537 unidades DLC del manifiesto original.

| Recurso DLC00 | Nuevo | Acumulado | Total |
|---|---:|---:|---:|
| char.dat | 0 | 156 | 156 |
| com.dat | 115 | 115 | 150 |
| kis.dat | 218 | 218 | 281 |
| magic.dat | 344 | 347 | 489 |
| mapinfo.dat | 93 | 93 | 100 |
| name.dat | 178 | 204 | 292 |
| ritem.dat | 220 | 220 | 272 |
| skill.dat | 75 | 75 | 81 |
| Total DLC00 | 1243 | 1428 | 1850 menos 29 exclusivos otros DLC |
| DLC01/02/03 | 0 | 29 | 29 |
| Total | 1243 | 1457 | 3537 (inventario completo, incluye TALK/script) |

Nota: campos fijos totales 1850. Campos fijos DLC00 1821. 1457/3537 = 41,1931%, frente a 214/3537 = 6,0503%. 1456 cambios físicos (41,1648%), 1443 completos, 13 compactos de ROM-024, 1 coincidencia original. No se suman estos IDs a la auditoría integral histórica 21805/26258.

## Evidencia binaria
Con los cuatro EDAT originales autenticados ROM-024 y el piloto anterior, se escribió un nuevo piloto en los campos exactos, sin cambios al conjunto de fuentes anterior. Se recompuso DAT y se recomprimieron los cuatro LZS con el compresor independiente local; los cuatro fueron releídos y descomprimidos sin solapamiento. Se volvió a ejecutar el verificador autónomo scripts/verificar_piloto_dlc_rom026.py sobre los cuatro originales y cuatro EDAT resultantes y el manifiesto auténtico: 1457 IDs únicos, 124 prefijos preservados, 335389 bytes exteriores de tablas intactos, 118/144 miembros iguales, 3683573 referencias LZS no solapadas, cero diferencias de origen NFKC con solo strip exterior. Los índices DAT y NISPACK salvo longitud del LZS permanecen iguales. Se comprobaron los glifos asignados en la fuente de cada EDAT. SHA256 del verificador local b0c3d94fe03d9fab5d793cb619e8fba9c32e649c935e25547e383835aa769d23. La prueba JSON conserva rangos exactos de IDs y SHA256 de cada EDAT y tabla; digest de IDs ordenados con LF e7c47150e6493537ff5fee647847125efcf35066904715c02a0acb79fbbecf78.

Para verificar el piloto privado (archivos resultado con sufijo _rom026.EDAT):
python scripts/verificar_piloto_dlc_rom026.py --originales /ruta/ULJS00244 --pilotos /ruta/piloto --manifiesto data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv --prueba docs/seguimiento/informes/ROM-026_dlc_piloto.json

El motor completo de integracion_total.py no se ejecutó debido al checkout incompleto y DNS local. El piloto local usa las mismas reglas de capacidad/codificación del motor y el subconjunto de fuentes ROM-024. Los 1243 nuevos campos no requieren variantes compactas nuevas. El verificador no acredita PPSSPP ni aprobación visual. Sigue pendiente reconstrucción de una candidata integral actual y ejecución C.

## Siguiente bloque
Quedan 2080 unidades de este piloto: 393 campos fijos, 1668 TALK y 19 scripts. De los 393 campos fijos, 364 tienen el diagnóstico anterior y 29 no estaban en el conjunto recuperado (revisión central). Priorizar fuente completa, adaptación de los campos excedentes y segmentación TALK. Mantener separados inventario físico y apariciones reutilizadas.
