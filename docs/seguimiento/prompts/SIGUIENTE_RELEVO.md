# LA PUCELLE: RAGNAROK — RELEVO-010 AUTÓNOMO: CENT-013, ROM-007, GFX-007 Y QA

**Corte:** 23/11/2026. **Repositorio:** https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama principal `main`. HEAD antes de RELEVO-009: `9fa5208a14b82c8430e00d6ea51c5a8167b470a3`. Rama del relevo anterior: `relevo/relevo009-cent012-rom006-20261123`. Commit editorial CENT-012: `a5db146a094eb6d9c1564ce2c753b30cabe7bc49`. Consultar el HEAD fusionado, PR y Actions reales al empezar. No sobrescribir avances.

## Misión y pruebas

Actúa como traductor sénior japonés/inglés→español, ingeniero PSP CP932/NISPACK/LZS/ISO9660/talk, editor de TXP/CLUT y tester PPSSPP. Ejecuta cambios reales, QA y PR; no inventes resultados. Evidencia A = originales auténticos; B = tests sintéticos y CI; C = candidata en PPSSPP real. No confundir metadatos originales, revisión editorial o compilación con evidencia C. No trabajar en segundo plano.

**CI real de RELEVO-009 (PR #36, commit `54d95e30e2bd9951b00a40f21842a2ea02cc3068`):** [QA corpus](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/actions/runs/45301178890) y [QA seguimiento, ROM-006 y GFX-006](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/actions/runs/45301178789) aprobaron. Las nuevas cinco pruebas de layout fijo y cuatro de estructura TXP son evidencia B; no certifican la candidata. Reconfirmar CI del commit de registro posterior.

## Estado verificado de partida

- **Traducción:** 15.121/15.525 grupos editoriales conocidos (97,40 % del catálogo provisional), **404 pendientes** (289 distribuidos y 115 centrales). Catálogo no exhaustivo. CENT-012 añadió 60 grupos: `9641, 9642, 9643, 9644, 9645, 9646, 9647, 9648, 9649, 9650, 9651, 9652, 9653, 9654, 9657, 9658, 15158, 15160, 15161, 15162, 15163, 15165, 15166, 15167, 15169, 15171, 15172, 15173, 15174, 15175, 15176, 15179, 15180, 15181, 15182, 15183, 15184, 15185, 15187, 15188, 15189, 15190, 15191, 15193, 15194, 15195, 15197, 15198, 15199, 15200, 15201, 15202, 15203, 15204, 15205, 15206, 15207, 15208, 15209, 15210`. Se cotejaron **124/124 unidades** mediante lectura CP932 desde offsets auténticos hasta NUL, NFKC solo para comparar, de `SCRIPTPACK.DAT/talk11_jp.dat` y `ISO_START/talk00.dat`. Ninguna inserción nueva, ninguna prueba de pantalla. Informe `docs/seguimiento/informes/CENT-012.json`.
- **Gráficos:** 62 unidades conocidas, 26 TXP distintos (19 en BGPACK, 7 en START_JP), metadatos y SHA256 de original cotejados para las 62. **16 títulos at01–at12 y at15–at18 de 480×170, 8bpp, 1 CLUT, 82640 bytes: altura parcial no compatible con decoder de bloques 16×8 completos.** `item.txp`, `sys3.txp`, `sys5.txp` tienen 16 bancos CLUT de 16 colores. No usar decoder monobanco en ellos. Cero texturas nuevas editadas y 0 certificadas PPSSPP v0.19.0. `wbg00.txp` y `wmap.txp` se preservan sin equivalencia demostrada de inscripciones; ocho candidatos adicionales no se suman. Informe `docs/seguimiento/informes/GFX-006_estructura_62.json`; herramienta `scripts/auditar_graficos_manifiesto.py`.
- **Romhacking:** `v0.19.0-integracion` histórico 21.805/26.258 unidades técnicas (83,04 %), 0 nuevas inserciones en este relevo. Original físico 419403 sectores; PVD declara 380120 sectores (diferencia 39283 sectores), endian coincide. NO corregir la diferencia a ciegas; original auténtico tiene recursos más allá del volumen declarado. `scripts/verificar_iso_layout_fijo.py` exige distribución y tamaño idénticos y protege todas las regiones no autorizadas incluidas PVD, rellenos y bytes sin entrada; no admite reubicación. Complementa `scripts/verificar_iso_aislamiento.py` que coteja hashes por archivo incluso si cambia LBA, y `scripts/verificar_bgpack_parche.py` para TXP. No se dispone de candidata real ni prueba física nueva. Informe `docs/seguimiento/informes/ROM-006_layout_fijo.json`.
- **Betatesting:** 82 casos catalogados, 0 ejecutados en PPSSPP v0.19.0, matriz no exhaustiva.
- **ISO original aportada:** 858.937.344 bytes, SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`; BGPACK SHA256 `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`. No modificada. No se encontraron candidata, cuatro EDAT originales `DL_JP_00.EDAT`–`DL_JP_03.EDAT` ni PPSSPP. Corazón 4268 U+FFE5 `￥` = CP932 81 8F, GID99 en fontB original; conservar y comprobar en pantalla.
- **HY-MT2:** propuestas adicionales pendientes excluidas de métricas; preservar aprobadas.

## Tareas ejecutables

1. Verificar HEAD y PR, leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/{COBERTURA,INTEGRACION,DESARROLLO,ERRORES_CONOCIDOS}.md`, `docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}`, informes `CENT-012.json`, `GFX-006_estructura_62.json`, `ROM-006_layout_fijo.json`, glosario y maestro, CSV central y `docs/seguimiento/prompts/REV-002.md`.
2. **CENT-013:** revisar 9660,9662,9665–9668 (cadenas completas ya cotejadas físicamente, pero sin aprobar), grupos 9633, 9639–9640, 9655–9656, 9659, 9661, 9663–9664, 9701,9703–9708,9718, 6072–6074,6077–6078,6100,6102,6109,15135,15140–15141,15144,15151,15153,15159,15164,15168,15170,15177–15178,15186,15192,15196. Reconstruir hablantes/bytecode y buscar textos contiguos en ISO auténtica, no inventar fragmentos. Solo aprobar grupos con contexto suficiente. En paralelo investigar los 289 pendientes de corpus, empezando `corpus/02` y REV-002, sin alterar partículas del generador sin comprender composición. DLC 2048–2049, 611/731/951, 1843/1845/1848–1853: exigir EDAT original para controles y segmentación; separar revisión editorial de inserción.
3. **ROM-007:** conseguir candidata real producida por `parcheador/app/scripts/integracion_total.py` (ver docs/DESARROLLO.md). Verificar ISO+SHA y recursos externos. Si layout fijo, ejecutar `verificar_iso_layout_fijo.py`; si motor anexa/reubica archivos, usar `verificar_iso_aislamiento.py` y diseñar auditoría de extents anteriores/nuevos, PVD y huecos; nunca exigir igualdad de PVD si el cambio está demostrado necesario y aprobado. Autorizaciones JSON mapa ruta ISO→SHA256 fuente calculada. Auditar BGPACK, EBOOT, START_JP, SCRIPTPACK y sus miembros internos. No publicar ISO/EDAT/arte; no inventar candidata ni evidencia.
4. **GFX-007:** resolver de manera verificable la distribución de las últimas dos filas de atXX.txp y bancos CLUT de item/sys3/sys5 comparando original, código `parcheador/app/scripts/atlas_ui_es.py`, `parcheador/investigacion/v0.11/txp_verify.py` y QA; no rellenar filas ni bancos sin demostrar formato. Diseñar fixture con payload parcial y roundtrip; localizar rectángulos de los 62 rótulos, cotejar anclajes y variantes. No editar mapas ornamentales sin evidencia. Certificación solo tras comparación visual real de candidata.
5. **QA:** ejecutar PPSSPP real con candidata y DLC aportados. Registrar versión, SHA, partida, configuración, pasos, capturas y defectos; priorizar 16 capítulos, HUD multibanco, corazón, rutas y escenas finales; ampliar matriz de 82 hacia exhaustividad. Separar pruebas sintéticas de pruebas ejecutadas.

## Comandos reproducibles

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python scripts/auditar_graficos_manifiesto.py --iso /ruta/original.iso --manifiesto data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv --sha-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --out /ruta/privada/gfx.json
python scripts/verificar_iso_layout_fijo.py --iso-original /ruta/original.iso --iso-candidata /ruta/candidata.iso --hash-original-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --allow-json /ruta/privada/permisos.json --out /ruta/privada/layout.json
```

Solo usar el segundo comando de auditoría de layout para candidatas con tamaño/distribución fija. No publicar recursos comerciales. Ejecutar QA de código, corregir fallos antes de fusionar y actualizar matrices. **Generar RELEVO-011 completo** en `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md`, con sección 14 íntegra y copia completa en respuesta. No declarar 100 % por promedios.

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
