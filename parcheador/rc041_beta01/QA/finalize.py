from pathlib import Path
import csv,json,zipfile,shutil
P=Path('/tmp/lapucelle_beta1');Q=P/'qa';M=Path('/mnt/data');r=json.loads((Q/'QA_BETA01.json').read_text())
def csvfile(name,fields,rows):
 with (Q/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
checks=[('PRE-001','Motor de parcheo REV6','Autoprueba de cinco flujos gzip','PASS','replay.log'),('PRE-002','Reconstrucción ISO y cuatro DLC','Cinco SHA-256 coinciden','PASS','QA_BETA01.json'),('PRE-003','Identidad de disco','PARAM.SFO: ULJS00244, DISC_VERSION 1.01; 28 entradas del árbol','PASS','QA_BETA01.json'),('PRE-004','EXE BETA01','Cinco deltas incrustados coinciden con REV6','PASS','QA_BETA01.json'),('PRE-005','ISO de tamaño incorrecto','Rechazo sin salida parcial (REV6)','PASS','wrong_iso.log'),('PRE-006','Carpeta de salida existente','Rechazo sin sobrescritura (REV6)','PASS','existing_output.log'),('PRE-007','PARAM.PBP válido','Copia exacta del paquete de referencia; ISO y 4 DLC idénticos a REV6','PASS','replay_beta01.log'),('PRE-008','PARAM.PBP ausente','Aviso y generación de cuatro DLC','PASS','missing_param.log'),('PRE-009','PARAM.PBP no reconocido','Rechazo sin salida publicada','PASS','invalid_param.log'),('PRE-010','Análisis TALK','21 recursos; 20.650 bloques alineados; 6 falsos positivos','PASS','QA_BETA01.json')]
fields=['id','prueba','criterio','estado','evidencia'];csvfile('Pruebas_preliminares.csv',fields,[dict(zip(fields,x)) for x in checks])
areas=[('BOOT','Arranque','Pantalla de título; iniciar juego desde ISO limpia'),('INTRO','Introducción','11 líneas y sombras; acentos y alineación'),('TUT','Tutorial','Purificación; sin línea inglesa duplicada; opciones completas'),('MENU','Combate','Mover, Atacar, Habilidad, Purificar, Objeto, Estado, Dirección, Deshacer'),('OBJ','Objetos','Usar, Equipar, Desechar; confirmación y ayuda'),('FONT','Fuente','Espaciado, acentos, comas y signos'),('SHOP','Tiendas','Inventario, compra/venta y menús secundarios'),('MAP','Mapa','Asset Mapa y carteles; animación y legibilidad'),('HUD','HUD','PV, PE, ATQ, VEL; anuncios, objetivos, ¡Reacción!, OMITIR'),('STAT','Estadísticas','Objetos, habilidades, efectos; textos de tablas y generador'),('SAVE','Guardado','Guardar, reiniciar, cargar; savestate propio y carga'),('NGP','Nueva Partida+','Cambio de ruta y continuidad de guardado'),('DARK','Inframundo','Eventos y contenido secreto'),('CRED','Créditos','Secuencia, retorno y guardado'),('END','Finales alternativos','Inventariar y ejecutar cada ruta, no inferir cobertura'),('ALLDLC','DLC simultáneos','Instalar cuatro EDAT con PARAM.PBP; comprobar reconocimiento')]
for i in range(1,13):
 for label,phase in [('INICIO','Tarjeta y diálogos iniciales'),('EVENTOS','Eventos, elecciones y batallas del capítulo'),('JEFE','Combate final y transición'),('CIERRE','Cierre y paso al capítulo siguiente')]:areas.append((f'CAP{i:02}_{label}',f'Capítulo principal {i}',phase))
for i in range(1,5):
 for label,phase in [('INICIO','Tarjeta de inicio y escenas'),('EVENTOS','Eventos, combates y decisiones'),('CIERRE','Cierre o desenlace correspondiente')]:areas.append((f'RAG{i:02}_{label}',f'Ragnarok adicional {i}',phase))
for i,name in enumerate(['Cornet / Ellie / Hero Prinny / Rozalin (asociación por comprobar)']*4):areas.append((f'DLC{i:02}',f'DLC {i:02}','Instalación aislada, reconocimiento, desbloqueo y evento; '+name))
for i in range(1,20):areas.append((f'GFX_CARTEL{i:02}',f'Cartel {i:02}','Identificar escena y verificar texto, anchura y animación'))
for i in range(1,23):areas.append((f'GFX_CIERRE{i:02}',f'Cierre físico {i:02}','Identificar ruta y recurso; comprobar aparición real'))
for i in range(1,17):areas.append((f'GFX_INICIO{i:02}',f'Tarjeta física {i:02}','Identificar capítulo y comprobar aparición real'))
fields=['id','area','criterio','estado','emulador','iso_sha256','guardado','captura','observacion'];csvfile('Matriz_betatesting.csv',fields,[dict(id=k,area=a,criterio=c,estado='BLOQUEADO_ENTORNO',emulador='PPSSPP 1.20.4 (requerido; no ejecutado)',iso_sha256=r['outputs'][0]['target_sha256'],guardado='',captura='',observacion='Punto de control provisional; ampliar según escenas reales.') for k,a,c in areas])
fields=['fuente','url','resultado','archivo_descargado','compatibilidad']
sources=[('GameFAQs','https://gamefaqs.gamespot.com/psp/971755-la-pucelle-ragnarok/saves','Listado solo PS2 CodeBreaker, Max Drive y SharkPort.'),('Apollo','https://bucanero.github.io/apollo-saves/PSP/','Sin coincidencia ULJS00244; La Pucelle: Tactics corresponde a PS2.'),('GBAtemp','https://gbatemp.net/threads/psp-la-pucelle-ragnarok-translation.320662/','Hilo inicial y resultados indexados: referencias y guías; no enlace PSP confirmado. No se revisaron exhaustivamente todas las páginas.'),('Foro PPSSPP','https://forums.ppsspp.org/showthread.php?tid=25471','Paquete de texturas, pide savestates para reportar errores; no adjunto confirmado.'),('Save Editor BBS','https://www.save-editor.com/bbs/savedata/psp/bbs.cgi','No coincide ピュセル en página indexada.'),('Uploader.jp','https://uu.getuploader.com/psp_savedata/','Aviso de cese y eliminación de archivos el 25/11/2026; no fuente activa confirmada.'),('GameBrew','https://www.gamebrew.org/wiki/La_Pucelle_Ragnarok_Translation_PSP','Referencia de traducción inglesa y guía; no savedata confirmado.'),('Cheat Happens','https://www.cheathappens.com/37890-Sony_PSP-La_Pucelle_Ragnarok_cheats','Indica que no dispone de guardados de PSP.'),('Archivos locales','La_Pucelle_Ragnarok_v1.1.2.7z; ULJS00244 (1).7z','Inspeccionados los listados reales: ISO, cuatro EDAT, PARAM.PBP y ficheros auxiliares; sin savedata.')]
csvfile('Fuentes_guardados.csv',fields,[dict(fuente=a,url=b,resultado=c,archivo_descargado='NO',compatibilidad='NO CONFIRMADA') for a,b,c in sources])
fields=['archivo','autor','procedencia','url','tipo','disc_id','region','emulador','parche','capitulo','escena','progreso','personajes','dlc','sha256','resultado_carga','utilidad'];csvfile('Inventario_guardados.csv',fields,[])
fields=['id','capitulo','escena','savestate','categoria','gravedad','original','anterior','correccion','recurso','captura_antes','captura_despues','version','regresion','estado'];csvfile('Incidencias.csv',fields,[dict(id='PACK-001',categoria='Empaquetado',gravedad='Por determinar en juego',original='Paquete DLC incluye PARAM.PBP',anterior='REV6 no copia PARAM.PBP',correccion='Copia opcional exacta y validada',recurso='ULJS00244/PARAM.PBP',version='RC041 REV6 BETA01',regresion='Pruebas PRE-007 a PRE-009 superadas; ejecución no probada',estado='INTEGRADO'),dict(id='ENV-001',categoria='Entorno',gravedad='Bloqueante de QA',correccion='Proporcionar PPSSPP oficial 1.20.4 Linux x86_64 o entorno Windows',version='RC041 REV6 BETA01',regresion='Descarga fallida y binario no disponible',estado='BLOQUEADO')])
r.update(preliminary_checks_passed=len(checks),runtime_matrix_initial=len(areas),runtime_matrix_executed=0,runtime_matrix_passed=0,notes=['La matriz es provisional, no un inventario exhaustivo de eventos.','Se incluyen 12 capítulos principales y 4 adicionales como cobertura inicial porque el inventario de texturas contiene at01–at12 y at15–at18; debe confirmarse la correspondencia real en juego.','El archivo PARAM.PBP se copia del paquete local si se facilita; no se distribuye en este ZIP.','El EXE se compiló para Windows x64 pero no se ejecutó su GUI.','No se publicaron cambios en GitHub.'])
(Q/'QA_BETA01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));shutil.copyfile(P/'replay.log',Q/'replay.log')
(Q/'LEEME.md').write_text('''# RC041 REV6 BETA01 — inicio de certificación

Base exacta RC041 REV6. Se reconstruyeron las cinco salidas del motor Linux y se verificaron los flujos del EXE Windows. BETA01 cambia solo el empaquetado: conserva PARAM.PBP original si está presente y su hash es el esperado. No cambia ningún byte de la ISO ni de los cuatro EDAT. El entorno no tiene PPSSPP ni Wine y la descarga del emulador falló; no hay capturas, guardados ni pruebas en juego inventadas.

## Siguiente insumo necesario

PPSSPP 1.20.4 Linux x86_64 oficial: https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage

SHA-256: 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

Para Windows, descarga oficial: https://www.ppsspp.org/download/.

## Uso de la beta

Aplicar el EXE a la ISO inglesa v1.1.2 y seleccionar la carpeta ULJS00244 extraída del archivo DLC original (incluye PARAM.PBP). El ejecutable no instala el emulador. Copiar la carpeta ULJS00244 de la salida a PSP/GAME/ de la Memory Stick dedicada, tal como indica el Readme original. No mezclar con otra edición. Conservar copias de partidas y no usar savestates antiguos para certificar una versión nueva sin reinicio y carga normal.

El inventario de guardados está vacío porque no se obtuvo ningún archivo confirmado. La matriz tiene todos sus casos de ejecución bloqueados, y se debe ampliar con los eventos y rutas reales. No confundir las pruebas preliminares con el betatesting.

Los fuentes Go del cambio de empaquetado y el manifiesto están incluidos, sin los cinco deltas binarios ni archivos comerciales. El script audit_static.py registra la auditoría realizada; depende del entorno de laboratorio anterior (se incluye su módulo de lectura como referencia). No es un instalador ni un emulador.
''',encoding='utf8')
shutil.copyfile('/tmp/rc38/audit.py',Q/'audit_reference.py')
shutil.copyfile(Q/'QA_BETA01.json',M/'QA_RC041_REV6_BETA01.json')
with zipfile.ZipFile(M/'LaPucelle_RC041_REV6_BETA01_QA.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(Q.iterdir()):
  if f.is_file():z.write(f,'QA/'+f.name)
 for f in (P/'gui').glob('*.go'):z.write(f,'gui/'+f.name)
 z.write(P/'gui/patches/manifest.json','gui/patches/manifest.json');z.write(P/'gui/patches/informe.json','gui/patches/informe.json')
print('Preliminary tests',len(checks),'runtime matrix',len(areas),'files',len(list(Q.iterdir())))
