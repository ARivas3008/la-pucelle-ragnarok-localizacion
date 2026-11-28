# RC041 REV6 BETA01 — inicio de certificación

Base exacta RC041 REV6. Se reconstruyeron las cinco salidas del motor Linux y se verificaron los flujos del EXE Windows. BETA01 cambia solo el empaquetado: conserva PARAM.PBP original si está presente y su hash es el esperado. No cambia ningún byte de la ISO ni de los cuatro EDAT. El entorno no tiene PPSSPP ni Wine y la descarga del emulador falló; no hay capturas, guardados ni pruebas en juego inventadas.

## Siguiente insumo necesario

PPSSPP 1.20.4 Linux x86_64 oficial: https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage

SHA-256: 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

Para Windows, descarga oficial: https://www.ppsspp.org/download/.

## Uso de la beta

Aplicar el EXE a la ISO inglesa v1.1.2 y seleccionar la carpeta ULJS00244 extraída del archivo DLC original (incluye PARAM.PBP). El ejecutable no instala el emulador. Copiar la carpeta ULJS00244 de la salida a PSP/GAME/ de la Memory Stick dedicada, tal como indica el Readme original. No mezclar con otra edición. Conservar copias de partidas y no usar savestates antiguos para certificar una versión nueva sin reinicio y carga normal.

El inventario de guardados está vacío porque no se obtuvo ningún archivo confirmado. La matriz tiene todos sus casos de ejecución bloqueados, y se debe ampliar con los eventos y rutas reales. No confundir las pruebas preliminares con el betatesting.

Los fuentes Go del cambio de empaquetado y el manifiesto están incluidos, sin los cinco deltas binarios ni archivos comerciales. El script audit_static.py registra la auditoría realizada; depende del entorno de laboratorio anterior (se incluye su módulo de lectura como referencia). No es un instalador ni un emulador.
