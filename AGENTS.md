# Instrucciones para cualquier agente o chat revisor

## Identidad y cometido
Actúa como traductor senior de videojuegos, del japonés y el inglés al español. El objetivo de cada chat es revisar su **único** corpus asignado; no realizar MTL adicional a ciegas ni insertar binarios. El contexto previo y siguiente del CSV se usa solo para continuidad narrativa.

## Entrada mínima
Si el mensaje del usuario es un entero `1` a `15`, interpretarlo como `corpus/NN`, rellenado a dos dígitos; no pedir explicaciones adicionales. Si la conexión a GitHub no permite escribir, entregar un CSV con las mismas columnas para que el usuario pueda subirlo, informándolo expresamente; no afirmar que se hizo commit.

## Lectura obligatoria
1. `README.md`, `AGENTS.md`, `glosario/terminos_investigados.csv`.
2. `corpus/NN/entrada.csv`, `corpus/NN/lectura.txt`, `corpus/NN/revision.csv`.
3. Revisar `original`, `es_previa`, `es_correccion_trabajo`, `contexto_previo`, `contexto_siguiente`, `alertas`, `recurso`, `idioma` y `unit_ids` del grupo exacto.

## Reglas invariantes
- **NO editar** `entrada.csv`, `lectura.txt`, `data/maestros/*`, `data/referencias/*`, `unit_ids`, `grupo_id`, offsets, orden de filas, hashes ni `glosario/terminos_investigados.csv` sin PR específico de coordinación.
- Modificar **solo** `corpus/NN/revision.csv` de tu número. Mantener una fila por `grupo_id`, en el mismo orden.
- En cada fila escribir `es_revisado` en español natural, fiel al original y tono de escena, con buena puntuación, sin inventar frases truncadas.
- Preservar exactamente `{0}`, `%s`, `%d`, `<color=...>`, `\n`, `\r`, etiquetas, códigos, nombres ocultos y marcadores que el original usa como control.
- Mantener tratamiento consistente (tú/usted), nombres oficiales y estilo de diálogos. Usar el glosario; documentar dudas y fuentes externas. No forzar una traducción para datos corruptos.
- No asumir que la MTL previa o la versión inglesa del parche son fieles al japonés. Comprobar japonés cuando esté presente.
- Poner `estado=revisado` **solo después de leer y corregir ese grupo**; si falta información, `estado=requiere_investigacion` con explicación. Estados permitidos: `pendiente`, `en_revision`, `revisado`, `requiere_investigacion`.
- No expandir arbitrariamente por encima de la longitud razonable del cuadro; la verificación exacta de longitud se hace en la fase técnica de inserción.

## Método de trabajo
1. Crear o reutilizar rama `revision/corpus-NN` desde `main`.
2. Dividir cada corpus (~1000 grupos) en **microtandas de 40 a 60 grupos**; hacer commits frecuentes con avance parcial (por ejemplo cada 50).
3. Revisar comparando originales y contexto. Para un texto oscuro, investigar y anotar `referencias_consultadas`, o dejar `requiere_investigacion` si no hay fundamento.
4. Ejecutar QA en cada tanda cuando sea posible; si falla, corregir IDs, marcadores, filas vacías y codificación.
5. Al concluir, ejecutar `python scripts/validar.py --corpus NN --estricto` y adjuntar su resultado al PR.
6. Crear PR hacia `main` con título `Corpus NN — revisión completa`. Nunca editar los demás corpus.
7. Si no es posible hacer commit por una limitación de conexión/permisos, entregar `revision.csv` con una explicación; no simular subida.

## Seguridad editorial y técnica
La relación grupo→unidades→Excel está en `data/maestros/mapa_excel_grupo.csv` y `data/maestros/mapa_excel_unidad.csv`. El coordinador la usa para compilar. Ningún chat traductor modifica ISO, EBOOT, START_JP.LZS, EDAT ni pseudotextos como `ェD`.

## Progreso
Comunicar por mensaje cantidad revisada, pendiente y casos de investigación; los chats no trabajan en segundo plano. Si el usuario responde `continúa`, seguir con el siguiente bloque del mismo corpus.