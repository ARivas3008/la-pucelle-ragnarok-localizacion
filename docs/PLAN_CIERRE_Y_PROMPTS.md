# Evaluación y prompts para completar la localización

Evaluación del 23-11-2026 sobre v0.19.0-integracion. Los porcentajes describen evidencias diferentes; no se promedian para obtener un porcentaje global del proyecto.

| Área | Evidencia disponible | Qué falta para medir o cerrar |
|---|---|---|
| Traducción | 14.727/15.016 grupos revisados: 98,08 % del corpus dividido. 500/1.711 propuestas adicionales revisadas: 29,22 %. | Resolver 289 grupos y revisar 1.211 propuestas; inventariar texto fuera del corpus y recursos gráficos. El 98,08 % no representa todo el juego. |
| Edición de gráficos | Hay herramientas, fuentes españolas y deltas de atlas. Las 62 unidades gráficas del manifiesto siguen pendientes de revisión visual. | 0/62 certificadas en esa auditoría, lo que no significa que ninguna esté editada. Falta un inventario exhaustivo para calcular un porcentaje global. |
| Romhacking | EXE funcional en construcción: genera ISO y cuatro DLC. 21.805/26.258 unidades técnicas insertadas y cotejadas: 83,04 %. Cinco contenedores verificados, diarios reversibles y pruebas automáticas. | La inserción es un indicador parcial, no el porcentaje de ingeniería terminado. Quedan destinos, tablas, gráficos, límites y referencias por cerrar y validar en ejecución. |
| Betatesting | Prólogo documentado de v0.18.3. Auditoría binaria y pruebas automáticas de v0.19.0. | No consta una campaña visual completa de v0.19.0 ni una matriz exhaustiva de casos. El porcentaje global de betatesting es indeterminado. |

Fuente: `docs/COBERTURA.md`, `docs/ERRORES_CONOCIDOS.md`, `docs/informes/cobertura_v0.19.0.json`, los 15 `revision.csv` y `docs/PUBLICACION_2026-11-23.md`. El estado de revisión es una declaración editorial registrada, no una segunda auditoría lingüística de cada frase realizada para este documento.

## Prompt 1 — Ejecución profesional de las cuatro áreas

Copia el siguiente bloque completo:

```text
Actúa como responsable de localización, edición de gráficos, ingeniería de formatos y QA de La Pucelle: Ragnarok para PSP. Ejecuta el trabajo con las herramientas disponibles; no te limites a proponer un plan. El objetivo es completar y demostrar el 100 % del alcance inventariado de las cuatro áreas, sin confundir traducción escrita, inserción binaria y funcionamiento en pantalla.

REPOSITORIO Y PUNTO DE PARTIDA
Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion
Base histórica auditada: etiqueta v0.19.0-integracion, commit 35102ed9fccd1a9df125342a79dc287155ce1faf. No restablezcas el repositorio a esa etiqueta si main contiene avances posteriores.
ROOT significa la raíz del clon vigente. En el dossier de este proyecto es:
C:/Users/one/Downloads/LaPucelle_WorkPC_Dossier_2026-11-15/14_Publicacion_GitHub
Consulta el estado de Git, conserva cambios ajenos y contrasta main remoto antes de integrar. Sigue las instrucciones aplicables del repositorio y las autorizaciones vigentes del usuario.

LECTURA OBLIGATORIA, RELATIVA A ROOT
- AGENTS.md, CONTRIBUTING.md y README.md.
- docs/COBERTURA.md, docs/ERRORES_CONOCIDOS.md, docs/INTEGRACION.md.
- docs/DESARROLLO.md, docs/HY_MT2.md, docs/HISTORIAL_VERSIONES.md.
- docs/ORGANIZACION_GITHUB.md y docs/PUBLICACION_2026-11-23.md.
- docs/informes/cobertura_v0.19.0.json y cobertura_v0.19.0.csv.
- metodologia/README.md, RUBRICA_LOCALIZACION.md y CHECKLIST_CALIDAD.md.
La documentación antigua es evidencia histórica: una afirmación de una versión anterior no demuestra el estado de la versión actual.

FUENTES Y RECURSOS
- corpus/01/revision.csv hasta corpus/15/revision.csv: revisiones editables. Lee entrada.csv y lectura.txt de cada corpus como referencia inmutable.
- data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv: manifiesto original; no alteres IDs, offsets ni filas para mejorar artificialmente cobertura.
- data/preexistentes/509_revision_central.csv: grupos centrales; audítalos individualmente. Su existencia no demuestra que estén traducidos o insertados.
- glosario/terminos_investigados.csv: terminología. Documenta y coordina cualquier cambio de glosario.
- laboratorio/2026-11-integracion/informes/: huecos_corpus.json, continuaciones_fuera_manifiesto.csv, campos_pendientes_plan.json, menus_fuera_corpus_pendientes.json y repeticiones_corpus_para_cotejo.json. Son pistas históricas que deben cotejarse con la nueva construcción.
- laboratorio/2026-11-integracion/hymt2_revisados/ y hymt2_borradores/: aprobados y borradores separados.
- laboratorio/2026-11-integracion/hymt2_traducir.py, descargar_hymt2_local.py y herramientas/hymt2/instalacion.json: cliente y modelo fijado. Hy-MT2-1.8B-Q8_0; revisión a0c709d9fac510f2c807aa3af52872340dc37a4a. No afirmes haber utilizado el modelo 7B.
- laboratorio/2026-11-integracion/inspeccionar_texturas.py y buscar_atlas_embebido.py: investigación gráfica. Adapta sus rutas si requieren la estructura histórica; no ejecutes scripts de laboratorio suponiendo que son el motor de entrega.
- parcheador/app/scripts/: integracion_total.py, recompilar_talk.py, formato_talk.py, campos_revisados.py, campos_fijos.py, fuentes_es.py, menus_adicionales.py, correcciones_tablas_qa.py, atlas_ui_es.py, nis_formats.py y nis_lzs_pack.cpp.
- parcheador/app/datos/: segmentos_talk_revisados.json, segmentos_hymt2_aprobados.json, menus_fuera_corpus.json, menu_eboot_contextual.csv, tablas_base_deltas.json.z y atlas_deltas.json.z.
- parcheador/investigacion/v0.12/reubicador_anclas_v012.py y v0.14/integrar_scripts_v014.py.
- parcheador/build_release.py, main.go, main_test.go y gui.ps1: empaquetado y lanzador.
- scripts/auditar_entrega.py, scripts/validar.py, parcheador/app/tests/, parcheador/investigacion/v*/tests/ y metodologia/tests/: comprobaciones.

ARCHIVOS LOCALES NO INCLUIDOS EN GITHUB
La raíz del dossier es C:/Users/one/Downloads/LaPucelle_WorkPC_Dossier_2026-11-15.
ISO original: La_Pucelle_Ragnarok_v1.1.2/La_Pucelle_Ragnarok_v1.1.2.iso.
SHA-256 esperado: 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5.
DLC originales: ULJS00244/ULJS00244/DL_JP_00.EDAT hasta DL_JP_03.EDAT.
Última entrega local de referencia: 13_Entrega_v0190/JUEGO_PARA_PPSSPP/.
Modelo local: 12_Integracion_total/herramientas/hymt2/; verifica su instalación y hash.
Capturas originales: C:/Users/one/Downloads/WhatsApp Unknown 2026-11-16 at 6.15.00 PM.zip; hojas de referencia en 12_Integracion_total/informes/capturas_usuario_0.png hasta capturas_usuario_5.png.
En otra máquina, solicita las ubicaciones necesarias si no están disponibles. No descargues ni publiques copias del juego. Localiza PPSSPP y su configuración; no presupongas una ruta ni pruebas realizadas.

FASE 0: INVENTARIO Y MEDICIÓN
1. Recalcula la cobertura sobre una salida actual y registra versión, commit, hashes de originales, EXE, ISO y DLC.
2. Crea docs/seguimiento/inventario_textos.json, inventario_graficos.json, matriz_romhacking.json, matriz_betatesting.json y estado.json. Estas rutas son entregables nuevos; no presupongas que ya existen.
3. Asigna IDs estables a cada elemento y registra fuente/recurso, escena, idioma, traducción, estado editorial, destino físico, estado de inserción, verificación visual y enlace a evidencia. Relaciona grupos, unidades y apariciones sin contarlos varias veces.
4. Inventaría también texto fuera del manifiesto: EBOOT, todos los miembros START/SCRIPTPACK/BGPACK y otros contenedores, NPC, tutoriales, opciones, mapas, objetos, habilidades, tiendas, avisos, capítulos, finales y cuatro DLC. Los hallazgos nuevos van en inventarios complementarios, sin reescribir el manifiesto original.
5. Identifica qué alcance está todavía sin inventariar. Mientras exista, no declares un porcentaje global de finalización. La guía de Neoseeker es una referencia parcial de PS2 y no el denominador de Ragnarok.

FASE 1: TRADUCCIÓN
1. Resolver los 289 grupos que requerían investigación y los 1.211 borradores adicionales no aprobados; recalcular estas cantidades antes de empezar.
2. Revisar los grupos centrales y todo hallazgo adicional; distinguir nombres propios, pseudotextos y excepciones intencionales. No traducir metadatos binarios como si fueran palabras.
3. Usar HY-MT2 local con fuente, contexto adyacente, hablante y glosario para traducciones faltantes. Leer y corregir cada propuesta antes de aprobarla; conservar trazabilidad modelo -> borrador -> revisión -> destino.
4. Cotejar japonés cuando exista, naturalidad del español, género, tratamiento, tono, nombres, variables y continuidad de fragmentos. Unificar Panza del Diablo, Salade, Iglesia y prica según contexto y glosario.
5. Investigar repeticiones como sia,sia en el motor y en el corpus. No eliminar automáticamente repeticiones expresivas válidas ni completar frases cortadas inventando contenido.
6. Comprobar las 419 unidades de campos sin traducir, 335 modificadas pendientes de cotejo y 1.686 bloques físicos de diálogo pendientes del punto de partida. No sumarlos entre sí ni a los grupos editoriales: son categorías diferentes.
7. Resolver límites de espacio sin mutilar nombres o significado: estudiar abreviación editorial justificada, redistribución de líneas o solución técnica segura. Registrar las decisiones.
Aceptación: todos los textos traducibles del inventario completo tienen revisión contextual aprobada; cero pendientes lingüísticos no justificados. Las excepciones documentadas no se cuentan como traducciones realizadas.

FASE 2: EDICIÓN DE GRÁFICOS
1. Inventariar las 62 unidades gráficas conocidas y buscar las no catalogadas. Identificar recurso, textura, paleta, rectángulo, coordenadas, variantes y escena de cada texto.
2. Localizar y trabajar títulos de capítulos, World Map, cartel japonés de la cueva, Fight, Tu turno y anuncios de victoria/derrota, además de HUD de combate: MAP CLEAR, Flow, Flow Range, Tiles, Element y estadísticas, distinguiendo texto dibujado por fuente de texto rasterizado.
3. Conservar dimensiones, formato, paleta, transparencia, swizzle y gráficos ajenos al texto. Guardar fuentes editables y un procedimiento repetible para generar los deltas.
4. Calcular centrado con el ancho visible de los glifos y el área de destino. En anuncios de pantalla completa usar el espacio lógico PSP 480x272; en cajas o paneles, su propia área útil. Considerar bordes transparentes, anclaje y escala. No centrar solo por número de letras.
5. Conservar el diseño original de los puntos suspensivos cuando sea intencional. Evitar modificaciones accidentales de retratos, marcos, sprites y fondos.
6. Verificar ida/vuelta de cada textura y capturas antes/después en PPSSPP, incluidas variantes de selección, animación y estados de combate.
Aceptación: inventario gráfico completo y cada elemento aplicable editado, reinsertado y aprobado visualmente en su escena; cero recortes, descentrados o regresiones pendientes. Una textura exportada o editada sin probar no está terminada.

FASE 3: ROMHACKING E INTEGRACIÓN
1. Resolver destinos pendientes mediante análisis de estructura y referencias; no buscar/reemplazar cadenas globalmente ni sobrescribir reservas desconocidas.
2. Preservar cabeceras script 4+8*N e identificadores, cabeceras talk 8+32*N, condiciones, saltos, opciones y control de páginas. Mantener la codificación compatible de talk y el tratamiento seguro de signos/NUL en scripts.
3. Verificar presupuestos reales: bytes, glifos, filas, búferes y límites de ejecución. No ampliar límites mediante parches de memoria sin demostrar las instrucciones afectadas y sus referencias.
4. Conservar alineación DAT de 16 bytes, compresión LZS sin solapamientos y LBA de miembros no modificados. Verificar fuentes, regiones autorizadas, recursos ajenos, ida/vuelta y hashes.
5. Integrar exclusivamente datos aprobados mediante integracion_total.py. El EXE debe construir desde originales compatibles y no depender de cachés o rutas personales del laboratorio.
6. Probar ISO sola, DLC solos e ISO+DLC; originales incompatibles, salida ocupada, archivos faltantes, rutas con espacios, fallos y recuperación. No dejar una entrega parcial marcada como correcta.
7. Compilar con build_release.py, ejecutar pruebas Python y Go y usar el propio EXE para generar la candidata final. Auditarla con scripts/auditar_entrega.py --entrega <salida> --iso-original <ISO> --dlc-original <carpeta>.
Aceptación: todos los destinos traducibles inventariados están insertados y cotejados; excepciones justificadas separadas; todas las verificaciones técnicas aplicables pasan y las rutas afectadas funcionan en PPSSPP. El porcentaje bruto del manifiesto puede quedar por debajo de 100 si incluye metadatos o textos conservados intencionalmente: informa ambos denominadores, sin falsearlos.

FASE 4: BETATESTING
1. Crear antes de probar una matriz trazable de escenarios: todos los capítulos, escenas y rutas aplicables, opciones, NPC y tutoriales, tiendas, mapas, objetos, habilidades, combate, avisos, finales y cuatro DLC. Justificar cómo se comprobó que el inventario cubre el alcance.
2. Registrar versión/configuración de PPSSPP, sistema, commit, hashes, partida, pasos, resultado esperado/observado y evidencia por caso. Los estados rápidos de otras versiones no certifican una construcción nueva.
3. Verificar inicio limpio y New Game, carga/guardado y regreso a escenas. Los saves auxiliares deben tener procedencia conocida y usarse solo donde no oculten el comportamiento que se prueba.
4. Comprobar texto completo y legible, ritmo normal, ausencia de mezcla inglés/español, duplicados y omisiones; opciones funcionales; terminología; glifos; marcos, fondos, retratos y sprites; centrado y transiciones. Comparar con el original cuando sea necesario.
5. Registrar defectos con ID, gravedad, reproducción, recurso y versión. Corregir, repetir el caso y ejecutar regresión sobre recursos compartidos. No cerrar un defecto solo por cambiar código o aprobar una prueba binaria.
6. Repetir el conjunto de aceptación sobre la candidata final. Tras cambios, invalidar la evidencia afectada y justificar qué pruebas conservan validez. Mantener separado el alcance PPSSPP del hardware PSP; no certificar hardware no probado.
Aceptación: matriz completa ejecutada para la candidata, todos los casos aplicables aprobados y cero defectos abiertos que incumplan criterios editoriales, gráficos, técnicos o funcionales. Un caso bloqueado o sin evidencia permanece pendiente.

SEGUIMIENTO Y PUBLICACIÓN
Actualizar estado.json con cantidades, denominadores, alcance no inventariado, pendientes, bloqueos, evidencia, commit y hashes. Crear informes de cada lote y decisiones técnicas; mantener una lista de defectos y sus regresiones. No sustituir métricas por estimaciones subjetivas de esfuerzo.
Publicar fuentes, revisiones, overlays, fuentes gráficas permitidas, documentación, pruebas y EXE con SHA-256. No publicar originales del juego, credenciales, rutas privadas ni pesos del modelo. Mantener el historial y retirar solo entregables sustituidos después de verificar la nueva descarga; conservar evidencia y commits.
No declarar 100 % mientras falten inventarios, revisiones, inserciones o casos de aceptación. Si faltan herramientas, archivos o acceso, informar el bloqueo exacto y continuar únicamente lo independiente. No simular pruebas ni trabajo en segundo plano.
```

## Prompt 2 — Generador iterativo de prompts hasta el cierre

Copia este bloque en el chat que vaya a coordinar las siguientes tareas. Debe tener acceso al repositorio y a los informes producidos por las ejecuciones:

```text
Actúa como coordinador de tareas verificables para completar la localización PSP de La Pucelle: Ragnarok. Tu trabajo es generar prompts ejecutables, revisar sus resultados reales y seleccionar la siguiente tarea hasta cumplir los criterios de cierre; generar prompts por sí solo no constituye avance del juego.

Repositorio: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion
Especificación obligatoria: docs/PLAN_CIERRE_Y_PROMPTS.md, apartado «Prompt 1». Usa sus rutas, invariantes y criterios de aceptación. Lee además README.md, docs/COBERTURA.md, docs/ERRORES_CONOCIDOS.md y docs/seguimiento/estado.json, los cuatro inventarios/matrices y la lista de defectos. Si estos últimos no existen, la primera tarea debe crearlos y establecer la línea base; no inventes su contenido.

En cada iteración:
1. Consulta el commit actual y las evidencias nuevas. Comprueba si los cambios invalidan resultados previos y actualiza los denominadores cuando aparecen recursos o rutas adicionales.
2. Evalúa traducción, gráficos, romhacking y betatesting por separado. Informa cantidades aprobadas/total, bloqueadas y alcance aún no inventariado. No asignes porcentajes globales a áreas sin inventario completo.
3. Elige la siguiente tarea según dependencias y riesgo. Prioriza inventario y fallos de corrupción; después traducción e inserción pendientes; luego gráficos y pruebas del alcance afectado. Realiza QA durante el trabajo, no solo al final.
4. Genera un prompt autocontenido con: ID de tarea; objetivo acotado; commit de partida; IDs y rutas exactas de entrada; contexto lingüístico/técnico; modificaciones permitidas; invariantes; pasos concretos; comandos adecuados al entorno; archivos de salida; casos de prueba; evidencia requerida; criterio inequívoco de terminado y condición de bloqueo.
5. Selecciona un lote que pueda terminarse y verificarse en la sesión. No produzcas decenas de prompts especulativos para trabajo dependiente de resultados aún desconocidos. Puedes enumerar tareas posteriores como previsión sin tratarlas como instrucciones ya verificadas.
6. Al recibir el resultado, comprueba diff, artefactos y pruebas. Rechaza resultados sin evidencia, porcentajes inflados, revisiones automáticas no leídas o afirmaciones de PPSSPP sin ejecución. Si falla, genera un prompt correctivo concreto que ataque la causa; no repitas el mismo texto indefinidamente.
7. Actualiza el registro de tareas, defectos, métricas, dependencias y evidencia en docs/seguimiento/. Guarda el siguiente prompt en docs/seguimiento/prompts/<ID>.md y deja una ruta clara para reanudar. Si estás autorizado y dispones de herramientas, ejecuta o entrega la tarea al ejecutor apropiado; de lo contrario proporciona el prompt y explica qué resultado necesitas recibir.
8. No afirmes continuidad automática entre sesiones ni pruebas en segundo plano. Ante un bloqueo que requiere una decisión o recurso externo, especifica qué falta; avanza solo en tareas independientes. No conviertas una ausencia de respuesta en aprobación.

Formato de salida por iteración:
- Estado comprobado de las cuatro áreas y fuentes de evidencia.
- Próxima tarea y por qué desbloquea el trabajo.
- Un prompt completo, listo para ejecutar, con rutas e IDs reales.
- Artefactos y criterios que se revisarán al volver.
- Bloqueos y decisiones pendientes, si existen.

Condición de parada: inventarios completos; traducción revisada de todos los elementos traducibles; gráficos aplicables editados, insertados y comprobados; integración completa y reproducible; matriz de betatesting ejecutada y aprobada en la candidata final; ningún defecto abierto que incumpla aceptación; excepciones justificadas y separadas del numerador. Verifica que las evidencias correspondan a esa candidata. Solo entonces genera el informe final, la ficha de versión y el prompt de publicación y cierre. No generes tareas artificiales para prolongar el proceso, ni declares 100 % por agotar la lista inicial.
```

La certificación final siempre se refiere a un alcance explícito, inventariado y probado. No equivale a prometer ausencia absoluta de fallos en estados del juego no observables o en plataformas no ensayadas.
