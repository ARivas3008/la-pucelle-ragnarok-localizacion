# Activación (pasos que debe realizar el propietario)

**GitHub**
1. **Repositorio YA CREADO**, https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion. Se comprobó que estaba vacío, **público** y NO autorizado para escritura por la integración. En GitHub > Settings > General > Danger Zone, pasar a **privado** antes de añadir textos comerciales. Luego ir a https://github.com/settings/installations/179480748 > Configure y conceder acceso a `la-pucelle-ragnarok-localizacion`.
2. **Método recomendado: usar el archivo `.bundle`**, que contiene el repositorio Git con su historial inicial:
   ```bash
   git clone LaPucelle_Repositorio_15_Corpus.bundle LaPucelleRagnarok
   cd LaPucelleRagnarok
   git remote set-url origin https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion.git
   git push -u origin main
   ```
   Si se utiliza únicamente el ZIP, se debe descomprimir, entrar en la carpeta y crear el repositorio Git local antes de añadir el remoto:
   ```bash
   git init -b main
   git add .
   git commit -m "Organizar 15 corpus para revisión"
   git remote add origin https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion.git
   git push -u origin main
   ```
3. Comprobar que `README.md`, `AGENTS.md`, `corpus/01/entrada.csv` hasta `corpus/15/entrada.csv` aparecen en GitHub.
4. Configurar protección de `main` mediante PR + CI. No compartir el repositorio públicamente por incluir diálogos con copyright.

**ChatGPT**
1. **Proyecto ChatGPT YA CREADO**: https://chatgpt.com/g/g-p-6af8a33cbd3c81919d859f02cbc7122c-la-pucelle-localizacin-es/project
2. Abrir las instrucciones del Proyecto y pegar `CHATGPT_PROJECT_INSTRUCCIONES.md`. El enlace real de GitHub ya está incluido.
3. Conectar GitHub si ChatGPT lo solicita (con permisos de lectura/escritura al repositorio); la instalación y permisos requieren acción del usuario.
4. Abrir 15 chats distintos en ese Proyecto, uno con el mensaje `1`, otro `2`, ..., `15`.
5. Cada chat trabaja exclusivamente en la carpeta indicada; las revisiones se guardan por ramas y PR.
6. Una vez fusionados los 15 PR, solicitar al chat coordinador que ejecute el QA final, el Excel y la preparación de inserción.

**Limitaciones importantes**
El paquete prepara todo, pero crear un Proyecto de ChatGPT y un repositorio GitHub nuevo puede requerir interacción del propietario. Tampoco los chats pueden continuar trabajando autónomamente si el usuario deja de enviar mensajes o habilita otra modalidad de ejecución.
