# Spec Delta

## Purpose

Responder preguntas de negocio sobre las ventas mediante consultas SQL
reproducibles, correctas y eficientes sobre el modelo cargado.

## ADDED Requirements

### Requirement: Top 3 de puntos por zona

La consulta SHALL devolver los tres puntos con más ventas de cada zona para la
fecha de corte, ordenados de mayor a menor y con un desempate determinista por
código de punto.

#### Scenario: Zona con más de tres puntos

- **WHEN** se ejecuta para `2026-10-27` en una zona con diez puntos con ventas
- **THEN** devuelve como máximo tres filas por zona y el total de cada fila
  coincide con las ventas de ese punto

### Requirement: Puntos activos sin ventas

La consulta SHALL listar los puntos activos del maestro que no registraron
ventas válidas en la fecha de corte.

#### Scenario: Punto activo sin transacciones

- **WHEN** un punto está activo y no tiene ventas el `2026-10-27`
- **THEN** aparece en el resultado con ventas en cero

#### Scenario: Punto inactivo

- **WHEN** un punto está inactivo y no tiene ventas
- **THEN** no aparece en el resultado

### Requirement: Variación de ventas por zona

La consulta SHALL devolver por zona las ventas de la fecha de corte, las del
día anterior y la variación porcentual, sin error cuando el día anterior no
tuvo ventas.

#### Scenario: Zona sin ventas el día anterior

- **WHEN** una zona no tiene ventas el `2026-10-26`
- **THEN** la variación se devuelve como nula o `N/A`, sin división por cero

### Requirement: Consulta de producción optimizada

La consulta de producción SHALL filtrar por un rango de fechas y por estado sin
aplicar funciones a las columnas indexadas, y SHALL usar un índice que evite
recorrer las 80 millones de filas.

#### Scenario: Filtro por fecha con índice

- **WHEN** se ejecuta la consulta optimizada para el `2026-10-27`
- **THEN** devuelve las mismas filas que la consulta original y el plan usa el
  índice de `fecha_transaccion` en lugar de un escaneo completo

### Requirement: Consultas documentadas y reproducibles

El repositorio SHALL incluir `sql/consultas.sql` con una consulta comentada por
pregunta y SHALL documentar en el informe el resultado obtenido sobre la base
con el delta aplicado.

#### Scenario: Reproducción de resultados

- **WHEN** se ejecutan las consultas sobre una base recién cargada con el delta
- **THEN** los resultados coinciden con los documentados en el informe
