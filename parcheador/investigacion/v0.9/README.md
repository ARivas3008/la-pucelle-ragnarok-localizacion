# La Pucelle: Ragnarok — investigación del almacenamiento variable (v0.9 experimental)

## Estado real

**NO inserta el 100 % de los textos y NO es un parche listo para jugar.** Es una prueba
reproducible de reconstrucción de tablas de desplazamientos y contenedores,
preparatoria para integrar todas las revisiones sin truncar oraciones. No hay ISO,
EDAT ni textos originales del videojuego en este paquete.

### Verificaciones ejecutadas con archivos originales del proyecto

- 21 archivos `talk*.dat` reconocidos (16 dentro de SCRIPTPACK.DAT, 1 de ISO_START
  y 4 de DLC). En todos, se valida que el primer campo de cada entrada de la
  tabla principal sea monótono y esté dentro del bytecode.
- Auditoría de 21 751 unidades de texto asociadas con `talk*.dat`:
  - 14 791 candidatas con grupo/caja comprobados;
  - 5 396 en intervenciones cuyo agrupamiento del manifiesto no está cerrado;
  - 337 en grupos sin cadena confirmada;
  - 788 con continuación sin mapear;
  - 439 cuya fuente no coincide exactamente.
  Estas clases son **elegibilidad estructural**, no pruebas de inserción,
  renderizado, traducción terminada ni jugabilidad.
- Pruebas de ampliación de cuatro cadenas consecutivas, actualización de índices
  y restauración exacta byte a byte.
- Reconstrucción de NISPACK al modificar `talk01_jp.dat`; comprobación de que los
  otros 31 miembros siguen iguales.
- Reconstrucción de la tabla de miembros del `START_JP.LZS` descomprimido.
- ISO de prueba reconstruida: `SCRIPTPACK.DAT` reubicado a un nuevo sector y
  directorio ISO9660 actualizado. Se verificó la lectura del archivo nuevo y
  que los bytes de `EBOOT.BIN` y `START_JP.LZS` seguían iguales. La ISO de prueba
  se eliminó; **no se incluye**.

## Archivos

- `relocador.py`: comprobación de cabecera `talk*.dat` y sustitución de cadenas
  con desplazamiento de los punteros principales. Rechaza NUL/solapamientos,
  originales distintos y punteros que entren en la zona modificada. Verifica
  restauración reversible.
- `contenedores.py`: reconstrucción de DAT interno y NISPACK (metadatos y tamaños).
- `iso_reubicar.py`: reubicación de UN archivo en una copia de una ISO9660, con
  actualización del registro y volumen. **No modifica el archivo original**.
- `auditar_manifiesto.py`: auditoría de grupos/recursos sin modificar binarios.
- `informes/`: CSV y JSON de la auditoría y prueba física de reubicación.
- `tests/`: 8 pruebas que requieren los archivos originales en una carpeta de
  trabajo para la parte de integración. Los tests **no descargan** el juego.

## Uso de la auditoría

Con un directorio que contenga `ISO_SCRIPT`, `ISO_START`, `DLC_00`...
`DLC_03` extraídos de tus archivos originales:

```powershell
python auditar_manifiesto.py --manifiesto "C:\Ruta\mapa_26258_unidades.csv" --extraidos "C:\Ruta\extraidos" --salida "C:\Ruta\auditoria"
```

El módulo `relocador.py` es una API para experimentos. **No lo habilites como
parche general** hasta verificar el resto de referencias del bytecode. Se ha
probado únicamente la tabla principal, no todas las rutas de ejecución del motor.

## Qué impide todavía declarar el 100 %

1. Referencias internas, saltos, llamadas, longitudes/estructuras del bytecode,
   aparte de la tabla principal de `talk*.dat`, aún sin identificación completa.
2. Segmentos de múltiples grupos con límite de hablante o de caja no cerrado:
   aplicar textos a esos offsets sería propenso a conversaciones mezcladas.
3. `script*.dat`, `EBOOT.BIN`, datos compactos del HUD y las fuentes necesitan
   parsers propios, límites gráficos y, en algunos casos, reubicación adicional.
4. Hay 509 grupos de coordinación fuera de los 15 corpus y grupos marcados
   `requiere_investigacion`. No se puede declarar final una traducción aún no
   revisada por completo.
5. Falta prueba visual y funcional en PPSSPP (escenas, menú, combate, DLC,
   guardar/cargar). Un contenedor técnicamente legible no prueba que un script
   movido funcione durante el juego.

El archivo «Now Loading» se deja fuera del alcance por instrucción del usuario.
No se acortan ni inventan diálogos para forzar una aceptación de 100 %.
