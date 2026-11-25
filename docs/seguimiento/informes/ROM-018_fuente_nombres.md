# ROM-018 — Fuente española y piloto nominal acumulado

Base PR #44, HEAD 24cca72842b0878d96c7ccee7ab61d20f0059cd4. 24/11/2026.

## Resultados reales
ISO original autenticada SHA256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5. Se contrastaron las 290 anclas nominales del manifiesto actual (blob 9563007adf8bd030b7ec04714e687525b7f81e0d) con las del ZIP local (huella rápida FNV32 1264290692 sobre unit_id,grupo_id,recurso,offset,original y cotejo CP932 de las 290 filas contra la ISO). Revisión vigente corpus02 blob e2c8159472689c48db2700f4bc5de1101767e664.

Piloto privado acumulado ROM-016/017/018:
- 255 sustituciones en el manifiesto (227 textos completos, 28 compactos), 34 coincidencias originales conservadas, un pendiente 23831/14299.
- 10 sustituciones y siete símbolos fuera del manifiesto (ROM-016).
- 16 gaiji españoles F040–F04F, GID 2417–2432; 12 alias. Reproducción local independiente del subconjunto inicial del algoritmo fuentes_es.py, no ejecución del motor completo.
- 32 miembros DAT ajenos intactos; solo modificados name.dat, fontB.fnt, fontB.ftd y FontB0001.txp. 22 archivos ISO ajenos idénticos y 853898677 bytes exteriores idénticos.
- ISO piloto SHA256 697a35f2df05528516bc15502c26da338fc08497d1b75bb3bea86e76cfd8d2de; name.dat 6317f80218329c32296ba05f1196135b813f0e25a72886ce689276afedc07bd5; DAT 1ad16e71032a2e3eaa4f8afddca70e601360fa9ddcccff6ac1fd5abbd35f1642; LZS 5038659 bytes, SHA256 6060f58b933d4bc9e88784e4888b0d5c5774008ca87835d0710ed6cbbfe326dd; 890928 referencias no solapadas. Relectura y descompresión byte a byte correctas.

## Comparación histórica exacta por unit_id
Recuperado CSV histórico cobertura v0.19.0, blob c2c8a013e1b58063c42e70dcff5beef97322b5f8. Históricamente name.dat ISO: 205 insertadas exactas, 29 coincidencias sin cambio, 56 sin traducir. De estas 56, ahora 26 sustituciones completas, 26 compactas, tres originales coincidentes con revisión nueva y una pendiente. De las 205 antes insertadas, 201 completas, dos compactas, dos coincidencias originales con la revisión actual. No sumar 52 al numerador histórico: el piloto no contiene el resto de la candidata histórica; las compactas requieren cotejo editorial/visual y no son equivalencias exactas según el auditor actual. Total global sigue 21805/26258 histórico. Cobertura de resolución estática nominal local 289/290, NO certificación PPSSPP.

## Motor
Se incorporan 14 variantes adicionales en el JSON de ROM-017 (28 en total). Fallback admite caracteres españoles codificables con gaiji, sin caracteres de control/formato ni NUL; conserva anclas, reserva y SHA fuente. Pruebas del motor ampliadas. Las variantes son propuestas de adaptación técnica; no cambian los CSV editoriales. Mantener pendiente 14299 por semántica contextual y longitud.

Bloqueos: checkout completo no disponible localmente, cuatro EDAT ausentes, PPSSPP no ejecutado. No publicar ISO, fuente comercial ni archivos extraídos. Siguiente: construir candidata integral con rama vigente y originales auténticos, cotejar las variantes en juego y auditar cobertura completa.
