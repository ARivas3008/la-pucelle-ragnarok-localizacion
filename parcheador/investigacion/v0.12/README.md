# La Pucelle: Ragnarok — propuestas de solución para los 66 recursos (v0.12)

**ESTADO: ingeniería experimental, no es una ISO/DLC lista para jugar.** Esta entrega es una ampliación del paquete v0.11. Se ha trabajado con la ISO original y los cuatro DLC proporcionados por el usuario, sobre copias de los recursos. No se incluyen datos binarios de los juegos.

## Resultado contrastado

La auditoría anterior tenía 4 507 unidades de 66 recursos no pertenecientes a `talk*.dat`: 3 664 candidatas estructurales y 843 sin resolver. Los nuevos ensayos v0.12 consiguen **296 candidatos estructurales adicionales**: 197 reducciones dentro de un campo sin mover nada externo (145 DAT + 52 EBOOT), 94 scripts adicionales con reubicación de anclas en límites de carácter y 5 casos con perfiles especiales de campo. En consecuencia, **547 casos siguen sin una solución conservadora comprobada**.

La prueba de 197 reducciones calcula los bytes reales, coteja la fuente contra el binario original, conserva el tamaño del archivo y comprueba que no cambien bytes fuera del campo correspondiente. Las propuestas editoriales NO están aprobadas simplemente por superar esta prueba. Hay 48 alternativas adicionales que caben según la longitud pero necesitan cotejo semántico y no se aplican por defecto; 335 no tienen todavía propuesta breve adecuada.

De los 503 scripts analizados (se excluye el rótulo **Now Loading**, por petición del usuario), 489 admiten un ensayo estructural de reubicación en modo conservador y 14 se bloquean porque 15 anclas caen dentro del **segundo byte de un carácter CP932**. El modo `--anclas-subcaracter-experimentales` permite reconstruir y revertir los 503 scripts, pero modifica la posición interpretada de 15 referencias y **NO está validado en PPSSPP**. Está DESACTIVADO por defecto. Reversibilidad binaria no implica corrección visual o de temporización.

## ¿Por qué no se parten todas las frases en dos?

- `char.dat`, `magic.dat`, `skill.dat`, `kis.dat`, `name.dat` y demás tablas fijas contienen **etiquetas, nombres y descripciones HUD**, no cajas de diálogo. Dividir una etiqueta crearía datos fuera del registro y puede corromper estadísticas. La solución segura es abreviar sin perder sentido o modificar, con ingeniería adicional del ejecutable, el formato del registro y su componente visual.
- Los scripts ya pueden expandir cadenas actualizando el opcode de longitud `0x32` y su tabla de referencias. Dividirlas en **dos cuadros** exigiría un opcode adicional y comprender su efecto en la línea temporal, el cambio de hablante y los índices. Entre los 14 casos de anclas mal alineadas, solo **1** tiene una instrucción de texto vacía inmediatamente posterior; esa presencia no demuestra que sea un lugar libre para insertar otro diálogo. **No se divide automáticamente ninguna caja**.
- Los 62 textos de textura requieren atlas, coordenadas UV y paleta; ninguna división en cadenas los reemplaza.
- Las cadenas `EBOOT.BIN` con símbolos no ASCII necesitan comprobar que el ejecutable admita realmente el mapa de glifos. Una codificación que cabe en bytes no acredita que se dibuje bien.

## Estructura del paquete

- `datos/estado_unificado_66.csv`: auditoría anterior de las 4507 unidades.
- `v012/propuestas_reduccion.csv`: 580 desbordamientos de campo con alternativa candidata, estado de investigación y capacidad en bytes.
- `v012/informe_final/estado_843_v012.csv`: las 843 unidades con su clasificación actual y recomendaciones individuales.
- `v012/informe_final/resumen_843_v012.json`: balance de 296 ensayos estructurales y 547 casos pendientes.
- `v012/aplicar_compactaciones_v012.py`: comprobador y aplicador opcional **solo en copias** de campos fijos, con fuente original verificada.
- `v012/reubicador_anclas_v012.py`: editor reversible de scripts con índices interiores. Rechaza por defecto anclas dentro de caracteres.
- `v012/ensayar_scripts_108.py`: audita 503 cadenas del script y genera reportes; modo subcarácter excepcional solo con bandera explícita.
- `v012/ensayar_especiales_v012.py`: ensayo de cinco campos especiales.
- `v012/probar_contenedores_v012.py`: ensaya la reconstrucción de seis contenedores, usando un compresor NIS LZS **externo que no se distribuye en este paquete**.
- `v012/ensayo_contenedores/resultado_contenedores.json`: resultado real sobre los archivos originales (estructural, sin juego corriendo).
- `v012/ensayo_anclas/auditoria_anclas.csv`: 109 casos de anclas interiores, incluido el único rótulo omitido deliberadamente.
- `LaPucelle_66_Recursos_v011_Investigacion/*.py`: utilidades de interpretación de recursos necesarias por v0.12.
- `v012/tests/`: nueve pruebas nuevas, sin ejecutar el juego; `LaPucelle_66_Recursos_v011_Investigacion/tests/`: quince pruebas anteriores (cinco requieren originales extraídos y se omiten sin ellos).

## Ejecutar pruebas y emitir informe en Windows (Python 3.10+)

Desde la carpeta en la que se extrae el ZIP:

```powershell
python -m unittest discover -s v012/tests -v
python -m unittest discover -s LaPucelle_66_Recursos_v011_Investigacion/tests -v
python v012/informe_integracion_v012.py --estado datos/estado_unificado_66.csv --propuestas v012/propuestas_reduccion.csv --scripts v012/ensayo_scripts/auditoria_scripts.csv --especiales v012/ensayo_especiales/casos_especiales.csv --destino informe_actualizado
```

Para ensayar sustituciones de nombres/etiquetas sobre recursos extraídos **propios**, sin escribir archivos modificados (modo auditoría por defecto):

```powershell
python v012/aplicar_compactaciones_v012.py --propuestas v012/propuestas_reduccion.csv --auditoria datos/estado_unificado_66.csv --source "C:\LaPucelle\extraidos" --output resultados_compactaciones
```

Si se añade `--guardar-borradores`, escribe archivos **individuales de prueba** solo en la carpeta de salida; **no genera una ISO jugable**. Para scripts:

```powershell
python v012/ensayar_scripts_108.py --auditoria datos/estado_unificado_66.csv --source "C:\LaPucelle\extraidos" --output resultados_scripts
```

La variante `--anclas-subcaracter-experimentales` se entrega **para investigación**, no debe activarse en una partida. Los archivos de trabajo permanecen propiedad del usuario y no se deben distribuir como juego parcheado.

## Alcance y límites de las pruebas

- Scripts: 489/503 en modo conservador; 503/503 en modo experimental, todos con reversión exacta, pero **sin ejecución confirmada**.
- Campos fijos: 197/197 propuestas seleccionadas pasan la comparación de fuente, capacidad y rango, sin escribir fuera de sus registros.
- Campos especiales: 5 inserciones con reversión, sin certificación editorial.
- Contenedores: la reconstrucción de los seis contenedores evaluados conservó sus miembros no modificados. No hay un nuevo ejecutable Windows ni un parche completo en este paquete.
- No se han alterado «Now Loading», los archivos originales ni partidas guardadas.

**Falta**: 335 textos sin abreviación válida, 48 sugerencias editoriales por cotejar, 14 anclas temporales sin prueba en PPSSPP, 62 referencias gráficas, 46 casos de EBOOT con código no ASCII, 34 grupos editoriales, entre otros casos. El informe por unidad muestra el estado preciso de cada uno, incluidos casos que no requieren sustitución.
