# Plan de validación en PPSSPP (pendiente de ejecución)

Usar siempre copias limpias de la ISO v1.1.2, DLC y partidas. Tras aplicar el parche, iniciar de cero sin cargar un savestate de una versión anterior. Documentar versión PPSSPP, sistema, modo gráfico, checksum de ISO y opciones activadas.

1. **Inicio:** logo y capas del prólogo; apertura y menú `Jugar/Seguir/Opciones`; cajas no recortadas.
2. **Diálogos:** casos de «¡Ya estoy harta!» y «¡No hables así!» más una ruta completa de la historia. Verificar idioma, acentos, cambios de hablante y avance de cajas.
3. **HUD:** inventario, habilidades, equipamiento, estadísticas, nombres largos; comprobar rebases y solapes en diferentes resoluciones.
4. **Combate:** turnos, objetivos, resultados, rótulos atlas `sys3/sys4`, sprites y texturas sin desapariciones.
5. **Transiciones:** guardado, carga y entrada/salida de escenarios; comprobar referencias internas de scripts.
6. **Cuatro DLC:** iniciar cada uno con EDAT recién generado; verificar textos del inicio, final y cambios entre contenido DLC y juego.
7. **Regresión:** comparar 10 escenas antes/después por capturas con mismos ajustes.

Registrar por caso: unidad/es, capítulo, recurso, configuración, captura original y española, comportamiento, `OK/ERROR`, capturas adjuntas y build SHA. El parche no pasa a final hasta que todos los casos estén `OK` y no queden traducciones pendientes.
