# La Pucelle: Ragnarok — Localización al español

Proyecto de traducción colaborativa para revisar 15 016 grupos textuales en **15 corpus** sin perder sus referencias exactas al Excel original.

**Proyecto ChatGPT:** https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project

## Acceso al corpus
La estructura de trabajo de los 15 corpus ya está preparada en un paquete local, pero **no se han publicado sus diálogos** porque este repositorio aún es público. Contiene textos extraídos de un videojuego comercial.

Antes de cargar los corpus completos, cambia el repositorio a **Private** en Settings → General → Danger Zone → Change repository visibility. Este cambio solo puede efectuarlo el propietario.

## Flujo de trabajo

1. Los chats del proyecto toman el número `1` a `15` para seleccionar `corpus/01` … `corpus/15`.
2. Cada chat corrige exclusivamente `corpus/NN/revision.csv` en su rama `revision/corpus-NN`.
3. Conserva IDs, hashes, original, orden, etiquetas de formato (por ejemplo `{0}`, `%s`, `\\n`) y mapa de filas.
4. El control automatizado revisa modificaciones antes del PR; no se considera revisado un corpus por tener solo borradores MTL.
5. Una vez fusionados los 15 PR, el coordinador valida los 509 grupos restantes, recompone una copia del Excel y prepara la inserción experimental en la ISO.

Consulta `AGENTS.md`, `CHATGPT_PROJECT_INSTRUCCIONES.md` y `CONTROL_CALIDAD_Y_REINTEGRACION.md`.

**No alojar ISO, EBOOT, EDAT de DLC ni otros binarios comerciales en este repositorio.**
