# Fichas de formatos y offsets reproducibles

Cada número de este documento deriva de los analizadores almacenados en el repositorio y de los ejemplares utilizados en la investigación. Se describe **lo que acepta nuestro parser**, no un estándar universal de Nippon Ichi.

## ISO9660
- Sector lógico: **2048 bytes**.
- Descriptor primario en sector **16** (offset 32768): tipo 1, firma ASCII CD001, versión 1.
- Registro raíz desde offset **156** del descriptor primario.
- Registro de directorio: LBA little endian en offset relativo +2, LBA big endian +6, tamaño LE +10, BE +14; nombre desde +33 y longitud en +32.
- El reubicador actualiza LBA, tamaño y tamaño total de imagen en ambos endian, añadiendo recurso al final alineado. Debe trabajar sobre copia.
- Fuente: [iso_reubicar.py](../investigacion/v0.10/iso_reubicar.py).

## NIS-LZS
~~~text
0x00  4 bytes   ext / firma contextual del payload
0x04  uint32 LE tamaño esperado descomprimido
0x08  uint32 LE tamaño comprimido (el parser exige compressed + 4 = longitud)
0x0C  uint8     marcador de escape LZS
0x0D  3 bytes   reservados
0x10  ...       tokens comprimidos
~~~
Un byte distinto del marcador representa literal; marcador seguido del marcador representa literal del marcador. Otras secuencias codifican distancia/longitud de copia hacia atrás. No se infiere que todo LZS del mundo comparta este encabezado. Fuente: nis_formats.py.

## NISPACK
~~~text
0x00  8B  NISPACK + NUL
0x08  u32 bandera endian (0 LE, 1 BE)
0x0C  u32 número de miembros N
0x10  ...  N entradas de 44 bytes:
       0x00 name[32] CP932 terminada por NUL
       0x20 offset u32
       0x24 size   u32
       0x28 unknown u32 (se conserva)
cuerpo: miembros frecuentemente alineados a 2048 B, verificado por reconstructor
~~~
Se rechazan nombres duplicados, offsets fuera de límites y longitudes inconsistentes. Fuente: [contenedores.py](../investigacion/v0.10/contenedores.py).

## DAT interno de START
~~~text
0x00  u32 número N
0x04  ... cabecera/reservado hasta 0x10
0x10  N entradas de 32 bytes:
        +0 u32 final relativo al inicio de datos (ACUMULADO)
        +4 nombre[28] CP932/NUL
inicio de datos = 16 + 32*N
~~~
El comienzo del miembro i es el final acumulado del miembro anterior (para el primero: inicio de datos). Por ello al modificar un miembro se recalculan **todos los finales siguientes**. Fuente: [contenedores.py](../investigacion/v0.10/contenedores.py).

## script*.dat — entradas del intérprete de eventos
~~~text
0x00 u32 N
0x04 N valores u32 LE relativos al inicio de bytecode
body = 4 + 4*N
...  opcode 0x32, u8 longitud L (incluye NUL),
     texto CP932/gaiji de L-1 bytes, byte NUL
~~~
- El índice se comprueba como monótono, dentro de tamaño. **No se ha demostrado que cada entrada apunte al principio de una instrucción de texto**.
- Para 14 textos hay 15 anclas sobre segundos bytes CP932. La ausencia de semántica de esos índices impide aprobar reubicaciones.
- El byte de longitud limita **L a 255 bytes** para esa instrucción concreta. El motor de caja puede admitir varios segmentos o instrucciones, pero no se deduce automáticamente cómo insertar otra instrucción.
- Se registran offsets de bytes, no «bits de texto». Fuente: reubicador_anclas_v012.py.

## talk*.dat — diálogos
- Cabecera con número de entradas y tabla de offsets, comprobada en 21 ficheros en v0.10.
- Control 0x01 observado en segmentos encadenados.
- La concatenación de originales no autoriza dividir oraciones por longitud sin comprobar cambio de hablante y controles.
- 21 751 unidades del mapa y 837 continuaciones recuperadas se investigaron estructuralmente; los informes incluyen casos sin traducción contextual.
- Semántica completa del bytecode **desconocida**.

## DAT fijos: ubicación dentro de cada registro
Los siguientes perfiles proceden exactamente de campos_fijos.py; el desplazamiento de texto es relativo al registro y se debe sumar la cabecera del archivo.

| Familia | Stride bytes | Cabecera bytes | Campo 1 (inicio, longitud) | Campo 2 |
|---|---:|---:|---|---|
| char.dat | 200 | 8 | (0, 24) | — |
| magic.dat | 116 | 8 | (18, 23) | (41, 57) |
| mapinfo.dat | 96 | 8 | (12, 28) | — |
| name.dat | 16 | 8 | (4, 12) | — |
| kis.dat | 148 | 8 | (0, 21) | (21, 57) |
| ritem.dat | 92 | 8 | (4, 13) | (17, 43) |
| skill.dat | 94 | 8 | (16, 21) | (37, 57) |
| com.dat | 92 | 8 | (0, 23) | (23, 49) |

**Regla:** campo finaliza en NUL, resto del campo en ceros, no se reescribe fuera de los límites. Un nombre de 24 bytes NO admite 24 bytes de texto: debe reservar espacio para NUL. La anchura visual en píxeles es otro límite independiente.

## fontB (PSP, textura comprobada)
- Textura: **512×512**, 4 bits por píxel; archivo TXP **132112 bytes**, datos gráficos desde **1040**.
- Reorganización de bloques/swizzle particular de estas fuentes. Celdas de **14×14**, cuadrícula 36×36 por página; páginas y rangos reales verificados antes de escribir.
- 65 glifos adicionales en códigos privados F0 xx. Los códigos no garantizan que el EBOOT interprete esa secuencia igual en todos los menús.
- Otras texturas sys*.txp y BGPACK pueden usar **otros formatos/paletas**. No utilizar el decodificador fontB indiscriminadamente.
- Fuente: [fuentes_es.py](../app/scripts/fuentes_es.py).

## Formatos no resueltos completamente
- Geometría de MAPPACK y animaciones de ANMPACK.
- Interprete íntegro de instrucciones talk/script y la temporización de escenas.
- Contenedores de vídeo/intros que no aparecen como texto de script.
- Cálculo de anchura y clipping de todos los menús y cambios de tamaño de cuadros.
- Cualquier EDAT diferente de los cuatro archivos comprobados.
