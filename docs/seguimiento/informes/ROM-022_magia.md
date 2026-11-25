# ROM-022 — magic.dat completo en piloto independiente

Fecha 24/11/2026 (Lima). Base PR #48 HEAD 3729e8623c1e2fcfa552a61c613613ccdf789b83. Pruebas locales reales, no PPSSPP.

A. ISO extraída del 7z aportado (únicamente ISO y archivo URL; no EDAT), SHA256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5. 23 archivos ISO, 36 miembros START. magic.dat original 36784 bytes, SHA256 9018e9c5ea277ad1acd5f9a2a9d10120c3d5864a1ee45d8fe789166b8a138fe3. 538/538 originales CP932/NFKC cotejados (281 reservas 23, 255 reservas 57, dos excepciones).
538 revisiones vigentes corpus14, blob b83dcc34fc90c5675edd1b0f6f8ea786afccd4c8, cotejadas contra el CSV local tras transferir 335 diferencias; FNV32 1180089236, SHA256 del flujo UTF8 grupo_id/tab/texto/LF 690949979cb98cd30be3e8eef4d4de514c476ef03298f82532e43f32e1a769e4.

B. Piloto privado independiente: 522 sustituciones completas, 13 compactas, 3 coincidencias; 538/538 campos verificables y con glifos asignados. 220 prefijos originales preservados byte a byte (8740:76, 8741:27, 8742:117). 15.748 bytes fuera de reservas de magic.dat intactos. 23133 reserva exacta 13 bytes, byte 09 siguiente intacto; 23302 reserva 25 bytes empieza en offset relativo 16 y el prefijo 8741 siguiente se conserva.
16 gaiji F040–F04F, GID 2417–2432, 12 alias; subconjunto de fuente implementado localmente de manera independiente, no se ejecutó motor integral del repositorio.
- magic.dat destino SHA256 a9f2bedbaf267c9072739138caa377d651f195e6c23e46ee524a99891feb6c88.
- DAT SHA256 ea6153cd858b67b125a988137d9dba1bb1ea6d2cde603555b62ffd26c5cdfbac; 32/36 miembros iguales; solo magic.dat, fontB.fnt, fontB.ftd, FontB0001.txp cambiados.
- LZS SHA256 4ff14517a53b794ecef0e0bce541a782a646d02735c150de85426f45a3ec9be4, 5040298 bytes, 891149 referencias no solapadas, descompresión exacta.
- ISO piloto SHA256 4e4df74f36c0d5980c9bf5f76d0987b48344706d60592d985e2f437fe39783dc. LBA START 182624 fijo, tamaño LE/BE actualizado, 22 otros archivos ISO y 853760611 bytes fuera de intervalos permitidos iguales.

Motor: 14 anclas (13 compactas, una reserva sin reducción), vinculadas a SHA exacto y revisión con marcador original restaurado, controles de capacidad y bytes siguientes. Tests nuevos; CI pendiente de consulta. Variantes requieren cotejo editorial/visual, no se cambia corpus. No publicar ISO ni archivos extraídos.
Avance agregado (pilotos distintos, no candidata única): 1831/1832 campos fijos ISO; no sumar al numerador histórico. Sigue pendiente 23831/14299 nominal, unión de tablas y diálogos/scripts/gráficos, cuatro EDAT ausentes y PPSSPP. DNS bloquea git clone local.
