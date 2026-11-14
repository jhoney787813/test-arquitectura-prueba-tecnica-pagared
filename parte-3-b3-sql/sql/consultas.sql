-- Consultas de la Parte B3 (SQLite)
-- Cada bloque se ejecuta con `python -m etl.consultas`.
-- La consulta de optimización es una propuesta para SQL Server y no se ejecuta aquí.

-- @consulta: top3
SELECT zona, cod_punto, nombre, ventas
FROM (
    SELECT p.zona,
           p.cod_punto,
           p.nombre,
           SUM(f.valor_cop) AS ventas,
           ROW_NUMBER() OVER (
               PARTITION BY p.zona
               ORDER BY SUM(f.valor_cop) DESC, p.cod_punto
           ) AS rn
      FROM fact_transacciones f
      JOIN dim_punto p ON p.punto_sk = f.punto_sk
      JOIN dim_estado e ON e.estado_sk = f.estado_sk
      JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
     WHERE d.fecha = :fecha AND e.cuenta_como_venta = 1
     GROUP BY p.zona, p.cod_punto, p.nombre
)
WHERE rn <= 3
ORDER BY zona, rn;

-- @consulta: puntos_sin_ventas
SELECT p.cod_punto, p.nombre, p.zona, 0 AS ventas
  FROM dim_punto p
 WHERE p.es_actual = 1
   AND p.activo = 'S'
   AND NOT EXISTS (
       SELECT 1
         FROM fact_transacciones f
         JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
         JOIN dim_estado e ON e.estado_sk = f.estado_sk
        WHERE f.punto_sk = p.punto_sk
          AND d.fecha = :fecha
          AND e.cuenta_como_venta = 1
   )
 ORDER BY p.cod_punto;

-- @consulta: variacion
WITH actual AS (
    SELECT p.zona, SUM(f.valor_cop) AS ventas
      FROM fact_transacciones f
      JOIN dim_punto p ON p.punto_sk = f.punto_sk
      JOIN dim_estado e ON e.estado_sk = f.estado_sk
      JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
     WHERE d.fecha = :fecha AND e.cuenta_como_venta = 1
     GROUP BY p.zona
),
anterior AS (
    SELECT p.zona, SUM(f.valor_cop) AS ventas
      FROM fact_transacciones f
      JOIN dim_punto p ON p.punto_sk = f.punto_sk
      JOIN dim_estado e ON e.estado_sk = f.estado_sk
      JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
     WHERE d.fecha = :fecha_anterior AND e.cuenta_como_venta = 1
     GROUP BY p.zona
),
zonas AS (
    SELECT zona FROM actual
    UNION
    SELECT zona FROM anterior
)
SELECT z.zona,
       COALESCE(a.ventas, 0) AS ventas_actual,
       COALESCE(b.ventas, 0) AS ventas_anterior,
       CASE
           WHEN COALESCE(b.ventas, 0) = 0 THEN NULL
           ELSE (COALESCE(a.ventas, 0) - b.ventas) * 1.0 / b.ventas
       END AS variacion_pct
  FROM zonas z
  LEFT JOIN actual a ON a.zona = z.zona
  LEFT JOIN anterior b ON b.zona = z.zona
 ORDER BY z.zona;

-- @consulta: optimizacion
-- Original (SQL Server, 80 millones de filas, 40 minutos):
--   SELECT * FROM transacciones
--    WHERE CONVERT(VARCHAR(10), fecha_transaccion, 120) = '2026-10-27'
--      AND UPPER(estado) = 'APROBADA'
--    ORDER BY fecha_transaccion;
-- Problema: las funciones sobre fecha_transaccion y estado impiden usar el
-- índice y fuerzan un escaneo completo; SELECT * suma I/O.
-- Versión propuesta:
--   SELECT id_transaccion, fecha_transaccion, cod_punto, valor, estado
--     FROM transacciones
--    WHERE fecha_transaccion >= '2026-10-27'
--      AND fecha_transaccion <  '2026-10-28'
--      AND estado = 'APROBADA'
--    ORDER BY fecha_transaccion;
-- Índice propuesto (SQL Server):
--   CREATE INDEX ix_transacciones_fecha_estado
--       ON transacciones (fecha_transaccion, estado)
--       INCLUDE (valor, cod_punto);
