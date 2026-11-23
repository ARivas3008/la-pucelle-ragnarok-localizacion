# Integración en curso — 16 de noviembre de 2026

No es una entrega final. La prioridad es completar el corpus, menús y HUD,
corregir diálogos invisibles/superpuestos y localizar textos fuera del corpus.
El usuario autoriza cambios de inserción y pruebas en PPSSPP.

## Hallazgos contrastados con el EBOOT original

1. **El lector anterior de scripts calculaba mal la cabecera.** El formato real
   tiene `N`, `N offsets`, `N identificadores`, y luego instrucciones. El inicio
   del cuerpo es `4 + 8*N`, no `4 + 4*N`. Se verificó en las instrucciones
   `0x08844e88..0x08844ec0`. Con la base correcta, los 105 falsos índices interiores
   desaparecen y los 503 textos de script no excluidos se pueden recompilar.
   Los identificadores de la segunda tabla deben quedar idénticos.
2. **Los diálogos talk consumen pares de bytes**, incluso cuando una captura
   parece mostrar ASCII correctamente. `0x41` activa sustitución de nombres.
   El código está en `0x08844700..0x08844864`. NO PUBLICAR las pruebas compactas.
   La alternativa actual usa CP932 ancho/gaiji, sin relleno, máximo 28 caracteres
   por línea y tres líneas por página con opcode `02`.
3. **El búfer de cada talk de capítulo estaba fijado en 155000 bytes.** Se
   identificaron nueve sitios de asignación/limpieza/carga. La prueba amplía
   solo `LUI v0,2` a `LUI v0,4`: capacidad 286072. Los nueve cambios exactos
   constan en `informes/prueba_dialogos.json`; no sustituir constantes a ciegas.
4. La tabla talk usa `8 + 32*N`; solo su primera columna es un offset.
   Los saltos `0C` usan identificadores de 24 bits. Los campos de condiciones
   se leen aparte (`0x08843e80..0x08844018`) y se conservan.
5. Las opciones `14` requieren escanear N marcadores `01` y el final `FD`.
   Interpretarlas como instrucciones lineales omitía opciones. El nuevo parser
   reconoce los 21 recursos, todas las unidades talk del manifiesto y cero
   opcodes desconocidos. Evidencia: `informes/interprete_talk.json`.
6. El manifiesto omite numerosas **apariciones repetidas** de diálogos en otros
   capítulos y DLC. No son necesariamente traducciones nuevas. El compilador
   coteja secuencias completas, prioriza contexto/ID y rechaza variantes ambiguas.

## Trabajo implementado

- Fuente aislada en `fuente`; originales y versiones anteriores conservados.
- Compresión LZS sin copias solapadas y alineación DAT conservadas desde v0.18.3.
- Recuperado `atlas_deltas.json.z` del EXE v0.17.4: no se ejecutó ese parcheador.
- 254 etiquetas EBOOT del corpus preparadas; cinco términos idénticos no
  necesitan traducción. Tildes comprobadas visualmente en Opciones.
- 136 etiquetas adicionales fuera del corpus preparadas con hash/offset exactos.
- Menú Jugar/Seguir/Opciones y HUD recuperado observados en PPSSPP.
- Nueva reconstrucción talk: 17030 bloques físicos aplicados, 3620 pendientes;
  **no equivale a 100 % del corpus**. La selección usada es solo `revisado`.
- ISO `prueba_dialogos/La_Pucelle_Ragnarok_ES_PRELIMINAR.iso` generada para ensayo.
  Usa scripts con cabecera corregida, 21 talk compilados, menús y HUD. START y
  SCRIPTPACK se anexan a la ISO actualizando sus registros y el tamaño del volumen.
  El mayor talk mide 204751 bytes. SHA en el informe de construcción.

## Pruebas y pendientes

- La prueba de scripts corregidos pasa el punto del prólogo donde antes
  aparecían nieve y personajes incorrectos (`scriptcorregido_dialogo_40.png`).
  Aún contenía los talk compactos de laboratorio: no es una entrega utilizable.
- La prueba `dialogos` necesita comprobarse desde New Game, opciones, escenas,
  combate y guardado/carga. No hay todavía validación completa de capítulos/DLC.
- Resolver grupos no catalogados (509 centrales, investigación, continuaciones),
  variantes ambiguas, glifo de punto y coma y textos físicos sin correspondencia.
- Incorporar todos los cambios al flujo reproducible del EXE, corregir fixtures
  antiguas que modelaban mal scripts, auditar y construir una nueva versión.
- Faltan títulos rasterizados de capítulos/mapa y revisión de campos fijos largos.
- No afirmar que las capturas aisladas prueban estabilidad ni traducción total.
