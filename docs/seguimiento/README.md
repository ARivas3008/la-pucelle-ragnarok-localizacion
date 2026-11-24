# Seguimiento del proyecto
Línea base 23-11-2026: main d2f3b0ced36173c8535c1ef3fcfb0124aacb1cf0.

Este índice inicial NO es inventario exhaustivo ni prueba de juego. inventario_textos.json identifica por ID los 15.016 grupos de corpus y referencia al manifiesto para su fuente y destino. inventario_graficos.json cataloga las 62 unidades conocidas, sin certificarlas en pantalla. Las matrices técnico/visual son casos iniciales y requieren ampliarse por escena, elección y DLC. auditoria_iso_original_20261123.json acredita únicamente el original auténtico aportado. estado.json no promedia porcentajes incompatibles. La siguiente tarea ejecutable está en prompts/REV-002.md.

Verificar con: python scripts/validar_seguimiento.py. No publicar ISO, DLC ni pesos de HY-MT2.

## Relé autonómico recursivo

[Último relevo ejecutable](prompts/SIGUIENTE_RELEVO.md) · [Dictamen CENT-004](informes/CENT-004.json).

Hasta certificar al 100 % traducción, gráficos, romhacking y betatesting, cada ejecución debe publicar un nuevo prompt de continuidad con esta misma obligación heredada. La cola de propuestas pendientes HY-MT2 queda expresamente excluida del seguimiento obligatorio y de los cálculos.

## RELEVO-002 / CENT-005

[Informe editorial y técnico](informes/CENT-005.json) · [Relevo-003 autónomo](prompts/SIGUIENTE_RELEVO.md). Se revisaron 19 grupos de texto de tutorial. Los prefijos magic.dat se estudiaron con trazabilidad y pruebas sintéticas, sin validar DLC real. Cuatro áreas todavía no certificadas; HY-MT2 pendientes siguen fuera del alcance obligatorio.

## RELEVO-004 (CENT-007 + GFX-001)

[Informe CENT-007](informes/CENT-007.json) | [Auditoría auténtica BGPACK](informes/GFX-001_bgpack_original.json) | [Prompt RELEVO-005](prompts/SIGUIENTE_RELEVO.md). Se revisaron editorialmente 48 grupos y se identificaron ocho candidatos TXP externos al inventario de 62; no están confirmados como texto ni certificados en PPSSPP.

## RELEVO-005 / CENT-008 / GFX-002

Se revisaron 44 grupos editoriales del episodio Eringa y se clasificaron visualmente desde la ISO auténtica ocho TXP sin publicar imágenes comerciales. Se incorporaron metadatos/hash por textura, una herramienta de deswizzle/CLUT 4/8 bpp y ocho casos nuevos de QA visual, aún sin ejecutar. [CENT-008](informes/CENT-008.json) · [GFX-002](informes/GFX-002_txp_original.json) · [RELEVO-006](prompts/SIGUIENTE_RELEVO.md).

## RELEVO-006 — CENT-009, GFX-003, ROM-003

Se aprobaron 43 grupos editoriales independientes en [CENT-009](informes/CENT-009.json), elevando lo conocido a 14.950/15.525. Un original real permitió identificar que el cierre `￥` del grupo 4268 codifica un **corazón**: CP932 `81 8F`, fnt índice 175 → GID99, atlas original; su visualización en la build parcheada sigue pendiente. [GFX-003](informes/GFX-003_inscripciones.json) mantiene sin cambiar dos texturas con inscripciones ambiguas. Matriz QA ampliada a 66 casos; ninguno ejecutado para v0.19.0. [RELEVO-007](prompts/SIGUIENTE_RELEVO.md) preserva el mandato recursivo.
