# CENT-002 — Primer lote de 20 grupos centrales pendientes
**Base examinada:** main `d2f3b0ced36173c8535c1ef3fcfb0124aacb1cf0`; antes de editar, verificar HEAD actual y no retroceder cambios.
**IDs estables del lote:** 16, 211, 212, 266, 544, 546, 548, 550, 552, 554, 556, 558, 560, 561, 562, 563, 564, 565, 566, 567.
**Objetivo acotado:** revisar desde cero estos 20 de los 509 grupos centrales, todos `pendiente` en el corte del 23-11-2026, y registrar revisión individual, capacidad física y excepciones sin afirmar inserción automática.

## Fuentes obligatorias
- `data/preexistentes/509_revision_central.csv`, con 509 filas.
- `data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv`; por cada grupo localizar unidad, recurso `DLC_00/char.dat`, `com.dat` o `kis.dat`, offset y original auténtico.
- `glosario/terminos_investigados.csv`: `魔王プリエ`, `Hな本`, `山ごもり`, `ソダーツ`, `アガール`.
- `docs/INTEGRACION.md`, `docs/COBERTURA.md` y `docs/seguimiento/estado.json`; catálogo técnico y su estado físico.
- Si las fuentes no resuelven el contexto, consultar bytes originales y archivos de texto del recurso sin confundir una entrada del maestro con prueba de juego.

## Pasos de ejecución
1. Verificar que los 20 IDs siguen pendientes y que no hay duplicados con los quince corpus. Comparar japonés de la unidad, propuesta previa y terminología.
2. Distinguir título propio (16), acción/resultado en `com.dat` (211, 212 y 266), y familias de habilidades `ソダーツ` y `アガール` (544–567), cuidando PV/PE/ATQ/DEF/INT/VEL/PREC/RES y la diferencia semántica entre aumentar y crecer.
3. Aprobar exclusivamente los campos fieles y naturales; si se desconoce la longitud, anotar que la aprobación **solo es editorial**, no física. Cualquier ambigüedad queda pendiente con causa concreta.
4. Modificar únicamente las columnas de revisión editorial y referencias de las filas indicadas dentro de `data/preexistentes/509_revision_central.csv`, preservando IDs, filas y orden. No modificar el manifiesto ni el original.
5. Actualizar `docs/seguimiento/inventario_textos.json` (lista y estados de los 509), `estado.json`, informe por ID y cualquier prueba afectada. Recalcular cantidades; no contar una unidad como insertada hasta cotejar ISO real.

## QA y evidencias
Ejecutar `python scripts/validar.py`, `python scripts/validar_seguimiento.py` y las pruebas de integridad del motor relevantes para campos fijos. Adjuntar diff, hashes/commit, IDs resueltos y los que siguen pendientes. Al aparecer un estado nuevo, ampliar el validador para aceptar los estados permitidos y comprobar la concordancia exacta con el CSV.

**Terminado:** revisión individual demostrada de los 20, sin cambios de original ni IDs, QA superado y contadores actualizados. **Bloqueo:** si falta el contexto, capacidad o bytes originales, dejar el registro pendiente y redactar una tarea técnica concreta; continuar con los demás. Tras este lote preparar uno nuevo con IDs reales no tratados.
