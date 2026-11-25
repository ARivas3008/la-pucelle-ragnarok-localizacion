# ROM-031 — Subgrupos TALK y variables reales

Base ROM-030 ae7cfc294451743f0e6572e83e7bff77cbca3254. Consultados cuatro workflows de base: corpus 45655975819, inventarios 45655976217, motor 45655975812 y Windows 45655975884; todos success.

## Cambios de motor
- La ruta parcial que admitía solo una línea ahora admite subgrupos de varias líneas con ancla física exacta, revisión aprobada, tantos IDs únicos como slots y una sola variante editorial inequívoca. Distribución de palabras en exactamente los mismos slots, límite 28 glifos por línea, sin cambiar separadores o añadir páginas. Mantiene el resto del run intacto.
- Rechaza grupos partidos por entradas, controles o elecciones.
- Distingue las variables A0..A9 reales (pares ASCII del intérprete) del texto literal en ancho completo. Exige secuencia exacta en la traducción; en modo parcial, también por línea. Si falla, conserva el original y registra pendiente.
- Se añaden ocho regresiones sintéticas en test_rom031_subgrupos.py, además de las siete del relevo ROM011.

## Alcance y límites
En esta sesión no fue posible acceder al contenedor de ejecución (ClientError en terminal y Python). No se ha abierto ni reconstruido una ISO real, ni los cuatro EDAT, ni PPSSPP. No se acredita ningún nuevo ID reinsertado; última cobertura documental sigue siendo 23187/26257 incluyendo las 190 adaptaciones históricas EBOOT (88,31%), y la última integral 21805/26258 (83,04%). Los 3006 TALK ISO, 2 rótulos EBOOT y 62 gráficos pendientes de la contabilidad agregada no se cierran con pruebas sintéticas. La mejora del motor requiere reconstrucción y relectura auténticas antes de contabilizar unidades. Sin recursos comerciales publicados. No se altera main.

## Próxima ejecución con originales
Ejecutar integracion_total.py con ISO autenticada, cuatro EDAT originales y checkout completo. Consolidar las pruebas ROM029, generar diarios por recurso, ejecutar auditar_entrega.py y cotejar IDs pendientes de ROM030. No promover candidata si falla una prueba o si faltan unidades. Separar los gráficos pendientes de validación visual.
