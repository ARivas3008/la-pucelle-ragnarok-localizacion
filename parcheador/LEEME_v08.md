# La Pucelle: Ragnarok — Parcheador ES v0.8 (EXPERIMENTAL)

## Objetivo y límites

Esta versión incorpora la localización de los **15 corpus** en los lugares que puede modificar con garantías técnicas verificables. **No traduce aún el 100 % del juego**. No sustituye ISO ni DLC originales y genera exclusivamente copias `PRELIMINAR` más `resumen.json` y `reporte_por_unidad.csv`.

### 1. Textos del HUD en campos de tamaño fijo (nuevo en v0.8)

- En **ocho tipos de recurso** de menús/nombres (`char.dat`, `magic.dat`, `mapinfo.dat`, `name.dat`, `kis.dat`, `ritem.dat`, `skill.dat`, `com.dat`) detecta campos de ancho fijo con terminador NUL y relleno cero.
- Si el texto español es más largo que el original pero **cabe íntegramente en el campo reservado**, utiliza ese espacio sin desplazar registros, tocar estadísticas ni mover punteros.
- Valida el offset, la alineación de la estructura, el byte NUL y todos los bytes de relleno antes de escribir. Si hay conflicto, deja el original y explica la causa.
- La prueba controlada con la ISO y los cuatro EDAT originales y con **2682 grupos de traducciones extraídos del informe proporcionado por el usuario** logró **1745 inserciones extra** de este tipo; **no equivale a aplicar ni validar los 15016 grupos reales de GitHub en un juego completo**. La ejecución de cada usuario descargará las revisiones actualizadas del repositorio.

### 2. HUD y menús reducidos

- Tabla editorial de equivalencias breves para `EBOOT.BIN`: en la misma prueba se aplicaron **98** cadenas. Un texto de tres bytes (`Bat`) queda intacto porque no admite un equivalente español corto e inequívoco.
- Nunca recorta automáticamente una oración narrativa para forzar su cabida. No altera por defecto las dimensiones de los cuadros de menú.
- Puede activar el atlas `sys3.txp`/`sys4.txp` experimental con una casilla en la interfaz. Se mantiene DESACTIVADO inicialmente.

### 3. Diálogos y textos de script

- Respeta el número original de líneas físicas (2–3) y los separadores de intervención. Solo resegmenta cuando todos los segmentos pueden verificarse; si no, conserva la intervención original y marca el bloqueo. **No crea nuevas cajas**.
- Inserta, con comprobación SHA del recurso, cuatro cadenas narrativas verificadas de `ISO_START/script00.dat`, correspondientes a una **secuencia distinta del rótulo japonés de la ciudad mostrado en las capturas**. No se ha demostrado aún que ese rótulo sea editable como texto plano del script.
- **«Now Loading» no se modifica**, expresamente a petición del usuario.

## Uso en Windows

1. Ejecuta `LaPucelle_Parcheador_ES_GUI_v0.8.exe` (Windows x64). Elige «ISO + DLC», «Solo ISO» o «Solo DLC».
2. Pulsa los botones de exploración para seleccionar la ISO y/o la carpeta que contiene `DL_JP_00.EDAT` a `DL_JP_03.EDAT`.
3. Selecciona una carpeta de salida **distinta** de las fuentes originales. Mantén la opción «solo fuentes» desmarcada si deseas traducir los textos.
4. Pulsa «INICIAR PARCHEO». Necesita acceso a Internet para obtener los CSV de revisión de GitHub y posiblemente Python portátil en el primer uso.
5. Consulta `resumen.json` (`campos_fijos_ampliados`, `menus_eboot_ascii_aplicados`, `rotulos_narrativos_script`, `unidades_bloqueadas`) y `reporte_por_unidad.csv`. Los resultados siguen siendo EXPERIMENTALES.

## Pruebas y advertencias

- **34/34 pruebas unitarias** de Python correctas. Reconstrucción completa de una ISO real y cuatro DLC, seguida de verificación de formatos y compresión, ejecutada con un **subconjunto de 2682 grupos de prueba** tomado del informe del usuario. El resto del corpus en la prueba estaba marcado como no revisado a propósito: sus cifras globales de bloqueos no equivalen al informe final del usuario.
- **No se ha ejecutado PPSSPP desde esta sesión** ni comprobado el renderizado real de todos los glifos/HUD. Guarda copias originales. No se garantiza que el juego esté completamente traducido ni que todos los DLC funcionen en una consola real.
- Los scripts `talk*.dat` y otros recursos de tamaño variable siguen requiriendo ingeniería inversa de **tablas de punteros y reconstrucción de bytecode**. Nunca se escriben sobre estructuras no verificadas.
- Quedan pendientes los grupos editoriales señalados con `requiere_investigacion`, además de los 509 registros de coordinación; no se elevan arbitrariamente a `revisado`.
- No se distribuyen ISOs, EDAT, vídeos originales ni contenidos protegidos; el paquete solo incluye programa y recursos de localización del proyecto.

## Motor por consola (opcional)

```bash
cd app
python -m unittest discover -s tests -p 'test_*.py'
python scripts/construir_parche.py --iso JUEGO.iso --dlc-directorio ULJS00244 --descargar-revisiones --salida salida --dialogos-atomicos --segmentar-conservador --incluir-investigacion
```

**Los 1745 ejemplos de campos fijos de la prueba se pueden inspeccionar en `LaPucelle_v08_Auditoria_Campos_Fijos.csv`.**
