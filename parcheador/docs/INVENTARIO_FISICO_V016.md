# Inventario físico reproducido — La Pucelle: Ragnarok v0.16 (PSP)

**Fecha:** 2026-11-15. **Muestras:** ISO 1.1.2 de 858 937 344 bytes; DLC `ULJS00244` con `DL_JP_00.EDAT` a `DL_JP_03.EDAT`; archivo `START_JP.LZS` separado. **Nivel de certeza:** tamaños y cabeceras obtenidos de los originales del usuario; finalidad de los archivos deducida de nombres y herramientas salvo indicación expresa. No es código fuente del juego ni prueba de ejecución.

## 1. Resumen para localizar un texto

1. Determina el **archivo físico** (ISO, EDAT, EBOOT, atlas o vídeo).
2. Encuentra su **contenedor**. La ISO usa sectores de 2048 B. `START_JP.LZS` se descomprime como NIS-LZS y su resultado es un DAT indexado. `SCRIPTPACK.DAT` es NISPACK; en estos DLC el EDAT también contiene NISPACK → `start_jp.lzs` → DAT.
3. Busca el **miembro** (`talk*.dat`, `script*.dat`, `char.dat`, `fontB...`).
4. Resuelve la **unidad** mediante `unit_id`, `recurso`, `offset` y comparación de fuente en el manifiesto; agrupa con `grupo_id`, contexto de escena y controles.
5. Cambia bytes en una **copia nueva** solo si caben, y reescribe índices de cada capa. Relee y compara hashes de vecinos. La prueba de juego en PPSSPP es independiente.

## 2. Dónde está cada capa (observación de esta ISO)

```text
La_Pucelle_Ragnarok_v1.1.2.iso (ISO9660, 858 937 344 B)
├─ /PSP_GAME/SYSDIR/
│  ├─ BOOT.BIN                 895 108 B
│  ├─ EBOOT.BIN                895 108 B (menús/código PSP parcialmente auditado)
│  └─ UPDATE/                  datos y ejecutable de actualización (NO editar)
├─ /PSP_GAME/USRDIR/
│  ├─ START_JP.LZS           5 176 725 B [NIS-LZS]
│  │  └─ DAT descomprimido: 36 miembros
│  │     ├─ script00.dat     915 472 B (eventos)
│  │     ├─ talk00.dat       122 000 B (diálogo)
│  │     ├─ char/magic/skill/kis/name/ritem/com/mapinfo.dat
│  │     ├─ fontB.fnt/fontB.ftd y FontB0000/0001.txp
│  │     └─ sys2..7.txp y otros recursos (atlas)
│  ├─ SCRIPTPACK.DAT         2 779 759 B [NISPACK, 32 miembros]
│  │  ├─ script01..18.dat y otros scripts (según tabla real)
│  │  └─ talk*_jp.dat (diálogos)
│  ├─ MAPPACK.DAT           38 943 202 B [NISPACK, 144 entradas]
│  ├─ BGPACK.DAT            68 830 224 B [NISPACK, 285 entradas]
│  ├─ ANMPACK.DAT           97 791 200 B [NISPACK, 360 entradas]
│  ├─ SOUND_01_JP.DAT      271 308 801 B [formato interno no determinado]
│  ├─ SOUND_02_JP.DAT           16 385 B [formato interno no determinado]
│  └─ DUMMY_DATA          262 144 000 B [contenido no investigado]
└─ otros: SFO, PNG, AT3, PRX, UMD_DATA.BIN

PSP/GAME/ULJS00244/
├─ DL_JP_00.EDAT 5 127 190 B ─ NISPACK → start_jp.lzs → DAT (36)
├─ DL_JP_01.EDAT 5 203 970 B ─ NISPACK → start_jp.lzs → DAT (36)
├─ DL_JP_02.EDAT 5 267 964 B ─ NISPACK → start_jp.lzs → DAT (36)
└─ DL_JP_03.EDAT 5 348 846 B ─ NISPACK → start_jp.lzs → DAT (36)
   cada DAT incorpora script00.dat, talk00.dat, fontB y tablas/atlas del DLC
```

**Precisión de nombres:** el archivo externo aportado se llama `START_JP(1).LZS`. Su SHA-256 es `22be383708fe5520cf9da7efa302a2502a9fca82727874b644ab64ad2d72620a`, igual al `START_JP.LZS` incluido en la ISO. **No se encontró `START_LP.LZS`** en esta muestra.

Hay **28 registros ISO9660** enumerados (incluidos directorios). Los contenedores ANMPACK y BGPACK tienen una cantidad de miembros superior al límite de 200 usado por algún parser histórico; **no concluir que estén corruptos** por dicho límite artificial. Su estructura exterior es NISPACK; el significado completo de sus miembros sigue sin estudiarse.

## 3. Cabeceras y límites para editar sin destruir datos

| Capa | Estructura observable | Qué debe actualizarse |
|---|---|---|
| ISO9660 | PVD en sector 16; registros con LBA/tamaño LE y BE | ambos endianness, LBA, tamaño, tamaño del volumen |
| NIS-LZS | cabecera 16 B; longitud original, longitud comprimida, marcador de escape | recomprimir, comprobar ida/vuelta, relocalizar si crece |
| NISPACK | `NISPACK\0`, flag endian, número de archivos, entradas de 44 B (nombre 32, offset, tamaño, auxiliar) | offsets, tamaños, alineación observada y auxiliares preservados |
| DAT indexado | 16 B iniciales y N entradas de 32 B; fin acumulado + nombre | todos los finales siguientes al miembro editado |
| `script*.dat` | u32 N + N×u32 índices; opcode `0x32`, u8 longitud y texto terminado NUL | índices, u8 (máximo 255 B **con** NUL), evento y tiempos por probar |
| tablas DAT fijas | campos de registros con longitudes por perfil; NUL | no invadir padding, números ni siguiente registro |
| `talk*.dat` | entradas encadenadas/control `0x01` observado | continuidad, límites por caja y referencias del diálogo |
| fuente `fontB` | 2 TXP de 132 112 B y mapas FNT/FTD de 23 232 B | CP932/gaiji, ubicación de glifos, ancho visual real |

**Bytes vs bits:** un campo de 24 bytes son 192 bits de almacenamiento, **no** 24 caracteres garantizados. Con NUL de 1 B quedan 23 B para texto; una letra española privada `F0xx` ocupa 2 B y requiere atlas y decodificador compatible. Ni espacio binario ni compresión garantizan que el texto quepa en pantalla.

## 4. Flujo técnico en el repositorio

```text
Fuentes legítimas ──┬─> parsers ISO/EDAT/NISPACK/LZS/DAT ──> unidades y SHA
                    └─> inventario original congelado
                           ↓
glosario → corpus/01..15 + 509 centrales → QA → presupuesto en bytes/píxeles
                           ↓
parcheador GUI Windows (Go main.go + PowerShell gui.ps1)
   v0.13: construir_parche.py → tablas fijas + diálogo + fuentes + menús
   v0.14: scripts 0x32 con reubicación conservadora
   v0.16: ensayo aislado de fase CP932 en 14 unidades problemáticas
                           ↓
copias ISO + 4 EDAT, informes por unidad, SHA y pruebas de reversión
                           ↓
PPSSPP: escena, timing, HUD, guardado, DLC, screenshots, revisión final
```

La **v0.16.1 experimental** añade un aislamiento fundamental: una referencia rechazada **no** puede cancelar la escritura de textos no relacionados del mismo script.

## 5. Lo que NO se sabe todavía

- La semántica real de los 15 índices que apuntan al segundo byte de caracteres CP932; pueden ser referencias de ejecución, marcas de flujo, temporización u otra estructura.
- El bytecode completo del intérprete, los consumidores de punteros MIPS, los formatos internos completos de sonido, mapas, animaciones, fondos y vídeo.
- El clipping/anchura de cuadros y todos los atlas a escala de pantalla; la integridad de una fuente no prueba que cada glifo se vea.
- La ejecución real de toda escena y los cuatro DLC en PPSSPP. Por eso **no** se declara 100 %.

Reproducción: `python parcheador/investigacion/v0.15/inventario_forense.py --iso original.iso --dlc-directorio ULJS00244 --salida catalogo --limite-mib 128` para metadatos; `auditar_anclas.py` para los 14 índices; `verificar_v014.py` para reversión ISO+DLC. No se publican binarios comerciales.
