# Exclusiones técnicas verificadas — no son texto del juego

## Grupo 1630 del corpus 15

- Recurso: `DLC_00/ritem.dat`
- Offset decimal: `7552` (hexadecimal: `0x1D80`)
- Extracción problemática: `ェD`
- SHA-256 del campo `original` en `entrada.csv`: `59a27ac7d76c43b4529b121fcf1e173a6207519f3427a362bd6cede7835f9f1c`
- Bytes originales en `ritem.dat` offsets 7552–7554: `20 AA 44`
- En `ritem.dat`, el siguiente campo de texto comienza en el offset 7556.
- En `START_JP.LZS` (juego base), el texto siguiente es `Miracle`; en DLC 00, 01, 02 y 03 es `奇跡の`.
- La secuencia `20 AA 44` aparece sin cambios en el juego base y los cuatro DLC: es un **falso positivo del extractor**, no una línea para traducir.

**Decisión de preinserción**: preservar íntegramente esos bytes en todos los paquetes y **excluir el registro 1630 del conjunto de textos insertables**. Nunca escribir `ェD` ni una traducción sobre esa secuencia.

Fuente de verificación: auditoría previa de los recursos originales, `03_evidencia_hex_y_slots.csv` y `LEEME_PREINSERCION.md` del paquete de preinserción (14-11-2026). La auditoría reportó cotejo de 180 recursos por SHA-256 y descompresión.

En `corpus/15/revision.csv` se mantiene `es_revisado` vacío y `estado=requiere_investigacion` como marcador técnico del formato vigente. La validación estricta **solo** acepta esta excepción cuando el ID, recurso, offset, original, SHA y prueba hexadecimal coinciden. No computa el registro como una traducción aprobada.

Los otros dos casos investigados del corpus 15, IDs 534 (`雷精エリツィンを宿した杖`) y 1562 (`パックン`), tienen traducción revisada; no se excluyen.
