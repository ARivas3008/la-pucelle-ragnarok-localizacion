# ROM-025 (preparación) — Censo TALK físico de DLC

Medición local independiente con la misma gramática de formato_talk.py y runs de recompilar_talk.py (no se ha ejecutado el motor integral). Cuatro originales identificados en ROM-024. Todos los índices y límites de opcode válidos, cero opcodes desconocidos. 1668 anclas TALK exactamente en cadenas del intérprete.

| DLC | Entradas | Tokens | Cadenas físicas | Opciones | Anclas directas | Bloques | Grupos que cruzan controles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 00 | 590 | 6965 | 1748 | 63 | 1424 | 778 | 22 |
| 01 | 589 | 7103 | 1818 | 63 | 85 | 819 | 0 |
| 02 | 596 | 7411 | 1886 | 63 | 80 | 866 | 0 |
| 03 | 595 | 7603 | 1952 | 63 | 79 | 914 | 1 |
| Total | 2370 | 29082 | 7404 | 252 | 1668 | 3377 | 23 |

SHA originales talk00.dat:
- 00 dc3bf60239288e60bd013b10a7fe8feb07cef5d8c26c871f40c4e0b7df31fe39
- 01 dea3a47e0e1db3ae93cd5e9b3e7a2e5571bfbc8d3ea3cbcd63643a23be1b2162
- 02 7d8efede89c9390c00dcf9d90b163a5a8368c69b558ee156b138dbaadcb0cee1
- 03 60800484359af18898dd4d38993324f3abe8f0d6fa277c193e27c0d8bf9af54b

692 bloques totalmente anclados, 72 parcialmente anclados y 2613 sin ancla directa. Entre las 5736 cadenas sin ancla directa, 5547 tienen coincidencia textual normalizada con un único grupo del manifiesto de DLC y 189 no coinciden. 2230 bloques no totalmente anclados tienen una coincidencia byte a byte con una secuencia de grupos de un bloque completo; 455 no. No implica autorización editorial ni equivalencia de contexto. No sumar a 26258: son apariciones físicas, no nuevos IDs.
Siguiente ejecución: compilar los bloques anclados con las revisiones vigentes y comparar contextos/ID de entrada para reutilización; dividir los 23 grupos que cruzan controles sin alterar retrato/voz, y revisar las 189 cadenas sin coincidencia. Conservar índices, controles, menús de una línea, glifos y reversibilidad.
Se añade scripts/verificar_dlc_talk.py para reproducir el censo con el checkout íntegro y los originales; CLI aún no ejecutada localmente. No se publican recursos binarios.
