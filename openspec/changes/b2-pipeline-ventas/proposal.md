# Proposal

## Why

El proceso actual de Laura depende de tres horas de trabajo manual en Excel y de
una persona que descarga y pega los datos. La prueba asigna 25 puntos al
pipeline que debe reemplazarlo, con reglas de negocio, un modelo dimensional,
carga idempotente, delta incremental, reporte Excel y pruebas automatizadas.

## What Changes

- Se amplía el ETL en Python para leer y validar los CSV del core y el maestro
  de puntos, aplicando reglas de limpieza documentadas.
- Se implementa el modelo dimensional en SQLite y la carga idempotente por
  `id_transaccion`.
- Se implementa la carga incremental con `--delta`, reportando insertados,
  actualizados e ignorados.
- Se genera el reporte Excel de tres hojas (`Resumen`, `Comparativo`, `Calidad`)
  y el borrador `.eml` listo para enviar.
- Se agregan pruebas de limpieza, idempotencia y carga incremental, y se
  documentan los resultados del 27/10 antes y después del delta.
- Se conservan las utilidades de fechas y la normalización ya creadas y se
  conectan al pipeline completo.
- Opcional: exportación del hecho a Parquet particionado por fecha.

## Capabilities

### New Capabilities

- `ingesta-ventas`: lectura, validación, normalización, deduplicación y
  trazabilidad de descartes de los archivos del core.
- `almacen-ventas`: modelo dimensional, SCD2 del punto, idempotencia, delta y
  auditoría de cargas.
- `reporte-ventas`: Excel de tres hojas, comparativo, calidad, correo `.eml` y
  contadores de ejecución.

### Modified Capabilities

Ninguna: las capacidades se introducen en esta feat.

## Impact

- Código nuevo en `parte-2-b2-pipeline/etl/` (`lectura.py`, `negocio.py`, `carga.py`, `reporte.py`,
  `cli.py`, `__main__.py`) y ampliación de `limpieza.py` y `fechas.py`.
- Pruebas nuevas en `parte-2-b2-pipeline/tests/` para limpieza, carga y reporte.
- Esquema y datos en `db/`, reporte en `salida/`, logs en `logs/`.
- Dependencias: `pandas` y `openpyxl` (ya declaradas); no se agregan servicios
  externos.
- Consume los CSV de `datos/` sin modificarlos.
