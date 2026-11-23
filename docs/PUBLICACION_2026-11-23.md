# Publicación y limpieza completadas — 23-11-2026

La [entrega v0.19.0-integracion](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/releases/tag/v0.19.0-integracion) está publicada como preliminar. Su etiqueta apunta a `35102ed9fccd1a9df125342a79dc287155ce1faf`.

## Entrega verificada

Los cuatro archivos de Releases —EXE, SHA256SUMS, instrucciones y cobertura— se descargaron públicamente y coinciden byte a byte con los locales. El EXE ocupa 10.915.328 bytes y tiene SHA-256 `7fe6f99e4c7e80c0a7d4709b32d50b112c72d5abaf5e5c04c9ce69453c6368bc`.

La ejecución completa generó ISO y cuatro EDAT con código 0. La auditoría del 23-11 confirma 21.805/26.258 unidades técnicas insertadas y cotejadas (83,04 %). La validación visual amplia continúa pendiente.

Las suites locales reúnen 159 pruebas Python: 129 correctas y 30 omitidas por faltar muestras externas. Los 15 corpus pasan la validación, además de cuatro pruebas Go. Las cuatro comprobaciones de [GitHub Actions](informes/CI_v0.19.0.json), incluida la compilación Windows desde un clon, terminaron correctamente.

## Organización completada

- 26 ramas antiguas retiradas después de preservar sus commits exactos en etiquetas `archivo/2026-11-19/*`.
- Siete PR experimentales superados cerrados: #18 a #24, con referencia a la entrega vigente.
- Una rama de trabajo vigente: `main`. El corpus 15, la metodología y el avance local están incorporados.
- Seis ejecutables históricos retirados de Releases. Se mantienen las fichas y etiquetas de cada versión, con aviso de sustitución y enlace a la actual.
- En el dossier local, 18 archivos generados sustituidos eliminados: **4,408,451,735 bytes**. La entrega actual se conserva en `13_Entrega_v0190/`; los originales, fuentes, modelos locales e informes permanecen.

La limpieza anterior del 17-11 retiró otros 102 archivos y 22.787.213.148 bytes; su diario se conserva en el laboratorio. No se suman ambas cifras como tamaño actual del proyecto.

## Evidencia

- [Inventario previo de ramas y commits](informes/ramas_2026-11-19.json).
- [Ramas y PR retirados](informes/github_limpieza_ejecutada.json).
- [Binarios históricos retirados de Releases](informes/github_binarios_retirados.json).
- [Descargas y hashes comprobados](informes/github_descarga_verificada.json).
- [Archivos locales eliminados](informes/limpieza_local_v0190.json).
- [Cobertura detallada](COBERTURA.md), [historial de versiones](HISTORIAL_VERSIONES.md) y [pendientes](ERRORES_CONOCIDOS.md).

Los informes permiten diferenciar código publicado, texto insertado, borradores pendientes y comprobación visual. La publicación no convierte la traducción parcial en una versión completa.
