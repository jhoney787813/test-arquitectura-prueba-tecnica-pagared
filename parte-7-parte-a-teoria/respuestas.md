# Parte A — Componente teórico

> **En progreso:** A1 respondida; A2 a A10 pendientes. Se procesa al final,
> después de B1 a B6.

Cada respuesta debe incluir su justificación y no superar 8 líneas, como pide
la prueba. Esta sección alimenta la sección 1 del informe consolidado.

## A1. SQL — LEFT JOIN y filtro en WHERE

**Respuesta:** No cumple: el `WHERE t.estado` descarta los `t.estado = NULL` y
convierte el LEFT JOIN en INNER JOIN; `SUM` da NULL y `NOT IN (0)` no lo corrige.
Se mueve el filtro al `ON` y se usa `COALESCE(SUM(t.valor), 0)`.

```sql
SELECT p.cod_punto, p.nombre, COALESCE(SUM(t.valor), 0) AS ventas
FROM puntos_venta p
LEFT JOIN transacciones t ON t.cod_punto = p.cod_punto AND t.estado = 'APROBADA'
GROUP BY p.cod_punto, p.nombre;
```

## A2. SQL — COUNT y NULL

## A3. Python — suma con float

## A4. RPA — Selenium y esperas

## A5. Jenkins — zona horaria del cron

## A6. ETL — idempotencia y reintentos

## A7. Seguridad y Git — secreto en el repositorio

## A8. Carga incremental — anulaciones tardías

## A9. Modelado — historia de zonas

## A10. Criterio — automatizar un proceso manual
