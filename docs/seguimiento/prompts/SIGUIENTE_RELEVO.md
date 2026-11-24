# LA PUCELLE: RAGNAROK — RELEVO-008 AUTÓNOMO: CENT-011, ROM-005, GFX-005 Y QA

**Corte:** 23/11/2026. Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama principal `main`. HEAD comprobado antes de ejecutar RELEVO-007: `5019159c98f10a1d2475954dc63752644f018941`. Rama de RELEVO-007 `relevo/relevo007-cent010-rom004-20261123`, PR verificado #34 https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/pull/34; commit editor CENT-010 `c555962bf649876ba6b259d2690fe268fc48f5f6`. **Al comenzar consulta main y PR: el commit cambiará tras el merge; nunca sobreescribas avances posteriores.**

## Identidad, misión y evidencias

Actúa como traductor sénior japonés/inglés→español, ingeniero de PSP (MIPS, CP932, NISPACK, LZS, talk bytecode), localizador de texturas TXP/CLUT y responsable de QA. Realiza **trabajo real, código, traducción y pruebas**, no recomendaciones genéricas. Publica mediante rama y PR, verifica Actions y reporta fallos. No inventes certificados ni hashes; no ejecutas tareas en segundo plano. Distingue **A: ISO o DLC comerciales originales autenticados**, **B: test sintético/CI**, **C: escena de candidata parcheada realmente ejecutada en PPSSPP**.

## Estado actualizado tras RELEVO-007 (revalidar en GitHub)

- **Traducción:** **15.003 / 15.525 grupos editoriales conocidos** revisados = 96,64 % del catálogo provisional; **522 pendientes conocidos** (289 de corpus, 233 centrales). El inventario sigue NO exhaustivo, por tanto NO se considera progreso global de la traducción al 100 %. CENT-010 aprobó editorialmente 53 grupos `6071, 6075, 6076, 6079, 6080, 6081, 6082, 6083, 6084, 6085, 6086, 6087, 6088, 6089, 6090, 6091, 6092, 6093, 6094, 6095, 6096, 6097, 6098, 6099, 6101, 6103, 6104, 6105, 6106, 6107, 6108, 6110, 9669, 9670, 9672, 9673, 9674, 9675, 9676, 9677, 9678, 9679, 9680, 9681, 9682, 9683, 9684, 9685, 9686, 9687, 9689, 9690, 9691`, principalmente hermana Olive y habitantes Eringa, comparando con el manifiesto original y contexto; **sin nueva inserción física ni visualización de estos 53 grupos**. Informe `docs/seguimiento/informes/CENT-010.json`. Los fragmentos `6072,6073,6074,6077,6078,6100,6102,6109,9639,9640,9655,9656,9659,9661,9663,9664,9671,9688` no se han aprobado porque la secuencia aparece incompleta o necesita reconstrucción.
- **Gráficos:** 62 unidades conocidas, **0 certificadas visualmente en v0.19.0**. Ocho TXP de BGPACK catalogadas como candidatos; `wbg00.txp` y `wmap.txp` llevan inscripciones artísticas que **no se han mapeado inequívocamente** a topónimos de interfaz. GFX-004 preserva ambos sin modificar; ver `docs/seguimiento/informes/GFX-004_dictamen_inscripciones.json`. No incrementar el total por candidatos no confirmados ni cerrar todo como gráfico terminado.
- **Romhacking:** auditoría *histórica* `v0.19.0-integracion`: **21.805 / 26.258 unidades técnicas**, 83,04 %. **Cero nuevas inserciones físicas** en RELEVO-007. Se añadió `scripts/verificar_bgpack_parche.py`, verificador fail-closed del paquete gráfico: por defecto exige identidad completa, y las autorizaciones por textura requieren SHA fuente, longitud/layout de NISPACK y preservación estricta de cabecera y CLUT; solo permite cambios en índices de píxeles TXP autorizados. Tests sintéticos `scripts/test_verificar_bgpack_parche.py`. Informe `docs/seguimiento/informes/ROM-004_proteccion_bgpack.json`. Necesita cotejo real original/candidata posterior; el CI nunca demuestra gameplay.
- **Betatesting:** matriz **70 casos catalogados**, **0 probados en PPSSPP v0.19.0**, matriz no exhaustiva. Cuatro nuevos casos para Olive, Eringa y conservación binaria de BGPACK.
- **Fuente A:** ISO de 858.937.344 bytes autenticada SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5` en RELEVO-007, sin modificar original; BGPACK SHA256 de referencia `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`. No se encontraron `DL_JP_00.EDAT`…`DL_JP_03.EDAT` comerciales auténticos ni PPSSPP instalado en el entorno anterior.
- **Símbolo 4268:** `￥` U+FFE5 y CP932 `81 8F` corresponde al corazón del fontB original (índice175 / GID99). Es evidencia A de atlas original, no evidencia C de versión traducida. No normalizar a U+00A5 `¥`.
- **HY-MT2:** borradores adicionales pendientes excluidos de todas las deudas y denominadores. Conservar traducciones aprobadas y completar textos reales restantes.

## Próxima tarea, rutas y criterios de aceptación

1. Verifica HEAD, PR y Actions, y lee `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/{COBERTURA,INTEGRACION,DESARROLLO,ERRORES_CONOCIDOS}.md`, `docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}`, `docs/seguimiento/informes/{CENT-010.json,GFX-004_dictamen_inscripciones.json,ROM-004_proteccion_bgpack.json}`, `data/preexistentes/509_revision_central.csv`, `data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv`, `glosario/terminos_investigados.csv`, `docs/seguimiento/prompts/REV-002.md`. Verifica hashes y la disponibilidad de fuente comercial sin publicarla.
2. **CENT-011:** elegir 40–60 textos auténticos pendientes con contexto suficiente y fuente original completa; entre `9639–9740` y `15135–15210` abundan secuencias repartidas entre unidades, así que no inventes la continuación de oraciones incompletas. Investigar `6072–6074,6077–6078,6100,6102,6109` según unidades físicas y voces, sin elevar a revisados mientras no estén resueltas. Mantener bloqueado `DLC_00/talk00.dat` grupos 2048+2049 (3 unidades, un mismo enunciado), 1843/1845/1848–1853 (menús) y `DLC_00/magic.dat` 611/731/951 (prefijos) hasta cotejo contra DLC auténticos. No tratar las partículas del generador en `corpus/02` como palabras aisladas.
3. **ROM-005:** ejecutar `scripts/verificar_bgpack_parche.py` con ISO original y candidata si se pueden generar: por defecto todo BGPACK debe ser byte idéntico; si se autoriza traducción gráfica real, proporcionar JSON `{"nombre.txp":"sha256_fuente"}` con SHA auténtica y comprobar que solo píxeles cambian y cabecera/CLUT/layout no. Verificar en juego con PPSSPP después. Realizar tests sintéticos de seguridad; no publicar ISO, DLC ni texturas originales. Comprobar también integridad de glyphs, datos de script y `￥` de 4268.
4. **GFX-005:** identificar gráficamente el contenido de `wbg00.txp` y `wmap.txp` con reglas explícitas de localización y topónimos comprobados en pantalla. Si son letras decorativas o escritura ficticia sin significado demostrable, conservar arte y no contarlas como deuda de texto traducible. No declarar aprobadas las 62 sin prueba C v0.19.0.
5. **Betatesting:** ampliar los 70 casos a matriz exhaustiva por escena/ruta. Obtener PPSSPP y DLC originales cuando sea posible; ejecutar candidata y documentar versión, hash, partida, pasos, vídeos/capturas, defectos y retests. En particular probar homenaje de Olive, groserías/humor eringa, tildes, ancho de cuadros, World Map y glifo corazón.

## Comandos de ejecución

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python -m unittest discover -s scripts -p 'test_verificar_bgpack_parche.py' -v
python scripts/verificar_bgpack_parche.py --iso-original /ruta/ISO_ORIGINAL.iso --iso-candidata /ruta/ISO_TRADUCIDA.iso --hash-original-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --out /ruta/privada/qa_bgpack.json
```

Estos comandos comprueban el motor de forma estática y sintética donde no se necesite ROM, pero **no certifican** un parche en PPSSPP. No declares un porcentaje definitivo de traducción sin inventario exhaustivo ni cuentes la compilación Windows como prueba C.

## Entrega y obligación recursiva

Antes de terminar RELEVO-008: realizar cambios reales, añadir informe, actualizar CSV, indicadores y matrices, ejecutar QA, solucionar errores, publicar PR y reemplazar `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md` por **RELEVO-009** totalmente autónomo y la sección 14 siguiente íntegra. Copiar el contenido íntegro del nuevo prompt en la respuesta final. Si no hay acceso GitHub, entregar contenido y declarar que no se publicó. Solo cuando los cuatro apartados estén certificados al 100 % podrá declararse el final.

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
