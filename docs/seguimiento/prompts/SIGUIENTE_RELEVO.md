# LA PUCELLE: RAGNAROK — RELEVO-009 AUTÓNOMO: CENT-012, ROM-006, GFX-006 Y QA

**Corte:** 23/11/2026. **Repositorio:** https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Rama principal `main`. Último HEAD comprobado ANTES de iniciar RELEVO-008: `a8b5900d4cd8b95c3e7e800528c9e0dda9af52bc`; rama del RELEVO-008: `relevo/relevo008-cent011-rom005-20261123`. Commit editorial CENT-011: `386c1cf566f79c7211b80bffd527a9ea12380a25`. **Verifica main, PR, Action runs y el SHA de fusión del RELEVO-008 al empezar RELEVO-009. No reemplaces trabajo de otros relevos.**

## Misión y evidencia

Actúa como traductor senior japonés/inglés→español, ingeniero romhacking PSP (MIPS/CP932/talk/NISPACK/LZS/ISO9660), editor de texturas/CLUT y tester PPSSPP. Trabaja realmente: cambia archivos, ejecuta pruebas, documenta, crea PR y fusiona solo con CI verde. Distingue **A: ISO/DLC original auténtico; B: sintéticos/CI; C: emulador PPSSPP ejecutando build candidata**. No inventes hashes, capturas, pruebas ni publicaciones; no declares 100 % sin evidencia completa.

## Estado exacto de partida (revalidar con GitHub)

- **Traducción:** **15.061 / 15.525 grupos editoriales conocidos** revisados, **464 pendientes**: 289 en corpus distribuidos y 175 centrales. Catálogo **no exhaustivo**, porcentaje sobre catálogo conocido: **97,01 %**, no avance global final. CENT-011 aprobó **58 grupos** `9692, 9693, 9694, 9695, 9696, 9697, 9698, 9699, 9700, 9702, 9709, 9710, 9711, 9712, 9713, 9714, 9715, 9716, 9717, 9719, 9720, 9721, 9722, 9723, 9724, 9725, 9726, 9727, 9728, 9729, 9730, 9731, 9732, 9733, 9734, 9735, 9736, 9737, 9738, 9739, 9740, 15136, 15137, 15138, 15139, 15142, 15143, 15145, 15146, 15147, 15148, 15149, 15150, 15152, 15154, 15155, 15156, 15157` cotejados con el original inglés en unidades del manifiesto; escenas de Homard, Yattanya y Éclair/Croix. **No se han insertado físicamente ni probado visualmente estas traducciones.** Informe `docs/seguimiento/informes/CENT-011.json`.
- **Gráficos:** 62 unidades conocidas del manifiesto, **0 certificadas en PPSSPP v0.19.0**. GFX-005 volvió a decodificar `wbg00.txp` y `wmap.txp` (original autenticado): hay grafemas estilizados cartográficos sin correspondencia lingüística demostrada con la UI. Mantener originales intactos. Ocho TXP candidatas fuera del inventario no se suman sin pruebas. Informe `docs/seguimiento/informes/GFX-005_cartografia_original.json`.
- **Romhacking:** histórica `v0.19.0-integracion` **21.805 / 26.258 unidades técnicas (83,04 %)**, **0 inserciones nuevas** en RELEVO-008. ROM-005 añade `scripts/verificar_iso_aislamiento.py`, que coteja recurso por recurso SHA256 de todos los archivos ISO9660, aun con reubicación LBA, exige hash fuente para excepciones, y rechaza modificaciones colaterales. Prueba A ejecutada: **ISO original contra ella misma, 23 archivos idénticos, ninguno modificado**. Pruebas B: **7 tests sintéticos pasaron localmente**; consultar CI del PR de RELEVO-008 para confirmar GitHub. Ni auto-comparación ni CI demuestran seguridad de una nueva build traducida.
- **Betatesting:** **76 casos catalogados y 0 ejecutados en PPSSPP v0.19.0**; matriz aún no exhaustiva.
- **Fuente A original:** ISO de **858.937.344 bytes**, SHA256 `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`; BGPACK SHA256 `56e26744c01ad34ac79b4170746ccb6157eb6c5585b09e0340e3dbaef8f42e78`. La ISO no se modificó. No están los cuatro DLC originales `DL_JP_00.EDAT` ... `DL_JP_03.EDAT` ni PPSSPP instalado (reconfirmar).
- **Corazón 4268:** `￥` U+FFE5 bytes CP932 `81 8F`, glifo 99 de `fontB` original. Conservar signo; no sustituir por `¥` U+00A5 ni afirmar prueba C.
- **HY-MT2:** propuestas adicionales pendientes excluidas de deuda y métricas; conservar aprobadas; el resto de textos auténticos sí entra en el alcance.

## Acciones ejecutables priorizadas

1. **Inicial:** leer `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/{COBERTURA,INTEGRACION,DESARROLLO,ERRORES_CONOCIDOS}.md`, `docs/seguimiento/{estado.json,inventario_textos.json,inventario_graficos.json,matriz_romhacking.json,matriz_betatesting.json,defectos.json}`, `docs/seguimiento/informes/{CENT-011.json,ROM-005_aislamiento_iso.json,GFX-005_cartografia_original.json}`, glosario, maestro y `data/preexistentes/509_revision_central.csv`, `docs/seguimiento/prompts/REV-002.md`. Comprobar SHA y bloqueos reales antes de trabajar.
2. **CENT-012:** revisar grupos completos independientes de `15158–15210` (incluye comentarios de monstruos), `9639–9668` y `6072–6109` con reconstrucción por unidades y hablantes. Evitar inventar fragmentos (`9701,9703–9708,9718,15135,15140–15141,15144,15151,15153,15159`). Traducir solo 40–60 unidades seguras si el contexto lo permite y conservar `corpus/02` generador de nombres con revisión estructural. Mantener pendientes los grupos DLC `2048,2049,611,731,951,1843,1845,1848–1853` hasta cotejar cuatro EDAT auténticos, selectores e iconos. No alterar glosario original sin PR específico.
3. **ROM-006:** obtener una ISO candidata legítima creada por motor de v0.19.0 y ejecutar `python scripts/verificar_iso_aislamiento.py --iso-original ... --iso-candidata ... --hash-original-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --allow-json permisos_recursos.json --out auditoria.json`. **Ejemplo de formato de permisos:** `{"PSP_GAME/USRDIR/START_JP.LZS":"<SHA256 ORIGINAL AUTÉNTICO>"}`; no inventar hashes: calcularlos sobre originales. Complementar con `scripts/verificar_bgpack_parche.py` para controles de TXP/CLUT, `qa_integridad_graficos.py` y comprobación EBOOT, fuentes y todos los assets. Añadir controles sobre sectores no indexados, PVD, autoría de modificaciones, y datos internos permitidos. No distribuir ISO/DLC/arte. Si falta candidata, continuar otras tareas y documentar el bloqueo.
4. **GFX-006:** comparar capturas auténticas en PPSSPP de `wbg00.txp` y `wmap.txp` con nombres visibles de lugares; si no hay equivalencia confiable, preservar arte original. Revisar otras de las 62 unidades declaradas para proponer QA y soluciones de fuente. No certificar gráficos solo por decodificar TXP.
5. **Betatesting:** ampliar los 76 casos hacia matriz exhaustiva por escena/ruta, y ejecutar en PPSSPP real cuando ISO candidata y DLC auténticos estén disponibles. Registrar versión, SHA, configuración, capturas reales, resultados, defectos y retrabajo. Priorizar Yattanya/tormenta, diálogo de Éclair/Croix, World Map, el corazón y los cuatro DLC.

## Comandos

```bash
python scripts/validar.py
python scripts/validar_seguimiento.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s scripts -p 'test_verificar_iso_aislamiento.py' -v
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
python scripts/verificar_iso_aislamiento.py --iso-original /ruta/original.iso --iso-candidata /ruta/candidata.iso --hash-original-iso 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5 --allow-json /ruta/privada/autorizaciones_sha.json --out /ruta/privada/informe_iso.json
```

Los ensayos originales A y fixtures B no equivalen a prueba C: no afirmar avance de romhacking físico, gráficos certificados ni gameplay PPSSPP sin evidencia ejecutada. Las propuestas HY-MT2 pendientes están excluidas.

**Entrega obligatoria:** realizar cambios reales, actualizar CSV de revisión sin tocar maestro, informes, matriz, estado, defectos y QA. Abrir/fusionar PR solo tras CI verde. Reemplazar `docs/seguimiento/prompts/SIGUIENTE_RELEVO.md` íntegramente por **RELEVO-010**, preservando exactamente la sección 14 siguiente, y copiar el prompt completo en la respuesta final. Si falta GitHub, entregar los archivos sin afirmar publicación. Continuar la secuencia hasta que las cuatro áreas lleguen al 100 % verificado individualmente.

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
