# Spec Delta

## Purpose

Permitir a la Gerente Comercial analizar las ventas diarias por zona, producto
y canal en un tablero de Power BI conectado al modelo cargado.

## ADDED Requirements

### Requirement: Indicadores del día seleccionado

El tablero SHALL mostrar para la fecha seleccionada las ventas totales, el
número de transacciones y el ticket promedio, calculados con las reglas de
venta del negocio.

#### Scenario: Selección del 27 de octubre

- **WHEN** Laura selecciona `2026-10-27`
- **THEN** las tarjetas muestran las ventas del día sin anuladas, sin rechazadas
  y sin el punto de pruebas

### Requirement: Comparación por zona y producto

El tablero SHALL incluir visuales que comparen las ventas por zona y por
producto para la fecha seleccionada.

#### Scenario: Comparación entre zonas

- **WHEN** se selecciona una fecha con ventas en varias zonas
- **THEN** el visual permite ordenar las zonas por ventas y compararlas en la
  misma escala

### Requirement: Variación contra el día anterior

El tablero SHALL mostrar la variación de ventas contra el día anterior por
zona, sin errores de división cuando una zona no tuvo ventas el día previo.

#### Scenario: Zona nueva

- **WHEN** una zona tiene ventas el 27 pero no el 26
- **THEN** la variación se muestra vacía o como `N/A`, sin un error de DAX

### Requirement: Filtros de fecha, zona y canal

El tablero SHALL permitir filtrar todos los visuales por fecha, zona y canal
desde segmentaciones de datos.

#### Scenario: Filtro combinado

- **WHEN** se selecciona una zona y el canal `APP`
- **THEN** las tarjetas y los visuales se recalculan solo con esa combinación

### Requirement: Medidas DAX explícitas

El tablero SHALL implementar ventas, transacciones, ticket promedio y variación
con medidas DAX documentadas, y no con cálculos implícitos del visual.

#### Scenario: Reutilización de medidas

- **WHEN** se agrega un visual nuevo
- **THEN** puede usar las medidas existentes y el resultado coincide con el
  Resumen del reporte Excel
