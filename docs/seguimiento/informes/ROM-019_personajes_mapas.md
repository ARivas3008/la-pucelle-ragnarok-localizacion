# ROM-019 — Personajes, enemigos y localidades, piloto independiente

Base: PR #45, HEAD 2c46e55e41e0d23b236bf32570b93fa2f3999570. Fecha: 24/11/2026 (Lima).
ISO original facilitada, SHA256 4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5.
Revisión corpus01 blob 47e59c28dc4108108e016855dbe94a994aa055ef; 252 estados revisado; FNV32 2113225157 sobre grupo_id + tab + revisión + LF, orden numérico (coincide con lectura local).
Manifiesto ZIP local: blob Git 58adab40237467ea49827321421b2faafb9008a7 (CRLF). Tras normalizar exclusivamente los 26259 CRLF a LF, sus 11889863 bytes generan exactamente el blob Git remoto 9563007adf8bd030b7ec04714e687525b7f81e0d. Por tanto las 252 anclas del maestro vigente son idénticas; sus originales cotejaron CP932/NFKC contra bytes de ISO. El motor exige ancla y revisión exactas, además de SHA del recurso.

## Evidencia A/B local, no emulador
| Tabla | Total | Sustitución completa | Compacta | Coincide |
|---|---:|---:|---:|---:|
| char.dat | 152 | 95 | 5 | 52 |
| mapinfo.dat | 100 | 89 | 8 | 3 |
| Total | 252 | 184 | 13 | 55 |

13 textos excedían reservas de 24/28 bytes. Variantes técnicas sujetas a aprobación editorial y visual; no cambian corpus.
Unidad 23493, offset 3476: Cafeteria termina en NUL tras 9 bytes, seguido de 00 03. Se escribe exclusivamente en los 10 bytes originales; se conserva 03. No se relajan perfiles globales.

Piloto privado separado de ROM-018 (no acumulativo): reimplementación local independiente del subconjunto necesario de la fuente (9 gaiji en los GID asignados por orden upstream, 11 alias de puntuación ancha) y compresor no solapado. 31/36 miembros DAT intactos; solo char.dat, mapinfo.dat, fontB.fnt, fontB.ftd y FontB0001.txp modificados; comprobación de todos los campos y disponibilidad de glifos. Recompresión y descompresión byte a byte; 22/22 otros archivos ISO intactos y 853760611 bytes exteriores a intervalos autorizados iguales. LBA fijos; tamaños LE/BE de START actualizados.
- char.dat destino SHA256 74d72130f40f14178cbca948fce3612903b995dee3739bca8bd15c75f92fe975
- mapinfo.dat destino SHA256 d5f539ea501a8192190fad8683b0c2a1459aa3ff3cea7dd77df99a92f8f1c7b9
- DAT SHA256 5c527f3ade91ef4804963865d8b259bbf78dc96e50ee5b1e16ebee3bcf654f1a
- LZS SHA256 6ac74d340255d0ed03e23734616cff505efc3ef01afeecf95228b90eea7e7fa6; 5038757 bytes, 890909 referencias no solapadas.
- ISO piloto SHA256 9c655957351a3b9bf348012201f8c18f518027b3817a5fc1c313a73d98288d9d.

## Motor
Sidecar campos_compactos_rom019.json: 13 adaptaciones y una reserva excepcional; fallback limitado a ISO_START, SHA fuente, revisión y anclas exactas, capacidad y controles. Pruebas nuevas test_campos_compactos_rom019.py. Empaquetado ya recorre app/datos. Motor completo no ejecutado localmente; CI de la nueva rama por comprobar.

No sumar 197 al numerador histórico: son sustituciones del piloto sobre la ISO original, no incremento respecto a v0.19.0. Cobertura global certificada sigue 21805/26258 histórico. No se dispone de EDAT ni PPSSPP; no distribuir ISO ni recursos comerciales. Próximo bloque: magic.dat y skill.dat, cotejo histórico y construcción integral.
