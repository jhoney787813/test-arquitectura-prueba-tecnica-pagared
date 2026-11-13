# Proposal

## Why

PagaRed prepara hoy el reporte diario de ventas de forma manual: una analista
descarga el archivo del core, lo pega en Excel y arma tablas dinámicas durante
unas tres horas, con riesgo de errores y sin una fuente de datos confiable para
Power BI. La prueba técnica exige reemplazar ese proceso por un pipeline
idempotente, persistir un modelo dimensional, entregar el reporte a las 6:00
a. m. (hora Colombia) y demostrar criterio en SQL, operación y análisis.

## What Changes

- Se crea un pipeline ETL en Python que lee los CSV del core y el maestro de
  puntos, normaliza codificaciones, fechas y valores, aplica las reglas de
  negocio y carga un modelo dimensional en SQLite.
- El cargue es idempotente y acepta un delta incremental: reejecutar una fecha
  no duplica información y el delta actualiza el estado más reciente de cada
  transacción.
- Se genera `salida/reporte_ventas_YYYYMMDD.xlsx` con las hojas **Resumen**,
  **Comparativo** y **Calidad**, más un borrador `.eml` listo para enviar.
- Se agregan consultas SQL para top 3 por zona, puntos sin ventas, variación
  por zona y una versión optimizada de la consulta de producción.
- Se revisa el script de envío actual, se documentan los hallazgos por
  severidad y se entrega `revision/enviar_reporte_v2.py` con envío idempotente.
- Se agrega `infra/Dockerfile`, el análisis del incidente de recaudos y la
  propuesta de despliegue y conectividad con Azure SQL.
- Se documenta el diseño del tablero de Power BI con medidas DAX, visuales y
  RLS opcional; por limitación de macOS no se genera un `.pbix` sin validarlo.
- Se completa el informe consolidado con la teoría, los resultados y el uso de
  IA, y se mantiene la suite de pytest y ruff en verde.

## Capabilities

### New Capabilities

- `ingesta-ventas`: lectura y normalización de los archivos del core y del
  maestro de puntos, con reglas de limpieza justificadas y descarte auditado.
- `almacen-ventas`: modelo dimensional, carga idempotente, aplicación del delta
  y tablas de auditoría listas para Power BI.
- `reporte-ventas`: reporte Excel de tres hojas, comparativo diario, hoja de
  calidad, log de contadores y correo listo para envío.
- `envio-reporte`: corrección del script de envío para que no duplique correos,
  falle de forma visible y registre cada intento.
- `consultas-ventas`: consultas analíticas de ventas y su optimización sobre la
  base cargada.
- `operacion-etl`: empaquetado Docker, ejecución programada, alertas, manejo de
  credenciales y conectividad con Azure SQL.
- `tablero-ventas`: modelo, medidas DAX y visuales del tablero de Power BI,
  incluida la variación diaria sin errores para zonas nuevas.

### Modified Capabilities

Ninguna: el repositorio parte de cero y no existen capacidades previas.

## Impact

- Código nuevo en `etl/`, `tests/`, `sql/`, `revision/`, `infra/` y `powerbi/`.
- Dependencias de ejecución: `pandas` y `openpyxl`; desarrollo: `pytest` y
  `ruff`. SQLite es parte de la biblioteca estándar.
- Datos de entrada en `datos/` (copia del kit, sin modificar) y artefactos en
  `salida/`, `db/` y `logs/`.
- No se tocan sistemas productivos ni se almacenan credenciales; el SMTP real
  queda fuera de alcance y se representa con un archivo `.eml`.
- Power BI Desktop no está disponible en macOS: se entrega el diseño, las
  medidas DAX y la exportación de datos, y se documenta la limitación.
