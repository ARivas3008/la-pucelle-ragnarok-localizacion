# La Pucelle — lectura española y editor visual

Entrega independiente. La rama contiene la edición plana de los 15 corpus (15.016 grupos) y un editor local de cuadros. No contiene ISO ni DLC. No se ha ejecutado sobre la ISO auténtica en esta sesión.

## Lectura
Abre `lectura/`: 02_localidades, 03_personajes_y_enemigos, 04_nombres_generados, 05_eventos_base_y_dlc, 06_dialogos y otras categorías. Cada texto conserva el grupo editorial. No se inventan hablantes ni orden de capítulos. La FAQ PS2 adjunta es modelo de presentación, no fuente de extracción PSP; explícitamente omite NPC y tutoriales. La edición corresponde a los corpus, no a las ocurrencias físicas de RC024. Los índices JSON registran recuentos y estados; las propuestas no revisadas aparecen marcadas. No se incluyen los 509 grupos fuera del reparto ni textos descubiertos después que no estén en esos corpus.

## Editor local
1. Descarga la rama como ZIP y extrae. Instala Python 3.10+ si no lo tienes.
2. Pon una copia de la ISO española RC024 en la raíz con nombre BASE.iso.
3. Terminal en Mac: escribe `cd ` y arrastra la carpeta extraída. Ejecuta:
   `python3 editor/editor_visual.py exportar BASE.iso REVISION`
   Windows: `py editor/editor_visual.py exportar BASE.iso REVISION`.
   Opcional: añade `--dlc "ULJS00244"` (solo lectura).
4. Se abre REVISION/EDITOR.html: busca textos, ve cuadros y líneas reales extraídos, modifica, redistribuye si está permitido, guarda cada cambio y descarga cambios.json. La vista es esquemática, no una emulación. Para mantener borradores, descarga JSON y vuelve a importarlo al mismo HTML.
5. Copia cambios.json a la raíz y ejecuta:
   `python3 editor/editor_visual.py insertar BASE.iso cambios.json PRUEBA_ES.iso`
   En Windows usa py en vez de python3.
6. Prueba PRUEBA_ES.iso en PPSSPP. No uses un estado rápido de otra ISO.
7. Para el siguiente lote exporta la nueva ISO a otra carpeta. Los offsets cambian.

La exportación física incluye TALK de SCRIPTPACK, START y DLC opcionales. Solo SCRIPTPACK es editable en este piloto; START y DLC son de consulta. No se editan elecciones, variables dinámicas, opcodes desconocidos ni recursos gráficos. Las modificaciones estructurales requieren confirmar una intervención continua y límites seguros. Si una cadena no cabe en el hueco del miembro, se rechaza; no se relocaliza el pack completo. No es una certificación PPSSPP.

## Límites y signos
28 pares por línea (56 bytes de texto + NUL), tres líneas por cuadro, 84 pares por cuadro como máximo conservador. Búfer documentado: 65 bytes por fila (64 datos + NUL, 32 pares teóricos, no objetivo de edición). Todas las letras y signos ordinarios admitidos por TALK se codifican a dos bytes, incluidos espacios y tildes. Variables A0..A9 son dos bytes, pero su expansión puede ocupar varias letras. 01 abre línea, 00 termina, 02 es salto de página en el motor documentado; otros controles deben conservarse. No son caracteres imprimibles.

La exportación crea valores_signos.csv: código real, bytes, pares, GID, FTD bruto y caja de tinta del atlas instalado para cada signo. FTD bruto y tinta no equivalen automáticamente al avance horizontal efectivo; para eso hace falta medir el renderizador. La interfaz cuenta caracteres como aproximación conservadora y el insertor vuelve a comprobar los pares y cobertura de fuente.

## Estado
Exportación editorial realizada; código visual y reinserción preparados. Sin ejecución de Python/PPSSPP en esta sesión por fallo del entorno. No sobrescribe la base. Verifica copias y realiza una sola edición pequeña antes de un lote grande.
