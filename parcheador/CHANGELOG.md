# Registro de versiones del parcheador

- [v0.17.3-lba-qa — Conservar LBA de START y SCRIPTPACK y abortar si no caben](docs/versiones/v0.17.3.md) (validación visual PPSSPP pendiente)

- [v0.17.2-diagnóstico — Corrupción visual PPSSPP y 3 diálogos bloqueados](docs/versiones/v0.17.2.md) (A/B pendiente, sin certificación de gráficos)

- [v0.17.1-qa — Corregir falta de DLC sin cambios y publicación final atómica](docs/versiones/v0.17.1.md) (pruebas Windows, PPSSPP pendiente)

- [v0.17.0-qa — Paginación de diálogos, once unidades del tutorial y salida final para PPSSPP](docs/versiones/v0.17.md) (QA visual pendiente)

- [v0.16 — GUI con segunda fase de scripts y ensayo de referencias CP932](docs/versiones/v0.16.md) (NO verificada en PPSSPP)

Cada versión tiene un documento propio en `docs/versiones/`. **Las métricas históricas provienen de sus respectivos paquetes; no equivalen a pruebas actuales en PPSSPP.**

- [v0.15 — Referencias CP932, dossier forense y auditoría de solo lectura](docs/versiones/v0.15.md)
- [v0.14 — Inserción y reubicación conservadora de 489 textos de script](docs/versiones/v0.14.md)
- [v0.13 — Integración versionada y verificación de reducciones](docs/versiones/v0.13.md)
- [v0.12 — Reducciones y anclas de script](docs/versiones/v0.12.md)
- [v0.11 — Auditoría de 66 recursos](docs/versiones/v0.11.md)
- [v0.10 — Ampliación masiva y continuaciones](docs/versiones/v0.10.md)
- [v0.9 — Reubicación de diálogos: prototipo](docs/versiones/v0.9.md)
- [v0.8 — Campos reservados en HUD](docs/versiones/v0.8.md)
- [v0.7 — Rótulos narrativos y abreviaciones](docs/versiones/v0.7.md)
- [v0.6 — Atlas localizados y capacidades](docs/versiones/v0.6.md)
- [v0.5 — Diálogos atómicos](docs/versiones/v0.5.md)
- [v0.4.1 — Desbordamientos controlados](docs/versiones/v0.4.1.md)
- [v0.4 — Interfaz gráfica ISO y DLC](docs/versiones/v0.4.md)
- [v0.3 — Ejecutable Windows inicial](docs/versiones/v0.3.md)
- [v0.2.1 — Preparación para Windows](docs/versiones/v0.2.1.md)
- [v0.2 — Compresión LZS y fuentes españolas](docs/versiones/v0.2.md)
- [v0.1 — Primeras herramientas](docs/versiones/v0.1.md)

## Convención a partir de v0.13

1. Un archivo de versión por cada entrega, con cambios, ensayos, riesgos y pendientes.
2. `resumen.json` y `reporte_por_unidad.csv` generados por el motor para cada build.
3. Pruebas unitarias en `app/tests` y de ingeniería inversa en `investigacion/v*/tests`.
4. Un PR por integración, con revisión de los hashes y sin incluir imágenes comerciales.
5. No confundir una prueba de reversibilidad binaria con una validación de jugabilidad.
