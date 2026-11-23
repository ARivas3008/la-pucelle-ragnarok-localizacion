# La Pucelle Ragnarok ES — v0.18.3

Esta versión corrige los fallos reproducidos de compresión y de ejecución del prólogo. **La traducción continúa incompleta.** Sustituye para pruebas a las versiones 0.18.0–0.18.2, que deben descartarse como base jugable.

## Abrir el juego ya generado

Desde la raíz del dossier, la ISO está en:

`10_Trabajo_v0181\salida_v0183\JUEGO_PARA_PPSSPP_V0183\La_Pucelle_Ragnarok_ES_V0183_PRUEBA_PPSSPP.iso`

Los cuatro DLC están en la subcarpeta `ULJS00244` de esa misma salida. No se han copiado sobre la instalación ni sobre las partidas del usuario. Para repetir la prueba de regresión, iniciar una partida nueva desde esa ISO.

## Usar el parcheador

Abrir `LaPucelle_Parcheador_ES_GUI_v0.18.3-fijo-qa.exe`, seleccionar la ISO original v1.1.2, la carpeta de los cuatro EDAT originales y una carpeta de salida. El ejecutable incluye las revisiones y las herramientas de compresión; utiliza Python 3 instalado en Windows, ya disponible en este equipo.

La configuración usada para generar la ISO comprobada está en `../10_Trabajo_v0181/config_v0183.json`: scripts de longitud fija, segmentación, reducciones verificadas y conservación de EBOOT. La opción de reducciones es opcional en la interfaz; desactivarla conserva más textos originales. La reubicación de scripts ya no está disponible en el ejecutable.

## Qué se corrigió y comprobó

- El compresor deja de generar copias LZS solapadas. Una prueba sin traducciones reprodujo el fondo transparente con el compresor anterior y recuperó el fondo correcto con el nuevo.
- Los contenedores mantienen la alineación de los miembros. La auditoría ahora detecta desplazamientos incompatibles aunque los píxeles sean idénticos.
- Los scripts conservan tamaño, índices, longitudes de instrucciones, terminadores y posiciones del código. Los textos que no caben se registran y se conservan en su idioma original.
- PPSSPP 1.15.4 / Direct3D11: menú, marcos, fondos, retratos y secuencia inicial comprobados. Se superó el punto donde aparecían nieve y personajes duplicados.
- Los 21 scripts finales se releyeron: fuera de los 234 textos declarados insertados, todos sus bytes coinciden con el original. La ISO mantiene tamaño y LBAs; EBOOT permanece intacto. La ISO y los cuatro DLC pasan la auditoría de compresión y gráficos.
- Pruebas: 69 correctas y 5 omitidas por falta de sus fixtures específicos, en 74 pruebas Python; 4 pruebas Go correctas. Autocomprobación del `.exe` y generación completa: código 0. Sintaxis de la interfaz PowerShell validada.

## Pendiente

Se insertan 7 901 de las 26 258 unidades técnicas inventariadas; esto **no equivale** a un porcentaje de diálogos o de traducción editorial. Permanecen frases y menús en inglés. Hay textos que necesitan versiones más breves, segmentación comprobada o investigación de referencias. Los subtítulos de eventos pueden mostrar idiomas mezclados cuando solo algunos campos son insertables.

No se certifican capítulos posteriores, combates completos, guardado/carga, finales ni ejecución de DLC. Los archivos originales y los 472 archivos del dossier se comprobaron intactos.

Informes y evidencia:

- `VALIDACION_BINARIA.json`: hashes de la ISO y los cuatro DLC, invariantes y estados.
- `../10_Trabajo_v0181/informes/estado_final_v0183.csv`: estado final de cada unidad.
- `../10_Trabajo_v0181/informes/pendientes_intro_v0183.csv`: pendientes del comienzo.
- `../10_Trabajo_v0181/informes/RESULTADOS_AISLAMIENTO.md`: variantes, causas y límites de las conclusiones.
- `../10_Trabajo_v0181/diagnostico/v0183_*.png`: capturas de ejecución.
- `../10_Trabajo_v0181/fuente/parcheador/`: código fuente utilizado.

SHA256 del ejecutable: `da3509966d68d57cce316edf14dcde2bf9cc47249ab935d52f9645275eeb79b6`.
