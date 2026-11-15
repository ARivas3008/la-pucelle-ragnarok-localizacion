# Protocolo de trazado de las 14 referencias en PPSSPP

**Propósito:** determinar qué hace el intérprete del juego con las 15 referencias que caen dentro de caracteres CP932 antes de permitir un nuevo parche. Este documento no inventa direcciones RAM ni interpreta automáticamente el código MIPS.

## Herramientas compatibles según documentación oficial

PPSSPP documenta el **depurador interactivo** de Windows, un depurador ImGui activable desde el menú de desarrollador, y un depurador remoto por WebSocket. Las expresiones del depurador admiten registros MIPS (`a0`, `v0`, `pc`, `ra`), lectura de memoria `[dirección,1]`, `[dirección,2]`, `[dirección]`, condiciones de breakpoint y contadores `flipcount` y `vcount`.

Fuentes externas verificadas:
- https://www.ppsspp.org/docs/development/getting-started/
- https://www.ppsspp.org/docs/development/developer-tools/
- https://www.ppsspp.org/docs/development/debugger/expressions/

## Preparación

1. Conservar hash de ISO/DLC original y su escenario; probar antes en una copia sin parche.
2. En PPSSPP abrir **Configuración → Herramientas → Herramientas de desarrollador** y habilitar el menú de desarrollador. Abrir el depurador desde el menú del juego o la herramienta interactiva de Windows.
3. Registrar versión PPSSPP, núcleo CPU (intérprete/JIT), renderizador, opciones de textura, save original y ruta precisa de acceso al capítulo.
4. Generar los datos estáticos de las 14 anclas con: `python parcheador/investigacion/v0.15/auditar_anclas.py --iso original.iso --dlc-directorio DLC --salida auditoria`.
5. El CSV da **offsets de archivo**, NO direcciones RAM. Para obtener una dirección RAM válida hay que encontrar dónde se carga/descomprime cada script en el proceso PSP. No sustituir uno por otro por una suma inventada.

## Captura de comportamiento original

1. Cargar la escena en el original. Buscar en memoria el texto o una secuencia distintiva de bytes CP932 tomada del CSV. Confirmar que el contenido coincide en ese instante.
2. Identificar el comienzo en RAM del cuerpo del script y verificar la tabla `u32 count + count*u32` que corresponde a la extracción. Si no se verifica, anotar `MAPEO_MEMORIA_NO_ENCONTRADO`.
3. Colocar un breakpoint de lectura en el área de la tabla o sobre las instrucciones que desreferencian su entrada. Registrar **PC, registros, dirección efectiva y secuencia de bytes leídos**. El depurador permite condiciones como `a0 == 0x08801234` (ejemplo de sintaxis, **NO** es una dirección de La Pucelle) y lectura `[a0,1]`.
4. Seguir la cadena de llamadas hasta identificar para qué usa el motor ese valor: índice de evento, puntero a bytecode, desplazamiento de lectura, tiempo u otro dato. No clasificarlo como «puntero a letra» si la observación no lo demuestra.
5. Capturar la duración en cuadros de la escena. `flipcount` cuenta fotogramas presentados y `vcount` interrupciones verticales; no son equivalentes. Guardar imágenes y los valores observados.

## Comparación A/B/C (si y solo si se dispone de un parche de ensayo)

- A: original limpio, sin modificación.
- B: referencia desplazada al **inicio** del carácter (hipótesis histórica v0.12).
- C: referencia trasladada a byte de **la misma fase** (candidato v0.15, con carácter destino de 2 bytes).

Usar **copias** de ISO/DLC y partida nueva o mismo save limpio anterior a la escena. Validar que A/B/C leen la misma instrucción y mantienen la secuencia de eventos, duración, texto y punteros no relacionados. Si B o C provoca un salto de escena, letras rotas o coordenadas alteradas, descartar ese candidato.

## Datos mínimos de acta

~~~text
unit_id / grupo_id / recurso / version_de_ISO / hash_original
offset_archivo / referencia_indice / offset_relativo
base_de_script_en_RAM (observada, no inferida)
PC_consumer / instruccion_MIPS / registros / lectura_efectiva
tipo_semantico_confirmado / evidencia / incertidumbre
modo_prueba (A,B,C) / frame_inicial / frame_final
captura/video / resultado / SHA_parche / conclusiones
~~~

## Decisión y límites

Una referencia cuya función NO se ha identificado mantiene estado `BLOQUEADO_INTERPRETE_PENDIENTE`, aunque el reubicador reconstruya el fichero o lo pueda revertir byte por byte. Si el motor interpreta esa entrada como **marcador temporal**, preservar la fase del byte puede ser irrelevante o incorrecto; se deberá actualizar el cálculo de temporización, no el texto. Si es un **puntero real a bytecode**, habrá que encontrar los límites de instrucción reales antes de desplazarlo.

Las 14 unidades **no pasan a «verificadas» solo por ejecutar las pruebas unitarias**.
