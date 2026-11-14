# Contrato para regresar al Excel sin alterar posiciones

- `grupo_id` es clave primaria lógica; `unit_ids` es la descomposición física. No se editan ni reordenan.
- La fuente maestra `data/maestros/03_TODOS_LOS_GRUPOS_15525.csv` se considera inmutable.
- `data/maestros/mapa_excel_grupo.csv` establece pestaña/fila de los 11 018 diálogos en el Excel original.
- `data/maestros/mapa_excel_unidad.csv` establece pestaña/fila de las 26 258 unidades en los seis volúmenes originales.
- Un texto de grupo no debe escribirse automáticamente en varias unidades por longitud proporcional; esa segmentación provisional solo facilita la edición y necesita revisión de cajas/bytes.
- Los 15 corpus editan SOLO `revision.csv` cada uno; el compilador consulta por `grupo_id` y reconstruye el orden maestro.
- `estado=revisado` requiere contenido no vacío, marcadores conservados y validación del grupo; ningún trabajo automático convierte `pendiente` a `revisado`.
- `--estricto` exige completitud de los 15; para preinserción completa el coordinador también debe resolver los 509 grupos previos y QA técnico.
- En exportaciones a Excel, escapar celdas que comiencen por `=`, `+`, `-`, `@` para evitar inyección accidental de fórmulas, sin cambiar el texto lógico guardado.
- Validar el español y su codificación Unicode; que SQLite o CSV acepten UTF-8 NO prueba compatibilidad CP932, fuentes ni punteros.