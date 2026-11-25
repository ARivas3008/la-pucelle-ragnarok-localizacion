# ROM-032 — Consolidación conservadora de los avances revisados

25/11/2026 Lima. Rama integracion/romhacking-conservadora-20261125. Base ROM-031 a78e9e8d21580bd11a2751d1780a40914c99f64d. Se comprobó mediante comparaciones GitHub que los 12 cortes (main y ROM018–030) son ancestros de ROM031, con cero commits ausentes en esa dirección. Los cuatro workflows de ROM031 terminaron success, incluida compilación Windows (IDs 45658486576, 45658486548, 45658486426, 45658486399). Se crea una única rama y PR directo a main, en borrador: no se modifica main ni se aplica force push. No se repiten commits.

## Evidencias incorporadas
Se registra y verifica el hash Git de 30 archivos de informes, adaptaciones compactas y verificadores, incluidos ROM016–023 (tablas ISO), ROM024–029 (DLC), ROM030 (EBOOT/contabilidad) y ROM031 (subgrupos y variables). El script auditar_rom032_consolidacion.py invoca la conciliación ROM030 y verifica el cierre aritmético del inventario y el estado; se agrega al CI. Código y evidencia versionada reunidos, no binarios.

| Métrica | Resultado |
|---|---:|
| Integral histórica | 21805/26258 (83,04 %) |
| Agregada sin 190 adaptaciones EBOOT históricas | 22997/26257 (87,58 %) |
| Agregada con 190 adaptaciones EBOOT históricas | 23187/26257 (88,31 %) |
| DLC traducibles resueltos entre pilotos | 3536/3536 |
| Ocho tablas ISO resueltas entre pilotos | 1832/1832 |
| Pendientes agregados | 3070 |

Pendientes: 3006 TALK ISO, 2 EBOOT y 62 gráficos. La unidad 1630 es metadato, preservada. No sumar nuevamente los pilotos al contador histórico. Las adaptaciones compactas y cambios de páginas conservan el alcance de las pruebas previas, no aprobación visual.

## Bloqueo y promoción
No se pudo abrir el entorno local (ClientError). La ISO original no se pudo materializar en ROM031 por tamaño, y no se dispone de una candidata única ISO+DLC releída. El ZIP privado ROM029 contiene la unión de pilotos y no está completamente versionado en GitHub. Se mantiene el PR en borrador y las pruebas funcionales pendientes. El nuevo auditor valida documentación, no reinserción física. No publicar ISO/EDAT/DAT/LZS ni fuentes comerciales.

Para cerrar: recuperar originales y checkout completo, reproducir pilotos ISO y DLC (incluido el ZIP de fuentes ROM029), unir recursos disjuntos sin sobrescribir controles ni tablas, ejecutar integracion_total.py y auditar_entrega.py, cotejar cada ID restante y ejecutar PPSSPP. No declarar 100 % por sumar evidencia documental.
