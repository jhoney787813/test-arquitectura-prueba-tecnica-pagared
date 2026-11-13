# Spec Delta

## Purpose

Persistir las ventas limpias en un modelo dimensional idempotente que soporte
Power BI y la carga incremental sin duplicar información.

## ADDED Requirements

### Requirement: Modelo dimensional en estrella

El almacén SHALL exponer `fact_transacciones` con grano por `id_transaccion` y
las dimensiones `dim_fecha`, `dim_punto`, `dim_producto`, `dim_canal` y
`dim_estado`, relacionadas por claves sustitutas.

#### Scenario: Consulta de ventas por zona y producto

- **WHEN** se consulta el hecho unido a `dim_punto` y `dim_producto` para la
  fecha de corte
- **THEN** cada transacción aparece una sola vez y su zona corresponde a la
  vigente en la fecha de la venta

### Requirement: Carga idempotente por fecha

Cargar la misma fecha varias veces SHALL dejar los mismos totales, el mismo
número de filas y ningún duplicado por `id_transaccion`.

#### Scenario: Reejecución del mismo día

- **WHEN** el pipeline se ejecuta dos veces para `2026-10-27`
- **THEN** la segunda ejecución no incrementa el conteo ni la suma de ventas

### Requirement: Carga incremental con delta

El delta SHALL insertar los `id_transaccion` nuevos, actualizar los existentes
cuando su `fecha_actualizacion` sea mayor e ignorar los registros obsoletos, y
SHALL reportar cuántos insertó, actualizó e ignoró.

#### Scenario: Transacción nueva en el delta

- **WHEN** el delta trae un `id_transaccion` que no existe en el hecho
- **THEN** se inserta y el contador de insertados aumenta en uno

#### Scenario: Anulación tardía en el delta

- **WHEN** el delta trae un `id_transaccion` existente con
  `fecha_actualizacion` posterior y estado `ANULADA`
- **THEN** se actualiza el estado, se conserva una sola fila y el total de
  ventas disminuye

#### Scenario: Registro obsoleto en el delta

- **WHEN** el delta trae un `id_transaccion` con `fecha_actualizacion` anterior
  a la ya almacenada
- **THEN** se ignora, se conserva la versión más reciente y se incrementa el
  contador de ignorados

### Requirement: Dimensión de punto con historia

`dim_punto` SHALL conservar una versión por vigencia (`valido_desde`,
`valido_hasta`) y SHALL asignar a cada transacción la versión vigente en su
fecha de negocio.

#### Scenario: Punto que cambió de zona

- **WHEN** el código `00117` tiene una versión en Oriente desde 2017 y otra en
  Valle de Aburrá desde 2024-03-04
- **THEN** una venta de 2026 se asocia a Valle de Aburrá y una venta de 2019 a
  Oriente

#### Scenario: Punto sin zona en el maestro

- **WHEN** el punto `00133` no tiene zona
- **THEN** la venta se conserva y se reporta en la zona `SIN ZONA`

#### Scenario: Punto que no está en el maestro

- **WHEN** una venta pertenece al código `00199`
- **THEN** la venta se conserva y se reporta en `NO CATALOGADO`

### Requirement: Auditoría de cargas y descartes

El almacén SHALL registrar por ejecución la fecha de corte, el archivo, el modo,
los contadores de leídos, descartados, cargados, insertados, actualizados e
ignorados, el estado y las marcas de inicio y fin.

#### Scenario: Ejecución fallida

- **WHEN** el pipeline falla después de abrir la conexión
- **THEN** la carga queda en estado `FALLIDA` con el detalle del error y el
  proceso termina con código distinto de 0

### Requirement: Exactitud monetaria

Los valores SHALL almacenarse en pesos enteros y las sumas del almacén SHALL
coincidir exactamente con la suma en `Decimal` de las filas cargadas.

#### Scenario: Suma de control

- **WHEN** se comparan las ventas del día en la base con la suma calculada en
  Python
- **THEN** ambos totales son iguales, sin diferencias de centavos

### Requirement: Modelo listo para Power BI

El modelo SHALL incluir claves, relaciones e índices que permitan filtrar por
fecha, zona, producto y canal sin recorrer el hecho completo.

#### Scenario: Filtro por fecha y zona

- **WHEN** Power BI filtra por `2026-10-27` y una zona
- **THEN** la consulta usa los índices del hecho y devuelve solo las filas
  correspondientes
