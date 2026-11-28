# RC041 REV6 BETA03 Compacta — registro vivo de QA
Fecha local: 2026-11-27 (Perú). PPSSPP 1.20.4, OpenGL por software, Xvfb 960×544, audio no certificado.
EXE SHA-256: `327d31fcf540f13eb9fd3244dc1f46abba27e8dbddfc11dedbc01ef572979717`.
ISO SHA-256: `7f10a641fe29cb40816d8aa4040d82b4adad3e74715dcbe62fae1e3a8059e691`.
Rama documental basada en BETA02 Compacta; no implica que el código fuente BETA03 esté publicado. No se modifican main, corpus, ISO ni DLC. Evidencias citadas por nombre local, no publicadas como binarios en GitHub.

## Incidencias abiertas
| ID | Prioridad | Hallazgo | Evidencia | Criterio de aceptación |
|---|---|---|---|---|
| B03-001 | Alta | En Objetos, «Pastilla para la tos» y «Recupera HP.» aparecen concatenados, con invasión del campo. Causa técnica no confirmada. | qa_beta03_menus/03_objetos.png | Auditar longitud, terminadores y límites de campos; nombre y descripción separados y legibles en todos los objetos, sin alterar índices. |
| B03-002 | Alta | «Desechar» desborda el botón de inventario. | 03_objetos.png | Rótulo completo dentro de su botón en todas las resoluciones; preservar UV y función. |
| B03-003 | Alta | «Habilidad» excede su recuadro en Estado. | 10_estado_prier.png | Ajustar ancho o abreviatura aprobada, sin recortes. |
| B03-004 | Media | Espaciado entre caracteres relativamente amplio, diálogos e interfaz; revisión de métricas FontB. | qa_beta03/dialogo_completo.png; 10_estado_prier.png | Proporciones legibles, sin solapes ni desbordes; probar acentos, ñ, signos y números. |
| B03-005 | Media | Abreviaturas estadísticas ATK, HIT, NEXT y mezcla HP/PV. No todas las siglas inglesas son necesariamente defectos; decidir glosario. | 10_estado_prier.png; 26_ordenar_real.png | Convención uniforme en todos los menús, tutoriales y combate; no cambiar HP/PV sin revisar glosario. |
| B03-006 | Alta | Título de guardado en inglés: Chapter 1 - On the Job Training, confirmado en SAVEDATA_TITLE del PARAM.SFO generado por el juego. | 31_guardar_cancelado.png; 42_lista_carga.png; 43_carga_confirmacion.png | Traducir títulos de todos los capítulos en origen; guardar en ranura nueva y comprobar SFO y carga. No editar solo el SFO existente. |
| B03-007 | Alta | SAVEDATA_DETAIL generado por el juego contiene Level, Clear Number, Play Time. | 42_lista_carga.png; lectura directa PARAM.SFO | Traducir etiquetas (Nivel, término de partidas completadas a validar, Tiempo de juego), preservar valores y formato. |
| B03-008 | Baja / configuración | Load, Back, Enter, Load completed, Save completed en interfaz del sistema PSP configurado en inglés. No atribuir al ROM sin comparación en idioma español. | 42_lista_carga.png; 43_carga_confirmacion.png | Repetir con idioma PSP español, distinguir cadenas del sistema y juego. |
| B03-009 | Media | Redacción del aviso Fin mejorable; pendiente transcripción exacta y revisión contextual. | 27_fin.png | Texto natural, sentido y confirmación inequívocos. |
| B03-010 | Baja / entorno | Renderizado lento por software; audio físico no validado. No es un fallo probado del juego. | Registros PPSSPP | Repetir en hardware acelerado / PSP real. |

## Pruebas dinámicas acumuladas (sin extrapolar a 137 casos)
- Arranque BETA03, menú principal, atlas «Presenta»: PASS observado.
- Inicio de partida mediante estado heredado BETA02; avanzar diálogo, omitir escena, acceder iglesia; guardar y restaurar estado BETA03: PASS observado; partida desde cero independiente pendiente.
- Iglesia → Calle Mayor → NPC junto al arco → Purificación → Ataques de purificación → regreso a Iglesia: PASS en páginas examinadas; cartel «Iglesia» confirmado. Otras ramas no certificadas.
- Menú general y opciones: accesibles; cambio de cursor comprobado.
- Objetos, Equipar, Estado, Habilidades, Ordenar: accesibles; incidencias visuales abiertas; no equivale a todas las operaciones funcionales.
- Entrenar: no disponible en progreso actual.
- Fin: vuelve al título. Guardar: ranura nueva creada y SFO leído.
- Seguir → seleccionar ranura → Load completed: PASS para lectura del guardado; retorno al patio de la iglesia confirmado visualmente (45_carga_escena.png). Guardado normal funcional; no depende de save states.
- Pendientes: todas las tiendas, combate, habilidades ejecutadas, entrenamiento, capítulos y finales, DLC en ejecución, regresión tipográfica, títulos de guardado de todos los capítulos, comparación PSP español.

## Política de cierre
Cada incidencia requiere reproducción antes/después en la misma ruta, captura, hash de build, control de datos y resultado funcional. Los nombres de evidencia son referencias a archivos locales de QA, no enlaces publicados. No declarar 100 % por un arranque o por cobertura parcial.
