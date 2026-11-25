# ROM-024 — Cuatro DLC aportados, auditoría y piloto de 214 campos

24/11/2026 Lima. Base ROM-023 79762f2c0e07c68d3edb3412af96342d41323c53; sus cuatro workflows CI aprobados. Archivo aportado ULJS00244 (1).7z, extraído localmente con libarchive: cuatro EDAT, PARAM.PBP, readme y URL. No se publica ningún recurso comercial.

## A — originales aportados

| DLC | SHA-256 EDAT | Bytes | DAT bytes | Referencias LZS no solapadas | Anclas |
|---|---|---:|---:|---:|---:|
| 00 | 723720fb885a092d1adb71b7ca24b90b6b03e828460669edb662ae6f38dfef00 | 5127190 | 11772016 | 670382 | 3264 |
| 01 | fc2bcc6cdb9ff84d0a365b1f873e12d7d4546b5215a165473eb292a8d72ce17d | 5203970 | 11957040 | 682662 | 90 |
| 02 | bd88a3409a1d78b810ff1a07f1eb0d4ded05b9056bea874e720dbdca64bc329e | 5267964 | 12081136 | 690424 | 99 |
| 03 | bb879fc608d42e326f41d1e460f97a6beacf6ead86b5734e2c200e515847175e | 5348846 | 12232624 | 700719 | 84 |

NISPACK little endian, una entrada start_jp.lzs a offset 2048, longitud exacta; cada DAT tiene 36 miembros, sin colisiones de nombres, intervalos ordenados. 3537/3537 C-strings del manifiesto coinciden con CP932 y NFKC (solo strip exterior). Esto identifica la edición aportada y su correspondencia física, no firma del fabricante. 1668 unidades TALK (1424/85/80/79) todavía no recompiladas; 19 script00.dat del DLC00 y 1850 campos fijos.

## B — piloto independiente real

214 grupos revisado recuperados de blobs corpus01 47e59c28dc4108108e016855dbe94a994aa055ef; corpus02 e2c8159472689c48db2700f4bc5de1101767e664; corpus13 cf4c43acb789a5dd4e38261530803f13a31e6a91; central dd01f8481024307c842786b09d705dfe10a2b1fc. Flujo grupo/tab/texto/LF orden numérico FNV32 remoto/local 2856732917, SHA256 local 250faa6f1f8122d9d0ef132b6e14f1f9d2ac1622beabbf5478cd159f868bee00.

| DLC | Completo | Compacto | Resuelto | Recursos intactos | Referencias LZS destino |
|---|---:|---:|---:|---:|---:|
| 00 | 179 | 6 | 185 | 30/36 | 900425 |
| 01 | 4 | 1 | 5 | 31/36 | 915977 |
| 02 | 16 | 3 | 19 | 31/36 | 926524 |
| 03 | 2 | 3 | 5 | 31/36 | 940261 |
| Total | 201 | 13 | 214 | 123/144 | 3683187 |

156 char.dat DLC00, 26 name.dat DLC00 (clases reales 22 sufijos clase 1, 4 prefijos clase 2, 11 bytes útiles), tres magic.dat centrales 611/731/951; 29 campos exclusivos DLC01/02/03. 16 marcadores circundados preservados, botón □ intacto. 18 gaiji (16 base, ê, ’) asignados en sus GID canónicos y alias de apóstrofo; se generaron desde cada fuente DLC original, no se copiaron texturas de ISO (fnt y página 0 distintas). Todas las cadenas tienen glifos. Se verificaron bytes exteriores de los campos y metadatos NISPACK salvo longitud +0x34, relectura del DAT y recompresión reversible sin solapamientos. Piloto local independiente, no ejecución integral del motor. Las 13 compactas necesitan cotejo visual/editorial.

| DLC | EDAT piloto SHA256 | Bytes |
|---|---|---:|
| 00 | 7df07cf9023e25ce07e91fe0c48ffd2d4a44739112cf41a39e53ebc1aab09efe | 5189850 |
| 01 | cc19559874eb16328ee1e1a69d433a02a5b6c991c40a9a3eea2ae6d47df81da1 | 5267214 |
| 02 | 3c38909d9975627d3b894e1ec33abe3efd1f4c052381f2f646cc250a4ab2a7fc | 5331998 |
| 03 | 2f8f5548a136b1ece8ff9bf3f048f5a47ac45ac370f8f16a498144238f54ce11 | 5413740 |

## Integración
Guardia de origen de cuatro EDAT antes de escribir en integracion_total.py; 13 variantes compactas vinculadas a original, revisión, capacidad y SHA, preservando circundados y □. Pruebas nuevas para capacidad, hashes y marcadores. No se modifica main ni corpus. CI pendiente.
No sumar 214 a 21805 históricos: pueden incluir unidades ya contabilizadas. Faltan 3323 unidades DLC de este piloto (1636 campos, 1668 TALK, 19 scripts). Continúa necesaria una candidata integral ISO/DLC con checkout completo, auditoría y PPSSPP real. No se publica EDAT ni DAT ni fuentes.
