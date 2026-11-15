# Parcheador de La Pucelle: Ragnarok — GUI v0.16 experimental (motor v0.13 + scripts v0.14)

Este directorio reúne el código fuente del parcheador Windows con interfaz, los controles técnicos de versiones anteriores y los ensayos de reubicación. No contiene el videojuego ni sus DLC. La edición se realiza localmente sobre copias aportadas por el usuario.

**Estado real:** parche parcial y experimental. **No se ha verificado el 100 % de la inserción ni la ejecución de todas las escenas en PPSSPP.** Los ensayos de expansión y reversión de bytecode no sustituyen una prueba jugable.

## Ejecución

El EXE compilado presenta selector de ISO, selector de carpeta DLC y opciones `ISO + DLC`, `Solo ISO` y `Solo DLC`. El programa descarga los 15 corpus publicados en GitHub o permite leer un checkout mediante el motor Python. Para utilizarlo sin EXE, dentro de `parcheador/`:

```bash
python app/scripts/construir_parche.py --iso "MI_ISO.iso" --repo-directorio .. --salida salida --dialogos-atomicos --segmentar-conservador
```

El formato de la ISO se valida antes de modificar una copia; nunca se sobrescribe el original. En Windows el CLI requiere un `nis_lzs_pack.exe` construido a partir del código C++ incluido. El EXE ya incorpora el compresor.

Para usar las 197 abreviaciones verificadas estructuralmente en la auditoría v0.12 (incluidas cuatro correcciones de espacio de v0.13), añade **`--reducciones-verificadas`**. El checkbox correspondiente en la interfaz está desmarcado por defecto porque estas abreviaciones siguen pendientes de comprobación editorial y visual. El motor rechaza propuestas obsoletas, entradas sin revisión, colisiones, cambios fuera de campo y cadenas cuyo original ya no coincide.

**No activa** el modo experimental de 14 referencias subcarácter de v0.12 en el EXE. Esos ensayos permanecen en `investigacion/v0.12/` para su validación antes de aplicarlos a escenas.

`Now Loading` se conserva en inglés por petición expresa del usuario.

## Código y recursos

- `app/scripts/construir_parche.py`: motor principal y emisión de `reporte_por_unidad.csv` y `resumen.json`.
- `app/scripts/integracion_v013.py`: puente validado para compactaciones por campo, sin tocar otras estructuras.
- `app/scripts/campos_fijos.py`: límites de registros corregidos según v0.11.
- `app/scripts/fuentes_es.py`: glifos españoles.
- `app/scripts/nis_lzs_pack.cpp`: código fuente de compresión LZS.
- `app/datos/propuestas_reduccion_v012.csv`: propuestas y trazabilidad de la v0.12.
- `app/datos/ajustes_reducciones_v013.csv`: cuatro reducciones nuevas para fuente de ancho completo.
- `app/datos/atlas_deltas.json.z`: diferencias de atlas conocidas, sujetas a SHA-256.
- `investigacion/v0.10`, `v0.11`, `v0.12`, `v0.14`: herramientas de índices, scripts y reversión.
- `informes/`: estados y resultados sin distribuir binarios del juego.
- `docs/versiones/`: **un documento por versión**, con alcance, pruebas y pendientes.

El manifiesto de 26 258 unidades no se duplica: usa el existente en `data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv`. Durante la compilación del EXE se incluye en el paquete interno.

## Pruebas

```bash
python -m unittest discover -s app/tests -v
python -m unittest discover -s investigacion/v0.12/tests -v
```

`build_release.py` necesita Go 1.23+, Python 3.10+ y un compilador C++ de Windows para producir `nis_lzs_pack.exe`. Ejemplo en Windows con consola de Visual Studio:

```powershell
cl /std:c++17 /EHsc /O2 /Fe:nis_lzs_pack.exe app\scripts\nis_lzs_pack.cpp
python build_release.py --packer-exe .\nis_lzs_pack.exe
```

La compilación Linux de Go con destino Windows no valida el comportamiento de la GUI en Windows. Nunca interpretes una reconstrucción estructural como una certificación de jugabilidad.

## Control editorial y versiones

El trabajo técnico **no modifica** `corpus/*/revision.csv`, `glosario`, hashes ni mapas maestros. Todas las modificaciones se registran en [CHANGELOG.md](CHANGELOG.md), [docs/versiones](docs/versiones) y los informes. Un resultado marcado como `APLICADO_REDUCCION_ESTRUCTURAL` significa que caben sus bytes en el registro; todavía necesita QA lingüístico y ejecución en PPSSPP.

Consulta [ESTADO_100_POR_CIENTO.md](docs/ESTADO_100_POR_CIENTO.md) y [PLAN_QA_PPSSPP.md](docs/PLAN_QA_PPSSPP.md) para los bloqueos restantes.

## Nueva fase: scripts de eventos v0.14

El complemento [v0.14](investigacion/v0.14/README.md) inserta experimentalmente **489 de 503 textos de script traducibles** sin dividir sus oraciones ni desplazar datos no relacionados; el texto de `Now Loading` se excluye. Hay **14 anclas subcarácter** bloqueadas por defecto. Incluye pruebas de reconstrucción de ISO + DLC y genera informes propios. **No está integrado como opción predeterminada del EXE v0.13** y no certifica PPSSPP ni el 100 % de los 26 258 registros.

## Dossier técnico v0.15

[Investigación de 14 anclas](investigacion/v0.15/README.md) · [Matriz de casos](investigacion/v0.15/MATRIZ_14.md) · [Forensia estructural](docs/FORENSE_ESTRUCTURA_JUEGO.md) · [Fichas de formatos](docs/FORMATOS_BINARIOS.md). La nueva herramienta enumera offsets/punteros y propone referencias de fase, pero **no inserta automáticamente esos 14 textos** ni certifica PPSSPP.


## Versión experimental v0.16

La v0.16.1 incorpora una segunda etapa opcional de scripts: `conservador` (v0.14) y `fase` (ensayo CP932 que preserva segundo byte cuando existe candidato próximo). **No se afirma cobertura del 100 %**: en los originales facilitados se reprodujeron 15 anclas en 14 unidades, pero 4 de esas unidades dieron candidatos teóricos cercanos; la reconstrucción real de v0.16.1 acepta **3 candidatos experimentales** (1758, 3924, 4170) y bloquea **11** (incluida 1759 por índice inválido). Ningún modo sustituye el QA con PPSSPP. Consulta [v0.16](docs/versiones/v0.16.md). El EXE v0.16.1 se compila y somete a autotest como artefacto de GitHub Actions, no contiene juegos ni DLC.


**Forensia ampliada:** [inventario físico de ISO/DLC](docs/INVENTARIO_FISICO_V016.md) · [retorno de las 14 referencias](investigacion/v0.16/MATRIZ_RETEST_14.md). El modo fase ahora preserva las 489 ediciones conservadoras aunque una referencia no supere la prueba; véase [ficha de versión](docs/versiones/v0.16.md).

[Descargar EXE experimental v0.16.1 desde GitHub Releases](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/releases/tag/v0.16.1-experimental) · [Estado editorial actual observado](docs/ESTADO_EDITORIAL_OBSERVADO_2026-11-15.md). El EXE se publica separado de los recursos comerciales y no es release validada en PPSSPP.


## Versión v0.17.0-qa — parche de incidencias aportadas por capturas

La [v0.17](docs/versiones/v0.17.md) repara el rechazo de grupos paginados por separador `NUL 02 01` y agrega adaptaciones de cuatro grupos del tutorial (11 segmentos recuperados en ensayo de la ISO original), sin tocar los corpus aprobados. La GUI activa la etapa de scripts conservadores por defecto y separa la salida final en `JUEGO_PARA_PPSSPP_V017`; **no pruebes la ISO preliminar**. Hay [un informe de los diez fallos visibles](docs/QA_CAPTURAS_V017.md) que identifica estados abiertos, incluida la textura de capítulo 1, etiquetas de EBOOT y el parpadeo no comprobable desde capturas. No se declara localización completa.


## v0.17.1 — Solución de «Parcheo interrumpido» al generar DLC_01

La [ficha v0.17.1](docs/versiones/v0.17.1.md) explica por qué la segunda etapa solo genera DLC modificados: el GUI de v0.17 buscaba los cuatro nombres de salida incondicionalmente. La corrección usa el informe `resumen_script_v014.json`, conserva los DLC que no cambiaron, comprueba las cinco salidas y publica atómicamente `JUEGO_PARA_PPSSPP_V0171`. También muestra un mensaje de error más específico. No usar la carpeta parcial de v0.17 ni confundir una comprobación de archivos con QA visual.


## v0.17.2 — Corrupción visual: aislación y medición

Las capturas del 15/11/2026 muestran menús y ventanas dañados. [Informe de nueve capturas](docs/QA_VISUAL_V0172.md). La v0.17.2 permite conservar EBOOT y atlas de UI (casilla de diagnóstico activada por defecto; partes del menú pueden quedar sin traducir), y el [auditor](investigacion/v0.17/qa_integridad_graficos.py) detecta cambios no autorizados de texturas, CLUT y glifos. Se han ajustado los grupos 5056, 5064 y 5072 para que los segmentos quepan en CP932. **Es una prueba de aislamiento, no solución de gráficos demostrada.** [Versión v0.17.2](docs/versiones/v0.17.2.md).


## v0.17.3 — Los recursos ya no se trasladan innecesariamente al final de la ISO

El integrador de eventos antes cambiaba los LBAs de START_JP y SCRIPTPACK incluso cuando cabían en su ubicación original. En la [v0.17.3](docs/versiones/v0.17.3.md) se escribe en el mismo LBA y se preserva el tamaño físico de la ISO. Se mantiene el modo diagnóstico de EBOOT/atlas sin cambios y los arreglos previos de diálogos y entrega de DLC. **La desaparición de las anomalías visuales aún debe comprobarse en PPSSPP original/parche con mismos ajustes.**


## v0.17.4 — Evitar error «exit status 2» al integrar scripts

La primera fase reducía START_JP.LZS a 4 937 836 bytes; la segunda lo aumentaba a 4 937 862 (+26). La v0.17.3 bloqueaba por longitud lógica, pese a tener 4 939 776 bytes reservados en sectores. La [v0.17.4](docs/versiones/v0.17.4.md) calcula la reserva ISO9660 por sectores, rechaza solapamientos y mantiene todos los LBAs. En la prueba real pasaron ambas fases. Al fallar, la interfaz muestra el diagnóstico concreto de Python, no solo código 2. No es certificación gráfica PPSSPP.
