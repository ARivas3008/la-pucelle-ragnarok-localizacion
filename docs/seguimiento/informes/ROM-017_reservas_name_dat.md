# ROM-017 — Reservas nominales, piloto real (24/11/2026)

Base: e63f87a0a5b20f0e236564fb637b845e44be2252, PR #43. No modifica main.
Se contrastaron las 290 unidades ISO_START/name.dat del manifiesto adjunto (SHA256 db93378b8d6d1768244aa4b6c5db99ac81bdeaf5becb1e9f57e650cada235414) con los 290 grupos revisados del corpus/02/revision.csv vigente (blob e2c8159472689c48db2700f4bc5de1101767e664), y con los bytes CP932 de la ISO auténtica 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5.

## Evidencia local
- 179 sustituciones directas y 14 variantes compactas de reserva (193 sustituciones físicas); 34 coincidencias originales conservadas; 63 pendientes: 56 requieren fuente extendida o cotejo de símbolos, 6 exceden 11 bytes, 1 glifo ausente en fuente original. No se presupone que esas 193 sean inéditas frente a v0.19.
- Piloto aislado, no acumulado con ROM-016: ISO SHA256 7266324d7c352fa3d9bcd14a11d987f55f76cdb53ae1144cf175ca39a8c42627.
- name.dat original SHA256 6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c; resultado 4e3b246d734194c71de7369215b8dd8caf42cd9020ecd70cc5c773b48b3e0706.
- DAT nuevo SHA256 4064a8f36ed66e3edc80accab69f4e4babddf1381f4d10b1e3bf92ba2bbd279a; LZS nuevo 5037602 bytes, SHA256 629c9cf3d1bcf19339db2acc96e777f3abd2ba47ac64412961b864776a3dccd7, 890729 referencias no solapadas. Decodificación idéntica al DAT construido.
- ISO releída: 22 archivos ajenos idénticos, 35 miembros DAT ajenos idénticos, cabeceras/clases de los slots intactas, LBA intacto, 853899734 bytes exteriores a regiones autorizadas idénticos.

## Motor
`campos_revisados.py` usa variantes de `nombres_compactos_rom017.json` únicamente cuando el texto aprobado desborda el campo, el recurso es name.dat de ISO, la reserva es 12 bytes, todos los identificadores y el texto aprobado coinciden y el SHA fuente es el autenticado. Reutiliza la comprobación de glifos. Registra texto completo y adaptación compacta. Errores de codificación se conservan pendientes. Las 14 variantes son decisiones de adaptación técnica, requieren cotejo editorial y de concatenación en PPSSPP; no modifican las revisiones originales. Las pruebas sintéticas verifican rechazo de anclas obsoletas, fuente incorrecta y capacidad. No se ha construido el motor completo en el entorno local, cuyo manifiesto adjunto es una versión anterior; no hay EDAT ni PPSSPP. El piloto usa la fuente original, no la fuente extendida. El numerador histórico 21805/26258 (83,04%) se conserva hasta nueva auditoría integral. No publicar ISO ni recursos comerciales.
