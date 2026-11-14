# Cómo iniciar la revisión de los 15 corpus

## Estado del proyecto

- Repositorio GitHub público y operativo: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion
- Proyecto ChatGPT: https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project
- Los 15 corpus originales y el material de referencia YA ESTÁN publicados en GitHub.
- El workflow de GitHub Actions QA se instaló y superó las pruebas iniciales.
- El usuario eligió expresamente el repositorio público; no se requiere cambiarlo a privado ni cargar otro ZIP.

## Activar la revisión desde ChatGPT

1. Abrir el proyecto de ChatGPT y comprobar que las instrucciones del proyecto coincidan con [CHATGPT_PROJECT_INSTRUCCIONES.md](CHATGPT_PROJECT_INSTRUCCIONES.md).
2. Abrir 15 chats independientes dentro del proyecto.
3. Escribir exclusivamente el número del corpus asignado: 1, 2, …, 15.
4. Cada chat consultará el glosario y su carpeta de GitHub, revisará unos 40–60 grupos por tanda y guardará cambios en la rama `revision/corpus-NN`.
5. Responder `continúa` en el chat correspondiente para procesar la siguiente tanda.
6. Al terminar, cada chat debe ejecutar QA estricto y abrir un PR dirigido a `main`.

El chat revisor **solo edita `corpus/NN/revision.csv`**. El texto fuente, el índice, los mapas Excel y los otros corpus son inmutables.

## Después de las 15 revisiones

El coordinador:
- comprueba los 15 PR y su QA,
- vuelve a validar los 509 grupos de control previo,
- reconstituye una copia del Excel maestro,
- resuelve códigos, codificación, longitud y punteros para el motor del juego,
- realiza una inserción experimental en una copia de la ISO y prueba los DLC.

No se declaran aprobadas automáticamente las traducciones MTL anteriores. La inserción en la ISO es una fase técnica posterior, no una acción de los chats de corpus.

## Aviso

El repositorio es público por decisión del titular y contiene diálogos extraídos del juego. Los derechos sobre el texto original continúan perteneciendo a sus respectivos titulares. No incluir imágenes de disco, archivos EDAT/EBOOT ni otros recursos binarios comerciales en commits o PR.
