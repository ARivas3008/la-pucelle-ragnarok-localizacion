# QA visual v0.17.2: nueve capturas de PPSSPP

**15-11-2026.** Se analizaron nueve capturas aportadas por el usuario de PPSSPP v1.15.4. La corrupción de menús y diálogos **NO está resuelta**. Este documento conserva los hallazgos sin añadir material comercial al repositorio.

| Captura | Síntoma | Recurso / estado |
|---|---|---|
| 1 | Menú del título con bordes sustituidos por barras | UI/EBOOT/PPSSPP por aislar |
| 2 | Caja de diálogo con fondo incompleto y área derecha transparente | Crítico, prueba original/parche pendiente |
| 3 | «Remember, two days in a row...» aún en inglés | `talk01_jp.dat`, grupo **5056**, unidades 6277–6281 |
| 4 | «And remember, we are servants...» aún en inglés | `talk01_jp.dat`, grupo **5064**, unidades 6293–6295 |
| 5 | Subtítulo «Aunque llevamos más tiempo...» sí está en español | `script01.dat`, grupo 3311; no valida las demás escenas |
| 6 | «Oh, Holy Goddess Poitreene...» aún en inglés | `talk01_jp.dat`, grupo **5072**, unidades 6306–6308 |
| 7 | «Skip the scene?» en inglés y barras en el cuadro | Recurso preciso sin identificar: requiere traza |
| 8 | «Button» en inglés y panel incompleto | EBOOT, grupo 3190, unidad 3705, traducción «Botón» no es ASCII |
| 9 | Menú con bloques morados y franjas negras | Crítico: origen GPU, textura, fontB o EBOOT no establecido |

## Por qué estos tres diálogos se quedaban en inglés

Se comprobaron los offsets y separadores sobre los scripts originales del propietario, con codificación española CP932 de ancho completo (2 bytes por carácter).

| Grupo | Capacidades por unidad, en bytes | Bloqueo | Ajuste ensayado |
|---|---|---|---|
| 5056 | 46/46/32/40/8 | El texto original revisado mide 164 B, pero el último cuadro de 8 B no admite «sola.» (10 B) | «Recuerda: llevas dos días dejando escapar a un fantasma por irte sola» |
| 5064 | 40/30/30 | Traducción revisada de 110 B, frente a 100 B disponibles | «Recuerda: somos siervos de la Santa Diosa...» (88 B) |
| 5072 | 32/46/46 | Traducción revisada de 136 B, frente a 124 B disponibles | «Oh, santa diosa Poitreene... ¡Perdón! Ya he terminado.» (108 B) |

`repartir` y los planificadores `planificar_intervenciones` / `planificar_paginados` aceptaron los **11 segmentos** sin mover opcodes, respetando el delimitador `00 02 01` del grupo 5056. Son candidatos de inserción estructural, **no** escenas verificadas en PPSSPP. Se preservan los textos editoriales originales en `ajustes_contextuales.csv`; no se sobrescribe `corpus/05/revision.csv`.

## Procedimiento de diagnóstico A/B

La v0.17.2 añade un modo marcado por defecto: **«Prueba gráfica: conservar EBOOT y atlas de interfaz originales»**. Este modo deja sin modificar el ejecutable del juego y las texturas optativas de UI. Algunas etiquetas pueden quedar en inglés; es una **prueba de aislamiento**, no la resolución de la localización. Las fuentes fontB continúan parcheándose, por lo que aún podrían intervenir en el problema.

1. Cargar la **ISO original** en PPSSPP, con los mismos ajustes. Desactivar temporalmente «Skip buffer effects», «Lazy texture caching», sustitución de texturas, escalado y demás aceleraciones. Comparar título, ventana de diálogo y estado.
2. Cargar la ISO **v0.17.2 diagnóstico** y reproducir los mismos puntos. Si la original también falla, comprobar ajustes y backend gráfico; no atribuir el problema únicamente al parche.
3. Si únicamente falla la parcheada, ejecutar `qa_integridad_graficos.py` para confirmar qué texturas se han alterado realmente y si EBOOT está intacto.
4. Si la versión de diagnóstico se ve bien pero la anterior no, investigar EBOOT/atlas. Si ambas fallan y el original no, investigar fontB, offsets, script y emulador mediante trazas y pruebas adicionales.
5. No declarar corregidos los parpadeos hasta disponer de vídeo A/B. Las capturas estáticas no permiten determinar su causa.

### Auditor forense de solo lectura

Ejemplo en PowerShell con Python instalado:

```powershell
python parcheador/investigacion/v0.17/qa_integridad_graficos.py `
  --iso-original "C:\Juegos\La_Pucelle_Ragnarok.iso" `
  --iso-parcheada "C:\LaPucelleES\salida_v0172\JUEGO_PARA_PPSSPP_V0172\La_Pucelle_Ragnarok_ES_V0172_PRUEBA_PPSSPP.iso" `
  --dlc-original "C:\Juegos\ULJS00244" `
  --dlc-parcheado "C:\LaPucelleES\salida_v0172\JUEGO_PARA_PPSSPP_V0172\ULJS00244" `
  --conservar-eboot --informe "C:\LaPucelleES\auditoria_visual.json"
```

El auditor compara bytes y hashes de texturas UI no autorizadas, CLUT/cabeceras y glifos originales de fontB, EBOOT y los cuatro DLC. **No prueba la representación correcta** en el juego.

Referencias PPSSPP: https://www.ppsspp.org/docs/troubleshooting/graphics-dont-look-right/ y https://www.ppsspp.org/docs/settings/graphics/.

**Criterio de aceptación:** vídeo/capturas de original y parche con mismo backend, cero corrupción nueva, diálogo visible, menú sin inglés residual y pruebas separadas de juego/DLC. Hasta entonces, v0.17.2 es únicamente diagnóstico experimental.
