# Plantillas, ramas, revisiones y actas

## Campos mínimos en unidades_extraidas.csv
~~~csv
unit_id,grupo_id,recurso,escena,hablante,offset,original,capacidad_bytes,tipo
101,A,ISO/talk00.dat,capitulo_1,Prier,1024,Hello!,36,dialogo
102,A,ISO/talk00.dat,capitulo_1,Prier,1060,Good morning.,36,dialogo
103,B,ISO/char.dat,menu,,,Potion,24,fijo
~~~

**El CSV es didáctico, no datos del juego real.** Una celda offset vacía requiere medición por parser antes de la inserción. No se debe confiar en que la posición sea definitiva si el recurso se reubica.

## Revisión por unidad
~~~csv
unit_id,es_revisado,estado,notas_editoriales
101,¡Hola!,revisado,
102,Buenos días.,revisado,
103,Poción,revisado,
~~~

Las anotaciones de MTL son separadas del texto revisado. Una revisión por grupo que corresponde a varias unidades requiere asignación explícita grupo→unidad; nunca cortar proporcionalmente por número de caracteres.

## Propuesta de estructura Git
~~~text
README.md
AGENTS.md
glosario/
data/maestros/                    # inmutable
adaptadores/<juego>/              # extracción, formatos, test de reversión
corpus/01..NN/
  entrada.csv                      # congelado
  revision.csv                     # editable por revisor responsable
  LEEME.md
parcheador/                        # construcción y pruebas de inserción
qa/                                # reportes por unidad y matrices de escenas
docs/versiones/v0.x.md             # un documento por cambio
~~~

## Ramas
- main: estado publicado y validado.
- extraccion/formato-X: ingeniería, lector, inventario, prueba reversible.
- revision/corpus-NN: **solo revision.csv del lote propio**; PR por corpus.
- integracion/version: build con QA, sin tocar originales.
- investigacion/bug-XXXX: hipótesis y pruebas, no parche estable.
- metodologia/pipeline-...: herramientas genéricas sin modificar el juego.

## Documento obligatorio de cada versión
Registrar: versión, fecha, referencia a commit, SHA de fuentes, formatos y archivos modificados, número de unidades por estado (con denominador), cambio exacto, pruebas superadas/fallidas, capturas PPSSPP, riesgos y regresión frente a versión anterior, instrucciones de reversión y pendientes.

## Acta breve PPSSPP
Versión PPSSPP; hardware y renderizador; configuración; SHA original y parche; identificador de escena y unidad; secuencia exacta para reproducir; capturas originales y localizadas; resultado (OK/ERROR/PENDIENTE); compromiso de bug y evidencia; responsable.
