# Parte A — Componente teórico

> **En progreso:** A1 y A2 respondidas; A3 a A10 pendientes. Se procesa al
> final, después de B1 a B6.

Cada respuesta debe incluir su justificación y no superar 8 líneas, como pide
la prueba. Esta sección alimenta la sección 1 del informe consolidado.

## A1. SQL — LEFT JOIN y filtro en WHERE

**Respuesta:** No cumple. El `OR t.valor = 0` no crea filas para los puntos
sin transacciones: `t.estado` y `t.valor` son NULL y `NULL = 'APROBADA' OR
NULL = 0` da UNKNOWN, así que el WHERE los elimina (y además incluye ceros no
aprobados). Se mueve el filtro al `ON` y se usa `COALESCE(SUM(t.valor), 0)`.

```sql
SELECT p.cod_punto, p.nombre, COALESCE(SUM(t.valor), 0) AS ventas
FROM puntos_venta p
LEFT JOIN transacciones t ON t.cod_punto = p.cod_punto AND t.estado = 'APROBADA'
GROUP BY p.cod_punto, p.nombre;
```

## A2. SQL — COUNT y NULL

**Respuesta:** La primera devuelve **700** y la segunda **0**. `estado <>
'ANULADA'` cuenta las 700 APROBADA; las 200 ANULADA no cumplen y las 100 NULL
quedan en UNKNOWN, que el `WHERE` descarta. En la segunda, `NOT IN ('ANULADA',
NULL)` equivale a `estado <> 'ANULADA' AND estado <> NULL`; como `x <> NULL` es
UNKNOWN para toda fila, ninguna pasa y el `COUNT` es 0.

**Para contar las 800 no anuladas incluyendo NULL:** `WHERE estado <> 'ANULADA'
OR estado IS NULL`. Para las 700 no nulas: `NOT IN ('ANULADA')`, sin el NULL.

## A3. Python — suma con float

## A4. RPA — Selenium y esperas

## A5. Jenkins — zona horaria del cron

## A6. ETL — idempotencia y reintentos

## A7. Seguridad y Git — secreto en el repositorio

## A8. Carga incremental — anulaciones tardías

## A9. Modelado — historia de zonas

## A10. Criterio — automatizar un proceso manual
