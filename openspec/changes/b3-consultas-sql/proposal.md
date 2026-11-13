# Proposal

## Why

La prueba pide cuatro consultas sobre la base cargada: top 3 por zona, puntos
activos sin ventas, variación por zona y la optimización de una consulta de
producción que tarda 40 minutos sobre 80 millones de filas. Es la parte B3
(10 puntos) y valida que el modelo dimensional sirva para responder preguntas
de negocio, no solo para almacenar.

## What Changes

- Se crea `sql/consultas.sql` con una consulta comentada por pregunta.
- Se agrega el índice necesario sobre el hecho y se reescribe la consulta de
  producción con filtros SARGables.
- Se documentan los resultados de cada consulta para el `2026-10-27` con el
  delta aplicado.
- Se agregan pruebas que ejecutan las consultas sobre la base de prueba y
  verifican los resultados esperados.

## Capabilities

### New Capabilities

- `consultas-ventas`: consultas analíticas de ventas, variación diaria y
  optimización de la consulta de producción.

### Modified Capabilities

Ninguna.

## Impact

- `sql/consultas.sql`, índice en el esquema del hecho y nuevo script de
  consultas.
- Pruebas en `tests/` que usan una base temporal con el delta.
- Sección 4 del informe con los resultados.
- No cambia el modelo de datos ni la carga.
