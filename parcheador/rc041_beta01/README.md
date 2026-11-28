# RC041 REV6 BETA01 — fuente y QA

Base de betatesting ULJS00244, ISO inglesa 1.1.2. La corrección BETA01 conserva PARAM.PBP original si está presente y valida su SHA-256. Las cinco salidas ISO/EDAT coinciden con REV6.

**No es una versión certificada en ejecución.** PPSSPP 1.20.4 no disponible en el entorno de la prueba; 0/137 puntos de ejecución comprobados, 10/10 pruebas preliminares. La GUI Windows no se ejecutó.

El código Go exacto y sus manifiestos están en `gui/`; los informes y la matriz en `QA/`. Los scripts históricos son registros del laboratorio: pueden depender de rutas locales, recursos privados y versiones previas. No se incluyen ISO, EDAT, PARAM.PBP, texturas extraídas, archivos XOR ni ejecutables que los incrusten. Para reconstruir el ejecutable localmente se necesitan los cinco deltas privados verificados; sin ellos la compilación no constituye un parcheador distribuible.

SHA-256 del EXE BETA01 entregado privadamente: `add7a999269d6242ae47fbe7a6b8c34a6375f71059669c235efdb872afa7f64d`.

La rama conserva la base FontB manual y no modifica los 15 corpus ni main. Los CSV históricos documentan intervenciones físicas, no textos únicos ni certificación total de traducción.
