# ROM-008 — Auditoría de alcance ISO base, 24/11/2026

Base: `cf95f14e8ef21b66d9fe83bd33d743107e6a71b3`. No cambia la métrica histórica 21.805/26.258 (83,04 %).

## Implementación
- `scripts/auditar_entrega.py` permite auditar una entrega ISO base sin originales EDAT, exige los cuatro originales y los cuatro destinos cuando se incluye DLC y rechaza omitir DLC existentes.
- Conserva el denominador global del manifiesto y distingue `DLC_NO_APORTADO` y el porcentaje dentro del alcance. No certifica inserciones por ausencia de datos.
- Une las revisiones centrales con las distribuidas mediante el mismo validador que utiliza el motor; registra hashes de fuentes. Un campo sin estado revisado no se declara coincidencia editorial. Talk sin diario no se interpreta como campo fijo.
- Se añadieron siete pruebas sintéticas y se conectaron al workflow de seguimiento. Consultar Actions para verificar su ejecución; no se declara CI verde sin evidencia.

## Pruebas ejecutadas localmente con el original aportado (A/B)
- ISO SHA-256: `4360707b251a0f7776a222512926f1f58fb47bda0060b667168de8a1e122e9f5`, 858937344 bytes.
- Inventario ISO9660: 23 archivos; registros de tamaño y LBA dual endian correctos, intervalos no superpuestos. PVD 380120 sectores, tamaño físico 419403; no modificado.
- START_JP.LZS descomprimido sin solapamientos: 11706208 bytes, 696038 referencias, 36 miembros DAT; SHA-256 raw `044056f5a80071dd6890f08c4adf6a4ec49e81637a4df09890df9f3a801ddfc5`.
- SCRIPTPACK: 32 miembros; BGPACK: 285, índices no solapados.
- Compresor C++ del HEAD (blob Git `9499dfca65b39f4e6face56f08ae562f7af420b9`) compilado con g++ -O2 -std=c++17. Dos recompresiones del START original: 5037425 bytes, 890712 referencias sin solapamiento, idénticas entre sí. SHA-256 comprimido `91ce4ea4984a82f4b55ac9f1a85df1987d017249247fb7e51e38de4d78f8f2a6`; descompresión idéntica byte a byte al original raw.
- Sin modificación de ISO ni distribución de binarios comerciales.

## Límites y siguiente acción
El entorno local no resuelve github.com; el acceso GitHub se realizó mediante conector de texto. El ZIP editorial adjunto no es checkout vigente: el blob del manifiesto local es `58adab40237467ea49827321421b2faafb9008a7`, frente a `9563007adf8bd030b7ec04714e687525b7f81e0d` del HEAD. No se construyó con datos obsoletos. No se aportaron EDAT ni PPSSPP está instalado.

En un checkout completo de esta rama, generar una ISO base:
```sh
python parcheador/app/scripts/integracion_total.py --iso ORIGINAL.iso --repo-directorio . --salida SALIDA_PRIVADA
python scripts/auditar_entrega.py --entrega SALIDA_PRIVADA --iso-original ORIGINAL.iso
```
Antes de generar la ISO, compilar el compresor en la ruta y con el nombre que exige `construir_parche.cpack`. No omitir comprobaciones de glifos, anclas, EBOOT o reservas. Repetir con EDAT cuando estén disponibles; contrastar diarios e inventario y ejecutar PPSSPP. No aumentar numerador sin cotejo de bytes de la candidata. Las propuestas HY-MT2 pendientes quedan excluidas.
