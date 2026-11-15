# Matriz de inspección de las 14 unidades con anclas CP932

**Fuente:** auditoria_scripts.csv conservadora v0.12 y estado_unificado_66.csv. **No confundir 14 cadenas con 15 referencias**; la unidad 1759 aparece con dos referencias problemáticas. La presencia de nombres propios no explica el defecto técnico.

| ID | Recurso | Texto revisado (fragmento) | Referencias | Tipo aparente por contenido | Experimento de aceptación |
|---|---|---|---:|---|---|
| 1758 | DLC_00/script00.dat | Gran Señora Demonio Unificadora | 1 | título narrativo | comprobar aparición del título y transición del DLC |
| 1759 | DLC_00/script00.dat | ¿Continuará? | 2 | rótulo de cierre | comprobar dos llamadas de índice y cierre de escena |
| 3883 | script02.dat | la memoria por completo | 1 | narración | comprobar secuencia de recuerdos |
| 3897 | script02.dat | Aquella noche | 1 | encabezado temporal | comprobar sincronía al cambiar de plano |
| 3898 | script02.dat | vi a Prier llorar a solas | 1 | narración con personaje | comprobar aparición y duración |
| 3924 | script04.dat | Tal vez tu ciudad sea la próxima | 1 | anuncio | comprobar tiempo de pantalla |
| 3969 | script06.dat | considerarte afortunado | 1 | diálogo fragmentado | comprobar continuación |
| 3989 | script09.dat | La visión de la hermana Alouette nos había guiado | 1 | narración con personaje | comprobar legibilidad/orden |
| 4007 | script10.dat | con nuestros propios ojos | 1 | final de intervención | comprobar terminador |
| 4083 | script15.dat | Mi hermana, Señora Demonio | 1 | narración con título | comprobar efecto de puntuación |
| 4095 | script16.dat | de nuevo a aquella muchacha | 1 | narración fragmentada | comprobar contexto anterior |
| 4098 | script16.dat | aquella muchacha | 1 | continuación | comprobar unión sin nueva caja |
| 4170 | script18.dat | Desde que Prier desapareció | 1 | narración con personaje | comprobar transición |
| 4220 | script18.dat | la luz que había perdido | 1 | narración | comprobar cierre de frase |

La clasificación «tipo aparente» deriva únicamente de la redacción; **no describe la semántica binaria ni demuestra que un texto sea un subtítulo en pantalla**.

## Procedimiento forense por caso

1. Desde el archivo binario original, extraer ruta y hash, índice de punteros y offset del manifiesto.
2. Confirmar pares de bytes Shift-JIS y si el offset apunta a primer o segundo byte.
3. Consultar la instrucción que consume la referencia (sin inventar su función).
4. Probar tres opciones A/B usando **copias**, con una escena por intento:
   - original sin modificar;
   - reubicación con puntero en comienzo del glifo (hipótesis v0.12);
   - reubicación con fase del segundo byte conservada (hipótesis v0.15).
5. Aceptar solo la que conserve la semántica de la instrucción, duración, texto, orden y caja; registrar vídeo o captura.
6. Si ninguna cumple, **no** forzar parche: investigar opcode consumidor o un cuadro adicional de texto válido.

## Decisión actual

**Las 14 permanecen BLOQUEADAS PARA RELEASE** hasta trazas y pruebas en PPSSPP. El prototipo de fase preservada es un mecanismo de investigación para evitar que un índice se desplace silenciosamente a un byte distinto; NO es una implementación de los 14 en un build jugable.
