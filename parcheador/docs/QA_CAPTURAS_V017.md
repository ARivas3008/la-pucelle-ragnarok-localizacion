# V0.17.0 QA — Informe de capturas entregadas el 15 de noviembre de 2026

**Origen de la evidencia:** diez capturas facilitadas por el usuario de PPSSPP. Son imágenes **estáticas**: documentan textos y superposiciones, pero **no permiten medir parpadeo temporal**. No se han incorporado los píxeles comerciales al repositorio.

## Matriz de incidencias observadas

| Captura | Evidencia | Recurso y grupo | Estado del arreglo |
|---:|---|---|---|
| 1 | Menú «Jugar / Seguir / Opciones» ya en español; logo con katakana original | Logo/título gráfico, archivo por confirmar | Se conserva el logotipo original hasta localizar textura y validar paleta; **pendiente gráfico** |
| 2 | «¡Ya estoy harta! / ¡No aguanto más!» visible | `talk01_jp.dat`, 5048–5049 | Se preserva la modificación vigente, 2 líneas en una intervención |
| 3 | «Why do I have to waste my time fighting zombies?!» | `talk01_jp.dat`, 5050, unidades 6264–6266 | **Arreglo estructural v0.17** con ajuste breve registrado, 3/3 cajas |
| 4 | «They are such wimps!» | `talk01_jp.dat`, 5051, unidad 6267 | **Arreglo estructural v0.17** «¡Qué debiluchos!»; 32/40 bytes de texto |
| 5 | «We are new at this...» en 3 líneas | `talk01_jp.dat`, 5055, unidades 6273–6276 | **Arreglo estructural v0.17** 4/4 segmentos; reconoce la paginación `NUL 02 01` |
| 6 | «Besides, I am the one ... laundry!!» | `talk01_jp.dat`, 5057, unidades 6282–6284 | **Arreglo estructural v0.17** 3/3 segmentos, adaptación en el contexto |
| 7 | «Me llamo Culotte / I am a novice demon hunter» | `script01.dat` en SCRIPTPACK, 3301–3302 | 3301 ya cabía; 3302 sobrepasa campo fijo (34/28 bytes). La GUI v0.17 **activa scripts conservadores por defecto** y entrega ISO de segunda fase claramente separada. **Pendiente prueba PPSSPP** |
| 8 | Tarjeta «Chapter 1 / On The Job Training» en inglés | `BGPACK.DAT/at01.txp`, grupo 3282 | Se ha decodificado `at01.txp`: **480×170, 8 bits indexados, paleta 256 RGBA, swizzle PSP de 16×8**, 82 640 bytes. No se activa sustitución raster no validada. **Pendiente asset** |
| 9 | «Cuidado, Prier ,)»/signos visualmente extraños | `talk01_jp.dat`, grupo 5084, unidad 6326 | Fuente `(Watch it、 Prier。)`; revisión `(Cuidado, Prier.)`. Original 36 B, español a ancho completo 34 B, se conserva NUL y padding. **Pendiente reproducir deformación en PPSSPP** |
| 10 | Etiquetas «Button»/otro texto y zonas superpuestas | Posible etiqueta EBOOT/HUD; `Button` en manifiesto EBOOT, grupo 3190 | No se modifica código/atlas sin identificar render y coordenadas; **pendiente investigación UI** |

## Análisis de causas

**Rechazos de texto correcto:** El motor anterior trataba `0x00 0x02 0x01` como otra intervención, aun cuando el grupo editorial seguía en la siguiente caja. El nuevo `planificar_paginados` únicamente une unidades del mismo grupo, en el mismo recurso, con saltos exactos `NUL 01` / `NUL 02 01`. Conserva bytes de opcodes, punteros y campo físico; escribe o rechaza el grupo entero.

**Traducciones que casi cabían:** `safe_encoding` usa CP932 y, para texto original de ancho completo, el español se recodifica al mismo ancho, por lo que los 42 B de `¡Son unos debiluchos!` exceden el campo original de 40 B. Los cuatro ajustes editoriales locales mantienen el significado y se registran con `grupo_id`, original anterior, español reducido y motivo; **no sobrescriben los corpus oficiales**.

**Scripts de eventos no integrados:** La primera fase v0.13 solo cambia cadenas que caben sin mover índices. La segunda v0.14 permite reubicar `script01.dat` y otros archivos; en v0.16 estaba desactivada inicialmente y generaba una ISO en una subcarpeta poco visible. En v0.17 queda activada por defecto, y la ISO final, cuando exista, se coloca en `JUEGO_PARA_PPSSPP_V017/La_Pucelle_Ragnarok_ES_V017_PRUEBA_PPSSPP.iso`; los DLC correspondientes en `JUEGO_PARA_PPSSPP_V017/ULJS00244/`.

**Parpadeo:** No es posible inferir su causa con capturas. Debe registrarse un vídeo de la misma secuencia en original y parche, con backend PPSSPP, versión, tasa de cuadros y shaders, y comprobar A/B: solo fuentes → fuente+talk → +scripts → +atlas UI. **No se afirma que el parpadeo haya sido resuelto** sin esta prueba.

## Pruebas reproducidas

Con la ISO original del usuario, la tabla de inserción y una copia aislada de los grupos pertinentes marcados revisados, se ejecutó `construir_parche.py --solo-auditoria --dialogos-atomicos --segmentar-conservador`.

Resultados focales de los grupos del tutorial:
- 5050: **6264, 6265, 6266** pasan de bloqueados a `APLICADO_BLOQUE_DIALOGO`.
- 5051: **6267** pasa de «excede 40 B» a `APLICADO`.
- 5055: **6273, 6274, 6275, 6276** pasan a `APLICADO_PAGINA_ESTRUCTURAL` sin modificar separadores.
- 5057: **6282, 6283, 6284** pasan de bloqueados a `APLICADO_BLOQUE_DIALOGO`.
- 3302: permanece bloqueada en la primera fase de **campo fijo**; su ensayo corresponde a la etapa de scripts reubicables.

**Límite:** estas son pruebas de tamaños y bytecode. No son capturas de una ejecución nueva del parche ni demuestran la ausencia de fallos en otros capítulos o DLC.

## Puerta para declarar resuelto
Comparar original y resultado de v0.17 en PPSSPP usando las **salidas finales**, y comprobar: cada línea visible y sin inglés residual, acentos y paréntesis sin errores, avance/pausa sin saltos, retratos intactos, no aparición de texturas corruptas, cero parpadeo nuevo en vídeo, guardar/cargar, los cuatro DLC, y tarjetas de capítulo traducidas cuando haya parche gráfico. Si falla una escena, conservar el original y registrar su `unit_id`.
