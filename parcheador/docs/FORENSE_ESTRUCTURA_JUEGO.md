# Dossier forense de La Pucelle: Ragnarok (PSP)
**Edición:** 2026-11-15 · **Versión técnica:** 0.15 · **Alcance:** ISO 1.1.2 y cuatro DLC suministrados en este proyecto · **Uso:** comprensión, preservación e inserción local de traducciones.

> Documento de ingeniería inversa de la **estructura observable en los recursos y herramientas** del proyecto, no del código fuente original del juego. Las estructuras no analizadas se marcan como desconocidas. La reversibilidad de un contenedor no demuestra que el juego se ejecute.

## 1. Qué se ha investigado y qué se puede afirmar

**Verificado por las herramientas y ensayos del repositorio:** lectura de ISO9660; lectura y reconstrucción de NISPACK, DAT y NIS-LZS para los recursos inspeccionados; campos de texto de tamaño fijo para ocho familias; origen de los textos de diálogo tipo talk y de eventos tipo script; fuentes fontB, glifos españoles privados y determinadas texturas de la interfaz; pruebas de reubicación y reversión, y los estados de cada unidad. La v0.14 documenta una reconstrucción de ISO + cuatro DLC que preserva recursos ajenos a los scripts.

**Parcialmente determinado:** semántica completa de bytecode de talk/script, llamadas internas del EBOOT, temporización de escena, límites gráficos reales de cada cuadro, atlas de todas las capas introductorias, sincronización de los 14 punteros subcarácter, capacidad real para traducir todas las cadenas sin división, e identidad de recursos no catalogados.

**No comprobado:** terminación o jugabilidad al 100 %, ejecución de todas las escenas en PPSSPP, desbordamientos de cualquier HUD, descifrado de formatos PSP externos a estos archivos, código fuente original de NIS.

## 2. Capas del juego: mapa de ubicación

~~~text
Disco PSP (ISO9660, bloques de 2048 B; PVD sector lógico 16)
└── /PSP_GAME/
    ├── SYSDIR/EBOOT.BIN
    │   ├── código/recursos PSP (no interpretados íntegramente)
    │   └── algunas cadenas de UI de longitud fija comprobada
    └── USRDIR/
        ├── START_JP.LZS — NIS LZS
        │   └── DAT descomprimido (índice de miembros y tamaños)
        │       ├── script00.dat / otros script*.dat
        │       ├── fontB / fontB000*.txp (según paquete)
        │       ├── sys3.txp, sys4.txp y otros atlas de UI
        │       └── datos de personajes/objetos y otros DAT
        ├── SCRIPTPACK.DAT — NISPACK
        │   ├── talk*_jp.dat — diálogo encadenado y bytecode
        │   └── script*.dat — eventos, textos y tabla de anclas
        ├── BGPACK.DAT — fondos y elementos gráficos
        ├── ANMPACK.DAT — animaciones
        ├── MAPPACK.DAT — mapas
        └── otros miembros del disco, todavía no todos clasificados

DLC: PSP/GAME/ULJS00244/DL_JP_00.EDAT … DL_JP_03.EDAT
└── NISPACK observado en estas copias
    └── START_JP.LZS — NIS LZS
        └── DAT de miembros (scripts, texturas, datos de UI y HUD)
~~~

El árbol representa las **rutas estudiadas** y no pretende enumerar todos los ficheros de la ISO. La extensión EDAT no se extrapola a un formato genérico: las cuatro copias suministradas aceptaron el parser NISPACK; otros EDAT pueden ser distintos. Para obtener el inventario de una copia concreta, ejecutar la herramienta de solo lectura de v0.15.

## 3. Índices, cadenas, controles y vistas

| Capa | Archivo | Para qué sirve en la localización | Qué NO hacer |
|---|---|---|---|
| ISO9660 | imagen .iso | localizar EBOOT, START, paquetes; relocalizar archivos sobre copia | cambiar LBA sin actualizar ambos endianness y tamaño |
| NIS-LZS | START_JP.LZS | descomprimir y comprimir recursos de la carga | sobreescribir comprimido mayor sin relocalizar |
| DAT indexado | START descomprimido | separar miembros y actualizar finales acumulados | insertar bytes sin rehacer tabla |
| NISPACK | SCRIPTPACK y EDAT verificados | separar miembros de 44 B, conservar auxiliares | cambiar offsets sin respetar alineación comprobada |
| talk | talk*_jp.dat | intervenciones, continuaciones y saltos de línea | repartir textos arbitrariamente por tamaño |
| script | script*.dat | textos de evento y narración con opcode 0x32 | asumir que toda entrada es comienzo de texto |
| DAT fijo | char, magic, skill, name, kis, ritem, com, mapinfo | nombres, descripciones y etiquetas de HUD | desplazar estadísticas o rellenar con contenido no nulo |
| EBOOT | EBOOT.BIN | opciones y menús probados | alterar bytecode PSP o expandir cadenas sin referencias |
| TXP/fuente | fontB, sys*.txp | glifos, turnos, objetivos y HUD | redimensionar atlas sin actualizar UV/posiciones |
| Intro | script + atlas/vídeo | algunos rótulos de evento están en scripts | deducir que cada subtítulo se guarda en texto |

## 4. Datos maestros y trazabilidad editorial

- Universo técnico: **26 258 unidades** en data/maestros/04_MANIFIESTO_INSERCION_26258_CON_DIVISION.csv. Una unidad tiene ID, recurso, offset original y ubicación editorial.
- Grupos: **15 525** en maestro; **15 016** grupos distribuidos entre quince corpus, **509** coordinados por separado.
- La fuente de traducción está en corpus/01 … corpus/15, columna es_revisado, con estado editorial. No debe sobrescribirse el original ni el orden por ID.
- Un grupo puede corresponder a varias unidades. **No es lícito inferir límites de cuadro de una división proporcional por longitud**.
- Las variables, códigos de control, glifos y offsets forman parte del contrato de inserción.
- Informes históricos: v0.10 auditó 21 751 cadenas talk del mapa y 837 continuaciones; v0.11 auditó 4507 unidades en 66 recursos no-talk; v0.12 añadió propuestas estructurales; v0.14 insertó 489 scripts en una prueba binaria. Estas métricas se superponen: **no deben sumarse** para calcular cobertura global.

## 5. Flujo real del programa de parcheo

~~~text
GUI Windows (Go main.go → Windows Forms gui.ps1)
  → selección ISO / DLC / salida / opciones
  → motor Python construir_parche.py
  → manifiesto 26 258 + revisiones de 15 corpus
  → validación de procedencia, controles, codificación
  → reemplazos de tamaño fijo + segmentación conservadora
  → ampliación segura de campos + atlas bajo SHA
  → reconstrucción DAT / NISPACK / LZS
  → copia ISO, nuevas entradas de LBA y tamaño; DLC nuevos
  → informe por unidad + resumen y huellas SHA
Investigación aislada:
  v0.9–v0.10 → ampliación de talk y reconstrucción estructural
  v0.11–v0.13 → campos fijos, scripts y compactación
  v0.14 → reubicación conservadora de scripts (489)
  v0.15 → análisis detallado de 14 anclas subcarácter SIN modificación
~~~

Las opciones peligrosas de las herramientas de investigación no están incorporadas a la GUI por defecto. El programa nunca debe escribir sobre la fuente original.

## 6. Hipótesis específicas de las 14 referencias

Los registros exactos están en investigacion/v0.15/casos_14.csv. La auditoría conservadora v0.12 halló **14 cadenas afectadas por 15 índices** que caen en el segundo byte de un carácter Shift-JIS: dos entradas corresponden a la unidad 1759. Los textos incluyen Prier, Alouette y frases sin nombre alguno.

**Hecho:** una referencia al segundo byte NO apunta al comienzo de una secuencia CP932 válida. Esto contradice cualquier interpretación simplista «puntero al texto». Puede ser un offset de entrada en otra representación, una frontera que atraviesa una cadena extraída, o una referencia a datos cuyo significado falta investigar. Ninguna hipótesis queda demostrada solo por la tabla.

**Intento v0.12:** desplazar una referencia subcarácter al primer byte del carácter anterior, para que resulte bien formada; pasa reversión binaria pero cambia su posición.

**Mejora v0.15:** informar del índice, offset, par CP932, SHA de origen y posibles referencias con la **misma fase** (segundo byte → segundo byte). No se escribe un parche con ese cálculo. Si la traducción usa únicamente ASCII en el entorno del ancla, puede no existir segundo byte equivalente; se marca sin candidato. Una prueba de archivo jamás convierte esto en una prueba del intérprete de eventos.

**Prueba pendiente:** instrumentar en PPSSPP la lectura de la tabla y la instrucción consumidora, seguir un caso con texto sin cambiar y determinar si el índice se usa como dirección, cursor, tiempo o dato. Solo entonces decidir entre reubicación, división en dos instrucciones o ajuste específico del intérprete. La división requiere confirmar un opcode de continuación y el efecto sobre la escena.

## 7. Por qué ocurren los fallos de las capturas

- **Inglés junto a español:** una unidad insertada y otra bloqueada dentro de la misma intervención. Aplicar política atómica por intervención; no reemplazar solo media caja.
- **Letras y símbolos erróneos:** bytes de fuente gaiji F0 sin glifo operativo en la textura/decodificador o mezcla de CP932 y codificación privada. Comprobar renderizado real, no solo longitud en bytes.
- **Atlas deformado o desaparecido:** disposición/tamaño/swizzle o índices de paleta afectados. Usar cambios de píxeles dentro de área y cabecera/paleta originales, con SHA de origen y comparación por región.
- **HUD desbordado:** cadena dentro del campo binario pero demasiado ancha en píxeles. Medir anchura real con la fuente y el clipping en PPSSPP, abreviar o reducir el tipo de letra solo con coordenadas verificadas.
- **Texto japonés de introducción:** algunos eventos usan script00.dat y opcode 0x32; otros rótulos pueden estar en capas, texturas o vídeo. Deben vincularse por observación en tiempo de ejecución.

## 8. Reproducción y criterios forenses

1. Conservar copias originales, versión del juego, nombres y SHA256 de ISO y cuatro DLC.
2. Capturar inventario por ruta/offset/tamaño/hash; tratar formatos no reconocidos como DESCONOCIDO.
3. Extraer sin escritura. Para cada miembro, conservar origen, compresión, contenedor padre y offset relativo.
4. Asociar cada unidad a ID/grupo/contexto/original y offset en manifiesto. Verificar exactamente el texto en binario.
5. Registrar antes/después de longitud, punteros, bytecode adyacente, saltos, fuentes, miembros intactos.
6. Al insertar: crear archivos nuevos, ejecutar relectura y reconstrucción inversa; comparar vecinos byte por byte.
7. Al validar en PPSSPP: probar la escena, incluir configuración y capturas, contraste con original, savestates limpios y DLC.
8. No clasificar «APLICADO_VERIFICADO_PPSSPP» sin prueba real; registrar pendientes en lugar de declarar 100 %.

### Entradas comprobables del repositorio

- [Formatos LZS y NISPACK](../app/scripts/nis_formats.py)
- [Reconstructor DAT y NISPACK](../investigacion/v0.10/contenedores.py)
- [Reubicación ISO9660](../investigacion/v0.10/iso_reubicar.py)
- [Campos fijos](../app/scripts/campos_fijos.py)
- [Fuentes y CP932/gaiji](../app/scripts/fuentes_es.py)
- [Reubicador de anclas v0.12](../investigacion/v0.12/reubicador_anclas_v012.py)
- [Prueba de inserción v0.14](../investigacion/v0.14/README.md)
- [Auditoría subcarácter v0.15](../investigacion/v0.15/README.md)
- [Estado editorial y técnico del proyecto](ESTADO_100_POR_CIENTO.md)

El inventario público debe contener solo metadatos, hashes, código propio y citas técnicas, no volcados completos de diálogos, ISO, EDAT o texturas comerciales.
