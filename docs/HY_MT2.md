# HY-MT2 local y revisión editorial

Se preparó y utilizó **Hy-MT2-1.8B-Q8_0.gguf** con llama.cpp **b12359**, CPU Windows x64. El modelo 7B no está instalado ni fue utilizado; su ficha se conserva únicamente como referencia evaluada.

- Modelo oficial: https://huggingface.co/tencent/Hy-MT2-1.8B-GGUF
- Revisión: `a0c709d9fac510f2c807aa3af52872340dc37a4a`.
- SHA-256: `5c3fe0b1408a5ceb0143184ef247b11b579c525f4b02b060e6c851bb76fef1a4`.
- Tamaño: 1.908.528.192 bytes.
- Runtime: `llama-b12359-bin-win-cpu-x64.zip`, con SHA-256 registrado en `instalacion.json`.

Los pesos y el runtime se descargan desde sus proyectos oficiales y no forman parte del repositorio. Consulta sus respectivas licencias.

## Preparación

Desde `laboratorio/2026-11-integracion`, ejecuta `python descargar_hymt2_local.py`. Lee las fichas fijadas en `herramientas/hymt2/`, descarga los archivos y verifica tamaño y SHA-256 antes de extraerlos. Después inicia el servidor local:

```powershell
.\herramientas\hymt2\bin\llama-server.exe -m .\herramientas\hymt2\Hy-MT2-1.8B-Q8_0.gguf --host 127.0.0.1 --port 8766 -c 8192 -np 1 -t 8 --no-webui --jinja
```

El cliente `hymt2_traducir.py` añade contexto de escena y glosario del juego, y guarda parámetros, fuente, respuesta y procedencia. La cola publicada contiene 1.711 propuestas; el cliente omite las que ya tienen borrador.

## Aprobación e inserción

Hay 1.711 borradores generados y 500 cotejados editorialmente en cinco lotes. Los otros 1.211 siguen pendientes. Se corrigieron nombres que el modelo traducía literalmente, género, sentido de expresiones japonesas, opciones demasiado largas y puntuación.

Los borradores en `hymt2_borradores/` **no se insertan automáticamente**. El motor usa únicamente `parcheador/app/datos/segmentos_hymt2_aprobados.json`: 1.113 destinos físicos que combinan los 500 textos aprobados y reutilizaciones del corpus ya revisado. Cada destino conserva recurso, offset y bytes fuente para rechazar aplicaciones incompatibles.

Antes de aprobar nuevas tandas: leer original y contexto, comprobar glosario y controles, corregir el texto, validar longitud y glifos, generar el overlay y comprobarlo en la entrega real. Una respuesta del modelo no equivale a una revisión.
