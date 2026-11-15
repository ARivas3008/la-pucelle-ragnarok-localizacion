# La Pucelle: Ragnarok — Localización al español

Repositorio **público**, publicado a petición del titular, para revisar **15 016 grupos de texto** mediante **15 chats independientes** del proyecto [La Pucelle — Localización ES](https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project).

Los **15 corpus ya están cargados** en `corpus/01` a `corpus/15`. Cada uno contiene:
- `entrada.csv`: originales, borradores, contexto previo/siguiente, hashes y referencias al Excel.
- `lectura.txt`: lectura organizada por grupos y escenas.
- `revision.csv`: único archivo editable por el chat asignado.
- `LEEME.md`: instrucciones particulares.

Se conservan además **509 grupos con revisión previa** en `data/preexistentes/`, los mapas de reintegración, glosarios, TXT, siete libros Excel y los scripts de QA.

## Inicio rápido: 1 chat por corpus

1. Abre el [proyecto de ChatGPT](https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project).
2. Verifica que tenga como instrucciones el contenido de [CHATGPT_PROJECT_INSTRUCCIONES.md](CHATGPT_PROJECT_INSTRUCCIONES.md).
3. Abre **15 chats diferentes**. En cada uno escribe solamente su número, de `1` a `15`.
4. Cada chat debe leer [AGENTS.md](AGENTS.md), el glosario y su carpeta, trabajar en sublotes de 40–60 grupos y guardar únicamente `corpus/NN/revision.csv` en la rama `revision/corpus-NN`.
5. Al terminar un corpus, validar y abrir un PR hacia `main`. No fusionar un PR si quedan grupos pendientes, variables modificadas o errores QA.
6. Tras los 15 PR, el coordinador valida los 509 grupos restantes, reconstruye una copia del Excel y prueba la inserción en la ISO.

**Estado editorial inicial:** 15 016 grupos **pendientes de revisión**, no «traducidos definitivamente». El 100 % de cobertura MTL previa no implica calidad editorial aprobada.

## QA y control de versiones

El workflow [QA de corpus](.github/workflows/qa.yml) comprueba la conservación de filas, IDs, hashes y códigos. Un PR de corpus solo puede modificar su propio `revision.csv`. Para verificar localmente:

```bash
python scripts/validar.py
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/validar.py --corpus 7 --estricto
```

Consulta [CONTROL_CALIDAD_Y_REINTEGRACION.md](CONTROL_CALIDAD_Y_REINTEGRACION.md) y [COORDINACION_FINAL.md](COORDINACION_FINAL.md).

**Aviso de distribución:** el proyecto es público por decisión del titular. Contiene textos originales de un videojuego comercial; no almacena ISOs, EBOOT, archivos EDAT ni claves de distribución. La publicación de los textos no implica una licencia comercial o redistribución otorgada por los titulares de derechos.


## Parcheador experimental e ingeniería de inserción

La implementación técnica del parcheador para ISO y cuatro DLC, los informes y **un documento por versión desde v0.1 hasta v0.14** están en [parcheador/](parcheador/README.md). Consulta [el historial de cambios](parcheador/CHANGELOG.md), [las fichas de versiones](parcheador/docs/versiones/) y [el estado de cobertura de las 26 258 unidades](parcheador/docs/ESTADO_100_POR_CIENTO.md).

**Estado:** parche parcial experimental, no traducción validada al 100 %. La v0.13 incluye una opción para aplicar 197 reducciones estructuralmente comprobadas; la reubicación experimental del bytecode permanece aislada hasta las pruebas en PPSSPP. No se distribuyen ISO, EDAT ni otros recursos comerciales.

El reubicador experimental [v0.14](parcheador/investigacion/v0.14/README.md) incorpora 489 inserciones estructuralmente validadas de `script*.dat` con prueba de reconstrucción ISO y DLC; no sustituye la GUI v0.13 ni acredita la traducción final.

[Forensia v0.15: estructura, offsets y mapa de las 14 referencias](parcheador/docs/FORENSE_ESTRUCTURA_JUEGO.md) · [Ficha de formatos](parcheador/docs/FORMATOS_BINARIOS.md). La investigación no modifica el juego ni equivale a traducción jugable completa.


### Desarrollo v0.16 (no aprobado)

La rama `desarrollo/parcheador-v0.16-referencias` agrega la integración opcional del reubicador de scripts en el EXE y un ensayo conservador de fase CP932. Se identificaron 14 textos con 15 referencias problemáticas en los originales facilitados: solamente 4 tienen candidato cercano en fase. Los resultados no acreditan 100 % ni ejecución PPSSPP. Véase [v0.16](parcheador/docs/versiones/v0.16.md).


### v0.16.1 — Corrección de scripts y documentación reproducida

El parcheador de la rama `desarrollo/parcheador-v0.16-referencias` pasa el autotest de Windows y tiene [un documento por versión](parcheador/docs/versiones/v0.16.md), [inventario forense de la ISO y los DLC](parcheador/docs/INVENTARIO_FISICO_V016.md) y [matriz exacta de 14 unidades/15 anclas](parcheador/investigacion/v0.16/MATRIZ_RETEST_14.md). En prueba binaria aislada: **489 inserciones conservadoras + 3 candidatos de fase = 492**, 11 anclas bloqueadas y Now Loading preservado. **No es 100 % del juego**, no modifica los corpus editoriales ni acredita PPSSPP. El EXE se publica como artefacto de GitHub Actions y no contiene la ISO ni EDAT comerciales.
