# ROM-033 — Cierre del inventario de diálogos ISO

25/11/2026 Lima. Base 3ac4d7c0a0bacde2fbc73574b6f9c59c2e5167f8; ocho workflows previos success. Original auténtica SHA-256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5. Cotejo de las 20.083 unidades TALK del manifiesto en 17 recursos originales; cero discrepancias de origen. 3.006 IDs históricamente pendientes en ocho recursos, 1.110 grupos revisados exactos. Todas las revisiones se recuperaron de corpus09–13 y central. FNV32 4240981430 cotejado independientemente en GitHub y local; SHA-256 en JSON. Se recompilaron 1.365 intervalos sobre anclas originales, sin duplicación, preservando 5.660 entradas, 81 opciones, IDs y condiciones, controles no textuales (excepto saltos de página reconstruidos), símbolos y variables. Reversión byte por byte comprobada; máximo 28 glifos por línea. 16 glifos y 12 alias nativos, ocupaciones previas protegidas. 117 adaptaciones de segmentación y menús; continuaciones no inventariadas solo cuando ancladas dentro de grupo; excepciones ASCII de 15156 y 15520 ligadas a bytes exactos. No contar cadenas físicas adicionales como IDs.

## Resultado

| Recurso | Nuevas | Pendientes |
|---|---:|---:|
| talk10_jp.dat | 88 | 0 |
| talk11_jp.dat | 506 | 0 |
| talk12_jp.dat | 203 | 0 |
| talk15_jp.dat | 339 | 0 |
| talk16_jp.dat | 361 | 0 |
| talk17_jp.dat | 254 | 0 |
| talk18_jp.dat | 407 | 0 |
| talk00.dat | 848 | 0 |
| Total | 3006 | 0 |

17077 históricas + 3006 nuevas disjuntas = 20083/20083 diálogos ISO catalogados (100% agregado); agregado global 26193/26257 (99,7563%), 64 pendientes = 2 EBOOT + 62 gráficos. No sustituye 21805/26258 de última auditoría integral histórica. El piloto no contiene las 17077 traducciones anteriores ni los demás pilotos.

## Pruebas físicas

Recompresión START 666600 referencias no solapadas, 32/36 miembros intactos; SCRIPTPACK 25/32 miembros intactos. Se construyó ISO piloto privada y se releyeron sus 8 recursos: todos los intervalos y hashes coinciden. START conserva LBA 182624; SCRIPTPACK crece por encima de su reserva y se anexa en LBA 419403, actualizando registros ISO9660. 21/23 archivos restantes y todos los bytes originales fuera de cuatro intervalos autorizados idénticos. Original intacto. SHA ISO piloto 383b5ce789489d0104df3dbe9931789eea5dfb8cfbaca68ffc6338d06382d86b. Reproducción independiente con el paquete de fuentes portátil: coincidencia exacta de proof.json e iso_proof.json, PASS 3006/1110/1365/5660/81. El ZIP ROM033_ISO_dialogos_100_fuentes.zip (SHA-256 d716f2d8309c81cab186503dc5434e70b3e2a948bf2afe879da95f92abf3f49e) se entrega al usuario, no está publicado en GitHub. Contiene código, revisiones, segmentación, diario y comprobadores; no ISO/DAT/LZS/EDAT ni fuentes comerciales. El nuevo auditor GitHub solo coteja contabilidad y revisiones, no prueba binarios.

## Pendiente

Unificar diarios y fuentes en una única candidata desde originales, preservar los avances históricos, resolver 2 EBOOT y 62 gráficos, releer y ejecutar PPSSPP. El nuevo SCRIPTPACK reubicado, las adaptaciones de menú, variables y paginación requieren prueba funcional. Las 24668 cadenas físicas sin ID no equivalen a 24668 textos inéditos ni se cuentan como verificadas. Sin merge automático.
