# Estado de GitHub — La Pucelle Ragnarok

Fecha: 14 de noviembre de 2026.

## Publicación comprobada
- Repositorio público: https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion
- Proyecto ChatGPT: https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project
- **15 corpus y 15 016 grupos pendientes** publicados, junto con lecturas, revisión editable, glosario y mapas de reintegración.
- **509 grupos** con revisión previa conservados por separado para la auditoría central.
- Al importar se verificó el Git bundle completo por SHA-256 (`23a69b383dc25eebf8aab75842175e64c3057cd7a44e38e5ca808d38cd6ca3f7`), se recuperaron 122 archivos de origen y se ejecutó `python scripts/validar.py` sin errores.
- El workflow `.github/workflows/qa.yml` se ha añadido mediante la conexión GitHub y comprobado satisfactoriamente.
- Los archivos de bootstrap temporales han sido retirados del árbol de `main` después de completar la importación.

## Próximos pasos
1. Asegurar que la configuración del Proyecto ChatGPT utilice `CHATGPT_PROJECT_INSTRUCCIONES.md`.
2. Abrir un chat para cada número del 1 al 15.
3. Procesar sublotes editoriales de 40–60 grupos; editar exclusivamente `corpus/NN/revision.csv` en una rama por corpus.
4. Abrir PR solo después de validar el corpus completo.
5. Coordinar la fusión, reconstrucción del Excel y preparación técnica de la ISO.

El repositorio continúa **público por elección expresa del usuario**; no debe presentarse la privacidad como requisito de activación.
