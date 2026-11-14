# Coordinación central — fusión y preparación de parche

## Cuándo empezar
Después de que cada corpus tenga un PR aprobado y fusionado en `main`. Los 15 corpus suman exactamente 15 016 grupos. La cola `data/preexistentes/509_revision_central.csv` exige una pasada adicional: algunos están revisados textual o contextualmente, pero **no aprobados técnicamente**.

## Protocolo

1. Comprobar en GitHub que las 15 ramas de revisión corresponden a sus carpetas, que ningún PR cambia archivos maestros, y que los estados revisados son verificables.
2. Fusionar cada PR mediante la herramienta de GitHub. Los 15 corpus no se pisan entre sí; si una edición interfiere con otro, no fusionar hasta resolver el conflicto.
3. Ejecutar `python scripts/validar.py --estricto` (15 016 grupos, controles y SHA256).
4. Revisar los 509 grupos de la cola central, incluyendo truncamientos y segmentación ambigua; no marcar aprobados si hay dudas.
5. Ejecutar `python scripts/compilar.py --estricto` y `python scripts/reintegrar_excel.py --estricto`. El Excel nuevo se guarda en `salidas/08_DIALOGOS_REVISION_REINTEGRADA.xlsx` y conserva claves y filas.
6. Ejecutar `python scripts/preparar_preinsercion.py --estricto` para generar manifiesto de 26 258 unidades. Las intervenciones de varias unidades quedan **NO_INSERTAR** hasta segmentar por cuadro/byte.
7. Hacer QA de terminología y etiquetas global entre todos los corpus; evaluar errores de expansión, fuentes japonesas/latinas, CP932, punteros, controladores y formatos de los cuatro DLC por separado.
8. Integración en **copia** de la ISO, base y cuatro DLC. Reconstruir contenedores, comprobar hashes de datos no modificados y hacer pruebas de menú, escenas, combate, guardar/cargar y créditos en PPSSPP.
9. No redistribuir material comercial del juego ni DLC; publicar preferentemente parches diferenciales y herramientas reproducibles cuando el usuario lo solicite y sea apropiado.

## Condiciones de bloqueo

- Cualquier `grupo_id`, `unit_id`, offset, hoja o fila Excel alterado.
- Pérdida/reorden de etiquetas como `{0}`, `%s`, `<color=#...>` o `\n`.
- Cadenas sin fuente clara como `ェD` o identificadores ocultos `??????` sustituidos sin validación de versión/offset.
- Diálogos de grupo completos introducidos en un único hueco binario de tamaño menor sin realineación.
- Errores CP932/glyph, widths o corrupción de descompresión, ausencia de prueba de carga de DLC.

La integración no puede ejecutarse automáticamente al terminar los 15 chats, porque requiere una nueva invocación del coordinador y las pruebas técnicas correspondientes.