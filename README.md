# La Pucelle: Ragnarok — Traducción al español

Traducción en desarrollo para PSP, con corpus revisado, motor de inserción y parcheador gráfico para Windows x64.

**Entrega vigente: v0.19.0-integracion · preliminar · 23 de noviembre de 2026.**

[Descargar parcheador y comprobaciones](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/releases/tag/v0.19.0-integracion) · [Cómo instalar](docs/INSTALACION.md) · [Cobertura](docs/COBERTURA.md) · [Errores y pendientes](docs/ERRORES_CONOCIDOS.md)

## Estado real

La ISO generada por el ejecutable contiene **21.805 de 26.258 unidades técnicas verificadas (83,04 %)**. La auditoría comprueba los bytes insertados y su destino. **No es un porcentaje de juego comprobado en pantalla ni una traducción completa.** La última comprobación visual documentada fue el prólogo de v0.18.3; la ampliación de v0.19.0 requiere nuevas pruebas en PPSSPP.

| Medida | Resultado |
|---|---:|
| Grupos editoriales de los 15 corpus | 15.016 |
| Grupos revisados / requieren investigación | 14.727 / 289 |
| Unidades del manifiesto insertadas y cotejadas | 21.805 / 26.258 |
| Apariciones físicas de diálogo insertadas | 18.601 |
| Apariciones físicas de diálogo pendientes | 1.686 |
| Bloques de signos originales conservados | 363 |
| Textos de script insertados | 503 |
| Propuestas adicionales HY-MT2 revisadas | 500 |
| Borradores HY-MT2 todavía sin revisión | 1.211 |

Estas medidas tienen denominadores diferentes; no deben sumarse. Permanecen textos de tablas, títulos de capítulos, carteles y elementos del HUD por completar o comprobar.

## Usar el parcheador

1. Descarga el `.exe` de la entrega enlazada y consulta su SHA-256.
2. Selecciona tu ISO compatible y, opcionalmente, la carpeta con los cuatro DLC originales.
3. Elige una carpeta de salida nueva y ejecuta el parcheo.
4. Abre la ISO de `JUEGO_PARA_PPSSPP` y consulta los informes generados. Para comparar versiones, inicia una partida nueva sin cargar un estado rápido anterior.

El repositorio y la descarga contienen herramientas y datos de traducción. Cada usuario aporta la ISO y los DLC; no se distribuyen aquí.

[Publicación, pruebas y limpieza completadas](docs/PUBLICACION_2026-11-23.md).

## Documentación

| Contenido | Ubicación |
|---|---|
| Requisitos, instalación, DLC y solución de problemas | [Instalación](docs/INSTALACION.md) |
| Qué está insertado y cómo se mide | [Cobertura y límites](docs/COBERTURA.md) |
| Cambios de cada versión y política de sustitución | [Historial](docs/HISTORIAL_VERSIONES.md) |
| Correcciones de esta entrega | [v0.19.0](docs/versiones/v0.19.0.md) |
| Formatos, controles, fuentes y reconstrucción | [Motor de integración](docs/INTEGRACION.md) |
| Compilación y pruebas reproducibles | [Desarrollo](docs/DESARROLLO.md) |
| HY-MT2 local, revisión y trazabilidad | [Traducción asistida](docs/HY_MT2.md) |
| Ramas históricas y conservación de commits | [Organización de GitHub](docs/ORGANIZACION_GITHUB.md) |
| Datos revisados, entradas inmutables y glosario | [Corpus](corpus/) · [Datos](data/) · [Glosario](glosario/) |
| Método reutilizable de localización | [Metodología](metodologia/README.md) |
| Investigación, borradores y diagnósticos anteriores | [Laboratorio](laboratorio/2026-11-integracion/README.md) |

Para contribuir, lee [CONTRIBUTING.md](CONTRIBUTING.md). Los informes históricos describen su versión y no sustituyen el estado vigente de esta portada.
