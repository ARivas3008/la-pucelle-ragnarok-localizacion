# LA PUCELLE: RAGNAROK — RELEVO-002 AUTÓNOMO PARA LAS CUATRO ÁREAS

**Corte documental: 23/11/2026.** Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Trabajar con `main` y conservar sus avances. Último HEAD de main comprobado **antes del PR CENT-004**: `a237b8bc63d9b8566894ec0e775ab5a564107152`; commit real editorial CENT-004 en la rama de trabajo: `9ec14aabc1f8ccd28e3ab46f1010a7c60b4f1887`. **Consultar obligatoriamente el HEAD de main al iniciar el siguiente relevo**: el merge puede producir otro SHA. No retroceder la rama.

## Misión y estado factual

Actúa como traductor senior japonés/español e ingeniero de localización PSP, romhacking, gráficos y QA. **Ejecuta** cambios comprobables, pruebas, PR y documentación; no te limites a planificar. No inventes capturas, bytes, pruebas, compilaciones ni resultados.

- **Traducción:** 14.756 de 15.525 grupos editoriales conocidos revisados; **769 pendientes conocidos** = 289 de corpus distribuidos + 480 centrales. Alcance no exhaustivo todavía.
- **Gráficos:** 62 elementos conocidos, ninguno certificado visualmente para v0.19.0. Pueden existir más.
- **Romhacking:** 21.805 de 26.258 unidades técnicas cotejadas en versión histórica v0.19.0 (**83,04 %**); sin nueva prueba de inserción desde ese corte. No equivale a completar los demás apartados.
- **Betatesting:** v0.19.0 sin certificación integral; existe matriz inicial de 31 casos, pendiente ampliar por escenas, elecciones y DLC. Sin denominador final exhaustivo.
- **HY-MT2:** se excluyen los borradores adicionales pendientes del seguimiento obligatorio y de todos los indicadores. Conservar las traducciones ya aprobadas. **No** eximir cadenas auténticas del juego pendientes de traducir.
- **Entrega:** v0.19.0-integracion preliminar. No divulgar ISO ni DLC.
- **Original auténtico:** ISO SHA-256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`, auditado previamente. Si lo reutilizas, comprueba que está disponible y vuelve a verificarlo.
- **Bloqueos anteriores:** cuatro EDAT DLC originales, PPSSPP y clon Windows del usuario no accesibles al entorno anterior. Verificar disponibilidad actual, no dar por hecho que siguen ausentes.
- **Novedad CENT-004:** revisión editorial segura del grupo 598, `水属性UP` → **«Aumenta el atributo celeste.»**, fundamentada en grupo 1876 del japonés que distingue 青(hielo) y 水(curación), grupo 599 y glosario. NO certificada inserción ni juego. Otros 11 grupos investigados siguen pendientes por controles/fragmentación.

Leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/INTEGRACION.md`, `docs/COBERTURA.md`, `docs/ERRORES_CONOCIDOS.md`, `docs/DESARROLLO.md`, `docs/seguimiento/estado.json`, los cuatro inventarios/matrices, `docs/seguimiento/informes/CENT-004.json`, y los archivos precisos de cada tarea.

## Próxima tarea ejecutable

**CENT-005 / REV-002:** investigar sin inventar los grupos 611, 731 y 951 de `DLC_00/magic.dat` (prefijos 1/2 ¿control o texto?), y 1843, 1845, 1848, 1849, 1850, 1851, 1852, 1853 de `DLC_00/talk00.dat` (opciones y frases divididas); usar `data/preexistentes/509_revision_central.csv`, manifiesto, original, glosario, el informe CENT-003 y parsers de `parcheador/app/scripts/`. **No aprobar si falta correspondencia de bytes**; mantener pendientes documentados. En paralelo, seleccionar otros grupos centrales que puedan resolverse con japonés y contexto y corregirlos con trazabilidad. Investigar también `docs/seguimiento/prompts/REV-002.md` para fragmentos concatenados en corpus/02. No reabrir grupos aprobados sin evidencia nueva.

Revisar seguridad y compatibilidad de inserción en `parcheador/app/scripts/integracion_total.py`, `formato_talk.py`, `recompilar_talk.py`, `fuentes_es.py`, `atlas_ui_es.py` y archivos relevantes; no alterar el binario sin pruebas. Preparar y ejecutar la auditoría desde original auténtico y los cuatro DLC cuando estén disponibles. Verificar texturas y un recorrido completo de juego con PPSSPP real, registrando versión, candidata, capturas y evidencia; no usar las capturas antiguas como pruebas de una versión nueva.

Ejecutar, según aplique:
```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
```
Consultar `docs/DESARROLLO.md` para comandos de construcción y pruebas adicionales. Si una prueba no es ejecutable, indicarlo; registrar la tarea bloqueada y seguir con otra independiente.

Archivos esperados: CSV central o revisión de corpus (sin cambiar ID ni filas); documentación de dictámenes con originales y notas; métricas `docs/seguimiento/estado.json`, inventarios, matrices, defectos, y un PR comprobado. Nunca contar revisión editorial como inserción física o certificación visual.

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
