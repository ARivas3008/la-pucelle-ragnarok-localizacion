# LA PUCELLE: RAGNAROK — RELEVO-006 AUTÓNOMO: CENT-009, GFX-003, ROM Y BETATESTING

**Corte comprobado: 23/11/2026.** Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama principal: `main`. HEAD al comenzar RELEVO-005: `ce8445fc58d0e1e871239238e6b653db0a200941`. Rama del trabajo actual: `relevo/relevo005-cent008-gfx002-20261123`. Commit real con las 44 revisiones: `d1bc11d408c60209aba52054148798722feb947e`; trabajo técnico posterior en esta misma rama, PR #32: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/pull/32. **Consultar HEAD actual de main y PR al iniciar RELEVO-006**: el merge posterior cambia SHA; jamás borrar avances ni reiniciar desde cero.

## Misión y reglas de evidencia

Eres traductor experto japonés/inglés→español, ingeniero de romhacking de PSP CP932/LZS/NISPACK, diseñador localizador de recursos TXP/CLUT y responsable de QA. **Realiza trabajo real y verificable**, actualiza archivos y publica PR tras CI. No inventes capturas, implementación, bytes originales que no tienes, resultados de tests ni porcentajes. Mantén separadas evidencias **A (original comercial auténtico)**, **B (fixture/CI)** y **C (juego real ejecutado en PPSSPP)**. No afirmar trabajo autónomo en segundo plano.

## Estado a reconfirmar en GitHub

- **Traducción:** **14.907 / 15.525 grupos editoriales conocidos** revisados, **618 pendientes**: 289 distribuidos en los corpus y 329 centrales. Catálogo todavía no exhaustivo. CENT-008 revisó 44 grupos de `ISO/PSP_GAME/USRDIR/SCRIPTPACK.DAT/talk01_jp.dat`, IDs `4256, 4257, 4258, 4259, 4260, 4261, 4262, 4263, 4264, 4265, 4266, 4267, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285, 4286, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297, 4298, 4299, 4300`, conservando `eri`, Eringa, Grand Champignon y Kinoko Jiru. Grupo **4268** con `¥` y grupos **4250–4255** del idioma eringa ficticio siguen pendientes por criterios de extracción/transliteración. Todo nuevo contenido editorial queda **sin inserción y sin comprobación de pantalla** hasta verificarlo aparte.
- **Gráficos:** 62 unidades textuales del manifiesto y **0 certificadas visualmente para v0.19.0**. Ocho TXP de BGPACK auténtico se **decodificaron e inspeccionaron** con swizzle 16x8, CLUT RGBA y 4/8bpp. Seis parecen ilustrativas/decorativas; **`wbg00.txp` y `wmap.txp` contienen inscripciones estilizadas** de posible escritura ficticia, cuyo tratamiento de localización requiere decisión. No contar esas dos ni las otras seis como textos traducibles confirmados, y no sumar ninguna como certificada PPSSPP. Informes `docs/seguimiento/informes/GFX-001_bgpack_original.json` y `GFX-002_txp_original.json`; decoder `scripts/inspeccionar_txp_bgpack.py`.
- **Romhacking:** **21.805 / 26.258 unidades técnicas** verificadas en una **auditoría histórica v0.19.0**, no avance nuevo físico de este relevo. Se añadió código reversible de TXP para original, y tests B de 4/8bpp. El parcheador preliminar sigue `v0.19.0-integracion`. Nunca modificar offsets, retratos, paletas ni regiones no autorizadas.
- **Betatesting:** matriz aumentada de 55 a **63 casos**, **0 ejecutados en PPSSPP para v0.19.0**; no exhaustiva. Se añadieron ocho casos de textura, ninguno constituye captura.
- **ISO original** aportada por usuario, 858.937.344 bytes, SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`, autenticada nuevamente en RELEVO-005. BGPACK SHA256 `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`. La ISO **nunca fue modificada** en este relevo.
- **Bloqueos** al cerrar RELEVO-005: no se encontraron los cuatro EDAT originales `DL_JP_00.EDAT`…`DL_JP_03.EDAT` ni ejecutable PPSSPP instalado. Verificar disponibilidad de nuevo.
- **HY-MT2:** excluir completamente los borradores adicionales pendientes del trabajo obligatorio y de los denominadores; conservar traducciones aprobadas y continuar revisión de textos auténticos restantes.

## Tareas concretas del siguiente relevo

1. Comprobar GitHub HEAD, PR y QA; leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/{COBERTURA,ERRORES_CONOCIDOS,INTEGRACION,DESARROLLO}.md`, `docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}`, `docs/seguimiento/informes/{CENT-008.json,GFX-002_txp_original.json}`, glosario, maestro japonés, `data/preexistentes/509_revision_central.csv` y `docs/seguimiento/prompts/REV-002.md`. No reabrir los 44 grupos ya aprobados sin evidencia nueva.
2. **CENT-009:** evaluar los 6 fragmentos de lengua eringa 4250–4255 y el extraño marcador `¥` del 4268 con unidades `5059,5060`. Para `DLC_00/talk00.dat`, grupos **2048+2049** forman una sola frase japonesa con unidades **2219,2220,2221** y offsets históricos **33797,33835,33873**; hay propuesta editorial en informe CENT-008, pero **no aprobar ni dividir arbitrariamente** sin reconstrucción de bytecode y EDAT auténtico. Investigar también los bloques 6040–6110, 9630–9740, 15135–15210: son ingleses de escenas, algunos agregan frases o interlocutores, revisar solo después de cotejo contextual individual. Trabajar en otros grupos editoriales independientes durante los bloqueos.
3. **GFX-003:** examinar `wbg00.txp` y `wmap.txp` para determinar si sus inscripciones son alfabeto ficticio de ambientación o topónimos traducibles. Contrastar con UI/mapas y glosario, sin cambiar texturas originales automáticamente. Usar `scripts/inspeccionar_txp_bgpack.py` para regenerar vistas privadas locales desde la ISO original. No introducir PNG comerciales en GitHub. Cotejar paleta, swizzle y SHA. Si se determina texto traducible, diseñar un parche reversible y pruebas visuales.
4. **ROM-003:** examinar los 11 grupos DLC bloqueados: 611/731/951 de `magic.dat`, 1843/1845/1848–1853 de `talk00.dat`. Conservar posibles iconos ①/② y selectores 0x14/0xFD. Los tests B existen, pero sin EDAT reales no pueden certificarse las entradas. Preparar regresiones que validen hashes/regiones protegidas y ejecutar compilación en CI.
5. **Betatesting:** completar los 63 casos, identificar escenas donde se presentan TXP y comprobar carácter, fuentes, HUD, menús, capítulos y los cuatro DLC en PPSSPP **real** si es accesible. Registrar candidato SHA256, versión PPSSPP, pasos, capturas, pruebas, defectos y retests. No declarar 100% si falta emulador, DLC o escenas.

## Rutas y comandos reproducibles

Archivos: `corpus/NN/{entrada.csv,lectura.txt,revision.csv}`, `data/preexistentes/509_revision_central.csv`, `parcheador/app/scripts/{integracion_total.py,formato_talk.py,recompilar_talk.py,campos_revisados.py,campos_fijos.py,fuentes_es.py}`, `scripts/{auditar_bgpack_original.py,inspeccionar_txp_bgpack.py,test_txp_bgpack.py,validar.py,validar_seguimiento.py}`, `docs/seguimiento/**`.

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python -m unittest discover -s scripts -p 'test_txp_bgpack.py' -v
python scripts/inspeccionar_txp_bgpack.py --iso /ruta/al/original.iso --expect-iso-sha256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --out /ruta/privada/analisis_txp.json --preview-dir /ruta/privada/previews
```

Publicar únicamente registros, tests y transformaciones propias, nunca ISO, DLC ni texturas extraídas. Los previews locales del original no equivalen a capturas de PPSSPP y no acreditan v0.19.0. Si hay fallos de CI, **corregirlos** y volver a ejecutarlo antes de fusionar. La generación de siguiente prompt no sustituye cambios reales.

**Antes de terminar:** actualizar las cuatro matrices/indicadores, informes, controles QA y `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md` con un **RELEVO-007 completo**; abrir/fusionar PR cuando corresponda; incluir el prompt completo y su obligación §14 verbatim en respuesta final. Mientras uno de los cuatro apartados siga sin certificación 100% independiente, debe continuar el encadenamiento.

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
