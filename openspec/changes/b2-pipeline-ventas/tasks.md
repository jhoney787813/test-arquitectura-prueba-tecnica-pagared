# Tasks

## 1. Lectura, validación y CLI

- [x] 1.1 Implementar `parte-2-b2-pipeline/etl/lectura.py` con detección de encoding, separador `;`, tipos y validación de columnas; verificar con `pytest parte-2-b2-pipeline/tests/test_lectura.py` sobre los tres CSV del kit
- [ ] 1.2 Implementar la validación de archivo faltante, archivo vacío, columna faltante y frescura; verificar que cada caso termine con código distinto de 0
- [x] 1.3 Implementar `parte-2-b2-pipeline/etl/cli.py` y `parte-2-b2-pipeline/etl/__main__.py` con `--fecha-corte`, `--delta`, `--db`, `--salida` y logging; verificar `python -m etl --help` y un argumento inválido con código 2
- [x] 1.4 Documentar los parámetros del CLI en el README y verificar que los comandos documentados funcionen

## 2. Limpieza y reglas de negocio

- [x] 2.1 Implementar la limpieza de transacciones (fechas, estados, productos, canales, códigos y valores) con motivos de descarte; verificar con pruebas unitarias de cada variante
- [x] 2.2 Implementar la limpieza del maestro (zonas canónicas, `SIN ZONA`, `NO CATALOGADO` y versiones del `00117`); verificar con pruebas sobre el maestro real
- [x] 2.3 Implementar la deduplicación exacta y la selección de la versión vigente por `fecha_actualizacion`; verificar con `TX102748223` y filas idénticas
- [x] 2.4 Implementar la exclusión del punto `90001` y su registro en calidad; verificar que sus 24 filas no sumen ventas
- [x] 2.5 Registrar cada descarte en `etl_descartes` con archivo, fila, id, motivo y detalle; verificar que el total por motivo coincida con el log
- [x] 2.6 Documentar cada regla de limpieza y su justificación en la sección 3 del informe; verificar que todos los motivos del código aparezcan en el documento

## 3. Modelo dimensional y carga idempotente

- [x] 3.1 Crear el esquema de `fact_transacciones`, dimensiones, índices y tablas de auditoría; verificar con una prueba que crea la base y consulta las tablas
- [x] 3.2 Implementar las dimensiones de fecha, producto, canal y estado con claves deterministas; verificar que una segunda carga reutilice las mismas claves
- [x] 3.3 Implementar `dim_punto` con vigencia y resolver la versión aplicable a cada venta; verificar con ventas de `00117` en dos vigencias
- [x] 3.4 Implementar el upsert idempotente por `id_transaccion` y los contadores de `etl_cargas`; verificar que dos ejecuciones del `2026-10-27` dejen el mismo conteo y total
- [x] 3.5 Verificar que las sumas del almacén coincidan exactamente con la suma `Decimal` de las filas cargadas
- [x] 3.6 Probar la carga completa del kit en una base temporal y verificar el número de filas del hecho y de descartes

## 4. Carga incremental con delta

- [x] 4.1 Implementar `--delta` con inserción, actualización por `fecha_actualizacion` e ignorado de registros obsoletos; verificar los tres escenarios con pruebas
- [x] 4.2 Ejecutar base y luego delta sobre una base temporal y verificar que los ids anulados o reversados queden en su estado más reciente
- [x] 4.3 Documentar en el informe cuántos registros insertó, actualizó e ignoró el delta del 28/10

## 5. Reporte Excel y correo

- [x] 5.1 Generar la hoja `Resumen` con ventas y transacciones por zona y producto; verificar el total contra una consulta directa a la base
- [x] 5.2 Generar la hoja `Comparativo` con variación absoluta y porcentual y `N/A` cuando no hay día anterior; verificar el caso de la zona nueva de Urabá
- [x] 5.3 Generar la hoja `Calidad` con descartes y correcciones por motivo; verificar que los totales coincidan con `etl_descartes`
- [x] 5.4 Generar el borrador `.eml` con asunto, destinatario y Excel adjunto; verificar con `email.parser` que el adjunto se pueda extraer
- [x] 5.5 Implementar el log de contadores y los códigos de salida; verificar que una falla simulada termine con código distinto de 0 y sin reporte publicado
- [ ] 5.6 Agregar pruebas de las tres hojas y del `.eml`; verificar que se ejecuten sin SMTP y sin tocar `salida/`
- [x] 5.7 Generar el reporte del `2026-10-27` antes y después del delta y documentar totales por zona, transacciones y descartes en la sección 3 del informe

## 6. Cierre de B2

- [ ] 6.1 (Opcional) Exportar el hecho a Parquet particionado por fecha; verificar que las particiones conserven el total de ventas
- [x] 6.2 Ejecutar `pytest -q`, `ruff check .` y el pipeline completo con y sin delta; verificar que todo quede en verde
- [x] 6.3 Revisar que no haya secretos, que `db/` y `logs/` estén ignorados y que el reporte se pueda regenerar desde cero
