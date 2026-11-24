# CENT-018 — Ingeniería inversa del generador de nombres PSP y revisión editorial

**Fecha:** 24/11/2026  
**Origen A:** `PSP_GAME/SYSDIR/EBOOT.BIN` de ISO PSP v1.1.2 autenticada, SHA-256 de ISO `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`.  
**ELF MIPS analizado:** SHA-256 `2b9a1a9864f3b236e83a2848f839023e92dcb7a5272bcb430cef527eafb563f6`.  
**Método:** `llvm-objdump` MIPS little endian y lectura directa de `ISO_START/name.dat` original. No se publican bytes comerciales.

## Hallazgos de ejecución

| Dirección MIPS | Evidencia |
| --- | --- |
| `0x0882ec80–0x0882eca8` | Obtiene índice aleatorio y direcciona un registro de 16 bytes (desplazamiento `índice << 4`). |
| `0x0882ece0` | `lbu $3, 3($16)`: clase de registro (1, 2 o 3). |
| `0x0882ecf0–0x0882ed08` | La clase 3 llama al generador con máximo 100 y elige clase 1 para resultado menor que 50 o clase 2 en caso contrario. |
| `0x0882ed14–0x0882ed28` | Clase 1: copia nombre base con `strcpy` (`0x0880d350`) y añade fragmento con `strcat` (`0x0880d240`). **SUFIJO**. |
| `0x0882ed34–0x0882ed44` | Clase 2: copia fragmento, concatena nombre base. **PREFIJO**. |
| `0x0882ed4c–0x0882ed58` | `strlen` (`0x0880d3d8`) y `sltiu $1, $2, 0x11`; rechaza y reintenta si longitud mayor que **16 bytes**. |
| `0x0882ed60–0x0882ed68` | Copia el nombre aceptado al destino. |

La composición **no inserta espacios ni delimitadores**. `name.dat` reserva 12 bytes desde el desplazamiento +4 de cada slot (11 útiles + NUL). El límite de salida es de 16 **bytes de la codificación original**, no caracteres Unicode. Todo lo anterior es evidencia de código, no prueba visual PPSSPP.

## Decisiones editoriales justificadas

Las entradas del generador no forman oraciones narrativas: son **morfemas que producen apelativos disparatados**, como el original inglés. Se revisaron 31 candidatos inicialmente bloqueados en ISO: cuatro sílabas nominales conservadas sin traducir (`Ma`, `Ni`, `Na`, `Co`), 24 adaptaciones cortas revisadas con semántica de nombres ficticios (ver `data/control/CENT018_NAME_DAT_27_PROPUESTAS.csv`) y tres ambigüedades conservadas: `Such?`, `Out to be` y `Vistor`. Ninguna de las 31 unidades se da por certificada en juego.

Se revisó además la transliteración japonesa `スコピル` → **Sukopiru** como componente nominal del DLC, sin asociarla falsamente al inglés `Pepper`. Su uso físico sigue sin prueba por falta de EDAT originales.

**Control de revisión:** `scripts/cent018_modelo_nombres.py` reproduce dirección, CP932 y límites; `tests/test_cent018_modelo_nombres.py` cubre 13 casos. La CI simula las 27 propuestas contra bases `Prier`, `Croix`, `Alouette`, `Culotte` y `Poitreene` sin aprobar automáticamente las tres dudosas. Que una combinación quepa en bytes no demuestra que la traducción sea adecuada ni que el juego la renderice correctamente.

## Estado de cierre y faltantes

- Catálogo original: **15.492 revisados / 15.525 = 99,79 %**, **33 registros pendientes**.
- **26** morfemas japoneses de `DLC_00/name.dat`: sin EDAT para cotejar clase, concatenación y límites físicos.
- **3** morfemas ingleses del generador ISO sin decisión semántica defendible.
- **3** grupos centrales `magic.dat` con prefijo de control sin EDAT: IDs `611`, `731`, `951`.
- **1** falso positivo de extractor: ID `1630` (`ェD`), documentado como datos `20 AA 44`, excluido técnicamente, sin sumarlo como texto traducido.
- Además: **10 fragmentos ingleses léxicos fuera de las 15.525 entradas** detectados entre los 17 slots no inventariados de `name.dat`, por resolver en censo complementario.

**No se puede declarar el 100 % de toda la traducción** mientras esos textos potenciales no tengan resolución verificable y el inventario siga sin ser exhaustivo. No alterar el denominador para dar por terminado el proyecto. Ni las revisiones editoriales ni la CI sintética sustituyen la reinserción en ISO/DLC y la validación PPSSPP.
