# Pruebas locales de aislamiento

## Resultado de las variantes

- **Original v1.1.2:** menú opaco y primer diálogo con fondo, marco y retrato correctos.
- **v0.18.0:** rechazada por el usuario, comenzando una partida nueva. Presenta corrupción de interfaz, retratos y escenas.
- **v0.18.1:** conserva la alineación DAT a 16 bytes. Recupera marcos y diálogos iniciales, pero el fondo del menú continúa transparente. No entregar como solución.
- **Original recomprimido con el compresor anterior, sin traducciones:** reproduce el fondo transparente. Es una prueba independiente del corpus y de los scripts.
- **Original recomprimido sin referencias LZS solapadas:** recupera el fondo opaco del menú.
- **v0.18.2:** corrige la compresión y la interfaz. Rechazada como versión jugable: al avanzar el prólogo aparecen partículas tipo nieve y dos sprites de Prier. Capturas `v0182_dialogo_30.png` y `v0182_dialogo_36.png`.
- **Preliminar v0.18.2, sin modificar script*.dat:** la misma secuencia avanza con los personajes correctos, sin nieve; llega a las intervenciones posteriores. Capturas `preliminar0182_dialogo_30.png` y `preliminar0182_dialogo_36.png`.
- **v0.18.3:** el menú y el prólogo superan el punto que fallaba. La captura `v0183_dialogo_40.png` muestra a Alouette, Prier y Culotte correctos, sin nieve, en la intervención posterior al fallo. Sustituye textos de scripts conservando cada intervalo, longitud, opcode, terminador e índice. Bloquea textos que no caben y referencias interiores no verificadas. No usa la reubicación que alteró las escenas. Esto no certifica los demás capítulos.

## Fallos encontrados

1. El compresor C++ permitía longitud de copia mayor que distancia. El descompresor Python reconstruía esos tokens byte a byte, por lo que el round-trip ocultaba la incompatibilidad del juego. El START original contiene 696 038 copias y ninguna solapada; la recompresión anterior generó 74 398 solapadas. La prueba visual de identidad diferencia ambos compresores sin cambiar el contenido descomprimido.
2. La reconstrucción DAT no conservaba alineación al crecer script00.dat. En v0.18.0 el crecimiento de 38 bytes dejó 15 intervalos con al menos un extremo desalineado: script00.dat y los catorce miembros posteriores.
3. Reubicar cadenas 0x32 y el índice principal no basta para conservar la ejecución del script. La reversibilidad binaria no prueba que se hayan corregido todas las referencias del programa. Se ha aislado el fallo en esa etapa; no se afirma conocer todavía toda la semántica del formato.

## Reproducción y límites

PPSSPP 1.15.4, Direct3D11, copia portátil aislada en `laboratorio/PPSSPP`. Configuración tomada del usuario, sin modificar sus partidas ni su instalación. Capturas mediante el depurador WebSocket local; cada variante arranca de nuevo. No se transfieren savestates entre versiones.

Las capturas y scripts de diagnóstico están en `diagnostico/`, `iniciar_laboratorio.ps1`, `ws_request.ps1` y `capturar_dialogos.ps1`. Los informes estructurales de v0.18.2 siguen siendo válidos como auditorías binarias, **no** como aprobación de ejecución. Las variantes de identidad son exclusivamente diagnósticas.

Las frases en inglés que exceden capacidad o contienen referencias no verificadas siguen pendientes. No confundir estas limitaciones de integración con una traducción editorial ausente. Consultar los estados por unidad antes de modificar texto o código.
