# La Pucelle: Ragnarok — pruebas de cobertura v0.10

**No es un parche final, no tiene un EXE de instalación y NO ha superado la prueba jugable.**

Este paquete es un avance de ingeniería inversa y QA destinado a llevar la inserción de los
15 corpus al 100 % sin romper el juego. El modo de ensayo **no introduce traducciones**:
añade dos bytes de prueba al final de cada cadena localizada y comprueba que puede
actualizar los índices, reconstruir los archivos y recuperar los originales.

## Resultados con los originales aportados

- 26 258 unidades registradas en el manifiesto de extracción.
- 21 751 unidades `talk*.dat` en el manifiesto, de 21 archivos binarios.
- 439 registros antes considerados «fuente no coincide» se corresponden con el texto del
  juego tras normalizar ancho Unicode y eliminar **únicamente los espacios externos de
  relleno**. No deben borrarse los espacios de sangría al aplicar traducciones.
- 809 arranques de continuación sin unidad en el manifiesto; al seguir las cadenas se
  extrajeron **837 cadenas de continuación** adicionales (517 textos distintos).
- De estas 837, 134 tienen una aparición de fuente en el mismo recurso, 684 en otro
  recurso, y 19 carecen de equivalencia en el manifiesto. Solo 180 tienen alguna
  *propuesta provisional* en la unidad encontrada; ninguna se aprueba automáticamente.
- **22 588 cadenas** (21 751 registradas + 837 sin unidad) fueron alargadas en memoria
  y revertidas exactamente sin error de tabla en los 21 archivos de diálogo.
- Los 6 contenedores probados (SCRIPTPACK y cinco START_JP) se reconstruyeron y
  descomprimieron con los 22 588 cambios sintéticos, sin alterar los demás miembros.
- Una ISO **temporal** con las 18 786 cadenas del SCRIPTPACK ampliadas se reubicó
  correctamente; se verificó la preservación de EBOOT y START_JP y se borró la ISO.
- 17 pruebas automáticas superadas.

### Lo que los tests NO prueban

1. Que las referencias internas/saltos de bytecode ajenos al índice principal sean seguros.
2. Que las 837 continuaciones tengan la traducción adecuada y la segmentación correcta.
3. Que las 4 507 unidades del manifiesto fuera de `talk*.dat` puedan reubicarse.
4. Que los 509 grupos de coordinación, las 289 investigaciones editoriales y los
   textos gráficos de la introducción estén terminados. (Son recuentos de ámbitos
   distintos; no deben sumarse como si fueran unidades disjuntas.)
5. Que PPSSPP dibuje adecuadamente las líneas, las fuentes, el HUD ni los DLC.

**Hasta validar esos puntos no hay evidencia de una inserción completa del 100 %.**
El indicador `EXITO_ESTRUCTURAL` nunca debe confundirse con `PARCHE_APTO`.
`Now Loading` se mantiene fuera de alcance por indicación del usuario.

## Herramientas

- `auditoria_ampliada.py`: clasifica coincidencia de fuente original y extrae cadenas no
  mapeadas; con `--stress` amplía de prueba todas las unidades mapeadas.
- `vincular_continuaciones.py`: enlaza las cadenas faltantes con fuentes idénticas.
- `prueba_expansion_con_continuaciones.py`: amplía y revierte también las cadenas nuevas.
- `prueba_contenedores_completa.py`: recompone en temporal SCRIPTPACK y todos los START
  (requiere el compresor del parcheador v0.8; se conserva la ISO/DVD original).
- `prueba_iso_reubicacion_total.py`: reubica temporalmente un SCRIPTPACK ampliado dentro
  de una ISO para comprobar las tablas ISO9660; elimina su copia al terminar.
- `inventario_pendientes.py`: inventario de recursos fuera de los diálogos.
- `relocador.py`, `contenedores.py`, `iso_reubicar.py`: motores experimentales v0.9.
- `informes/`: CSV y JSON, con referencias físicas para investigación.
- `tests/`: pruebas sin uso de las revisiones editoriales como cadenas de ensayo.

## Reproducir en Windows

Se requiere Python 3.10+, los recursos originales del propietario y la carpeta extraída
`ISO_SCRIPT`, `ISO_START`, `DLC_00`, `DLC_01`, `DLC_02`, `DLC_03` que generó el
parcheador v0.8. Como argumento `--manifiesto`, usar el archivo del v0.8:
`datos/mapa_26258_unidades.csv`.

```powershell
python auditoria_ampliada.py --manifiesto "C:\LaPucelle\datos\mapa_26258_unidades.csv" --extraidos "C:\LaPucelle\extraidos" --salida "C:\LaPucelle\audit" --stress
python vincular_continuaciones.py --continuaciones "C:\LaPucelle\audit\continuaciones_sin_unidad.csv" --manifiesto "C:\LaPucelle\datos\mapa_26258_unidades.csv" --salida "C:\LaPucelle\audit"
python prueba_expansion_con_continuaciones.py --manifiesto "C:\LaPucelle\datos\mapa_26258_unidades.csv" --continuaciones "C:\LaPucelle\audit\continuaciones_sin_unidad.csv" --extraidos "C:\LaPucelle\extraidos" --salida "C:\LaPucelle\audit\test.json"
```

Los otros dos ensayos necesitan una ISO y un compresor LZS locales y se ejecutan por
separado con `--help`. No ejecutar sobre archivos que no tengan copia de seguridad.
La investigación no contiene ni distribuye ISO, DLC, EDAT o binarios comerciales.

## Plan de ingeniería necesario para llegar al 100 %

1. Desensamblar y verificar los operadores de salto, las referencias internas y la
   forma en que el motor calcula tamaño/posición de cada cuadro de diálogo.
2. Actualizar el manifiesto añadiendo y alineando las 837 continuaciones recuperadas;
   cotejar las 19 sin equivalente y la relación contextual de las repetidas.
3. Recuperar revisiones de los 509 grupos de coordinación y resolver los casos de
   investigación editorial; verificar que ninguna intervención en juego quede partida.
4. Implementar parsers y pruebas equivalentes para los 66 recursos no talk y la
   geometría del HUD, siempre preservando sus controles y límites gráficos.
5. Construir el parcheador end-to-end y probar escenas representativas de todos los
   capítulos y los cuatro DLC en PPSSPP. Comparar capturas y registros de carga.

No se debe modificar el estado editorial para aprobar artificialmente una cadena.
