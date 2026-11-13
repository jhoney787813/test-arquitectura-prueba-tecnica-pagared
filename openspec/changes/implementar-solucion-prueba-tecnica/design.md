# Design

## Context

El repositorio parte con la estructura base, los CSV del kit copiados sin
modificar y utilidades de fechas y limpieza ya probadas (48 pruebas). Los datos
tienen problemas deliberados: el core viene en UTF-8 con BOM, el maestro en
Latin-1, las fechas usan tres formatos, los estados tienen 24 variantes, hay
140 filas duplicadas, códigos de punto sin ceros y un delta que modifica
transacciones ya cargadas.

La ejecución de la prueba es en macOS, sin Power BI Desktop ni SMTP corporativo.
La fecha de corte es `2026-10-27` y el día contable del negocio es
`America/Bogota`, aunque el core exporte en UTC. El detalle de la motivación y
el alcance está en `proposal.md`; el comportamiento exigido, en `specs/`.

## Goals / Non-Goals

**Goals:**

- Un pipeline ejecutable de punta a punta con un solo comando, idempotente y
  con salida distinta de 0 ante cualquier falla.
- Un modelo dimensional en SQLite que se pueda inspeccionar con SQL estándar y
  conectar a Power BI mediante exportación o un driver ODBC.
- Reporte Excel de tres hojas y borrador `.eml` reproducibles para la fecha de
  corte, antes y después del delta.
- Pruebas automatizadas sobre limpieza, carga repetida y carga incremental.
- Decisiones de operación documentadas: Docker, Jenkins/AWS, alertas,
  credenciales y Azure SQL.

**Non-Goals:**

- Enviar correos reales: no hay SMTP disponible; se genera el `.eml`.
- Generar un `.pbix` validado sin Power BI Desktop: se entrega el diseño, las
  medidas DAX y los datos exportados.
- Implementar el pipeline de recaudos del incidente B5.1: se analiza y se
  proponen las correcciones, no se reescribe ese job en producción.
- Dar soporte multi-tenant, alta concurrencia o streaming en tiempo real.

## Decisions

### 1. SQLite como motor por defecto y SQL portable

Se usa `sqlite3` de la biblioteca estándar para que la sustentación funcione sin
infraestructura. El esquema se escribe con tipos y sintaxis compatibles con
PostgreSQL/SQL Server en lo posible (`NUMERIC`, `DATE`, `ON CONFLICT`), y la ruta
se puede cambiar con `--db` o `PAGARED_DB_PATH`.

- Alternativa descartada: PostgreSQL en Docker, porque agrega un servicio y
  credenciales que no aportan al objetivo de la prueba.
- Alternativa descartada: solo CSV/Parquet, porque B2 exige una base relacional
  y B3 consultas SQL.

### 2. Conversión UTC → America/Bogota antes de asignar el día

Todas las fechas se interpretan como UTC y se convierten con `zoneinfo` antes de
calcular la fecha de negocio. El hecho guarda `fecha_hora_utc` y
`fecha_hora_local` para trazabilidad. Esto evita perder 652 transacciones del
27/10 que en UTC aparecen con fecha 28/10.

- Alternativa descartada: usar el día UTC, porque no representa el “día de 12 de
  la noche a 12 de la noche” que pidió Laura.
- Alternativa descartada: restar 5 horas a mano, porque no es explícito ni
  portable a otras zonas.

### 3. Pipeline por capas y CLI delgado

Módulos: `lectura` (CSV y encodings), `limpieza` (normalización),
`negocio` (reglas), `carga` (modelo y upsert), `reporte` (Excel y `.eml`) y
`cli` (argumentos, logging, códigos de salida). `python -m etl` orquesta las
capas. Cada capa recibe y devuelve DataFrames/tablas, sin efectos globales.

- Alternativa descartada: un único script monolítico, difícil de probar y
  explicar en la sustentación.
- Alternativa descartada: un framework de orquestación (Airflow/Prefect), que
  excede el alcance y complica el despliegue.

### 4. Modelo dimensional con SCD2 en el punto

Hecho por `id_transaccion`; dimensiones `dim_fecha`, `dim_punto`,
`dim_producto`, `dim_canal` y `dim_estado`. `dim_punto` conserva versiones con
`valido_desde`/`valido_hasta`, de modo que la zona asignada sea la vigente en la
fecha de la venta. El punto `00117` se interpreta como traslado (Oriente hasta
2024-03-03, Valle de Aburrá desde 2024-03-04).

- Alternativa descartada: guardar la zona directamente en el hecho, porque
  congela el dato y no explica los cambios del maestro.
- Alternativa descartada: quedarse con la última versión del maestro, porque
  reescribe la historia (caso A9).

### 5. Idempotencia por clave natural y control de cargas

`fact_transacciones.id_transaccion` es llave primaria. La carga usa
`INSERT ... ON CONFLICT DO UPDATE`; el delta actualiza solo si
`fecha_actualizacion` es mayor. `etl_cargas` registra cada ejecución y
`etl_descartes` cada fila rechazada con su motivo.

- Alternativa descartada: `DELETE` + `INSERT` por fecha, porque una anulación
  tardía de un día anterior no se corregiría y el delta quedaría incompleto.
- Alternativa descartada: append-only sin llave, porque duplica en cada
  reintento (pregunta A6).

### 6. Dinero con `Decimal` y pesos enteros

La limpieza convierte los valores con `Decimal`; la base guarda pesos enteros
(`INTEGER`). Las sumas del reporte se hacen sobre enteros y se comparan con la
suma Decimal de origen. Nunca se usa `float` para dinero.

- Alternativa descartada: `REAL`/`float`, por el error de redondeo de la
  pregunta A3.
- Alternativa descartada: guardar centavos, porque los datos no traen centavos
  distintos de `.00` y el peso es la unidad de negocio.

### 7. Reglas de limpieza explícitas

- `522.500` se interpreta como 522.500 pesos (punto de miles) y `10000.00` como
  10.000 con dos decimales.
- Los estados se normalizan a mayúsculas y sin espacios; los desconocidos se
  descartan con motivo.
- Los códigos de 3 dígitos se rellenan a 5; los vacíos o no numéricos se
  descartan.
- El punto `90001` se excluye de los totales y se reporta en Calidad.
- `00199` se conserva como `NO CATALOGADO` y `00133` como `SIN ZONA`.
- Las filas idénticas se deduplican; para un mismo id gana la
  `fecha_actualizacion` más reciente.

### 8. Reporte Excel y correo sin SMTP

`openpyxl` genera las hojas Resumen, Comparativo y Calidad con formato y anchos
legibles. El correo se arma con `email.message.EmailMessage` y se guarda como
`.eml`; el envío real queda detrás de una función que solo se activa si existen
las variables SMTP.

- Alternativa descartada: `pandas.ExcelWriter` solo, porque no permite controlar
  formato, títulos ni la hoja de calidad con el detalle requerido.

### 9. Pruebas con SQLite temporal

Las pruebas de integración crean una base en `tmp_path`, cargan un subconjunto
de filas y verifican: normalización, idempotencia (dos cargas), delta
(inserción, actualización e ignorado) y totales. Las pruebas unitarias cubren
fechas, estados, códigos y valores.

- Alternativa descartada: probar contra la base real del repositorio, porque
  contamina el estado y hace que las pruebas dependan del orden.

### 10. Operación y Power BI

Docker con usuario no root, volúmenes para `datos/`, `salida/` y `db/`. Jenkins
con `TZ=America/Bogota`, `disableConcurrentBuilds()`, `timeout` y alerta en
`post { failure }`. En AWS, EventBridge + ECS Fargate/Batch con secretos en
Secrets Manager. Power BI se documenta con DAX y exportación CSV/Parquet; RLS
por zona queda como diseño opcional.

## Risks / Trade-offs

- **Zona horaria mal interpretada** → pruebas explícitas de medianoche UTC y
  comparación de conteos por día; el informe muestra la diferencia UTC vs COT.
- **Maestro con `00117` duplicado** → SCD2 y supuesto documentado; si el
  negocio confirma que son dos puntos distintos, se separa el código en el
  maestro y se reejecuta la carga.
- **Delta con registros fuera de su ventana** → se aceptan por
  `fecha_actualizacion` y se reportan como insertados/actualizados, sin confiar
  en el nombre del archivo.
- **Sin SMTP real** → `.eml` validable y función de envío aislada; el informe
  explica cómo se activaría en Jenkins.
- **Sin Power BI Desktop** → se entrega diseño y DAX; se documenta la
  limitación y se exportan los datos para reconstruirlo en Windows.
- **SQLite y concurrencia** → un solo escritor a la vez; el job usa
  `disableConcurrentBuilds()` y, en producción, se recomienda PostgreSQL.
- **Volumen de 80 millones de filas en producción** → la consulta optimizada y
  el índice se prueban en el subconjunto; el diseño escala con particionamiento
  por fecha y un índice compuesto.

## Migration Plan

No hay sistema anterior que migrar. El despliegue es:

1. Ejecutar el pipeline en local y validar reporte y base.
2. Construir la imagen Docker y ejecutarla con volúmenes.
3. Programar el job en Jenkins con credenciales y alertas.
4. Publicar el reporte y conectar Power BI a la base o a la exportación.

Rollback: si una carga falla, no se publica el reporte; la base conserva la
última versión válida y el job se puede reejecutar porque es idempotente.

## Open Questions

- Nombre completo del candidato para el archivo `INFORME_<nombre>.pdf`.
- Disponibilidad de un equipo Windows para validar el `.pbix` y las capturas.
- Servidor SMTP y destinatarios definitivos para el envío real.
- Confirmación del negocio sobre el punto `00117` (traslado o dos puntos con el
  mismo código).
