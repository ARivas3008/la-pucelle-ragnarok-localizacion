# Rúbrica operativa de localización rápida y reproducible

## Principio rector
Optimizar el **tiempo hasta una versión utilizable y verificable**, no maximizar el porcentaje aparente. Las etapas se paralelizan solo después de definir contratos; el tiempo ahorrado por dividir un corpus se pierde si luego se cambian IDs, offsets y glosario.

## Fase 0 — Alcance, licencia, versiones, laboratorio
**Entradas:** copias legítimas del juego, plataforma, idioma fuente, versiones de ISO/DLC, derechos de distribución, capturas iniciales. Registrar SHA256 y tamaño, y guardar en solo lectura.

**Entregables:** inventario inicial, árbol de rutas, manifiesto de hashes, matriz de riesgo y CI vacío. No subir recursos comerciales a repositorios públicos.

**Puerta:** identificar versión y posibilidad de reproducir el arranque del original.

## Fase 1 — Ingeniería inversa mínima viable
Reconocer el sistema de archivos externo, contenedores, compresión, índices, cadenas y codificación. Crear lectores read-only y exportar metadatos sin mezclar originales con traducción. Documentar cabeceras, endianness, offsets, punteros y checksums. Los recursos no reconocidos se etiquetan DESCONOCIDO.

**Regla de rapidez:** empezar por un solo ejemplo representativo de cada familia (diálogo, HUD, ejecutable, textura y vídeo); probar extracción → reconstrucción idéntica sin tocar textos. Congelar ese adaptador y automatizar todo el lote. No escribir expansiones hasta demostrar reversión.

**Puerta:** 100 % de archivos que se van a modificar tienen método de extracción + reempaquetado reproducible, o bloqueo justificado por tipo.

## Fase 2 — Extraer todas las unidades y rastrear contexto
Cada unidad almacena unit_id, grupo_id, recurso, offset_original, segmento, original, idioma, escena, hablante, contexto_previo/siguiente, controles, hash y referencia al archivo padre. Separar contenido humano de metadatos, pseudotextos y marcadores. Registrar huecos y continuaciones sin mapeo.

**No inventar grupos por longitudes**: una intervención puede tener varias unidades y opcodes, y una unidad puede ser una etiqueta del HUD. Las relaciones se determinan por estructura + contexto.

**Puerta:** IDs únicos, orden estable, originales verificables en fuente, cobertura de extracción y excepciones documentadas.

## Fase 3 — Glosario y memoria de traducción
Antes de usar MTL, aprobar nombres propios, términos de interfaz, convenciones de tratamiento, símbolos, fórmulas, tags y convenciones de acentos. Crear una memoria de coincidencias exactas/segmentos equivalentes para evitar retrabajo. Mantener una sola autoridad editorial del glosario.

**Puerta:** inventario de variables y tokens; políticas para títulos, nombres, signos, y variantes de un mismo menú.

## Fase 4 — Reparto y traducción MTL como BORRADOR
Ejecutar planificar_corpus.py con límite de 40–60 **grupos** por microtanda, nunca cortar grupo o escena. Si hay varios revisores, un corpus/rama/propietario y CI que rechace cambios fuera de la carpeta de cada revisor.

La MTL inicial puede producir un CSV borrador con unit_id, original, mtl_es, modelo/método, confianza y alertas. **No aprobarla automáticamente**, especialmente para japonés elíptico, escenas emotivas, chistes, diálogos cortados y nombres. Validar diccionario y preservar `{0}`, `%s`, `<color>` y controles; mantener reversión al texto original.

**Puerta:** todos los grupos con borrador o causa de ausencia, sin alterar el archivo original.

## Fase 5 — Revisión humana por contexto y QA
El revisor lee unidades contiguas y el evento completo, coteja japonés e inglés si existen, revisa tono, narrador, relaciones entre personajes, intención y terminología. Introducir es_revisado y estado (revisado / requiere_investigacion). Todo lo dudoso tiene nota, no una aprobación forzada.

QA automático: IDs, filas, hashes, etiquetas, controles, Unicode, sintaxis, espacios y glosario. QA humano: fluidez, humor, fidelidad, continuidad, nombres y boxes. Integrar en rama solo tras PR y QA.

**Puerta:** versión editorial aprobada por grupo, con dudas pendientes identificadas.

## Fase 6 — Presupuesto de almacenamiento por TIPO
**No medir en caracteres, ni decir que 50 «bits» equivalen a 50 letras.** Calcular el tamaño de los bytes realmente codificados, controles binarios, terminador NUL, padding, tablas y alineación. Un carácter CP932/gaiji puede ocupar dos bytes, un ASCII uno; las fuentes y el ancho en píxeles son una restricción distinta.

En La Pucelle:
- Texto HUD fijo: campo de N bytes ⇒ texto codificado + NUL **≤ N**, sin atravesar el registro.
- Opcode de script 0x32: longitud de un byte incluye NUL ⇒ **≤255 bytes por opcode**; además hay que actualizar la tabla de anclas y probar escena.
- talk: cadena de longitud variable con punteros internos; agrupar por intervención y reubicar únicamente con referencias verificadas; no introducir un segundo cuadro a ciegas.
- EBOOT: solo cambios de campos documentados; expansión requiere localizar consumidores.
- Atlas/texturas: el número de bytes del texto no aplica; medir coordenadas, atlas, UV, paleta y ancho de glifo.
- Introducción/vídeo: separar elementos script, textura y vídeo con observación.

Ejecutar verificar_presupuesto.py; las entradas sin capacidad acreditada quedan CAPACIDAD_FISICA_NO_DOCUMENTADA. Las entradas con controles requieren parser binario específico y NO se aprueban por una estimación textual.

**Resolución de excesos, orden de menor a mayor riesgo:** abreviar manteniendo sentido → usar padding comprobado del mismo campo → redistribuir líneas dentro de la misma intervención si el bytecode lo permite → reubicar cadena y TODAS las referencias → añadir un segundo cuadro únicamente si el script lo admite → modificar geometría de UI/código si se entiende su origen. Cada elección deja justificación.

**Puerta:** estado por unidad y grupo, no existen escrituras fuera de campo ni fuentes faltantes; QA visual pendiente explícito.

## Fase 7 — Compilación e inserción experimental
Construir a partir de originales exactos, registrar hash base y delta, validar lectura de cada miembro, actualizar índices/offsets/tamaño de archivo, comprobar compresión reversible. Si una intervención falla, **no insertar media intervención**: rollback atómico. Generar ISO/DLC nuevos, nunca reemplazar copias origen.

**Puerta:** relectura binaria, comparación de vecinos y test de inicio.

## Fase 8 — QA visual y jugabilidad por matriz de riesgos
Probar por clase de contenido: intro, menú, HUD, inventario, combates, guardado, carga, cada DLC, escenas con nombres largos, acentos, cambios de hablante y textos de borde. Captura misma pantalla del original y parche. No basta con ejecutar sin crash.

Distinguir cuatro estados: SIN_TRADUCCION, APTO_BINARIO, INSERTADO_EN_PRUEBA, VERIFICADO_EN_JUEGO. Verificar fuentes, clipping, tamaño de caja y referencias. La cobertura del 100 % se mide por **unidades válidas**, no por cadenas sintéticas de laboratorio.

**Puerta:** todas las unidades han pasado prueba o tienen exclusión justificada; no hay cortes, errores gráficos ni textos pendientes que deban traducirse.

## Fase 9 — Publicación y repetición
Guardar README, CHANGELOG, documento por versión, código fuente, pruebas, lista de hashes, informe por unidad y bitácora de regresiones. Para distribución pública, usar parches/deltas aplicados al original del usuario; no distribuir ISOs, EDAT ni assets comerciales.

## Distribución eficiente del equipo

| Rol | Trabajo en paralelo | Contrato |
|---|---|---|
| Ingeniería formatos | parsers, extracción, repaquetado y offsets | versiona esquemas, IDs y hashes |
| Coordinación | glosario, controversias, migración de manifiesto | protege datos maestros |
| Traducción | MTL inicial y revisión de corpus | escribe solo su revisión |
| Integración | presupuestos, fuentes, punteros, builds | rechaza cambios inseguros |
| QA | matrices de escenas, PPSSPP, reportes visuales | no marca aprobado por prueba de bytes |

**Ruta crítica mínima:** lector reversible → extracción con IDs estables → primeros corpus en paralelo → inserción de humo temprana → QA → revisión de bloqueos. Traducir 100 % primero y averiguar después qué se puede insertar suele provocar más retrabajo.

## Indicadores por iteración

- % unidades extraídas con fuente verificada.
- % grupos revisados y aprobados; % pendientes de investigación.
- % unidades con presupuesto conocido y codificación soportada.
- % unidades insertadas y re-leídas en copia.
- % unidades/escenas verificadas visualmente en PPSSPP.
- errores de variables, clipping, punteros y texturas por gravedad.
- regresiones por versión / tiempo de reparación.

No sumar varias métricas de universos superpuestos. Congelar los denominadores para comparar versiones y documentar exclusiones.

## Aplicación concreta a La Pucelle

El repositorio principal ya proporciona maestro de 26 258 unidades, 15 corpus, QA de grupos, glosario y herramientas v0.1–v0.15. Los 14 punteros de script en segundo byte CP932 siguen siendo un ejemplo de **bloqueo legítimo** aunque la traducción editorial esté revisada. La [investigación forense](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/blob/main/parcheador/docs/FORENSE_ESTRUCTURA_JUEGO.md) muestra cómo documentarlos sin forzar que el juego acepte datos corruptos.
