# Organización y conservación del historial

La consolidación del 23-11-2026 reúne el motor vigente, las 15 revisiones del corpus, la metodología y la investigación local en `main`.

Las 26 ramas anteriores se archivan mediante etiquetas `archivo/2026-11-19/<nombre-original>`, conservando exactamente su commit. La fecha identifica el inventario inicial, no la fecha de publicación. El [inventario de ramas y SHA](informes/ramas_2026-11-19.json) permite recuperar cualquier estado. Las ramas solo se retiran después de publicar y verificar estas etiquetas y la nueva entrega; si una rama cambia entretanto, la limpieza se detiene.

Las ramas de revisión 01–14 ya eran antecesoras de main. La revisión 15 y la metodología se incorporan completas; las correcciones locales posteriores se conservan sobre ellas. Las implementaciones experimentales anteriores permanecen accesibles en sus etiquetas y fichas históricas. Los PR experimentales superados se cierran con referencia a la entrega vigente, sin atribuirles una validación visual que no tienen.

## Política de entregas

1. Compilar una candidata y ejecutar las comprobaciones estructurales y el parcheo completo con originales compatibles.
2. Registrar cobertura, cambios, retiradas, pendientes, pruebas y SHA-256.
3. Publicar el `.exe` y sus informes en Releases; etiquetar como preliminar mientras falte la validación visual.
4. Comprobar la descarga y su hash. Después retirar los binarios de versiones sustituidas y registrar su eliminación, manteniendo sus notas, etiquetas y fuentes.
5. Mantener una sola entrega binaria vigente. Conservar los originales del usuario y toda la evidencia técnica necesaria.

Para nuevo trabajo, abrir ramas breves por tarea desde main. Las ramas `revision/corpus-NN` se reservan a revisión editorial; las ramas de integración pueden abarcar código, corpus y documentación con QA completo.
