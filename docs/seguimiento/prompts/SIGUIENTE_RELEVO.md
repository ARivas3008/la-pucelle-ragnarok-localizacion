# LA PUCELLE: RAGNAROK — RELEVO-011 EXTENDIDO: CENT-014, ROM-008, GFX-008 Y QA

**Corte:** 23/11/2026 (Lima). **Repositorio:** https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama de trabajo del relevo anterior: `relevo/relevo010-extendido-cent013-rom007-20261123`. HEAD previo al cierre documental: `20667bdd134cba8409ece01dce6934ee58675e23`. Base previa: `01cf421ed46351dd829cbb35e8922b7895454cfd`. Consultar el PR de esta rama, su fusión y HEAD real antes de modificar nada. Versión histórica `v0.19.0-integracion`; no se ha publicado una versión final.

## 0. NUEVO RÉGIMEN DE EJECUCIÓN EXTENDIDA OBLIGATORIA

A partir de este relevo, debes ejecutar sesiones de trabajo intensivo, con una carga de trabajo orientativa equivalente a aproximadamente 20 minutos de procesamiento activo, en lugar de los relevos breves anteriores de aproximadamente seis minutos.

La duración es una referencia de planificación y no sustituye los objetivos técnicos. No esperes artificialmente, no desperdicies recursos y no inventes avances para satisfacer una duración.

**El objetivo es multiplicar aproximadamente por tres la cantidad de trabajo útil realizado en cada ejecución.**

### 0.1. Cantidad de trabajo por ejecución

Siempre que existan recursos y tareas aplicables, cada relevo deberá intentar completar:

| Área | Carga de trabajo objetivo |
|---|---|
| Traducción | 120–180 grupos investigados y revisados |
| Edición gráfica | 10–20 unidades gráficas investigadas o intervenidas |
| Romhacking | 3–5 mejoras, experimentos o correcciones técnicas sustanciales |
| Pruebas técnicas | 15–30 comprobaciones significativas, según aplicabilidad |
| Betatesting | 10–20 casos funcionales ejecutados cuando exista candidata y emulador |
| Integración | Construcción y auditoría de una candidata cuando sea posible |
| Documentación | Consolidación completa de las evidencias obtenidas |
| GitHub | Publicación de todos los avances verificables |

Estos valores son objetivos de productividad, no cuotas de aprobación. Si una tarea necesita investigación extensa, dedica el esfuerzo necesario aunque produzca menos elementos aprobados.

No apruebes traducciones incompletas, no inventes gráficos ni declares pruebas inexistentes para alcanzar las cifras.

### 0.2. Ejecución mediante macrolotes

Divide internamente cada relevo en cinco macrolotes de trabajo.

**Macrolote A — Auditoría y recuperación del estado**

- Consultar GitHub.
- Verificar HEAD, PR, commits y CI.
- Identificar todos los grupos pendientes.
- Comprobar disponibilidad de originales, candidata y herramientas.
- Determinar tareas independientes y dependencias.

**Macrolote B — Traducción intensiva**

- Revisar varios lotes consecutivos de 40–60 grupos.
- Reconstruir diálogos fragmentados.
- Consultar originales japoneses e ingleses.
- Investigar términos y controles.
- Corregir problemas narrativos y terminológicos.
- Registrar los resultados en los CSV correspondientes.

**Macrolote C — Implementación gráfica y romhacking**

- Ejecutar varios experimentos técnicos.
- Modificar herramientas y código.
- Resolver formatos pendientes.
- Probar extracción, edición, reconstrucción y reinserción.
- Construir una candidata cuando sea posible.
- Verificar que no se alteren recursos ajenos a la traducción.

**Macrolote D — Validación y corrección**

- Ejecutar las pruebas disponibles.
- Investigar los fallos.
- Corregir los defectos encontrados.
- Volver a ejecutar las pruebas.
- Verificar la candidata en PPSSPP cuando exista un entorno real disponible.

**Macrolote E — Consolidación**

- Actualizar los indicadores.
- Registrar evidencias.
- Consolidar cambios.
- Crear PR.
- Comprobar GitHub Actions.
- Fusionar únicamente después de aprobar las validaciones.
- Generar el siguiente relevo.

### 0.3. Prohibición de finalizar prematuramente

No debes finalizar una ejecución únicamente porque:

- Terminaste un lote de traducción.
- Creaste una herramienta de auditoría.
- Añadiste pruebas sintéticas.
- Actualizaste documentación.
- Encontraste un bloqueo.
- Publicaste un commit.
- GitHub Actions terminó correctamente.
- Completaste una de las cuatro áreas.

Después de completar cada macrolote, consulta nuevamente las tareas pendientes y continúa con otra tarea independiente que pueda ejecutarse.

Si la ausencia de DLC impide una tarea, continúa con la ISO base.

Si PPSSPP no está disponible, continúa con traducción, edición gráfica y construcción estática.

Si no puedes aprobar un diálogo fragmentado, investiga otro grupo.

Si una investigación gráfica está bloqueada, trabaja con otras texturas.

**No dediques el relevo entero a documentar reiteradamente bloqueos que ya están identificados.**

### 0.4. Prioridad a la implementación real

Orden de prioridad:

1. Resolver defectos reales del parche.
2. Completar traducciones auténticas pendientes.
3. Integrar traducciones aprobadas.
4. Editar e integrar gráficos traducibles.
5. Construir candidatas funcionales.
6. Ejecutar pruebas reales.
7. Crear pruebas de regresión.
8. Documentar los resultados.

La documentación es obligatoria, pero no puede sustituir el trabajo de implementación.

No generar auditores redundantes cuando ya existe una herramienta suficiente. Utilizar las herramientas existentes sobre recursos reales y mejorar su funcionamiento cuando se detecten limitaciones concretas.

### 0.5. Condiciones para finalizar una sesión

Finaliza únicamente cuando se cumpla alguna de estas condiciones:

- Se haya completado una carga de trabajo extensa y sustancial.
- Se hayan agotado las tareas ejecutables con los recursos disponibles.
- Existan límites efectivos del entorno que impidan continuar.
- Los cuatro apartados hayan alcanzado el 100 % verificado.

En caso de limitaciones, entregar todo el trabajo efectivamente realizado, sin prometer ejecución futura ni trabajo en segundo plano.

**La sección 0 completa deberá heredarse obligatoriamente en todos los relevos posteriores.**

---

## 1. Estado verificado y misión

Actúa como especialista sénior japonés/inglés→español, PSP MIPS, CP932, NISPACK/LZS, ISO9660, gráficos TXP/CLUT y QA PPSSPP. Ejecuta trabajo real; A = originales auténticos, B = cambios/ensayos estáticos y CI, C = ejecución auténtica de candidata en PPSSPP.

| Apartado | Estado conocido |
|---|---|
| Traducción editorial | 15.262/15.525 (98,31 % provisional); 263 pendientes (58 centrales, 205 distribuidos) |
| Gráficos | 62 unidades conocidas/26 TXP, 16 títulos piloto editados e insertados en una ISO gráfica local; 0 certificados C |
| Romhacking | 21.805/26.258 histórico, sin nuevo numerador de textos insertados; motor corregido y una ISO piloto gráfica parcial verificada |
| Betatesting | 85 casos catalogados, 0 ejecutados en PPSSPP v0.19.0 |

El inventario no es exhaustivo; excluir propuestas HY-MT2 adicionales pendientes y conservar aprobadas. No sumar imágenes piloto a certificados, ni 109 segmentos históricos a nuevas traducciones físicas. No publicar ISO, EDAT ni texturas comerciales.

## 2. Lecturas y archivos

Leer README.md, AGENTS.md, CONTRIBUTING.md, CHATGPT_PROJECT_INSTRUCCIONES.md, docs/COBERTURA.md, docs/INTEGRACION.md, docs/DESARROLLO.md, docs/ERRORES_CONOCIDOS.md, docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}, glosario/terminos_investigados.csv, data/preexistentes/509_revision_central.csv, data/maestros/03_TODOS_LOS_GRUPOS_15525.csv y 04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv, los 15 corpus NN/entrada.csv, lectura.txt, revision.csv y LEEME.md. Informes nuevos: docs/seguimiento/informes/CENT-013.json, ROM-007_integracion_central.json, GFX-007_capitulos_piloto.json y GFX-007_README.md. Leer docs/seguimiento/prompts/REV-002.md.

## 3. CENT-014 y sucesivos

El CENT-013 revisó 141 grupos (57 centrales, 84 distribuidos), recuperó 165 bloques y comprobó 109 coincidencias exactas de SHA de líneas y texto histórico aprobado. Otros 56 bloques tienen nueva reconstrucción. Sus anclas están en `parcheador/app/datos/segmentos_centrales_anclados.json`, con SHA de recurso, SHA de cadenas CP932 enmarcadas por longitud, recurso, offset y grupos_objetivo/grupos. NO convertir sus textos de contexto CSV en sustituciones genéricas. Mantener las traducciones aprobadas y sus claves.

Consultar IDs pendientes directamente en inventario_textos.json; revisar primero los restantes de ISO base, reconstruyendo todo el bloque desde opcodes, sin mezclar hablantes, y estudiar 7952 (profecía aún incompleta). Investigar corpus/02 y el generador de nombres en forma estructural. No aprobar partículas ambiguas; excluir 1630 (pseudo texto binario) del alcance textual conforme a criterio técnico existente, sin alterar estado por mera cuota. Grupos DLC 2048,2049,611,731,951,1843,1845,1848–1853 requieren EDAT auténticos. Objetivo 120–180 investigados si hay contexto; si escasean, trasladar esfuerzo a integración y QA.

## 4. ROM-008: candidata real completa de ISO base

Se detectó que el motor no leía los 509 registros centrales y el EXE no los empaquetaba. Se corrigieron `parcheador/app/scripts/revisiones_coordinadas.py`, `integracion_total.py`, `recompilar_talk.py`, `parcheador/investigacion/v0.14/integrar_scripts_v014.py`, `parcheador/build_release.py` y `parcheador/main.go`. La carga exige unión exacta de 15.525 IDs y registra 16 fuentes editoriales (15+central). CI previa verde: corpus 45303682036, seguimiento 45303682117, motor 45303682121 en `4dbbc4de765396ac87f2667d939bcbdca2a6014f`. Verificar CI del último HEAD/PR.

Prioridad: conseguir checkout completo vigente en entorno local que pueda acceder a ISO auténtica y ejecutar `python parcheador/app/scripts/integracion_total.py --help`. Compilar compresor NIS LZS para plataforma local según docs/DESARROLLO.md. Ejecutar `python parcheador/app/scripts/integracion_total.py --iso ORIGINAL.iso --repo-directorio REPO --salida SALIDA_PRIVADA`. No exigir DLC para prueba de ISO base. Auditar que los 165 bloques lleguen al catálogo, comparar hashes y revisar rechazos concretos de glifos, menús EBOOT y campos fijos; no desactivar controles ni declarar éxito de build sin terminar. Investigar EBOOT si las nuevas aprobaciones centrales exceden reservas: conservar bytes originales para los no aplicables y documentar cada rechazo, no rebajar QA. Verificar reubicaciones, integridad de miembros de NISPACK/DAT y BGPACK; no forzar layout fijo si el motor anexa. El PVD auténtico declara 380120 sectores y el físico 419403; no modificar sin prueba. Preservar corazón grupo 4268 U+FFE5 / CP932 81 8F (fontB GID99), tildes, ñ, ¿¡, variables y controles. Registrar todos los hashes y cobertura real por unidad sin contar segmentos históricos dos veces.

## 5. GFX-008: integrar los capítulos al motor y avanzar con HUD

La ISO original SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5` (858937344 bytes) contiene BGPACK SHA `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`. GFX-007 demostró swizzle parcial 16 bytes × 8 filas, últimas dos filas sin relleno. Se editaron at01–at12 y at15–at18 a partir de las aprobaciones 3282–3297, con fuente Liberation Serif Bold local; los 16 roundtrips y reencodificaciones mantienen 82640 bytes, CLUT y fuera de rectángulo [50,35,430,116] intactos. Restauración debajo de la tinta aproximada. ISO piloto gráfica local SHA `b0f4521223bbeadd0665f2f821659b595049807bbfa0869a5a4fb35965ec2642`, BGPACK nuevo SHA `f50e26515b2f8f26ea58213627cceffd9afef8484fab996bceb32d1253890193`. 16 miembros cambiados, 269 idénticos, 22 archivos ISO restantes idénticos de 23 y todos los bytes externos BGPACK idénticos. No es candidata de texto ni certificada PPSSPP. Herramienta `scripts/gfx007_editar_capitulos.py` e informe GFX-007. Reproducir en entorno con numpy 2.3.5, Pillow 12.3.0, OpenCV 4.13.0 y fuente local SHA `443a4dbd694b6e4689925947b456e0532e10b19c90fa32eb39ea6c2cd9db9ebd`; no distribuir fuente.

Ejecutar: `python scripts/gfx007_editar_capitulos.py --iso-original ORIGINAL.iso --salida PILOTO.iso --fuente FUENTE_LOCAL.ttf --informe piloto.json`. Revisar los cuatro capítulos demoníacos por contraste y posibles restos ingleses; preparar edición final sin degradar ornamentos. Integrar únicamente deltas autorizados y reproducibles del BGPACK al motor, preservando archivos ajenos; comprobar atlas de sys3/sys4, item/sys5 con 16 bancos CLUT, sys2/sys6/sys7, title2/title_mj/wmap_03. Revisar posición de rótulos y controles de bancos; las vistas privadas de bancos 0,1,15 no prueban selector en juego. No traducir inscripciones ornamentales de wbg00/wmap sin significado demostrado. Objetivo 10–20 recursos, sin declarar certificado antes de C.

## 6. QA

Ejecutar PPSSPP oficial disponible, probar primero candidata ISO base y después DLC aportados. Documentar versión, renderer, configuración, hash candidato, partida, captura auténtica y resultado de cada caso. Priorizar los 165 bloques, rutas normales y demoníacas, 16 títulos, World Map, menú configuración, corazón, fuentes y HUD multibanco. Corregir fallos y repetir pruebas en la misma sesión. No sumar más casos sin justificación; no fingir PPSSPP instalado. Los cuatro DL_JP_00.EDAT–DL_JP_03.EDAT siguen ausentes. El entorno anterior no tenía checkout completo accesible localmente ni PPSSPP; GitHub connector permitió publicar código. Reconfirmar recursos y buscar alternativas legítimas, no subir originales.

## 7. Validaciones y entrega

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python parcheador/app/scripts/integracion_total.py --help
python scripts/verificar_iso_aislamiento.py --iso-original ORIGINAL.iso --iso-candidata CANDIDATA.iso --hash-original-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --allow-json AUTORIZACIONES_SHA.json --out aislamiento.json
```

Utilizar verificar_iso_layout_fijo.py solo si aplica; verificar_bgpack_parche.py con recursos autorizados y hashes auténticos. Actualizar CSV, inventarios, matrices, defectos, informes, estado y PR. Distinguir 141 grupos nuevos aprobados de 165 bloques, 109 previamente aprobados, 56 nuevos y cero inserciones de texto verificadas en candidata completa. Registrar la comparación antes/después de los cuatro apartados, incluidos textos insertados, gráficos editados/insertados/certificados, defectos, tests y PPSSPP, sin cuotas ficticias. Preparar RELEVO-012 EXTENDIDO con secciones 0 y 14 íntegras. No cerrar temprano si quedan tareas independientes ejecutables; no esperar artificialmente.

---

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

**ORDEN ADICIONAL PERMANENTE: MANTENER EL RÉGIMEN EXTENDIDO DE LA SECCIÓN 0 EN TODOS LOS RELEVOS POSTERIORES, PRIORIZANDO LA IMPLEMENTACIÓN REAL Y UNA CARGA DE TRABAJO APROXIMADAMENTE TRES VECES SUPERIOR A LOS RELEVOS BREVES ANTERIORES.**
