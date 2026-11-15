# Parcheador de La Pucelle: Ragnarok — GUI v0.13 / reubicador de scripts v0.14

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
