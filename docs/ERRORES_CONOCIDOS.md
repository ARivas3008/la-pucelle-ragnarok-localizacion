# Clasificación y seguimiento de las 24 capturas

Las capturas corresponden al ZIP aportado por el usuario. Los números remiten
a las hojas `capturas_usuario_0.png` a `capturas_usuario_5.png`.
No se considera completada una corrección solo por existir en el corpus.

| Tipo | Evidencia | Origen localizado | Corrección y validación pendiente |
|---|---|---|---|
| Lectura después del final de frase | 0, 7: «sia,sia» | Script01, grupos 3311/3313; el texto binario es correcto. EBOOT 0x0885be1c consume un segundo byte para la coma ASCII y salta el NUL | Codificar signos ASCII 0x21..0x2d como CP932 ancho. Comprobar ambas narraciones en PPSSPP |
| Abreviación impropia | 6: «Igles.» | EBOOT 708478, grupo 3025, ajuste de menú | Iglesia completa usando reserva NUL verificada, sin desplazar referencias |
| Topónimo inconsistente | 5, 13: Estómago del Diablo / Panza diabla | Corpus 13926 y menú 3031; tablas de mapa y diálogos | Unificar en «Panza del Diablo», conservar nombre completo |
| Recorte de nombre propio | 14: «Cuarto del padre Sala» | char.dat, grupo 12935 / DLC 136 | Etiqueta «Cuarto de Salade», comprobar límite visual y búfer |
| Nombre demasiado largo sin insertar | 15: Infirmary | char.dat, grupo 12934: «Enfermería de la Santa Doncella» | Etiqueta «Enfermería» |
| Grupo editorial con varias opciones y hablantes | 8, 11, 17 | Grupos 14685, 14901, 5106 | Segmentos revisados individualmente, conservar selectores/controles. Sí/No y categorías separadas |
| Texto incompleto o sin revisión contextual | 2, 3, 9, 18, 20 | Grupos 5091, 3806, 5106, 15184; otros fragmentos físicos | Traducción completa cotejada con bytecode, reutilizar en apariciones equivalentes |
| Orden gramatical del HUD | 21: Total Prica | EBOOT 791616 y 791636 fuera del corpus | «Prica total», conservar formato numérico |
| Etiqueta de compra compuesta | 10: Buy | EBOOT 784120: ○Buy ／△Try | «○Comprar△Ver», conservar iconos y campo |
| Texto rasterizado sin traducir | 4: título; 13: World Map; 16: cartel japonés | BGPACK/atlas; no basta editar CSV | Localizar textura y rectángulo de texto, conservar paleta, dimensiones y marco |
| HUD de combate pendiente | 19, 21–23: MAP CLEAR, Flow, Flow Range, Tiles, Element, estadísticas | Mezcla de EBOOT, atlas y tablas | Separar cada recurso, traducir y comprobar en combate |
| Posición de anuncios | Observación del usuario: Fight / Tu turno | Atlas y coordenadas de dibujo, no diálogo | Centrar según ancho visible en pantalla PSP 480×272; comprobar área transparente del asset |
| Puntuación con diseño original | 1, 12 | Glifos del juego | Conservar el diseño original de los puntos suspensivos |

## Revisión editorial

Se han cotejado 96 grupos problemáticos con 187 segmentos físicos completos.
Esto incluye fragmentos omitidos por el manifiesto y opciones mezcladas con
diálogo. El fichero de segmentos guarda los bytes originales para impedir
aplicarlos sobre un recurso diferente. No equivale a cobertura total del corpus.
