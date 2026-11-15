# Método reutilizable para localizar videojuegos (rama independiente)

Esta rama convierte las lecciones del proyecto La Pucelle: Ragnarok en una **rúbrica replicable, auditable y paralelizable**. No sustituye ni modifica los 15 corpus ni los binarios del juego. Está pensada para empezar un proyecto nuevo y evitar repetir meses de investigación manual.

## Cómo usarlo

1. Lee [RÚBRICA DE LOCALIZACIÓN](RUBRICA_LOCALIZACION.md) para el proceso completo y sus puertas de calidad.
2. Lee [MAPA DE ARCHIVOS Y DECISIONES](MAPA_FORMATOS_Y_DECISIONES.md) para escoger la estrategia por recurso.
3. Consulta [PLANTILLAS Y BRANCHING](PLANTILLAS_Y_ROLES.md) para repartir el trabajo sin colisiones.
4. Usa los scripts para lotear unidades extraídas y comprobar **bytes reales**, no el número de letras.

~~~bash
python metodologia/scripts/planificar_corpus.py --unidades unidades_extraidas.csv --salida lotes --grupos-por-lote 50
python metodologia/scripts/verificar_presupuesto.py --unidades lote_revisable.csv --revisiones revisiones_por_unidad.csv --gaiji-json mapeo_fuentes.json --salida informe_bytes.csv
python -m unittest discover -s metodologia/tests -v
~~~

El primer comando requiere CSV de unidades con unit_id, recurso, grupo_id, original y, preferiblemente, escena, hablante, offset, tipo y capacidad_bytes. La extracción de binarios es **específica de cada juego**: no se presume que todos usen NISPACK o CP932. Se propone el adaptador inicial en [MAPA DE ARCHIVOS Y DECISIONES](MAPA_FORMATOS_Y_DECISIONES.md).

El segundo comando exige revisiones por **unidad** con unit_id, es_revisado y estado. Si la traducción se revisa por grupo, se debe resolver explícitamente grupo→unidad antes de usarlo: **no redistribuir automáticamente por longitud proporcional**.

## Ejemplo histórico aplicado al proyecto

- 26 258 unidades físicas localizadas y 15 525 grupos editoriales.
- 15 016 grupos asignados a 15 corpus independientes, otros 509 en coordinación.
- Los corpus mantienen originales, hash y variables inmutables; se revisa en ramas separadas.
- Luego se ejecuta QA editorial y reconstrucción conservadora por formato.
- Investigación de capacidad: byte fijo + NUL / texto u8 en script / índice dinámico de talk / atlas gráfico / cadenas EBOOT.
- Las reubicaciones de bytecode de v0.12–v0.15 requieren validación en PPSSPP; **no convierten automáticamente una MTL en parche jugable**.

## Estrategia para reducir trabajo redundante

Congelar formatos y glosario antes de distribuir, automatizar extracción, lotes y tests, emitir informes por unidad con IDs estables, priorizar cadenas que bloquean el arranque y el HUD, y ejecutar compilaciones de humo desde la primera semana de trabajo. La traducción masiva se hace en paralelo; la aprobación de seguridad binaria se centraliza. 

**No se incluyen textos del juego comercial ni recursos originales en las plantillas.**
