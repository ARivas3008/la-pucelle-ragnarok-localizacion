# Informe forense de las 14 unidades / 15 referencias — ensayo v0.16.1

**Muestra:** ISO v1.1.2 + cuatro DLC ULJS00244 aportados. **Alcance:** 504 cadenas de evento candidatas, excluyendo `Now Loading`. **Importante:** el hecho de aparecer nombres de personajes no explica el defecto: solo parte de las frases contienen Prier/Alouette, el resto son narraciones, títulos o puntuación.

## Hallazgo (diferenciar puntero, byte y personaje)

Los scripts contienen una tabla `u32 N` + `N × u32` antes del bytecode. En catorce unidades, quince valores señalan el **segundo byte** de un carácter CP932 de la cadena extraída. Este byte no es el inicio de un carácter, de modo que reinterpretar todas estas posiciones como direcciones de texto es incorrecto. **No está demostrada la función de la tabla en el motor PSP.**

| Unit ID | Recurso | Índice(s) de tabla y byte relativo | Resultado v0.16.1 |
|---:|---|---|---|
| 1758 | DLC_00/script00.dat | #2026 +7 | Fase reconstruida; **PPSSPP pendiente** |
| 1759 | DLC_00/script00.dat | #2032 +33, #2034 +35 | Bloqueado: índice no válido al reubicar |
| 3883 | ISO/script02.dat | #67 +13 | Bloqueado: no hay segundo byte equivalente próximo |
| 3897 | ISO/script02.dat | #259 +11 | Bloqueado: no hay segundo byte equivalente próximo |
| 3898 | ISO/script02.dat | #264 +32 | Bloqueado: no hay segundo byte equivalente próximo |
| 3924 | ISO/script04.dat | #319 +30 | Fase reconstruida; **PPSSPP pendiente** |
| 3969 | ISO/script06.dat | #319 +29 | Bloqueado: no hay segundo byte equivalente próximo |
| 3989 | ISO/script09.dat | #22 +35 | Bloqueado: candidato fuera de tolerancia |
| 4007 | ISO/script10.dat | #180 +36 | Bloqueado: no hay segundo byte equivalente próximo |
| 4083 | ISO/script15.dat | #37 +31 | Bloqueado: no hay segundo byte equivalente próximo |
| 4095 | ISO/script16.dat | #39 +10 | Bloqueado: no hay segundo byte equivalente próximo |
| 4098 | ISO/script16.dat | #47 +27 | Bloqueado: no hay segundo byte equivalente próximo |
| 4170 | ISO/script18.dat | #429 +29 | Fase reconstruida; **PPSSPP pendiente** |
| 4220 | ISO/script18.dat | #442 +33 | Bloqueado: candidato fuera de tolerancia |

Estas entradas corresponden al **índice de la tabla del recurso particular**, no a un número global de escena. Los offsets de archivo de las 14 unidades se conservan en `investigacion/v0.15/casos_14.csv` y el manifiesto maestro. En `DLC_00` la unidad 1759 tiene DOS referencias problemáticas.

## Tipos de carácter realmente observados en las 15 referencias

La decodificación estricta de los **dos bytes CP932 completos que rodean cada ancla** revela la siguiente distribución, reproducida de los recursos originales:

| Par CP932 | Carácter | Referencias | Interpretación permitida |
|---|---|---:|---|
| `81 40` | `　` (espacio ideográfico U+3000) | **10** | El índice cae en el segundo byte de un espacio de ancho completo |
| `82 8E`, `82 94` | `ｎ`, `ｔ` (letras de ancho completo) | **2** | Las dos referencias de la unidad 1759, no nombres propios |
| `91 E5` | `大` (kanji) | **1** | Unidad 1758, parte del título narrativo |
| `81 42` | `。` (punto japonés) | **1** | Unidad 3924, puntuación |
| `81 41` | `、` (coma japonesa) | **1** | Unidad 4170, puntuación |

**Conclusión probada:** la mayoría de las referencias problemáticas no se encuentran sobre nombres de personajes. **Conclusión NO probada:** no sabemos si esos bytes representan avance del texto, marcador temporal, inicio de instrucción, efecto de una localización previa u otra semántica interna. No modificar referencias por similitud léxica.

## Error corregido durante la v0.16.1

Prueba real con `estado_unificado_66.csv` y los scripts originales:

| Modo | Inserciones estructurales de script | Anclas bloqueadas | Now Loading |
|---|---:|---:|---|
| v0.14 conservador | 489 | 14 | 1 excluida |
| v0.16 original, modo fase | 159 | se rechazaban 344 candidatas del lote | 1 excluida |
| **v0.16.1, modo fase aislado** | **489 conservadoras + 3 fases experimentales = 492** | **11** | **1 excluida** |

**Causa:** el reubicador v0.16 antiguo pasaba las 14 ediciones de fase junto con las seguras y, si fallaba una referencia de un archivo completo, rechazaba *todas* las ediciones candidatas de ese archivo. La corrección aplica y verifica primero el lote conservador. Después propone cada referencia peligrosa individualmente, aceptándola solo si el archivo **completo** sigue siendo reversible. Mantiene los motivos de rechazo individualizados.

Se pasó una segunda prueba de escritura y reconstrucción **sobre copia nueva de la ISO y los cuatro DLC** (no distribuida): se releyeron 28 entradas ISO, los 32 miembros de SCRIPTPACK, los 36 del START y 36 por DLC; EBOOT y miembros `talk` no cambiaron. FontB se amplió en los cinco paquetes. Esta es una prueba **binaria**, no jugabilidad.

## Cómo completar los 11 pendientes de forma válida

1. En el original, identificar la escena exacta y localizar en RAM el bloque `script*.dat` de cada caso.
2. Obtener la dirección RAM real del cuerpo y el PC de la instrucción que consume cada entrada de tabla. **No convertir un offset de archivo directamente en dirección RAM.**
3. Registrar lectura efectiva, contenido de registros MIPS, valor anterior/posterior, cuadro y duración. Determinar si es puntero de bytecode, cursor, límite, índice de evento o tiempo.
4. Si es puntero al bytecode, buscar límites de instrucciones reales. Si es tiempo, registrar la fórmula de sincronización. Si no se conoce, mantener `ANCLA_FASE_BLOQUEADA`.
5. Probar copia A (original), B (hipótesis al inicio del carácter), C (fase conservada), y comparar eventos, render, voces, textos y cuadros.
6. Incorporar una prueba de regresión por `unit_id` (incluidas **ambas** entradas de 1759). Actualizar hashes y evidencias PPSSPP antes de marcar `APLICADO_VERIFICADO_PPSSPP`.

No intentar «arreglar» las referencias traduciendo nombres de personajes de otro modo ni insertando bytes de relleno no sustentados: la mayoría de casos no tratan nombres y cambiar el original para hacer caber la traducción puede introducir fallos graves.

**Fuentes técnicas versionadas:** `v0.12/reubicador_anclas_v012.py`, `v0.14/integrar_scripts_v014.py`, `v0.15/auditar_anclas.py`, `docs/TRAZADO_PPSSPP_ANCLAS.md`. **Advertencia permanente:** 492/503 cadenas sometidas a inserción estructural **no** representan 492/26 258 unidades aprobadas del juego completo.
