# Contribuir

Consulta primero la cobertura, los errores conocidos, el glosario y la ficha vigente. Para informar de un fallo, incluye versión y SHA-256 del parcheador, escena/personaje, texto observado, captura del juego y si se reproduce desde New Game.

La revisión de un corpus se limita a su `revision.csv`: conserva IDs, orden, originales, variables y marcadores. Marca como revisado solo lo que hayas cotejado con su contexto; las dudas quedan como investigación pendiente.

La integración técnica requiere comprobar los bytes originales, la capacidad o estructura del destino, los glifos y la reversibilidad. No modifiques manifiestos ni offsets para hacer pasar una inserción. Usa una rama de coordinación para cambios transversales y ejecuta las pruebas documentadas en `docs/DESARROLLO.md`.

No adjuntes ISO, DLC, archivos completos del juego, credenciales ni rutas personales. Los binarios del parcheador se publican en Releases con su hash y vínculo al código; los borradores del modelo permanecen separados de los datos aprobados.
