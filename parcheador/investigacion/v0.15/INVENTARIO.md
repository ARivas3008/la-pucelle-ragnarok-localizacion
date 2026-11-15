# Inventario binario reproducible (solo lectura)

El programa inventario_forense.py enumera archivos de una ISO ISO9660 y los cuatro DLC indicados. Para formatos comprobados intenta entrar en NISPACK, LZS y DAT de manera recursiva. El resto queda **DESCONOCIDO**, no se adivina su estructura.

Ejemplo desde la raíz del repositorio:

~~~bash
python parcheador/investigacion/v0.15/inventario_forense.py --iso copia_original.iso --dlc-directorio mis_dlc --salida catalogo
~~~

Resultados: inventario_forense.csv (ruta, padre, capa, tamaño, offset dentro del padre y SHA256), inventario_resumen.json (conteos y advertencias). No incluye bytes originales, recursos gráficos, claves ni contenido de texto.

El límite de lectura predeterminado es de 64 MiB por archivo; grandes recursos se anotan como omitidos. La lista resultante es el **inventario de los archivos que proporcionas**, no una enumeración universal de todas las variantes del juego. Ninguna operación escribe a los originales.

Para cruzar las unidades del manifiesto, usa auditar_anclas.py y los informes de la localización.
