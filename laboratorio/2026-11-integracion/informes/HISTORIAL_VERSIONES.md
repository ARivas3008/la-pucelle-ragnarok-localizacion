# Historial de versiones y conservación

Actualizado el 17 de noviembre de 2026. Se conservan los originales, el corpus, el código y la evidencia histórica. La limpieza elimina entregables generados; no borra la explicación de cómo se construyeron.

## Estado conservado tras la limpieza

- Ejecutable: `11_Entrega_v0183/LaPucelle_Parcheador_ES_GUI_v0.18.3-fijo-qa.exe`. Es la última versión publicada del parcheador; no incluye aún las modificaciones del laboratorio 12.
- ISO de trabajo: `12_Integracion_total/prueba_correcciones/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso`, con sus cuatro EDAT en `ULJS00244`. Es experimental y su última revisión no tiene comprobación visual en PPSSPP.
- Limpieza realizada: 102 archivos, 22.787.213.148 bytes. Inventario individual y resultado en `limpieza_versiones_ejecutada_20261117.json`.
- Los enlaces antiguos a ISO/EXE eliminados en documentos históricos describen entregas pasadas y ya no son rutas de descarga válidas.

## Versiones documentadas

“Sin retirada documentada” significa que la documentación no registra una eliminación; no se ha inventado una diferencia a partir del número de versión.

| Versión | Qué agrega o corrige | Qué quita, desactiva o sustituye |
|---|---|---|
| 0.1 | Inventario de 26.258 unidades, formatos ISO y contenedores, base del motor. | Sin retirada documentada. |
| 0.2 | Tratamiento LZS y fuente B. | Sin retirada documentada. |
| 0.2.1 | Compilación de Windows con Visual Studio. | Corrige el procedimiento de construcción anterior. |
| 0.3 | Lanzador inicial para Windows. | Sin retirada documentada. |
| 0.4 | Interfaz gráfica y selección de ISO/DLC. | Sustituye el flujo exclusivamente manual. |
| 0.4.1 | Medición de texto ancho, bloqueo e informes de desbordamiento. | Rechaza inserciones que exceden capacidad. |
| 0.5 | Inserción atómica de diálogos y tratamiento ASCII de EBOOT; protección de atlas. | Evita aplicar parcialmente un diálogo. |
| 0.6 | Auditoría SHA de atlas y trabajo de etiquetas de combate sys3/sys4. | Sin retirada documentada. |
| 0.7 | Menús y cuatro narraciones de script00. | Sustituye esas cadenas originales por español. |
| 0.8 | Campos fijos con relleno cero, HUD, menús y fuentes. | Elimina residuos de texto en los campos intervenidos. |
| 0.9 | Prototipo de reubicación talk con diario reversible. | Sin retirada documentada; no equivale a validación completa del intérprete. |
| 0.10 | Extensión a 21 talk, 837 continuaciones y seis contenedores; anexado experimental a ISO. | Sustituye la limitación a los primeros recursos experimentales. |
| 0.11 | Auditoría de 66 recursos y 4.507 unidades; 3.664 candidatos estructurales. | Sin retirada documentada. Candidatos no significa inserciones comprobadas. |
| 0.12 | Propuesta de 197 reducciones, 94 textos de script adicionales y cinco campos especiales. | Sin retirada documentada; las propuestas todavía necesitan integración. |
| 0.13 | Integra las 197 reducciones opcionales y cuatro alternativas; corrige límites. | Sustituye formulaciones largas solo cuando se activa la opción. |
| 0.14 | Inserción variable de 489 textos 0x32 y reconstrucción ISO/DLC. | Mantiene 14 unidades bloqueadas por referencias según el analizador de entonces. Ese diagnóstico fue revisado posteriormente. |
| 0.15 | Investigación de 14 unidades y 15 supuestas referencias interiores. | No agrega cambios jugables; conserva los bloqueos. |
| 0.16 | Fase experimental CP932 opcional y segunda etapa en la interfaz. | No sustituye por defecto el modo conservador. |
| 0.17 | Diálogos paginados atómicos, cuatro correcciones de contexto y salida separada para PPSSPP. | Sustituye inserciones parciales de los casos corregidos. |
| 0.17.1 | Recupera DLC sin cambios desde la primera etapa. | Corrige la omisión de archivos en la salida final. |
| 0.17.2 | Diagnóstico de EBOOT/atlas y corrección de once segmentos. | Desactiva modificaciones de EBOOT/atlas por defecto; no resolvió toda la corrupción. |
| 0.17.3 | Conserva LBA cuando el recurso cabe en su espacio reservado. | Evita anexados innecesarios. |
| 0.17.4 | Corrige relleno de sectores y rechazo incorrecto de 26 bytes; muestra stderr real. | Sustituye el cálculo de reserva anterior. |
| 0.18.0 | Incorpora 15 revisiones al ejecutable; corrige opciones EBOOT y doble etapa de scripts. Registra 8.156 unidades y 489 scripts. | Sustituye la entrega 0.17.4. Fue descartada como base jugable por fallos gráficos reportados desde New Game. |
| 0.18.1 | Alineación de miembros DAT a 16 bytes; recuperación de marcos. | Sustituye contenedores mal alineados. Persistía transparencia incorrecta. |
| 0.18.2 | Compresión LZS sin referencias solapadas; recuperación del menú opaco. | Retira la compresión incompatible. Persistían nieve y sprites erróneos con scripts reubicados. |
| 0.18.3 | Scripts de tamaño fijo; 234 textos de script, 7.901/26.258 unidades técnicas. Prólogo comprobado en PPSSPP; 69 pruebas Python correctas, cinco omitidas, cuatro Go correctas. | Retira la reubicación de scripts del ejecutable y mantiene EBOOT original en la configuración comprobada. Sacrifica cobertura para recuperar estabilidad. |

Fuentes: fichas individuales `02_Motor_parcheador_v0174/parcheador/docs/versiones/v0.*.md`, ficha 0.18.0 en `10_Trabajo_v0181/fuente/parcheador/docs/versiones/`, `10_Trabajo_v0181/informes/RESULTADOS_AISLAMIENTO.md` y `11_Entrega_v0183/LEEME.md`. Las cifras de esta tabla son históricas, no la auditoría de la ISO de trabajo actual.

## Construcciones posteriores de laboratorio, sin número de entrega

| Construcción | Agrega o investiga | Retira o sustituye; estado |
|---|---|---|
| prueba_compacta | Ensayo de diálogos con ASCII compacto. | Descartado: el intérprete talk consume pares y algunos bytes ASCII son controles. ISO eliminada. |
| prueba_integrada | Ensayo ampliado de corpus y reconstrucción. | Sustituido por el análisis completo del formato. ISO eliminada. |
| prueba_scripts_corregidos | Cabecera real de scripts `4+8*N`: offsets e identificadores separados. | Sustituye la interpretación `4+4*N` que generaba falsas referencias y corrupción. ISO eliminada; evidencia y fuentes conservadas. |
| prueba_dialogos | Compilador de bloques talk completos, controles preservados, paginación y ampliación verificada del búfer. | Sustituye la inserción fragmentaria y el experimento ASCII. ISO eliminada al pasar a correcciones. |
| prueba_correcciones | 17.434 bloques talk aplicados, 3.216 pendientes; 503 textos de script. Correcciones de Iglesia, Panza del Diablo, Cuarto de Salade, Comprar y Prica total; puntuación segura y alias de fuente. | Sustituye signos ASCII que podían consumir el terminador y mostrar residuos. No es aún un nuevo EXE ni una traducción completa. Última ISO conservada. |

## Regla para las siguientes versiones

1. Construir la candidata en un directorio temporal identificado, desde originales verificados y datos de traducción.
2. Ejecutar las comprobaciones de formato, controles, fuentes, integridad y generación mediante el EXE. Registrar cobertura real y limitaciones visuales.
3. Registrar versión, fecha, hashes, añadidos, correcciones, elementos retirados y pendientes. No convertir una prueba de estructura en una certificación de PPSSPP.
4. Promover la candidata a última entrega. Después, eliminar el EXE, ISO y DLC generados de la entrega sustituida, con lista exacta de rutas dentro del proyecto y un diario nuevo de eliminación.
5. Mantener únicamente los entregables de la última versión. Conservar fuentes, corpus, originales e informes históricos. No borrar la versión vigente si la candidata falla.

El corpus traducido, las unidades técnicas insertadas, las apariciones físicas y los textos gráficos son medidas distintas. Los informes futuros deben separarlas.
