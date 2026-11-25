# ROM-023 — Último campo nominal y criterios de cierre

Base ROM-022. 24/11/2026 Lima. Original SHA256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5.

Unidad 23831, grupo 14299, offset 4636 de name.dat, SHA original 6af6d7de4b001fc7bafce586f88ba0c971b9d0c39388e4ff6b10b227b1e8b27c. Registro original de 16 bytes, clase 2 (prefijo), 12 bytes de reserva incluida terminación. Original Look good; revisión aprobada Se mire como se mire, basada en japonés どう見ても (cotejo editorial corpus02). Se propone adaptación técnica «Sin duda » con un espacio final intencional, 9 bytes más NUL; no se modifica corpus. El modelo histórico CENT-018 confirma concatenación sin separador y reintento para más de 16 bytes: Prier/Croix 14, Culotte 16, Alouette 17 y Poitreene 18 (estas dos se rechazan). No prueba funcional en juego. La variante debe aprobarse editorial/visualmente.

Piloto local sobre ROM-022 con únicamente magia y un slot nominal (539 unidades; no contiene las demás 1293 resoluciones históricas). Bytes ajenos al campo nominal preservados y código original de clase 2 intacto. Glifos de la cadena asignados.
- name.dat SHA256 destino 2f7a52431fe97504e24df0d1ebe5dc80e3dc6ad3cbd332054953c33b8bb82772
- DAT SHA256 2946aa879a1a019c8efaab6ac2c7f66cc41bf24ceffd0f6823bb004325d28eaf
- LZS SHA256 1034dfaceab5af3ec3e6d8d811ca267d659041bea29794360fe5dfc742a9bde5; 5040296 bytes, 891149 referencias no solapadas, descompresión exacta.
- ISO SHA256 84935d74b999592fb9f5deae82f28b522823ea875becf0968c2f286d578fae90; 22/22 otros archivos ISO y 853760611 bytes fuera de intervalos permitidos idénticos. 31/36 miembros START intactos.

Verificación agregada de pilotos de ocho tablas: 1832/1832 con propuesta físicamente viable. No se afirma candidata única ni equivalencia exacta de compactas. No se incrementa el contador integral histórico 21805/26258.

## Ruta al 100% integral
1. Unificar todas las tablas mediante scripts/verificar_tablas_iso.py con ISO y checkout completo autenticados; validar diario, zonas exteriores, prefijos y recompresión. El verificador de tabla se ejecutó localmente con 538 campos reales de magia y rechazó una mutación del byte 09 fuera de reserva. No se ejecutó la CLI completa: DNS local impide git clone.
2. Ejecutar integracion_total.py con ISO, corpus vigentes y fuente de capítulos; auditar por unidad con scripts/auditar_entrega.py. Priorizar los 3527 TALK pendientes del informe histórico, 419 campos sin traducir, 335 campos modificados sin cotejo, 1 script y 62 unidades gráficas. No asumir que son los pendientes de la nueva candidata hasta reconstruirla.
3. Conseguir cuatro EDAT legítimos DL_JP_00..03.EDAT (3537 unidades DLC en manifiesto). Verificar origen, compresión, scripts, fuentes y no solapamiento. El archivo 7z local solo incluye ISO y URL.
4. Ejecutar PPSSPP real, validar cuadros, gaiji, menú, combate, nombres y gráficos. Cerrar únicamente con evidencia C, no por CI o porcentaje agregado.
5. Mantener sin publicar ISO, DAT, EDAT, fuentes comerciales ni recursos extraídos.
