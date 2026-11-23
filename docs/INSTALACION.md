# Instalación — Windows x64

Descarga `LaPucelle_Parcheador_ES_GUI_v0.19.0-integracion.exe`, `SHA256SUMS.txt` y el informe de cobertura en [Releases](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/releases/tag/v0.19.0-integracion).

## Archivos compatibles

- ISO de trabajo `La_Pucelle_Ragnarok_v1.1.2.iso`, 858.937.344 bytes.
- SHA-256 de esa ISO: `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`.
- DLC opcionales: `DL_JP_00.EDAT`, `DL_JP_01.EDAT`, `DL_JP_02.EDAT`, `DL_JP_03.EDAT`, juntos en una carpeta. La selección de DLC requiere los cuatro.
- Una carpeta de salida nueva con espacio para copias y archivos temporales; se recomiendan al menos 4 GB libres.

El motor verifica firmas y bytes originales antes de aplicar las modificaciones. Una edición distinta puede ser rechazada; no renombres archivos incompatibles para forzar su aceptación.

## Aplicación

1. Ejecuta el `.exe`, selecciona ISO, DLC o ambos y elige una carpeta de salida vacía.
2. Pulsa el botón de parcheo y espera al mensaje de finalización. Los originales se leen y la entrega se escribe en otra carpeta.
3. Usa `JUEGO_PARA_PPSSPP/La_Pucelle_Ragnarok_ES.iso`. Los DLC generados están en `JUEGO_PARA_PPSSPP/ULJS00244/`; cópialos a `PSP/GAME/ULJS00244/` dentro de la Memory Stick configurada en PPSSPP.
4. Conserva `informes/` y el registro de ejecución para identificar fallos. Empieza desde New Game para comprobar gráficos y diálogos sin memoria de otra ISO.

El ejecutable incluye el motor y las revisiones. Usa Python 3.10 o posterior si está disponible; si falta, intenta descargar Python 3.11.9 portátil desde python.org en la primera ejecución. HY-MT2 no es necesario para aplicar el parche. El `.exe` no lleva firma Authenticode; su integridad se comprueba con SHA-256:

```powershell
Get-FileHash .\LaPucelle_Parcheador_ES_GUI_v0.19.0-integracion.exe -Algorithm SHA256
```

## Si algo falla

| Mensaje o síntoma | Acción |
|---|---|
| Original desconocido o bytes distintos | Comprueba la ISO y los DLC contra las firmas; usa originales compatibles. |
| La salida ya contiene una entrega | Selecciona una carpeta nueva. |
| No se puede preparar Python | Instala Python 3.10+ o permite su descarga oficial y vuelve a ejecutar. |
| Texto aún en inglés o japonés | Consulta cobertura y pendientes; esta entrega es parcial. |
| Omisión, duplicación o corrupción visual | Registra escena, personaje, versión, captura y si ocurre desde New Game. No des por resuelto un caso por figurar en un CSV. |

La validación binaria está completada; la validación visual amplia de esta versión sigue pendiente. No hay certificación de compatibilidad con una PSP física.
