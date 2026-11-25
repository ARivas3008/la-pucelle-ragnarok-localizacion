# ROM-030 — Reconciliación de avances y puerta de cierre integral

Base 9a61ea6c6b698abd561003a2258ce4a5aa3e270e, ROM029 PR54 abierto, cuatro workflows de esa base success: motor 45646820049, corpus 45646820092, inventarios 45646819936 y Windows 45646820158. Se recuperó el CSV histórico completo por blob c2c8a013e1b58063c42e70dcff5beef97322b5f8, 26.258 filas y ocho estados, y se cotejaron los contadores. Auditoría documental real, no ejecución de ISO en esta sesión.

## Contabilidad
21805 unidades del informe integral histórico. Se añaden 940 DLC, 247 tablas ISO, 5 coincidencias exactas fuera de esos lotes = 22997/26257 (87,5843%). La unidad 1630 es metadato, no texto. No se contabilizan gráficos sin revisión visual. De las 3260 filas pendientes, 3006 son TALK ISO, 192 rótulos EBOOT y 62 gráficos. Los 192 rótulos ya existían físicamente en el informe histórico como CAMPO_MODIFICADO_COTEJO_PENDIENTE; todos coinciden con el menú contextual de ROM029 y conservan los marcadores printf. Se corrigen los rótulos de velocidad máxima de movimiento y texto (3774/3778) para distinguirlos del rápido. No se contabilizan esas dos correcciones como binario nuevo. Si se aceptan las 190 adaptaciones históricas sin cambio en el motor como evidencia de reinserción técnica, cobertura agregada 23187/26257 (88,3079%), 3070 pendientes. No es aprobación editorial ni visual. Para texto solamente, 23187/26195 (88,5169%). El 83,04% histórico integral no se sustituye.

## Cambios integrados en código
- Actualizado menu_eboot_contextual.csv (dos rótulos distintos, sin tocar corpus).
- Nuevo auditor reproducible scripts/auditar_rom030_agregado.py, ligado al flujo QA inventarios. Comprueba anclas del manifiesto, solapamientos, filas históricas, adaptaciones y variables. Genera lista de pendientes por recurso con --salida.
- Informe y evidencia JSON de los 192 rótulos contrastados, y estado.json actualizado para no declarar DLC originales ausentes.
- Próximos pasos: reconstruir la ISO con integracion_total.py, reconstruir/consolidar los DLC con el paquete ROM029 aportado, ejecutar auditar_entrega.py sobre ambos y revisar cualquier fallo antes de promover. Priorizar las 3006 TALK ISO históricas por recurso, sin reutilizar IDs de origen como inserciones de destino.

## Bloqueo real
No se pudo abrir el entorno de ejecución local (ClientError/TransportError en herramientas de terminal/Python). Files recuperó el ZIP ROM029 y el 7z DLC, pero el archivo ISO comprimido de 332791211 bytes supera su límite de materialización de 104857600. No se ha construido ni integrado un binario nuevo, ni se ha ejecutado PPSSPP. No se publica ningún recurso comercial. No declarar 100% integral hasta la relectura real de la candidata única y cotejo de todos los IDs.
