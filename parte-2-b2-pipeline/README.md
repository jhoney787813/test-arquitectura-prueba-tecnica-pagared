# Parte 2 — B2: Pipeline de ventas

Pipeline ETL que reemplaza el trabajo manual de Paola: lee los CSV del core,
normaliza, carga el modelo dimensional, aplica el delta y genera el reporte
Excel más el borrador de correo.

## Contenido

- `etl/`: paquete Python (`config`, `fechas`, `limpieza` y las capas que se
  agregarán en la implementación).
- `tests/`: pruebas con pytest de contratos, fechas, limpieza e incrementales.
- `scripts/perfil_datos.py`: perfilado reproducible de los CSV.
- `features/`: historias Gherkin de ingesta, almacén y reporte.

## Comandos

Desde la raíz del repositorio:

```bash
make test                 # pytest
make lint                 # ruff
make perfil               # perfilado de datos
```

El paquete se instala en modo editable con `make setup` o
`pip install -e ".[dev]"`; `pyproject.toml` mapea `etl` desde esta carpeta.

## Entregable

`salida/reporte_ventas_YYYYMMDD.xlsx`, la base `db/pagared.db` y los resultados
del 27/10 antes y después del delta en la sección 3 del informe.
