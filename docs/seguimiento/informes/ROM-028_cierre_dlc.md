# ROM-028 — Cierre técnico del inventario DLC: 802 unidades nuevas
Fecha: 25/11/2026 (Lima). Base ROM-027 16a02cc59efab713a36cc7eeeec04afd133bf6cc. Los dos workflows de base consultados terminaron success (QA corpus, QA inventarios). Sin modificar main, corpus ni originales.

## Cobertura
- ROM-027: 2733/3537 unidades verificadas en su piloto.
- ROM-028: 392 campos fijos, 392 unidades TALK, 18 scripts = 802 IDs únicos nuevos. Los cuatro EDAT originales se reextrajeron y coincidieron con sus SHA ROM-024. Se reconstruyó el piloto independiente dos veces y se releyeron los EDAT.
- 3535/3537 = 99,94345 % de cobertura agregada entre pilotos; 100 % de unidades técnicamente clasificadas. NO es una candidata acumulada ejecutada ni 100 % de sustituciones. No sumar a la cobertura integral histórica 21805/26258.

| DLC | Previas | Nuevas | Traducibles resueltas | Inventario |
|---|---:|---:|---:|---:|
| 00 | 2467 | 795 | 3262 | 3264 |
| 01 | 90 | 0 | 90 | 90 |
| 02 | 96 | 3 | 99 | 99 |
| 03 | 80 | 4 | 84 | 84 |
| Total | 2733 | 802 | 3535 | 3537 |

Dos exclusiones motivadas: 1630 apunta a metadatos de ritem.dat (registro 7552, campos auténticos 7556 y 7569, unidades 1631/1632 ya inventariadas); no escribir. 1744 corresponde al rótulo de carga cuya conservación exige la política anterior del motor. No se cambia el denominador maestro. Las 392 adaptaciones fijas son propuestas técnicas, no aprobación editorial nueva. Incluyen tres reservas name.dat llenas de 12 bytes y corrección del ancla de habilidad 1804: conservar byte de metadatos 0x28 en 3689; escribir a partir de 3690.

## Evidencia A/B
- 227 grupos TALK vigentes recuperados de corpus02, corpus03 y central, todos revisado. Huellas FNV32 por lotes 3777133799, 932442840, 529374060. 392 unidades / 279 intervalos nuevos. 621 intervalos antiguos / 1276 unidades reproducidos como límites de origen y comprobados disjuntos. Variable A1 preservada con el par 4131, opciones de una línea, páginas de hasta tres líneas, preservación de 2370 registros/252 opciones y controles no textuales. Tres líneas físicamente omitidas (grupos 1853,1944,1965) adaptadas sin contar IDs adicionales. Cambios de página requieren prueba visual.
- 18 scripts 0x32 conservadores, 2152 índices, sin punteros interiores, reversión idéntica. SHA script destino f62a2dac90d22e5a452d06af02743d8eb54ae3bd4fe3e61231ab960d9e285d32.
- 392 cambios de campos reales, 78 prefijos circundados preservados, reservas y bytes exteriores verificados. Revisión visual y cotejo editorial de variantes compactas pendientes.
- Cuatro EDAT leídos y 2.746.540 referencias LZS sin solapamiento; 124/144 miembros originales intactos, DLC01 íntegramente original en este nuevo piloto independiente porque no tiene IDs nuevos. SHA de cada EDAT/DAT/TALK y lista de nuevos IDs en el JSON adjunto.
- SHA flujo de IDs nuevos ordenados LF e595298e58fddd56967b88dc9067e2c2d46bd627d07a51cd3888a700140a4a1b.
- No se conservan los pilotos privados ROM027 en el entorno local de esta ejecución. DNS impide descargar el checkout completo. El paquete de código local entregado al usuario incluye reconstructor probado, TSV, verificador y unir.py, que reconstruye las tablas y TALK previos desde el checkout vigente, exige sus hashes y combina los intervalos disjuntos. Se ensayó merge_talk con 621 intervalos antiguos como identidad y los 279 nuevos reales; reprodujo los cuatro TALK nuevos. La ruta acumulada completa NO se ha ejecutado. El ZIP de fuentes se entrega en el chat, no está publicado por este commit. SHA ZIP 713785ce699cc8acb8760484b6f0ddbd5bdaac2a838791248eeb06620db9bc12. Sin ISO/EDAT/DAT/LZS, fuentes comerciales ni recursos extraídos publicados.

## Cierre pendiente
Construir la candidata acumulada única con el checkout íntegro y los cuatro originales. Auditar las 3535 unidades traducibles y las 2 exclusiones, todas las apariciones físicas reutilizadas, y ejecutar PPSSPP real. El 100 % de clasificación no certifica el 100 % del romhacking integral.
