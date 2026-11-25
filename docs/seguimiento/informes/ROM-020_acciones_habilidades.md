# ROM-020 — Acciones y habilidades, piloto conjunto de cuatro tablas

24/11/2026. Base PR #46, HEAD 17c46b6689a3216d39720f2f21eab29ff3a3319c. ISO original SHA-256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5. Maestro del ZIP local verificado idéntico al remoto tras LF en ROM-019. Revisiones vigentes corpus14 blob b83dcc34fc90c5675edd1b0f6f8ea786afccd4c8; corpus15 c5f876c526d8fc6ba7f08d5fae3a0a132b6342e7; 261 estados revisado, FNV32 local/remoto 958280066 (grupo_id, tab, texto, LF, orden numérico).

## Evidencia A: original
1290/1290 anclas CP932/NFKC de las cinco tablas cotejadas con bytes de ISO. Distribución:
- magic.dat: 538, 2 reservas especiales (23133 Butt Attack con byte 09 fuera de C-string; 23302 Boxes Galore empieza en offset relativo 16 en vez de 18).
- kis.dat: 277, ninguna excepción al perfil.
- ritem.dat: 214, ninguna excepción.
- com.dat: 148, ninguna excepción.
- skill.dat: 113, 2 reservas excepcionales (24106 y 24111, offset relativo 15, no 16; 22 bytes hasta la descripción, fuente exacta con terminador y relleno cero).
No equiparar origen cotejado con español insertado.

## Evidencia B: piloto privado real, acumulado sobre ROM-019
| Tabla | Unidades | Completo | Compacto | Coincide |
|---|---:|---:|---:|---:|
| com.dat | 148 | 137 | 10 | 1 |
| skill.dat | 113 | 91 | 21 | 1 |
| Total nuevo | 261 | 228 | 31 | 2 |

259 sustituciones nuevas en este piloto. Las 513 unidades de char/mapinfo/com/skill se releen con los bytes esperados (456 cambios y 57 coincidencias en conjunto, 44 compactas). Se preservaron todos los bytes no autorizados de DAT respecto a ROM-019; 29/36 miembros intactos respecto a original; 22/22 otros archivos ISO idénticos; 853760611 bytes fuera de los dos intervalos autorizados iguales. Nueve gaiji y 11 alias de puntuación, sin añadir glifos ajenos. Motor completo no ejecutado: reconstrucción independiente del subconjunto necesario y compresor local no solapado.
- com.dat destino SHA256 13ab5db30915df94c9963021482eb631ecc4e6554d5837b683c77c12d4964c47
- skill.dat destino SHA256 622b771d92aad2234284d8af104be96e98c0e349cac228d47970834994eafaed
- DAT SHA256 72effc52a9e2cc01188e0ae9ff717598f8c0775ff2dba54363c6d6d1a4d4a627
- LZS SHA256 f12545d5c8043beaa1a16d12480360f10519a204c972dc6e415d8afd4b23b583; 5106574 bytes, 891043 referencias no solapadas; descompresión reversible.
- ISO piloto SHA256 bbbc2e8beb60229a88551522d729c09d2381fcc5abf41e5b49006f766e4d2aa8.
- LBA fijos, tamaño START LE/BE actualizado.

## Motor
33 anclas nuevas (31 propuestas compactas y 2 reservas excepcionales, fuente exacta y SHA fuente). Preservar prefijo '(' en 24111 tal como figura en original y revisión. Las abreviaturas requieren cotejo editorial y visual. No se modifica el corpus. Tests de fallback y rechazo, integración CI a verificar. No se publica ISO, DAT, fuente ni LZS.

## Cierre pendiente
1. Integrar magic/kis/ritem (1029), resolver dos excepciones magic sin invadir metadatos.
2. Unir piloto nominal, diálogo, scripts, gráficos y cuatro DLC en candidata actual; cotejar todas las unidades con auditor.
3. Probar PPSSPP real. EDAT ausentes y clon GitHub directo bloqueado por DNS local; no ejecutar ni certificar ficticiamente.
La cobertura integral histórica 21805/26258 (83,04%) no cambia por pilotos: no sumar sustituciones sin comparar candidata integral.
