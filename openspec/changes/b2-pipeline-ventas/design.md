# Design

## Context

Ver `proposal.md` para la motivación. El repositorio ya tiene la configuración,
el parseo de fechas UTC, la conversión a `America/Bogota` y las funciones base
de limpieza con 48 pruebas. Falta el pipeline que las conecta, el modelo
dimensional, el delta, el reporte y la auditoría.

Los datos del kit tienen problemas deliberados: 24 variantes de estado, 890
códigos sin ceros, 140 filas duplicadas, tres formatos de fecha, 6 valores
inválidos y un delta que modifica transacciones ya cargadas. Las reglas de
limpieza están en `specs/ingesta-ventas/spec.md`.

## Goals / Non-Goals

**Goals:**

- Un comando (`python -m etl`) que ejecute el pipeline completo y permita
  repetirlo sin duplicar datos.
- Un modelo en estrella entendible y consultable desde SQL.
- Un reporte Excel que Laura pueda abrir y un `.eml` listo para enviar.
- Pruebas que cubran las reglas de limpieza y los tres escenarios del delta.

**Non-Goals:**

- Enviar correos reales o programar el job (eso es B5).
- Construir el tablero (B6).
- Reescribir el job de recaudos del incidente (B5.1).

## Decisions

### 1. SQLite con SQL portable

Se usa `sqlite3` de la biblioteca estándar para que la sustentación no dependa
de Docker ni de un servidor. La ruta se configura con `--db` o
`PAGARED_DB_PATH`; el esquema usa tipos compatibles con PostgreSQL/SQL Server y
`ON CONFLICT` para el upsert. Alternativa descartada: PostgreSQL en Docker,
porque agrega credenciales y un servicio que no aportan al objetivo.

### 2. Día contable en America/Bogota

Las fechas se interpretan como UTC y se convierten con `zoneinfo` antes de
asignar la fecha de negocio. El hecho guarda la hora UTC y la local. Sin esto se
perderían 652 transacciones del 27/10 que en UTC figuran como 28/10.

### 3. Capas y CLI delgado

`lectura` (CSV y encodings), `limpieza` (normalización), `negocio` (reglas),
`carga` (esquema y upsert), `reporte` (Excel y `.eml`) y `cli` (argumentos,
logging y códigos de salida). El CLI orquesta y no contiene reglas de negocio.

### 4. Modelo dimensional con SCD2 en el punto

Hecho por `id_transaccion`; dimensiones de fecha, punto, producto, canal y
estado. `dim_punto` guarda `valido_desde`/`valido_hasta` para asignar la zona
vigente a la fecha de la venta. El punto `00117` se interpreta como traslado:
Oriente hasta 2024-03-03 y Valle de Aburrá desde 2024-03-04.

### 5. Idempotencia y delta

`fact_transacciones.id_transaccion` es llave primaria. La carga normal inserta
o actualiza según la clave; el delta actualiza solo si
`fecha_actualizacion` es mayor. `etl_cargas` registra contadores y estado;
`etl_descartes` registra cada fila rechazada con archivo, fila, id, motivo y
detalle.

- Alternativa descartada: `DELETE` + `INSERT` por fecha, porque una anulación
  tardía de un día anterior no se corregiría.
- Alternativa descartada: append-only, porque duplica en cada reintento.

### 6. Dinero exacto

`Decimal` en la limpieza y pesos enteros (`INTEGER`) en la base. Las sumas del
reporte se hacen sobre enteros y se comparan con la suma Decimal de origen. No
se usa `float` para dinero.

### 7. Reglas de limpieza

- `522.500` es 522.500 pesos; `10000.00` es 10.000.
- Estados a mayúsculas y sin espacios; desconocidos se descartan.
- Códigos de 3 dígitos se rellenan a 5; vacíos se descartan.
- `90001` se excluye; `00199` va a `NO CATALOGADO`; `00133` a `SIN ZONA`.
- Filas idénticas se deduplican; gana la `fecha_actualizacion` más reciente.

### 8. Reporte y correo

`openpyxl` genera las tres hojas con encabezados, formato y totales. El correo
se arma con `EmailMessage` y se guarda como `.eml`; el envío real queda detrás
de una función que solo se activa con configuración SMTP.

### 9. Pruebas

Unitarias para fechas, estados, códigos y valores; integración con SQLite en
`tmp_path` para carga repetida, delta y totales. Las pruebas no tocan `db/` ni
dependen del orden de ejecución.

## Risks / Trade-offs

- **Zona horaria mal interpretada** → pruebas de medianoche UTC y comparación de
  conteos por día.
- **Maestro duplicado (`00117`)** → SCD2 y supuesto documentado; si el negocio
  confirma que son puntos distintos, se separa el código y se recarga.
- **Delta con filas fuera de ventana** → se aceptan por `fecha_actualizacion` y
  se reportan, sin confiar en el nombre del archivo.
- **SQLite y concurrencia** → un solo escritor; en producción se recomienda
  PostgreSQL y `disableConcurrentBuilds()`.
- **Reporte grande** → las tres hojas se generan en streaming por filas; el
  volumen del kit es pequeño y el diseño escala por fecha.

## Migration Plan

No hay sistema anterior. Se ejecuta el pipeline en local, se valida el reporte
y la base, y luego se empaqueta en Docker (B5). Rollback: si falla una carga no
se publica el reporte y se reejecuta la fecha, que es idempotente.

## Open Questions

- Confirmación de Laura sobre el valor de las reversadas (se asume el valor
  completo).
- Confirmación sobre `00117` (traslado o dos puntos distintos).
