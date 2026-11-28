# La Pucelle: Ragnarok ES — RC041 REV6 BETA02 Compacta

Reempaquetado sin pérdidas de BETA02 (ULJS00244, base inglesa 1.1.2). No modifica el contenido del juego: la ISO y los cuatro EDAT reproducidos coinciden con los SHA-256 de BETA02. PARAM.PBP se copia del original y se comprueba. El EXE nativo Windows x64 es autónomo; Python y C++ solo se necesitan para regenerar los deltas durante el desarrollo, no para aplicar el parche.

| Ejecutable | Bytes | SHA-256 |
|---|---:|---|
| BETA02 anterior | 38662656 | `9a7e43ab782d3c1d3469c0b7b36e4f0d865b7f097acc1b31b176bb6c3aa38a0d` |
| BETA02 Compacta | 21823488 | `1ae3f63efe3871bd923ab263eaf6becf248307a9ecf070fe31d8a8cdf5b2ca44` |

Reducción: 43,5541 %. El algoritmo LPCOPY01 alterna referencias a bloques del original y literales; el flujo se comprime con gzip. El motor comprueba SHA-256 de origen y destino, límites, longitud total y CRC. La salida se prepara en una carpeta temporal y no sobreescribe originales ni destinos existentes.

## Reproducción local desde fuentes

En Linux con Go, G++ y Python 3.11 o superior, utilizar una carpeta `ORIG` con la ISO inglesa `La_Pucelle_Ragnarok_v1.1.2.iso` y los cuatro EDAT originales, y una carpeta `TARGET` con la ISO BETA02 y los EDAT en `ULJS00244/`, ya reconstruidos por BETA02. El manifiesto exige los hashes exactos de ambas entradas; no acepta revisiones distintas.

```sh
g++ -O3 -std=c++17 makedelta.cpp -o /tmp/lp-makedelta
python3 build_deltas.py /ruta/ORIG /ruta/TARGET gui/patches /tmp/lp-makedelta
cd gui
GO111MODULE=off CGO_ENABLED=0 go test -v ./...
GO111MODULE=off CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go vet ./...
GO111MODULE=off CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags='-s -w -H=windowsgui' -o ../LaPucelle_Parcheador_RC041_REV6_BETA02_Compacta.exe .
```

La ruta y versión del compilador pueden producir diferencias en el binario. Los hashes de las cinco salidas son obligatorios en cualquier compilación. Los deltas privados `*.copy.gz` no se incluyen en este árbol; sin regenerarlos el ejecutable no puede aplicar el parche. No publicar ISO, EDAT, PARAM.PBP ni texturas originales. El directorio `historico_beta02/` conserva fuentes de laboratorio y documentación BETA02; sus scripts pueden requerir rutas y datos privados.

## Estado de QA

10 casos unitarios superados, `go vet` para Windows superado, 5/5 reconstrucciones con el motor Linux y 5/5 flujos incrustados en el EXE Windows cotejados. La GUI Windows todavía no se ha ejecutado. No se repitió PPSSPP por este cambio de empaquetado; BETA02 tenía evidencia de arranque y dos frases de introducción, no certificación integral. No recupera correcciones históricas ausentes en la base. Ver `QA/QA_RC041_REV6_BETA02_Compacta.json`.
