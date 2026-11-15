# Estado de integración de texto: 15 de noviembre de 2026

## Universo de datos

- 26 258 unidades del manifiesto principal.
- 15 016 grupos editoriales distribuidos entre 15 corpus; 509 grupos centrales.
- La v0.10 identificó 21 751 cadenas de la familia talk y 837 continuaciones adicionales; las pruebas de ampliación son sintéticas, **no un porcentaje de cobertura española**.
- La v0.11 auditó 4507 unidades de 66 recursos no-talk y clasificó 3664 como candidatas estructurales.
- La v0.12 produjo 296 nuevas soluciones de ensayo: 197 reducciones, 94 casos script y 5 especiales. Otros 547 casos siguieron sin validación conservadora en el balance del informe.
- La v0.13 conserva los archivos de investigación y añade una vía **optativa** de 197 sustituciones breves. En una prueba con recursos originales sin otras inserciones se pudieron aplicar 197/197: 145 a tablas DAT y 52 a cadenas ASCII de EBOOT. Es una prueba de compatibilidad estructural, **no de fidelidad ni de renderizado**.

- La v0.14 escribió **489 de las 503 unidades traducibles de `script*.dat`** sobre una ISO y cuatro DLC de prueba, verificó los contenedores y conservó `Now Loading`. El modo experimental consigue reubicar estructuralmente 503/503, pero las 14 referencias subcarácter requieren QA de ejecución. Los 489 textos son **una subfamilia de las 4507 unidades no-talk**: no deben sumarse de forma directa a cifras anteriores para inferir una cobertura global.

## Pendientes reales

1. Cadenas de formato variable con referencias de bytecode y temporización no completamente documentadas. En v0.12 se probaron 14 referencias en el segundo byte de caracteres CP932 solo bajo modo experimental, excluido del ejecutable de producción.
2. Campos de etiqueta sin abreviación aceptable y propuesta de nuevo esquema/anchura de HUD todavía no confirmada.
3. 62 entradas de textura que requieren atlas y pruebas visuales; no tratarlas como cadenas de diálogo.
4. Traducciones pendientes de investigación editorial, controles no ASCII de EBOOT y escenas de introducción.
5. Verificación de cada capítulo, menú, combate, transición, guardado y DLC en PPSSPP.

## Reglas de aceptación del 100 %

No se marcará completado hasta que cada unidad tenga uno de los estados `APLICADO_VERIFICADO_PPSSPP` o `NO_TRADUCIBLE_JUSTIFICADO`, sin entradas de contenido pendientes, y un acta de regresión visual que demuestre ausencia de desbordamientos, texturas corruptas y referencias inconsistentes.

Los estados `APLICADO_*` actuales no implican el primero de esos dos estados de aceptación. No se alterará «Now Loading».

## Investigación posterior v0.15

Las 14 unidades con 15 anclas internas CP932 quedaron catalogadas y pueden auditarse en los originales sin escritura. La hipótesis de fase segundo byte → segundo byte se genera como candidato, no como parche aprobado. La cobertura española real **no aumenta** hasta que se identifique la semántica de los índices y se validen las escenas en PPSSPP. Detalles en [MATRIZ_14.md](../investigacion/v0.15/MATRIZ_14.md).


## Evaluación v0.16 (experimental, 15-11-2026)

Se verificaron 15 referencias CP932 dentro de 14 cadenas sobre la ISO y los 4 DLC originales. El ensayo de fase conservada halló solo 4 unidades con candidato cercano (1758, 1759, 3924, 4170). Los otros 10 casos permanecen bloqueados. La compilación de EXE y la reversibilidad no sustituyen las pruebas de PPSSPP ni la aprobación editorial de las 26 258 unidades: el cumplimiento global **no es 100 %**.


## Corrección de balance v0.16.1 (reproducción real)

La primera v0.16 rechazaba **344 candidatos** de script al combinar referencias inseguras con un lote: solo 159 ediciones sobrevivían. Después de corregir el aislamiento, los **489** textos conservadores siguen insertándose y **3** referencias subcarácter adicionales generan archivos reversibles, pero **no están verificadas en PPSSPP**. Las **otras 11** unidades siguen bloqueadas, incluida 1759 (dos referencias). No confundir `492/503` de esta familia con el 100 % del manifiesto general (26 258 unidades).

Las familias restantes con pendientes incluyen tablas fijas que exceden campo, EBOOT, 62 texturas no tratadas como textos, continuaciones talk, renderización/anchuras y aprobación editorial. El estado de cumplimiento final permanece **NO CERTIFICADO**. Véase [v0.16](versiones/v0.16.md).
