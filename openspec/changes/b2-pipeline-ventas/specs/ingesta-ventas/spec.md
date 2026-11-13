# Spec Delta

## Purpose

Leer los archivos del core y el maestro de puntos, normalizar sus formatos
heterogéneos y aplicar las reglas de negocio antes de persistir las ventas.

## ADDED Requirements

### Requirement: Lectura de archivos con la codificación del proveedor

El pipeline SHALL leer transacciones y delta como UTF-8 con BOM y el maestro de
puntos como Latin-1, usando `;` como separador, y SHALL fallar con un mensaje
accionable si falta un archivo o una columna obligatoria.

#### Scenario: Lectura de los archivos del kit

- **WHEN** se ejecuta el pipeline con los tres CSV entregados en `datos/`
- **THEN** lee 5.965 filas de transacciones, 2.111 del delta y 42 puntos sin
  perder acentos ni ceros a la izquierda

#### Scenario: Archivo de transacciones faltante

- **WHEN** no existe `datos/transacciones.csv`
- **THEN** el proceso termina con código distinto de 0 y un mensaje que indica
  el archivo faltante, sin iniciar la carga

### Requirement: Fechas en UTC y día contable en Colombia

El pipeline SHALL interpretar las fechas en UTC en sus tres formatos (ISO-8601
con `Z`, `YYYY-MM-DD HH:MM:SS` y `DD/MM/YYYY HH:MM`) y SHALL asignar el día
contable en `America/Bogota`.

#### Scenario: Medianoche UTC que pertenece al día anterior en Colombia

- **WHEN** una transacción tiene `fecha_transaccion` igual a
  `2026-10-28T03:00:00Z`
- **THEN** su día contable es `2026-10-27` y se incluye en el reporte de esa
  fecha

#### Scenario: Fecha con formato desconocido

- **WHEN** una fila trae `27-10-2026 13:45`
- **THEN** la fila se descarta con motivo `fecha_invalida` y queda registrada en
  la auditoría

### Requirement: Normalización de estados, productos y canales

El pipeline SHALL normalizar estados, productos y canales eliminando espacios
extremos y aplicando mayúsculas, y SHALL descartar los valores fuera del
catálogo con su motivo.

#### Scenario: Variantes de estado del archivo

- **WHEN** una fila trae `' aprobada '`, `'Aprobada'` o `'ANULADA '`
- **THEN** el estado normalizado es `APROBADA` o `ANULADA` según corresponda

#### Scenario: Estado desconocido

- **WHEN** una fila trae un estado `PENDIENTE`
- **THEN** la fila se descarta con motivo `estado_invalido` y no suma ventas

### Requirement: Normalización del código de punto

El pipeline SHALL normalizar el código de punto a cinco dígitos con ceros a la
izquierda y SHALL descartar los códigos vacíos o no numéricos.

#### Scenario: Código sin ceros a la izquierda

- **WHEN** el archivo trae el código `131`
- **THEN** el código normalizado es `00131` y cruza con el maestro

#### Scenario: Código vacío

- **WHEN** una fila no trae `cod_punto`
- **THEN** la fila se descarta con motivo `cod_punto_invalido`

### Requirement: Exclusión del punto de pruebas

El pipeline SHALL excluir de las ventas y del reporte el punto de pruebas
`90001` y SHALL registrar la exclusión en la hoja de calidad.

#### Scenario: Venta del punto de pruebas

- **WHEN** una transacción aprobada pertenece al punto `90001`
- **THEN** no suma en los totales y aparece reportada como excluida por
  `punto_pruebas`

### Requirement: Interpretación de valores monetarios

El pipeline SHALL interpretar los valores en COP con punto decimal o de miles,
convertirlos a `Decimal` y descartar los no interpretables o no positivos.

#### Scenario: Valor con punto de miles

- **WHEN** el archivo trae el valor `522.500`
- **THEN** el monto es 522.500 pesos y no 522,50

#### Scenario: Valor no interpretable

- **WHEN** una fila trae `valor` vacío o `N/A`
- **THEN** la fila se descarta con motivo `valor_invalido`

### Requirement: Deduplicación y versión vigente por transacción

El pipeline SHALL eliminar las filas idénticas y SHALL conservar, para cada
`id_transaccion`, la versión con `fecha_actualizacion` más reciente.

#### Scenario: Transacción duplicada con cambio de estado

- **WHEN** un `id_transaccion` aparece aprobado a las 13:01 y anulado a las
  22:25
- **THEN** la versión vigente es la anulada y no cuenta como venta

#### Scenario: Filas idénticas

- **WHEN** el archivo repite exactamente la misma fila dos veces
- **THEN** se procesa una sola vez y la otra se reporta como duplicada

### Requirement: Trazabilidad de los descartes

El pipeline SHALL registrar cada fila descartada con archivo, número de fila,
`id_transaccion`, motivo y detalle, sin exponer datos sensibles.

#### Scenario: Fila descartada por valor inválido

- **WHEN** una fila no tiene valor interpretable
- **THEN** queda un registro en `etl_descartes` y el contador de descartes del
  motivo se incrementa
