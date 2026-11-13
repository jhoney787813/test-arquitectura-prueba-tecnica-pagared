# Tasks

## 1. Consultas de negocio

- [ ] 1.1 Escribir en `sql/consultas.sql` la consulta de top 3 por zona con `ROW_NUMBER` y desempate por código; verificar con una prueba sobre una base temporal
- [ ] 1.2 Escribir la consulta de puntos activos sin ventas para la fecha de corte; verificar que excluya inactivos y que devuelva los puntos sin filas
- [ ] 1.3 Escribir la consulta de variación por zona con ventas del día, del día anterior y porcentaje; verificar el caso de zona sin día anterior
- [ ] 1.4 Ejecutar las tres consultas sobre la base con el delta del 28/10 y guardar los resultados para el informe

## 2. Optimización de la consulta de producción

- [ ] 2.1 Reescribir la consulta con rango de fechas y estado sin funciones sobre columnas y sin `SELECT *`; verificar que devuelva el mismo conjunto que la versión original
- [ ] 2.2 Crear el índice `(fecha_transaccion, estado)` y verificar con `EXPLAIN QUERY PLAN` que la consulta lo use
- [ ] 2.3 Documentar la causa de los 40 minutos y la propuesta de índice para SQL Server en la sección 4 del informe

## 3. Cierre de B3

- [ ] 3.1 Agregar pruebas automatizadas que ejecuten cada consulta y validen columnas y resultados; verificar `pytest -q`
- [ ] 3.2 Documentar en la sección 4 del informe cada consulta con su resultado y una frase de interpretación
