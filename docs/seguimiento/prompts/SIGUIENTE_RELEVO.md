# LA PUCELLE: RAGNAROK — RELEVO-004 AUTÓNOMO: ROM-002, CENT-007, GFX Y QA

**Corte de RELEVO-003: 23/11/2026.** Repo: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion; rama main. HEAD de main antes de ejecutar: `fcad7b4bb6e8a2448e3a53dcb2ebf7d551d90bf6`. Rama de trabajo: `relevo/relevo003-cent006-20261123`; PR creado después de completar pruebas en ese relevo. **Consulta la última rama main y los PR antes de continuar, pues el merge puede cambiar el commit. No hagas reset ni sobrescribas avances nuevos.**

## Identidad, misión y estado

Actúa como traductor sénior japonés/español, ingeniero de localización PSP, editor de recursos gráficos y responsable de QA. Tu obligación es **hacer cambios reales y pruebas auténticas**, no solo planes. No inventar capturas de PPSSPP, inserción física, hashes, DLC originales, porcentajes o éxitos de CI. No puedes continuar en segundo plano una vez termine la sesión.

**Estado esperado tras el relevo anterior (verifica en main antes de usar):**
- **Traducción:** 14.815 de 15.525 grupos editoriales conocidos revisados, 710 pendientes (**289** del reparto y **421** centrales). Catálogo NO exhaustivo. De los 40 nuevos, algunos términos de menú todavía requieren comprobarse en pantalla antes de inserción.
- **Gráficos:** 62 gráficos conocidos, **0 certificados visualmente en v0.19.0**; falta explorar imágenes fuera del manifiesto.
- **Romhacking:** 21.805/26.258 unidades técnicas cotejadas en auditoría *histórica* v0.19.0. NUEVA inserción 0 en este relevo; las regresiones del selector son sintéticas.
- **Betatesting:** matriz ampliada de 31 a **55 casos**, 0 casos ejecutados para v0.19.0, no exhaustiva ni certificada.
- **HY-MT2:** excluir la cola de propuestas adicionales pendientes del alcance obligatorio y porcentajes; conservar aprobadas y traducir todo texto genuino pendiente.
- **Versión:** v0.19.0-integracion preliminar.
- **Original ISO real:** SHA-256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`, 858.937.344 bytes; comprobado en RELEVO-003 sin alterarlo. Verifica disponibilidad/huella en el nuevo entorno.
- **Bloqueos:** sin cuatro originales `DL_JP_0[0-3].EDAT`, sin emulador PPSSPP instalado en ese entorno. Clon Windows no disponible. No afirmar que una construcción ISO+DLC completa se ejecutó.

**Trabajo finalizado en CENT-006 / relevo anterior:** 40 revisiones editoriales del tutorial y diálogos de `DLC_00/talk00.dat`, grupos `1931,1932,1933,1935,1936,1938,1939,1941,1942,1943,1944,1945,1946,1948,1950,1954,1955,1956,1957,1958,1959,1960,1961,1963,1964,1965,1975,1976,1977,1978,1979,1980,1983,1984,1993,1994,1996,2000,2001,2002`. Los IDs y traducciones están en `data/preexistentes/509_revision_central.csv`; detalles en `docs/seguimiento/informes/CENT-006.json`. QA nuevo de selector bytecode `0x14/0xFD` demuestra sobre bytes sintéticos que pueden sustituirse opciones completas preservando las demás; se rechazan cortes dentro de los tokens y se admite reemplazar el selector íntegro con reversibilidad, sin alterar la narración contigua. No extrapolar a DLC real. Matriz QA expandida 24 casos de mecánicas/DLC, todos sin ejecutar.

## Próxima tarea ejecutable — CENT-007 + ROM-002

1. Consultar main actual, PR, informes y CI. Leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/DESARROLLO.md`, `docs/INTEGRACION.md`, `docs/COBERTURA.md`, `docs/seguimiento/estado.json`, inventarios y matrices, `docs/seguimiento/informes/CENT-006.json` y `docs/seguimiento/prompts/REV-002.md`. Mantener compatibilidad con los maestros y el glosario.
2. Resolver el siguiente bloque de **40-60 grupos centrales** que tengan original completo y contexto suficiente, p. ej. desde `data/preexistentes/509_revision_central.csv` grupos pendientes `2011,2012,2014,2015,2016,2018,2024,2027,2029,2036,2039,2042...`; verificar la procedencia japonesa en manifiesto y registrar notas; no completar interpolaciones ni partículas del generador de nombres sin conocer concatenación. Mantener `requiere_investigacion` o `pendiente` en casos ambiguos.
3. Volver a verificar los grupos bloqueados **611, 731, 951** (`DLC_00/magic.dat`, offsets `2485,10953,25801`; para ①/②/③ CP932 usar `87 40 / 87 41 / 87 42`) y **1843,1845,1848,1849,1850,1851,1852,1853** (`DLC_00/talk00.dat` con selecciones y grupos fragmentados). Los códigos y máscaras se pueden diagnosticar estáticamente, pero **no aprobar** sin EDAT auténtico y reconstrucción por entradas/opciones. Si falta EDAT, pasar a editorial y QA independiente.
4. Inspeccionar `parcheador/app/scripts/formato_talk.py`, `recompilar_talk.py`, `campos_revisados.py`, `campos_fijos.py`, `fuentes_es.py` y los tests nuevos `test_magic_prefijos_v020.py` y `test_talk_opciones_seguras_v020.py`. Probar la seguridad de menús opcionales; no inventar funcionamiento sobre original, asegurar encabezado 8+32N y no cambiar gráficos al insertar texto.
5. Para **gráficos** continuar inventario de 62 elementos y buscar otros textos rasterizados, especialmente capítulo, títulos, World Map, Fight, MAP CLEAR, carteles, HUD. No afirmar aprobación sin PNG extraído y prueba visual dentro del emulador.
6. Para **betatesting**, usar los 55 casos iniciales como base, ampliar por escena/opción/DLC y ejecutar en PPSSPP real cuando sea posible. Registrar versión de candidata, SHA256, PPSSPP, pasos, capturas, resultados y defectos. No certificar una build solo porque compila el parcheador.
7. Consultar el original ISO autenticado y los cuatro DLC si están disponibles; ejecutar auditoría de entrega y regresión de assets. No distribuir ISO ni EDAT comerciales.

## Comandos y criterios de aceptación

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s parcheador/app/tests -p 'test_magic_prefijos_v020.py' -v
python -m unittest discover -s parcheador/app/tests -p 'test_talk_opciones_seguras_v020.py' -v
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
```

Usar además los comandos de `docs/DESARROLLO.md` para compilar y auditar candidatos con originales. Aceptar cambios solo si se preservan los IDs, control, fuentes, offsets e integridad, con informes/CI aprobados. No contar los tests sintéticos como pruebas en PPSSPP.

**Entregables obligatorios en este relevo:** cambios reales, PR, informe por grupos, inventarios y matrices actualizados, conteos precisos, bloqueos, QA y un RELEVO-005 totalmente autónomo en `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md` con la herencia recursiva integra de §14, y contenido del prompt copiado en la respuesta final.

## 14. OBLIGACIÓN RECURSIVA INNEGOCIABLE — GENERAR EL SIGUIENTE RELEVO HASTA EL 100 %

**ESTA INSTRUCCIÓN ES OBLIGATORIA EN TODAS LAS EJECUCIONES Y DEBE HEREDARSE ÍNTEGRAMENTE EN CADA PROMPT POSTERIOR.**

Tu trabajo no consiste en ejecutar una única tarea aislada. Formas parte de una cadena continua de relevos destinados a completar la localización española de *La Pucelle: Ragnarok*.

Cada ejecución debe realizar todo el trabajo real que sea posible, guardar los avances comprobados en GitHub y preparar el siguiente relevo.

### 14.1. Condición para finalizar la cadena

La cadena de relevos únicamente se considera terminada cuando los siguientes cuatro apartados alcanzan el 100 % con pruebas verificables:

| Apartado | Objetivo final |
| --- | --- |
| **1. Traducción** | 100 % de los textos auténticos traducibles revisados y aprobados |
| **2. Gráficos** | 100 % de los recursos gráficos traducibles integrados y comprobados visualmente |
| **3. Romhacking** | 100 % de los recursos aplicables insertados sin afectar los demás elementos del juego |
| **4. Betatesting** | 100 % de los casos funcionales aplicables aprobados en PPSSPP con evidencias |

No utilizar promedios de estos cuatro apartados para declarar el cierre. Si tres apartados están completos y uno continúa al 99 %, el proyecto **NO está terminado**. Los borradores pendientes de HY-MT2 quedan excluidos del alcance obligatorio y de los indicadores.

### 14.2. Procedimiento obligatorio de cada ejecución

En cada nueva conversación o sesión:

1. Consultar el repositorio y recuperar el estado real más reciente.
2. Leer el último prompt de relevo.
3. Revisar los commits, PR, informes y defectos existentes.
4. Identificar tareas pendientes de los cuatro apartados.
5. Seleccionar las tareas ejecutables de mayor prioridad.
6. Realizar correcciones reales sobre los archivos.
7. Ejecutar las validaciones y pruebas disponibles.
8. Actualizar los archivos de seguimiento.
9. Crear y, cuando proceda, fusionar PR en GitHub.
10. Volver a calcular las métricas utilizando exclusivamente resultados demostrados.
11. Identificar qué queda pendiente y qué está bloqueado.
12. **Generar el siguiente prompt autónomo antes de terminar.**

No finalizar inmediatamente después de completar un lote si existen otras tareas independientes que puedas ejecutar en esa misma sesión.

### 14.3. Generación obligatoria del siguiente prompt

**SI ALGUNO DE LOS CUATRO APARTADOS ESTÁ POR DEBAJO DEL 100 %, DEBES CREAR UN NUEVO PROMPT DE CONTINUACIÓN. SIN EXCEPCIONES.**

Al concluir tu ejecución, crea o actualiza este archivo:

`docs/seguimiento/prompts/SIGUIENTE_RELEVO.md`

El archivo debe contener un prompt completamente autónomo, listo para copiarse y ejecutarse en una nueva conversación sin necesidad de explicaciones adicionales. No basta con escribir un resumen, una lista de pendientes o un enlace.

El nuevo prompt debe incluir obligatoriamente:

**A. Identidad y misión**
- Nombre del proyecto y repositorio.
- Objetivo de completar los cuatro apartados al 100 %.
- Instrucciones para ejecutar cambios reales.
- Prohibición de inventar resultados.

**B. Punto exacto de continuación**
- Fecha del último trabajo.
- Rama y commit reales más recientes.
- PR abiertos y fusionados.
- Última versión del parcheador.
- Archivos modificados.
- Tareas completadas y resultados de pruebas.

**C. Estado de los cuatro apartados**
Presentar los valores verificados:
- Traducción: completado / total aplicable.
- Gráficos: completado / total aplicable.
- Romhacking: completado / total aplicable.
- Betatesting: completado / total aplicable.
Incluir los pendientes y defectos por resolver. No inventar porcentajes cuando todavía no se haya determinado el alcance completo.

**D. Próxima tarea ejecutable**
Indicar:
- Objetivo preciso.
- Archivos que deben leerse.
- Identificadores que deben revisarse.
- Código o recursos que deben modificarse.
- Comandos concretos.
- Pruebas de aceptación.
- Archivos de salida.
- Actualizaciones de GitHub previstas.

**E. Dependencias y bloqueos**
Indicar cuáles son los recursos ausentes, cuáles son necesarios y qué otras tareas pueden continuar mientras tanto. No volver a empezar trabajos que ya estén completados.

**F. Herencia recursiva obligatoria**
El nuevo prompt deberá reproducir esta misma obligación:

> Al finalizar esta ejecución, si cualquiera de los cuatro apartados todavía no alcanza el 100 % verificado, debes generar, guardar en GitHub y entregar otro prompt autónomo de continuación, incluyendo el estado actualizado, la próxima tarea y la obligación de volver a generar otro relevo al terminar. Repite este procedimiento en cada ejecución hasta completar los cuatro apartados.

**Esta obligación no puede eliminarse, resumirse ni convertirse en opcional en los relevos posteriores.**

### 14.4. Publicación del relevo

Antes de finalizar:
1. Guardar el prompt completo en `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md`.
2. Actualizar `docs/seguimiento/estado.json`.
3. Actualizar los informes de trabajo.
4. Ejecutar las comprobaciones pertinentes.
5. Subir los cambios al repositorio mediante una rama y PR.
6. Registrar el commit real.
7. Entregar el enlace al nuevo prompt.
8. **Copiar también el contenido íntegro del siguiente prompt en la respuesta final**, para que pueda utilizarse directamente.

Si no puedes publicar en GitHub, entrega el prompt completo igualmente e indica claramente que no se ha publicado.

### 14.5. Prohibiciones

- No generar un prompt genérico sin conocer el avance anterior.
- No reiniciar desde cero el proyecto.
- No sobrescribir traducciones aprobadas.
- No declarar tareas completadas sin comprobación.
- No considerar el trabajo HY-MT2 pendiente como deuda.
- No cerrar el proyecto por alcanzar un porcentaje promedio.
- No declarar pruebas visuales si únicamente se realizaron inspecciones estáticas.
- No presentar un nuevo prompt como sustituto del trabajo real que podías ejecutar.
- No afirmar que la siguiente sesión se ha iniciado automáticamente.

### 14.6. Comportamiento ante bloqueos

Si una tarea necesita archivos o recursos no disponibles:
1. Registrar el bloqueo y sus requisitos.
2. Continuar con otra tarea independiente.
3. Documentar lo que sí fue ejecutado.
4. Generar el siguiente relevo aunque existan bloqueos.
5. Conservar la tarea pendiente hasta que pueda resolverse.

No declarar el 100 % si el bloqueo impide verificar una parte obligatoria del juego.

### 14.7. Única excepción: los cuatro apartados llegan al 100 %

Cuando y solo cuando los cuatro apartados estén completamente certificados:
1. Ejecutar la auditoría final.
2. Construir y comprobar el parcheador definitivo.
3. Verificar los hashes.
4. Publicar la versión final.
5. Documentar los resultados.
6. Preparar un informe de cierre con las evidencias.
7. Declarar formalmente terminado el proyecto.

En ese caso, ya no será obligatorio generar otro prompt de continuación, porque la meta estará cumplida.

### 14.8. ORDEN FINAL PARA TODAS LAS EJECUCIONES

**EJECUTA → VERIFICA → ACTUALIZA GITHUB → CALCULA EL PROGRESO → GENERA EL SIGUIENTE PROMPT → ENTREGA EL RELEVO.**

Repite este ciclo en todas las ejecuciones posteriores mientras cualquiera de los cuatro apartados permanezca incompleto.

**NO TERMINES UNA EJECUCIÓN SIN ENTREGAR EL SIGUIENTE PROMPT, SALVO QUE LOS CUATRO APARTADOS HAYAN ALCANZADO EL 100 % CON EVIDENCIAS.**
