# Design

## Context

Ver `proposal.md`. El hecho tiene grano por `id_transaccion`, con llaves a
`dim_punto` (zona), `dim_producto`, `dim_estado` y `dim_fecha`; la fecha de
negocio se guarda en `dim_fecha`. El estado de venta se resuelve con
`dim_estado.cuenta_como_venta` (APROBADA y REVERSADA).

## Goals / Non-Goals

**Goals:**

- Consultas correctas, legibles y reproducibles sobre SQLite.
- Una versión de la consulta de producción que use índice y no recorra la
  tabla completa.
- Resultados documentados y verificables con el delta aplicado.

**Non-Goals:**

- Optimizar el pipeline de carga o el tablero.
- Probar sobre 80 millones de filas: se razona sobre el plan y se mide con el
  subconjunto del kit.

## Decisions

### 1. Top 3 con función de ventana

Se usa `ROW_NUMBER() OVER (PARTITION BY zona ORDER BY ventas DESC, cod_punto)`
para numerar y filtrar `rn <= 3`. El desempate por código hace el resultado
determinista. Alternativa descartada: `LIMIT 3` por zona con subconsultas
correlacionadas, más difícil de leer y de mantener.

### 2. Puntos activos sin ventas

`dim_punto` se filtra por `activo = 'S'` y se une con el hecho para la fecha de
corte; se conservan los puntos sin filas o con suma nula. El punto `90001` no
está en el hecho, por lo que no aparece.

### 3. Variación por zona

Una CTE calcula las ventas por zona para la fecha de corte y otra para el día
anterior; el `LEFT JOIN` conserva las zonas nuevas y `NULLIF` evita la división
por cero. La variación se devuelve nula cuando no hay base de comparación.

### 4. Consulta de producción SARGable

La consulta original aplica `CONVERT(VARCHAR(10), fecha_transaccion, 120)` y
`UPPER(estado)`, lo que impide usar el índice de fecha y fuerza un escaneo de
80 millones de filas. Se reescribe con:

```sql
WHERE fecha_transaccion >= '2026-10-27'
  AND fecha_transaccion <  '2026-10-28'
  AND estado = 'APROBADA'
```

Se elimina `SELECT *` (solo se piden las columnas necesarias) y se crea un
índice compuesto `(fecha_transaccion, estado)` con `valor` incluido en SQL
Server; en SQLite, `(fecha_transaccion, estado)` y luego el acceso a la fila.
Alternativa descartada: índice sobre una columna calculada
`CAST(fecha_transaccion AS date)`, válido pero menos portable.

### 5. Resultados reproducibles

Las consultas se ejecutan en pruebas sobre una base temporal y se documentan
con el resultado del kit; no se copian números a mano sin una consulta que los
respalde.

## Risks / Trade-offs

- **Empates en el top 3** → desempate por código, documentado.
- **Zona sin ventas previas** → `NULLIF` y resultado nulo, sin error.
- **Diferencia SQLite/SQL Server** → se entrega la versión SQLite ejecutable y
  la variante SQL Server comentada para producción.
- **Índice poco selectivo** → se propone índice compuesto por fecha y estado y
  se verifica el plan con `EXPLAIN QUERY PLAN`.

## Migration Plan

No aplica: las consultas se agregan al repositorio y se ejecutan sobre la base
ya cargada. En producción, el índice se crea en ventana de mantenimiento y se
mide el plan antes y después.

## Open Questions

- Confirmar si el top 3 debe excluir puntos inactivos (se asume que no, solo
  cuentan las ventas).
