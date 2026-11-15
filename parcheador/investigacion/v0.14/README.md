# La Pucelle: Ragnarok — reubicación de scripts v0.14 (experimental)

Esta versión **no es la traducción definitiva al 100 %**. Incorpora un paso técnico
real de escritura y reconstrucción de scripts de eventos `script*.dat` utilizando
las traducciones ya revisadas. No reparte ni fragmenta las oraciones: conserva
el número de entradas y reubica tablas y cadenas de tamaño variable.

## Resultado comprobado sobre los originales aportados

- 504 unidades de `script*.dat` auditadas.
- 489 insertadas y reconstruidas con el modo conservador.
- 14 excluidas porque el índice referencia el **segundo byte de un carácter CP932**.
- 1 entrada de carga `Now Loading` dejada sin cambios.
- Modo optativo experimental: 503/503 textos sometidos a reubicación y reversión;
  **sin prueba de sincronización de escenas en PPSSPP**.
- ISO + cuatro DLC reconstruidos en archivos nuevos. Cinco fuentes `fontB`
  extendidas con 65 glifos españoles por juego/DLC sin alterar los demás atlas.
- `EBOOT.BIN` y 16 miembros `talk*_jp.dat` de `SCRIPTPACK.DAT` intactos;
  recursos no fuente ajenos a scripts preservados.

La verificación es **binaria**, no de ejecución. Los cambios de v0.14 sobre los
scripts son independientes de los demás textos y no corrigen automáticamente
los 26 258 registros del manifiesto. El modo conservador nunca toca las 14
referencias subcarácter. No renombra ni edita `Now Loading`.

## Uso

Partir de un checkout actualizado del repositorio, en su carpeta raíz. Se necesita
Python 3.10 o superior y el compresor `nis_lzs_pack` compilado desde los fuentes
del parcheador (o el ejecutable provisto por el paquete Windows previo). El
script no descarga ni distribuye archivos comerciales.

```powershell
python parcheador/investigacion/v0.14/integrar_scripts_v014.py --iso "MI_JUEGO.iso" --dlc-directorio "MI_CARPETA_DLC" --salida "auditoria_v014"
```

Por defecto solo produce `informe_script_v014.csv` y `resumen_script_v014.json`.
Para generar **una copia de prueba** de la ISO y los cuatro DLC:

```powershell
python parcheador/investigacion/v0.14/integrar_scripts_v014.py --iso "MI_JUEGO.iso" --dlc-directorio "MI_CARPETA_DLC" --salida "prueba_v014" --construir --packer "ruta/al/nis_lzs_pack.exe" --acepto-riesgo-ppsspp
```

Se recomienda partir de la **salida de la versión v0.13**, no de una ISO original,
para conservar el trabajo ya realizado en menús y HUD. En ese caso los cuatro
DLC deben estar nombrados `DL_JP_00.EDAT` … `DL_JP_03.EDAT` dentro de la carpeta
seleccionada (renombrar copias de los EDAT generados por v0.13 si es necesario).
El modo de ensayo de v0.14 recalcula las fuentes de forma idempotente.

El modo `--modo experimental --acepto-riesgo-referencias` admite también las 14
referencias subcarácter, pero **puede alterar temporización o renderizado**.
No es modo predeterminado ni se considera aprobado para jugar.

## Invariantes y verificaciones

1. Nunca sobrescribe los archivos de entrada.
2. Coincidencia de texto original en el offset exacto del manifiesto.
3. Opcode `0x32`, longitud de un byte y terminador verificados.
4. Variables/controladores preservados, si existen.
5. Índices de script recalculados y reversión exacta de cada archivo.
6. DAT, NISPACK y LZS reconstruidos y comprobados.
7. Entradas ISO9660 actualizadas a una ubicación nueva, sobre una copia.
8. Miembros no modificados comprobados byte por byte.
9. Las 65 posiciones gaiji se comprueban en los cuatro DLC.
10. `Now Loading` permanece intacto en `DLC_00/script00.dat`.

Ejecutar pruebas unitarias sin archivos comerciales:

```bash
python -m unittest discover -s parcheador/investigacion/v0.14/tests -v
```

Para comprobar una copia construida:

```bash
python parcheador/investigacion/v0.14/verificar_v014.py --original-iso MI_JUEGO.iso --iso prueba_v014/La_Pucelle_Ragnarok_ES_SCRIPT_V014_EXPERIMENTAL.iso --original-dlc MI_CARPETA_DLC --dlc prueba_v014 --salida prueba_v014/QA_v014.json
```

## Pendiente antes de afirmar «100 %»

- Corregir semánticamente y verificar en PPSSPP los 14 punteros subcarácter.
- Vincular esta fase con las cadenas de `talk*.dat` y el resto de tablas fijas,
  texturas, subtítulos de introducción y HUD sin edición segura.
- Resolver los grupos editoriales aún en investigación.
- Ejecutar QA visual de todos los capítulos y DLC y aportar acta de prueba.

**No subir ISO ni EDAT al repositorio público.** Solo scripts, documentos e
informes derivados sin datos comerciales. Se debe preservar la ISO original.