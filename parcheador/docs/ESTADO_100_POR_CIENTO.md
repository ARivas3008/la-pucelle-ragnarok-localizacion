# Estado de integración de texto: 15 de noviembre de 2026

## Universo de datos

- 26 258 unidades del manifiesto principal.
- 15 016 grupos editoriales distribuidos entre 15 corpus; 509 grupos centrales.
- La v0.10 identificó 21 751 cadenas de la familia talk y 837 continuaciones adicionales; las pruebas de ampliación son sintéticas, **no un porcentaje de cobertura española**.
- La v0.11 auditó 4507 unidades de 66 recursos no-talk y clasificó 3664 como candidatas estructurales.
- La v0.12 produjo 296 nuevas soluciones de ensayo: 197 reducciones, 94 casos script y 5 especiales. Otros 547 casos siguieron sin validación conservadora en el balance del informe.
- La v0.13 conserva los archivos de investigación y añade una vía **optativa** de 197 sustituciones breves. En una prueba con recursos originales sin otras inserciones se pudieron aplicar 197/197: 145 a tablas DAT y 52 a cadenas ASCII de EBOOT. Es una prueba de compatibilidad estructural, **no de fidelidad ni de renderizado**.

## Pendientes reales

1. Cadenas de formato variable con referencias de bytecode y temporización no completamente documentadas. En v0.12 se probaron 14 referencias en el segundo byte de caracteres CP932 solo bajo modo experimental, excluido del ejecutable de producción.
2. Campos de etiqueta sin abreviación aceptable y propuesta de nuevo esquema/anchura de HUD todavía no confirmada.
3. 62 entradas de textura que requieren atlas y pruebas visuales; no tratarlas como cadenas de diálogo.
4. Traducciones pendientes de investigación editorial, controles no ASCII de EBOOT y escenas de introducción.
5. Verificación de cada capítulo, menú, combate, transición, guardado y DLC en PPSSPP.

## Reglas de aceptación del 100 %

No se marcará completado hasta que cada unidad tenga uno de los estados `APLICADO_VERIFICADO_PPSSPP` o `NO_TRADUCIBLE_JUSTIFICADO`, sin entradas de contenido pendientes, y un acta de regresión visual que demuestre ausencia de desbordamientos, texturas corruptas y referencias inconsistentes.

Los estados `APLICADO_*` actuales no implican el primero de esos dos estados de aceptación. No se alterará «Now Loading».
