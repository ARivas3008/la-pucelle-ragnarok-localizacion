# ROM-021 — Objetos y modificadores, piloto conjunto de seis tablas

24/11/2026, base PR #47 HEAD 4a930712db26ef047a355aa242a9054fa1ace3f8. Original autenticado SHA256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5. Maestro cotejado por normalización LF en ROM-019. Revisiones vigentes corpus01/02/14/15 consultadas en GitHub; 491 filas revisado. Huella FNV32 de grupo_id, tab, revisión, LF: kis 4293698246, ritem 1518545431, coincidentes con remoto. Se corrigió localmente la discrepancia de transferencia de 13306 (Aumenta, no Aumentan) tras cotejo de huella individual 2027026265; no se alteró corpus.

| Tabla | Total | Completo | Compacto | Coincide |
|---|---:|---:|---:|---:|
| kis.dat | 277 | 255 | 13 | 9 |
| ritem.dat | 214 | 192 | 17 | 5 |
| Total nuevo | 491 | 447 | 30 | 14 |

A: 491 anclas auténticas CP932/NFKC ya cotejadas en ROM-020; ninguna reserva atípica. B: 477 sustituciones nuevas (30 compactas), 14 coincidencias. Piloto privado acumulado de ROM-019/020/021: 1004 unidades, 933 sustituciones, 71 coincidencias, 74 compactas. Verificación byte a byte de cada campo y de los intervalos exteriores respecto al piloto anterior. 27/36 miembros intactos, 22/22 otros archivos ISO intactos, 853760611 bytes fuera de dos intervalos autorizados. Doce gaiji y 11 alias de puntuación. Algoritmo de fuente local independiente de subconjunto; no se ejecutó el motor completo.
- kis.dat SHA256 destino 0e5e0f6d7df0f23aa045c962abedd5af8fe7cd27e11d6dd09a5f1f0558ed24ef
- ritem.dat SHA256 destino 0626b75ef046cf5ff349f39386a62145b530595bfe5a196b5245dde6bf50dce0
- DAT SHA256 e8f81864fbdc61f6b91ce1b99b560fd450047a72a741041e8ab4f4b8ba11de5c
- LZS SHA256 954f39d6a877bbd6f4e6192b45e22473d0f5fcf207c86f0af7352fbf9bcbad80, 5108950 bytes, 891366 referencias sin solapamiento, reversible.
- ISO piloto SHA256 9c5137d1ef33033a31d78727c85b946ddb95affada8c9f60b6e2b2d1a4559e0b.
- LBA fijo, tamaño START LE/BE corregido.

Motor: 30 anclas de variantes nuevas, SHA exacto por recurso y capacidad, sin degradar gaiji ni perder botón cuadrado. Regresiones test_campos_compactos_rom021.py. Variantes sujetas a cotejo editorial y visual; no se cambia el maestro ni el corpus. Sin publicación de ISO ni recursos comerciales.

Pendiente: magic.dat 538 unidades (2 reservas excepcionales), piloto nominal aún separado, candidata integral de textos/diálogos/gráficos/DLC, verificación funcional PPSSPP. Cuatro EDAT no disponibles; clon directo bloqueado por DNS. No sumar 933 a 21805 histórico, falta cotejo integral actual. Cero pruebas C nuevas.
