# Compilación y validación

El código vigente está en `parcheador/`; los CSV aprobados, en `corpus/`. Trabaja desde la raíz de un clon completo. No necesitas el dossier local para compilar el parcheador.

## Compilar en Windows x64

Requisitos: Python 3.10+, Go y un compilador C++17. La entrega local se compiló con Python 3.15 y Go 1.27.4. GitHub Actions usa Python 3.11 y Go 1.23 para comprobar compatibilidad; los ejecutables de compiladores distintos pueden tener SHA-256 distintos.

Desde una consola de desarrollo de Visual Studio:

```powershell
cl /nologo /std:c++17 /EHsc /O2 /Fe:parcheador/app/scripts/nis_lzs_pack.exe parcheador/app/scripts/nis_lzs_pack.cpp
python parcheador/build_release.py --packer-exe parcheador/app/scripts/nis_lzs_pack.exe
```

La salida está en `parcheador/dist/`. El empaquetado incluye manifiesto, revisiones, datos de inserción, motor y compresor. Las marcas de tiempo y el orden del archivo de recursos están fijados; el binario final depende también de la versión y plataforma del compilador Go. Los pesos HY-MT2 no se incorporan.

## Comprobaciones sin el juego

```powershell
python scripts/validar.py
python -m unittest discover -s scripts -p 'test_*.py'
python -m unittest discover -s metodologia/tests -p 'test_*.py'
python -m unittest discover -s parcheador/app/tests -p 'test_*.py'
```

Ejecuta también cada carpeta `parcheador/investigacion/v*/tests` en un proceso independiente de unittest. Algunas pruebas históricas se omiten cuando faltan sus muestras comerciales externas; la omisión queda registrada y no cuenta como validación de esas muestras. Las pruebas artificiales comprueban cabeceras reales `4+8*N`, identificadores, referencias, reservas y reversibilidad.

Después de generar `resources.tar.gz`:

```powershell
Push-Location parcheador
go test -v main.go main_test.go
Pop-Location
```

## Comprobación con originales del usuario

Ejecuta el `.exe` con su interfaz, o usa `--worker --config config.json`. Configuración mínima, con rutas absolutas:

```json
{
  "iso": "D:/juegos/La_Pucelle_Ragnarok_v1.1.2.iso",
  "dlc": "D:/juegos/ULJS00244",
  "output": "D:/pruebas/salida_nueva",
  "log": "D:/pruebas/parcheador.log"
}
```

Es un programa gráfico: para esperar su final desde PowerShell, usa `Start-Process -Wait -PassThru`. Comprueba código 0, existencia de ISO y cuatro EDAT, hashes e informes. Para medir la inserción real:

```powershell
python scripts/auditar_entrega.py --entrega D:/pruebas/salida_nueva --iso-original D:/juegos/La_Pucelle_Ragnarok_v1.1.2.iso --dlc-original D:/juegos/ULJS00244
```

El auditor reconstruye los intervalos desde los originales y diarios, relee el resultado y clasifica las 26.258 unidades. Conserva los informes y después verifica en PPSSPP escenas, elecciones, NPC, tienda, capítulos, HUD y DLC. La compilación y las pruebas de formato por sí solas no certifican el juego completo.

## Publicación

Actualiza versión de Go/GUI/motor/empaquetado, ficha de cambios y cobertura; publica el `.exe`, SHA256SUMS, instrucciones y resumen de auditoría en Releases. Los recursos comerciales permanecen locales. Sigue la política de sustitución y archivo descrita en `ORGANIZACION_GITHUB.md`.
