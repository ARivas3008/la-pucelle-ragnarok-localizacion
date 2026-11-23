# Cobertura de v0.19.0

Auditoría binaria realizada el 19-11-2026 y repetida el 23-11-2026 sobre la ISO generada por el motor del ejecutable. Publicación preparada el 23-11-2026.

**21.805 / 26.258 = 83,04 % de unidades técnicas insertadas y cotejadas.** No se conoce todavía un porcentaje fiable de texto funcional en todas las escenas del juego. La prueba visual histórica de v0.18.3 cubrió el prólogo, no sus 7.901 unidades completas.

| Clasificación del manifiesto | Unidades |
|---|---:|
| Diálogo dentro de bloques insertados verificados | 18.224 |
| Script insertado y verificado | 503 |
| Campo fijo que coincide con su revisión | 3.078 |
| Diálogo pendiente | 3.527 |
| Campo sin traducir | 419 |
| Campo modificado pendiente de cotejo editorial | 335 |
| Campo original ya coincide con la revisión | 109 |
| Script conservado: Now Loading | 1 |
| Texto gráfico pendiente de revisión visual | 62 |
| **Total** | **26.258** |

Las primeras tres filas forman el 83,04 %. Las demás se mantienen fuera de ese indicador, incluso si parte del texto modificado resulta útil. Las 62 unidades gráficas no representan necesariamente todas las texturas que contienen texto.

## Apariciones físicas y texto fuera del manifiesto

El compilador recorre 20.650 bloques físicos de diálogo: 18.601 insertados, 1.686 pendientes y 363 bloques de signos conservados. Un bloque puede reunir varias unidades, y un grupo editorial puede aparecer en varios destinos. Los 1.113 segmentos adicionales aprobados reutilizan revisiones existentes y 500 propuestas nuevas; no se suman otra vez al porcentaje.

Los menús de EBOOT incluyen 254 sustituciones del catálogo y 136 etiquetas adicionales. Algunas quedan fuera del manifiesto o requieren cotejo, por lo que tampoco se suman sin más al numerador. Se conservan variables, iconos, límites de campo y terminadores.

## Pruebas y límites

La construcción completa por el `.exe` terminó con código 0 y generó ISO más cuatro EDAT. Los cinco contenedores se descomprimieron para comprobar identidad tras la compresión; el auditor releyó los recursos de salida, comprobó cada intervalo de inserción y verificó los diarios reversibles.

Esto detecta corrupción estructural e inserciones ausentes, pero no garantiza selección correcta de cada diálogo, composición visual, centrado ni todas las rutas de eventos. La verificación de esas condiciones en PPSSPP está pendiente para esta entrega.

Evidencia: [resumen JSON](informes/cobertura_v0.19.0.json), [detalle por unidad CSV](informes/cobertura_v0.19.0.csv), [construcción y hashes](informes/construccion_v0.19.0.json).

## Guía de Neoseeker

La referencia aportada es [La Pucelle: Tactics FAQ/Walkthrough v1.10](https://www.neoseeker.com/la-pucelle/faqs/78770-a.html), de CrimsonPhantom, para PS2. La guía excluye diálogos de NPC itinerantes y tutoriales; además, no cubre todos los añadidos de Ragnarok ni sus DLC. Por tanto, no constituye un inventario completo de este juego.

El cotejo exacto normalizado encontró 29 coincidencias largas en el manifiesto: 28 de script y una gráfica. Es una comprobación parcial limitada por idiomas y segmentación, no una medición del porcentaje traducido. El informe y el script se conservan en el laboratorio; el texto completo de la guía no se redistribuye.
