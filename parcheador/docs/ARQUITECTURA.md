# Arquitectura y barreras de seguridad

`gui.ps1` (WinForms) recopila ISO, carpeta DLC, salida y opciones. `main.go` actúa como lanzador y escribe el motor empaquetado en una carpeta de caché aislada por versión. `app/scripts/construir_parche.py` lee las 15 revisiones y el manifiesto, aplica reemplazos y reconstruye **copias**.

## Formatos

- `START_JP.LZS`: compresión NIS LZS de un DAT de miembros indexados.
- `SCRIPTPACK.DAT`: contenedor NISPACK de scripts y diálogos.
- `talk*.dat`: tabla de referencias principal y segmentos de bytecode 0x01; la herramienta de laboratorio v0.10 permite ampliación y prueba de reversión.
- `script*.dat`: índice de offsets, texto marcado por opcode 0x32 seguido de longitud de un byte que incluye NUL; la herramienta v0.12 reubica referencias, pero las anclas en bytes interiores requieren revisión de escena.
- `char`, `magic`, `skill`, `name`, `kis`, `ritem`, `com`, `mapinfo`: campos de longitud fija. Se conserva padding y estadísticas.
- `EBOOT.BIN`: sustituciones ASCII limitadas a campos NUL existentes; no se sobrescriben instrucciones ejecutables.
- `sys3.txp`, `sys4.txp`: diferencias de atlas aprobadas por SHA del original, sin modificar cabeceras, dimensiones ni paletas.

## Integración v0.13

Las propuestas `CABE_ESTRUCTURAL` de v0.12 se cargan por `unit_id`, se comparan contra manifiesto, grupo, original y texto español actual de GitHub. Los cuatro ajustes v0.13 son explícitos y conservan la propuesta original. Solo se aplican si el resultado v0.8 sigue bloqueado, el campo está intacto y la traducción tiene revisión editorial. No se aplican propuestas `POR_REVISAR` ni cadenas de análisis provisional.

Si falla una comprobación, el registro se deja intacto y se documenta en el informe. Es más importante evitar daño que elevar artificialmente un porcentaje.
