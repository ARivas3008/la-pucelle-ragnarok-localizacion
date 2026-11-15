# Matriz de formato, límite, técnica y prueba de aceptación

| Recurso | Dónde vive | Unidad de presupuesto | Inserción aceptable | Bloqueador |
|---|---|---|---|---|
| cadena fija de HUD | char/magic/skill/etc. DAT | bytes incluyendo NUL, también píxeles | caber dentro de campo verificado, no invadir estadísticas | no cabe; ancho visual |
| cadena EBOOT | EBOOT.BIN | campo y decodificador del menú | sustitución exacta con SHA y referencia conocida | punteros/código sin localizar |
| diálogo talk | SCRIPTPACK | longitud variable + cajas | grupo atómico, reubicación de todos los consumidores | bytecode incompleto |
| script evento | START / SCRIPTPACK | un byte de longitud incluye NUL; índices | recalcular longitudes y tabla con análisis de anclas | puntero interno o sincronización |
| glifos | fontB | mapa de bytes y píxeles de atlas | reutilizar ranura libre e instalar en cada paquete | gaiji no interpretado/atlas |
| rótulos en textura | sys*.txp, BGPACK | UV, paleta, píxeles | delta regional con SHA de textura y prueba en pantalla | swizzle, clipping, geometría |
| prólogo/cinemática | scripts, capas, vídeo según escena | depende de formato | determinar si rótulo es script, textura o PMF | formato no identificado |
| contenedor | LZS, NISPACK, DAT, ISO9660 | offsets, tamaños, alineación | reconstrucción reversible y relectura | CRC/índice/offset incorrecto |

## Qué significa dividir una línea en dos

Antes de partir, comprobar (1) que la línea forma parte de una intervención con 2–3 segmentos, (2) que el control de continuación existe y pertenece al mismo hablante, (3) que las nuevas longitudes caben en el bytecode sin introducir opcodes desconocidos, y (4) que la escena funciona en PPSSPP. Una «caja más grande» solo cambia la geometría visual: no arregla un índice que apunta a memoria incorrecta.

## Ejemplo simple: campo de 36 bytes

Con texto codificado a 34 bytes y NUL de 1 byte: se consumen **35 bytes = 280 bits**, dejando 1 byte. Con texto a 36 bytes más NUL: **37 bytes = 296 bits**, excede. Si solo se dispone de 36 bytes físicos, la traducción debe compactarse o utilizar otro esquema comprobado. Un carácter acentuado de gaiji puede costar 2 bytes aun cuando ocupe un glifo en pantalla.

La decisión final debe incluir **ancho visual** medido con la fuente, no solo el cálculo de memoria.

## Compresión y alineación

El tamaño del texto descomprimido, los offsets de DAT, los offsets de NISPACK y el tamaño comprimido de LZS son cuatro números diferentes; ninguno reemplaza al otro. Una frase que cabe en un campo no implica que el contenedor comprimido pueda reemplazarse sin relocalizar su entrada ISO9660.
