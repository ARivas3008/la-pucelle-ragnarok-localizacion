# ROM-016 — Inserción nominal adicional en ISO real

Base de desarrollo: `5fedd323ba2f695235964782159b4c75774803c0` (PR #42). Se conserva el alcance histórico 21.805/26.258, 83,04 %. Los diez nombres son externos al manifiesto; no se suman a dicho numerador.

- Original SHA-256: `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`.
- ISO piloto privada, 858937344 bytes, SHA-256: `a84757ff01ee24f1c30c83173ef63fbc2fed6aeb97cb9b8a0a0724e7af3b41f7`.
- name.dat original SHA-256 `6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c`; nuevo `e717c517ae75b12af727f33560de4b03100f70cb44d803bb6d9642242c738d64`.
- Slots verificados e insertados: 1788,2188,2380,2668,2684,3356,4060,4220,4348,4700. Siete símbolos conservados, 35 miembros DAT restantes intactos, cabeceras y clases intactas, 22 recursos ISO restantes con SHA idéntico.
- START_JP.LZS recompuesto: 5037452 bytes, SHA-256 `ea5d14da935bd71e852fa76f2734ab6ebeee3721a966493a859f9e87d79de9e7`; 890713 copias sin solapamiento. DAT reconstruido SHA-256 `28fa093f0263f76292286b59d5cb2551522a6b1735326daab203d2d526ed84b1`.
- Se conservan LBA 182624 y tamaño físico ISO. Los 853899884 bytes externos a las dos regiones autorizadas (campo de tamaño ISO dual-endian y nuevo LZS) coinciden exactamente.
- Se comprobó el sidecar editorial de CENT-019 frente a los slots de la ISO auténtica, con el manifiesto local adjunto y fuente fontB original (ASCII). La candidata piloto NO contiene las demás traducciones históricas y NO constituye una candidata integral. La integración en el motor vigente usa el manifiesto actual y falla de forma segura si hay conflicto con revisiones o deltas previos.
- Motor: `nombres_fuera_manifiesto.py`, llamado tras campos revisados, y empaquetado del CSV desde `data/control` sin duplicar el archivo en el repo. Nueve pruebas sintéticas de regresión añadidas. Consultar Actions antes de declarar CI aprobada.
- No se publica ISO ni archivos comerciales; PPSSPP y los cuatro EDAT auténticos no disponibles. Próximo paso: ejecutar build completo del HEAD y auditar su salida real, incluidos los diez nombres fuera del manifiesto, conservar los denominadores separados.
