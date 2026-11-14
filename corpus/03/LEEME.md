# Corpus 03 — revisión contextual y editorial

Incluye **949 grupos**. El orden del archivo es deliberadamente por recurso y desplazamiento para mantener cerca las escenas.

- `entrada.csv`: **INMUTABLE**. Incluye originales, traducción de trabajo, vecinos, identificadores, hash y mapeo Excel.
- `lectura.txt`: vista legible para contrastar las intervenciones.
- `revision.csv`: **ÚNICO ARCHIVO EDITABLE** de este corpus. No cambiar número ni orden de registros.

Para revisar un grupo, escribir el español final en `es_revisado`, indicar `estado=revisado` y explicar en `notas_editoriales` las decisiones no triviales. Si hay un problema irresoluble, usar `estado=requiere_investigacion`, dejar nota y no declarar terminada la tarea.

Ejecutar `python scripts/validar.py --corpus 03 --estricto` y abrir PR `revision/corpus-03` solo cuando el script lo permita. No alterar otras carpetas `corpus/`.

Conserva `{0}`, `%s`, etiquetas `<...>`, secuencias `\n`, marcadores de control y nombres DLC tal como aparecen en el original. No cambies IDs, recursos, offsets ni hashes.
