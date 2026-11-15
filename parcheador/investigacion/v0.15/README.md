# v0.15 — Investigación forense de 14 anclas subcarácter

El proyecto registró 14 unidades de `script*.dat` que no superaban el reubicador conservador v0.14. **No se afirma que los 14 sean nombres propios**. Hay narración, una despedida, referencias a Prier/Alouette y una frase «¿Continuará?».

## Hallazgo verificable

- 14 unidades concretas: `1758, 1759, 3883, 3897, 3898, 3924, 3969, 3989, 4007, 4083, 4095, 4098, 4170, 4220`.
- El informe v0.12 registra **15 referencias en el segundo byte** de caracteres Shift-JIS (dos afectan a la unidad 1759).
- v0.12 experimental movía la referencia al **primer** byte de un carácter; era una hipótesis, **no una corrección demostrada**.
- v0.15 propone como nueva hipótesis **mantener la fase del byte** al mapear una referencia, sin redirigir silenciosamente a la cabecera del carácter. Si el destino no tiene un carácter de dos bytes próximo, se rechaza. La propuesta **NO se escribe en el juego** hasta identificar el significado del índice y probar su escena.
- Las tablas pueden apuntar a puntos intermedios: estos bytes podrían representar otra cosa que el comienzo de una cadena. No se atribuye a todos una semántica de cursor.

## Cómo reproducir la auditoría

Desde la raíz del repositorio, con una copia original de ISO y la carpeta de cuatro DLC:

```bash
python parcheador/investigacion/v0.15/auditar_anclas.py --iso original.iso --dlc-directorio DLC --salida auditoria_anclas
python -m unittest discover -s parcheador/investigacion/v0.15/tests -v
```

Sin los binarios, genera una tabla documental con estado `SIN_BINARIO_ORIGINAL`. El CSV con recursos reales registra SHA256, offsets originales, índice de puntero, hex del par CP932 y candidato de fase. Ninguna opción modifica el juego.

**Criterio para aprobar:** verificar cada puntero mediante traza de bytecode/PPSSPP y confirmar que no causa saltos de escena, texto corrupto o cambio de temporalización. Mantener bloqueado el modo que modifique anclas de fase desconocida.

Consulta [registro de 14 casos](casos_14.csv) y [informe forense global](../../docs/FORENSE_ESTRUCTURA_JUEGO.md).
