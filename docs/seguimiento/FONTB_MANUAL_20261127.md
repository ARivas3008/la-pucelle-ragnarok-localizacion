# FontB manual — 27/11/2026
Base Git: 574d15750ef2128d0294dd5ea55cbf8f8020ebfd. El RAR del usuario es prioritario.
La plantilla completa 4x solo aporta F050/F051; sus bloques 4x son uniformes.
La comparación rápida negra aporta F040/F041/F042/F043/F044/F047/F04A/F04C, F04E/F04F (estrechos), 3F, 8141, 8169, 8163. El punto sólido 8144 sustituye el dibujo circular 8142 sin cambiar la codificación de textos ya compilados. 8148 usa 3F estrecho. Se conserva la admiración regular, que no cambió en el RAR.
Se mantienen FNT/FTD, tamaños, CLUT y los restantes glifos; remapeo por alpha a la paleta real. En DLC 3F y 8148 son alias. El reemplazo 8142 es global en las fuentes localizadas: cambia también el punto japonés en texto residual. No se alteran originales ni se publican ISO/DLC. No se certifica anchura efectiva, render PPSSPP ni reconstrucción RC024 completa.
integracion_total.py llama a apply_manual después de extender fuentes en cada pack. Para START_JP.LZS RC024 ya extendido: scripts/rc027_integrar_fontb_manual.py --start RUTA --salida CARPETA_NUEVA. No ejecutar el antiguo corrector automático RC026 sobre la fuente manual.
