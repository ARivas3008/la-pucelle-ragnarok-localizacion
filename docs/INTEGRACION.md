# Motor de integración

El punto de entrada vigente es `parcheador/app/scripts/integracion_total.py`. Reconstruye desde los originales aportados por el usuario; no depende de una ISO previamente parcheada ni de la caché del laboratorio.

1. Comprueba fuentes y carga las 15 revisiones, las correcciones de menú y los segmentos aprobados.
2. Aplica deltas mínimos de tablas, glifos y atlas; coteja originales, límites y capacidad de campos fijos. No amplía campos de capacidad desconocida ni trata metadatos como texto.
3. Compila bloques talk completos conservando las condiciones e identificadores. La cabecera es `8 + 32*N`; solo la primera columna contiene offsets. Las opciones se analizan con su estructura y sus controles.
4. Codifica talk en pares CP932, con glifos españoles y paginación de 28 caracteres por línea y tres líneas por página. El ASCII compacto se descartó por ser incompatible con el intérprete.
5. Reconstruye scripts con cabecera `4 + 8*N`, separando offsets e identificadores. Conserva controles y limita la fila a 64 bytes más NUL. Codifica ciertos signos como CP932 ancho para impedir que una coma consuma el terminador y exponga residuos de texto.
6. Reconstruye DAT con alineación de 16 bytes y comprime LZS sin copias solapadas. Verifica ida y vuelta de cada contenedor.
7. Anexa START/SCRIPTPACK a la ISO y actualiza sus registros. Conserva los LBA de otros miembros. Modifica únicamente los intervalos previstos de EBOOT, incluidos nueve sitios verificados para ampliar el búfer talk a 286.072 bytes.
8. Escribe diarios, hashes y motivos de rechazo; promueve la carpeta de construcción a entrega solo al terminar.

Las correcciones de Iglesia, Panza del Diablo, Cuarto de Salade, Comprar y Prica total están en datos o reservas verificadas. Los signos originales que no contienen letras ni números se conservan. Los títulos gráficos, carteles y centrado de anuncios requieren trabajo específico sobre textura o coordenadas y siguen pendientes.

Los modos y experimentos históricos se conservan para investigación. La interfaz vigente ejecuta una sola secuencia de integración; no aplica una segunda traducción sobre la primera salida.
