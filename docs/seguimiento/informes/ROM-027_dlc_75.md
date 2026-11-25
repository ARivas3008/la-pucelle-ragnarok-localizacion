# ROM-027 — Piloto DLC acumulado: 77,27 % (meta 75 % superada)

Fecha 24/11/2026 Lima; base ROM-026 f091b85d2104729c25a7c23264554d98d159fdbc. Verificados los dos workflows ejecutados de esa base: QA inventarios 45546904471 y QA corpus 45546904482, ambos success. Sin modificar main ni corpus. No se publica ningún EDAT, DAT, fuente, ISO ni bytes originales del juego.

## Inventario técnico

| DLC | Fijos previos | TALK nuevos | Total | Inventario |
|---|---:|---:|---:|---:|
| 00 | 1428 | 1039 | 2467 | 3264 |
| 01 | 5 | 85 | 90 | 90 |
| 02 | 19 | 77 | 96 | 99 |
| 03 | 5 | 75 | 80 | 84 |
| Total | 1457 | 1276 | 2733 | 3537 |

2733/3537 = 77,26887192536047 %. Incremento 36,07577 puntos respecto a ROM-026. No sumar al contador histórico integral 21805/26258, puede existir solapamiento. 804 unidades restantes: 393 fijas, 392 TALK, 19 script. El DLC01 alcanza el 100 % del inventario directo, no 100 % de las apariciones físicas, ni certificación visual.

## Evidencia A/B real

Cotejados los cuatro EDAT originales de ROM-024, cuatro pilotos ROM-026 y cuatro nuevos ROM-027. Recuperadas 967 revisiones vigentes (incluyen filas no aplicadas), 926 utilizadas de grupos TALK completos. FNV32 remoto/local 892123174 sobre grupo_id TAB revisión LF orden numérico. La comprobación remota de unidad/grupo fue independiente y confirmó 1276/1276 IDs cubiertos, ningún grupo parcial. Blobs: corpus02 revisión e2c8159472689c48db2700f4bc5de1101767e664, corpus03 revisión d218ec8eb926809e15b0be2068b377ad0873c7ad, central dd01f8481024307c842786b09d705dfe10a2b1fc. No se usa el borrador del ZIP para diálogos. Selección exacta de 622 bloques completos (1277 unidades); excluida opción del grupo 2090 / unidad 2312 (más de 28 glifos en una sola línea). También excluidas anclas parciales, grupos atravesando controles y variables potenciales. 621 bloques finalmente reinsertados, 1789 líneas y 837 páginas de tres líneas como máximo. Cero símbolos de botón/nota musical modificados. Toda edición parte de un inicio de entrada o un reinicio de caja 02/03.

Conservados 2370 registros de índice, 252 opciones, todos los opcodes no textuales y argumentos (salvo reflujo de 02); cada edición fue revertida y el resultado iguala byte a byte la fuente. Añadidos únicamente los dos gaiji F050/F051 (GID 2433/2434, FTD 0x0101) por DLC, sin modificar otros píxeles/mapeos. Se conservan los 1457 campos de ROM-026 y todos los miembros fuera de talk00.dat y las fuentes autorizadas. 114/144 miembros iguales al original, 3.693.698 referencias LZS sin solapamiento. Relectura completa de los cuatro EDAT finales, con verificación de directorio DAT reubicado y cabecera NISPACK salvo longitud del LZS.

## Reproducibilidad

scripts/verificar_piloto_dlc_rom027.py vuelve a validar ROM-026 desde los originales y recompila los 621 bloques exclusivamente desde la revisión actual para comparar el TALK final byte a byte. Se ejecutó localmente con los cuatro originales, cuatro EDAT ROM-026, cuatro EDAT ROM-027 y manifiesto auténtico, usando TSV de revisiones transferidos desde GitHub y cotejados con sus huellas (siete lotes: 114/148/160/160/165/113/107 grupos, FNV32 2568421057/1281967938/2269781004/2455796940/3153182307/3027453127/1337053687). SHA256 del script local 1d5d1b8d2d6f889b033884ca7e41b8161bbce29eaf37b47d12cc84281ef27563. La prueba JSON contiene IDs, SHA de las revisiones, diario y recursos. En un checkout completo se pueden leer directamente los CSV, sin los TSV. El verificador no crea ni publica binarios.

python scripts/verificar_piloto_dlc_rom027.py --originales /ruta/originales --base /ruta/rom026 --pilotos /ruta/rom027 --manifiesto data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv --prueba docs/seguimiento/informes/ROM-027_dlc_piloto.json --prueba-base docs/seguimiento/informes/ROM-026_dlc_piloto.json --repo .

Limitaciones: piloto acumulado local, no ejecución de integracion_total.py ni PPSSPP. Las 252 opciones se conservaron, no se tradujeron en este lote. El reflujo de texto y la nueva paginación requieren validación visual. Los cuatro EDAT candidatos son privados. La CI de este commit debe verificarse antes de declarar éxito.

## Siguiente bloque
Resolver 393 campos fijos (adaptaciones, glifos y reservas), 392 unidades TALK restantes (segmentos parciales, grupos que atraviesan controles, variables y una opción larga), 19 scripts. Inventariar y validar por separado las apariciones reutilizadas. No forzar ni recortar en automático. Conservar el contador físico independiente y completar la candidata integral más PPSSPP real.
