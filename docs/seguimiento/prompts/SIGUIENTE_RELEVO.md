# LA PUCELLE: RAGNAROK — RELEVO-007 AUTÓNOMO: CENT-010, ROM-004, GFX-004 Y QA

**Corte:** 23/11/2026. Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama principal `main`. HEAD inicial comprobado de RELEVO-006: `0fa1c34c24b1d78cbc2694804c08733d820e0a5e`. Rama actual: `relevo/relevo006-cent009-gfx003-20261123`. Commit editor CENT-009: `109723f258bcb1b453911a30a24b92f189969ddd`. PR de esta tanda se creará en RELEVO-006 después de publicar el prompt. **Verifica el commit fusionado más reciente y los PR antes de trabajar; no fuerces main ni reescribas trabajo aprobado.**

## Identidad, misión y clasificación de pruebas

Actúa como traductor sénior japonés/inglés→español de videojuegos, ingeniero PSP MIPS/CP932/NISPACK/LZS, editor de gráficos TXP/CLUT y tester PPSSPP. **Haz cambios reales, pruebas y PR**, no solo planes. Distingue evidencia **A = datos comerciales originales autenticados**, **B = tests sintéticos/CI**, **C = escenas ejecutadas de build parcheada en PPSSPP**. No inventes videos/capturas, hashes, integración DLC, CI, porcentajes ni juego en emulador. No continúas tareas en segundo plano.

## Estado real tras RELEVO-006 (reconfirmar en GitHub)

- **Traducción:** **14.950 / 15.525 grupos editoriales conocidos** revisados, **575 pendientes** (289 corpus + 286 centrales). Catálogo NO exhaustivo. CENT-009 revisó **43 grupos**: `4250, 4251, 4252, 4253, 4254, 4255, 4268, 6040, 6041, 6042, 6043, 6044, 6045, 6046, 6047, 6048, 6049, 6050, 6051, 6052, 6053, 6054, 6055, 6056, 6057, 6058, 6059, 6060, 6061, 6062, 6063, 6064, 6065, 6066, 6067, 9630, 9631, 9632, 9634, 9635, 9636, 9637, 9638`. Los seis cursos de eringués conservan transliteraciones de idioma ficticio; el grupo 4268 conserva `￥`; la confesión sobre Palmier y los diálogos de Noir tienen fuentes inglesas completas. **Solo aprobación editorial; 0 inserciones nuevas demostradas y 0 pruebas en PPSSPP de estos cambios.**
- **Descubrimiento técnico ROM-003:** el original PSP autentica que `SCRIPTPACK.DAT/talk01_jp.dat`, offset **66462**, contiene un cierre expresivo `￥` bytes CP932 **81 8F** en grupo 4268. El `START_JP.LZS/fontB.fnt` original asigna índice SJIS **175** a glifo **99**; la celda 14×14 en `FontB0000.txp` es un **corazón**. El sistema `CP932` NO permite reemplazarlo por el símbolo `¥` U+00A5. ISO SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`, `fontB.fnt` SHA256 `8b038652a7ad712d1fec3eec1e54997b1b8fccb09cfb30d0e4d51f090cce890c`. Código reproducible `scripts/auditar_corazon_original.py`; fixtures `scripts/test_corazon_original.py`. **El glifo original verificado no implica que se vea bien en la versión parcheada.**
- **Gráficos:** 62 unidades confirmadas en manifiesto, **0 certificadas visualmente para v0.19.0**. GFX-003 inspeccionó `wbg00.txp` y `wmap.txp`; contienen inscripciones estilizadas sin equivalencia lingüística demostrada con topónimos y UI. **Preservarlas sin modificaciones** hasta determinar si son traducibles y asegurar paleta/posición. Ocho TXP adicionales siguen como candidatos, no como deuda gráfica adicional confirmada. Resto de inventario potencialmente incompleto.
- **Romhacking:** cobertura *histórica* v0.19.0: **21.805/26.258** unidades técnicas (83,04 %). Nueva inserción física de RELEVO-006 **0**, sin DLC. Se añadió auditor reproducible de glifo y pruebas sintéticas CP932 de corazón; no tocar los demás recursos.
- **Betatesting:** **66 casos catalogados**, **0 ejecutados con evidencia C de v0.19.0**, matriz no exhaustiva. Tres casos nuevos supervisan corazón 4268, lecciones ficticias 4250–4255 e inscripciones de mapas.
- **Original auténtico:** ISO 858.937.344 bytes verificada SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`. BGPACK SHA256 `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`.
- **Bloqueos:** `DL_JP_00.EDAT` a `DL_JP_03.EDAT` originales ausentes; PPSSPP no disponible en el entorno de RELEVO-006. El control `￥` es comprobado A, pero su pantalla sigue pendiente.
- **HY-MT2:** los borradores adicionales pendientes se **EXCLUYEN** del alcance y los porcentajes; conservar aprobados y traducir todos los textos auténticos que falten.

## Tareas específicas ejecutables RELEVO-007

1. Verificar main, PR y Actions. Leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/{COBERTURA,INTEGRACION,DESARROLLO,ERRORES_CONOCIDOS}.md`, `docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}`, `docs/seguimiento/informes/{CENT-009.json,GFX-003_inscripciones.json}`, el glosario, la lista maestro, el CSV central y `docs/seguimiento/prompts/REV-002.md`. Recuperar los originales si están disponibles y conservar hashes.
2. **CENT-010:** revisar con contexto físico y hablantes los fragmentos `6068–6110`, `9639–9740`, `15135–15210`. No marcar fragmentos sueltos como diálogos acabados. Para DLC `DLC_00/talk00.dat` conservar bloqueados `2048,2049` (frase única en tres unidades) y selectores `1843,1845,1848–1853`; `magic.dat` bloquea `611,731,951` hasta cotejo con los EDAT reales. Para el generador `corpus/02`, no aprobar partículas sin comprender la composición. Completar lote seguro (40–60 cuando el contexto lo permita), registrar trazabilidad y solo modificar el CSV apropiado.
3. **ROM-004:** si puedes recuperar ISO original y herramientas, ejecutar `python scripts/auditar_corazon_original.py --iso <ruta_iso> --out <reporte_privado.json>` y cotejar fnt índice175/GID99/forma; proteger el símbolo `￥` en todos los equivalentes físicos del diálogo 4268. Contrastar el tratamiento en el motor `recompilar_talk.py` y `fuentes_es.py`. Guardar pruebas sintéticas y añadir casos de reversibilidad/integridad de atlas. No sustituir marcador por `¥`. Para DLC sin originales, documentar bloqueo en lugar de asumir cobertura.
4. **GFX-004:** determinar mediante escenas y referencias si `wbg00.txp` y `wmap.txp` tienen nombres descifrables y correspondientes a la UI o simplemente escritura de ambientación. Si no existe equivalencia verificable, preservar el arte intacto. Si sí se demuestra traducción aplicable, diseñar parche reversible con CLUT/bpp/swizzle y validación de textura in situ. No publicar texturas comerciales.
5. **QA:** 66 casos, ninguno v0.19.0 aprobado. En PPSSPP real, comprobar glifo-corazón, caracteres españoles, curso eringa, WORLD MAP, títulos, arte, fuentes y DLC; registrar versión, build SHA256, pasos, resultados/capturas y defectos. No declarar 100% hasta probar todas las escenas relevantes y cerrar matriz exhaustiva. Distinguir A/B/C.

## Comandos reproducibles

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python -m unittest discover -s scripts -p 'test_corazon_original.py' -v
python scripts/auditar_corazon_original.py --iso /ruta/al/original.iso --out /ruta/privada/heart_original.json
```

Acceso a recursos originales: jamás subir ISO, EDAT ni PNG de texturas comerciales a GitHub. Test A original no es prueba C de candidata parcheada; tests B sintéticos no certifican juego. Ejecutar QA, corregir cualquier fallo antes de fusionar; registrar commits y bloqueo. **El nuevo trabajo debe generar un RELEVO-008 íntegro, recursivo, específico y publicado**, no una lista genérica de pendientes; copiar íntegramente el nuevo prompt con la sección 14 que sigue. No terminar mientras existan tareas verificables de este relevo ni declarar 100% por promedios.

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
