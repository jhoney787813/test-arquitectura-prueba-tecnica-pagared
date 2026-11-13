# Spec Delta

## Purpose

Generar el reporte diario de ventas por zona y producto, con comparativo,
hoja de calidad y correo listo para enviar a la Gerente Comercial.

## ADDED Requirements

### Requirement: Archivo Excel con tres hojas

El pipeline SHALL generar `salida/reporte_ventas_YYYYMMDD.xlsx` con las hojas
`Resumen`, `Comparativo` y `Calidad`, usando la fecha de corte en el nombre.

#### Scenario: Reporte del 27 de octubre

- **WHEN** se ejecuta con `--fecha-corte 2026-10-27`
- **THEN** se crea `reporte_ventas_20261027.xlsx` con las tres hojas y sin hojas
  vacías

### Requirement: Resumen por zona y producto

La hoja `Resumen` SHALL mostrar, para la fecha de corte, las ventas y el número
de transacciones por cada combinación de zona y producto, contando solo
`APROBADA` y `REVERSADA` y excluyendo el punto `90001`.

#### Scenario: Total del día

- **WHEN** se suma la columna de ventas del Resumen
- **THEN** el total coincide con el de la base para la fecha y no incluye
  anuladas, rechazadas ni el punto de pruebas

### Requirement: Comparativo contra el día anterior

La hoja `Comparativo` SHALL mostrar por zona las ventas del día, las del día
anterior y la variación absoluta y porcentual, sin dividir por cero cuando la
zona no tuvo ventas el día anterior.

#### Scenario: Zona nueva sin ventas previas

- **WHEN** una zona solo tiene ventas en la fecha de corte
- **THEN** la variación se reporta como `N/A` o vacía, sin error de división y
  sin inventar un porcentaje

### Requirement: Hoja de calidad

La hoja `Calidad` SHALL listar los registros descartados y corregidos con su
motivo, archivo, fila, identificador y detalle, y SHALL incluir los totales por
motivo.

#### Scenario: Descartados por motivo

- **WHEN** el archivo trae filas con valor, estado o código inválidos
- **THEN** cada una aparece en `Calidad` con su motivo y el total del motivo
  coincide con el log del pipeline

### Requirement: Parámetro de fecha de corte

El pipeline SHALL aceptar `--fecha-corte YYYY-MM-DD` y, si se omite, SHALL usar
el día anterior en `America/Bogota`.

#### Scenario: Fecha de corte inválida

- **WHEN** se pasa `--fecha-corte 2026-13-01`
- **THEN** el proceso termina con código distinto de 0 y no genera un reporte
  incompleto

### Requirement: Correo listo para envío

El pipeline SHALL generar un borrador `.eml` con asunto, destinatario
configurable y el Excel adjunto, sin requerir un servidor SMTP corporativo.

#### Scenario: Borrador sin SMTP

- **WHEN** se ejecuta el pipeline en un entorno sin SMTP
- **THEN** se crea un `.eml` válido con el reporte adjunto y el proceso termina
  correctamente

### Requirement: Log de contadores y código de salida

Cada ejecución SHALL registrar cuántos registros se leyeron, descartaron por
motivo y cargaron, y en el delta cuántos se insertaron, actualizaron e
ignoraron; ante cualquier falla SHALL terminar con código distinto de 0.

#### Scenario: Falla durante la carga

- **WHEN** la base de datos rechaza una escritura
- **THEN** el log contiene el error, no se reporta éxito y el código de salida
  es distinto de 0
