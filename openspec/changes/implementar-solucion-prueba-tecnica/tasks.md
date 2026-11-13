# Tasks

## 1. Fundaciones del pipeline

- [ ] 1.1 Implementar `etl/lectura.py` con detección de encoding, separador `;` y validación de columnas; verificar con `pytest tests/test_lectura.py` sobre los tres CSV del kit
- [ ] 1.2 Implementar la configuración de logging y el CLI `python -m etl` con `--fecha-corte`, `--delta`, `--db` y `--salida`; verificar `python -m etl --help` y que un argumento inválido salga con código 2
- [ ] 1.3 Implementar la validación de frescura y archivo de control antes de cargar; verificar con pruebas de archivo faltante, columna faltante y archivo vacío

## 2. Limpieza y reglas de negocio

- [ ] 2.1 Implementar `limpiar_transacciones` (fechas UTC, estados, productos, canales, códigos y valores) con motivos de descarte; verificar con pruebas unitarias de cada variante
- [ ] 2.2 Implementar `limpiar_puntos` con normalización de zonas, versión SCD2 del código `00117`, `SIN ZONA` para `00133` y `NO CATALOGADO` para `00199`; verificar con pruebas sobre el maestro real
- [ ] 2.3 Implementar la deduplicación y la selección de la versión vigente por `fecha_actualizacion`; verificar con `TX102748223` y con filas idénticas
- [ ] 2.4 Implementar la exclusión del punto `90001` y su registro en la hoja de calidad; verificar que sus 24 filas no sumen ventas
- [ ] 2.5 Documentar cada regla de limpieza y su justificación en la sección 3 del informe; verificar que todos los motivos del código aparezcan en el documento

## 3. Modelo dimensional y carga idempotente

- [ ] 3.1 Crear el esquema de `fact_transacciones`, dimensiones, índices y tablas de auditoría; verificar con una prueba que crea la base y consulta las tablas
- [ ] 3.2 Implementar las dimensiones de fecha, producto, canal y estado con claves sustitutas deterministas; verificar que una segunda carga reutilice las mismas claves
- [ ] 3.3 Implementar `dim_punto` con vigencia y resolver la versión aplicable a la fecha de cada venta; verificar con ventas de `00117` en dos vigencias
- [ ] 3.4 Implementar el upsert idempotente por `id_transaccion` y registrar contadores en `etl_cargas`; verificar que dos ejecuciones del `2026-10-27` dejen el mismo conteo y total
- [ ] 3.5 Registrar los descartes en `etl_descartes` con archivo, fila, id, motivo y detalle; verificar que el total por motivo coincida con el log
- [ ] 3.6 Verificar que las sumas del almacén coincidan exactamente con la suma `Decimal` de las filas cargadas

## 4. Carga incremental con delta

- [ ] 4.1 Implementar `--delta` con inserción, actualización por `fecha_actualizacion` e ignorado de registros obsoletos; verificar los tres escenarios con pruebas
- [ ] 4.2 Ejecutar base y luego delta sobre una base temporal y verificar que los ids anulados o reversados queden en su estado más reciente
- [ ] 4.3 (Opcional) Exportar el hecho a Parquet particionado por fecha; verificar que las particiones conserven el total de ventas

## 5. Reporte Excel y correo

- [ ] 5.1 Generar la hoja `Resumen` con ventas y transacciones por zona y producto; verificar el total contra una consulta directa a la base
- [ ] 5.2 Generar la hoja `Comparativo` con variación absoluta y porcentual y `N/A` cuando no hay día anterior; verificar el caso de la zona nueva de Urabá
- [ ] 5.3 Generar la hoja `Calidad` con descartes y correcciones por motivo; verificar que los totales coincidan con `etl_descartes`
- [ ] 5.4 Generar el borrador `.eml` con asunto, destinatario y Excel adjunto; verificar que `email.parser` pueda abrirlo y encuentre el adjunto
- [ ] 5.5 Implementar el log de contadores y los códigos de salida; verificar que una falla simulada termine con código distinto de 0 y sin reporte publicado
- [ ] 5.6 Generar el reporte del `2026-10-27` antes y después del delta y documentar totales por zona, transacciones y descartes en la sección 3 del informe

## 6. Consultas SQL (B3)

- [ ] 6.1 Escribir `sql/consultas.sql` con top 3 por zona, puntos activos sin ventas y variación por zona; verificar cada consulta con pruebas sobre la base con delta
- [ ] 6.2 Reescribir la consulta de producción con rangos de fecha y estado, crear el índice adecuado y verificar con `EXPLAIN QUERY PLAN` y los mismos resultados
- [ ] 6.3 Documentar en la sección 4 del informe cada consulta con su resultado para el `2026-10-27`

## 7. Revisión de código (B4)

- [ ] 7.1 Analizar `enviar_reporte.py` y documentar los hallazgos por severidad, línea e impacto en la sección 5 del informe
- [ ] 7.2 Implementar `revision/enviar_reporte_v2.py` con validación de configuración, clave de idempotencia, registro de intentos y códigos de salida; verificar con un SMTP falso y dos reintentos
- [ ] 7.3 Explicar en el informe por qué el correo se duplica, por qué a veces no llega y por qué Jenkins marca éxito

## 8. Operación y despliegue (B5)

- [ ] 8.1 Crear `infra/Dockerfile` con usuario no root, dependencias y volúmenes; verificar `docker build` y una ejecución completa del pipeline
- [ ] 8.2 Documentar la ejecución diaria a las 6:00 a. m. (Jenkins o AWS), con `TZ=America/Bogota`, `disableConcurrentBuilds`, timeout, alertas y manejo de credenciales; verificar que el cron propuesto deje el reporte antes de las 6:00
- [ ] 8.3 Analizar el incidente de `carga_recaudos_bi` con evidencia de logs, archivos de control, SFTP y Power BI; documentar causa raíz, corrección de datos y verificación
- [ ] 8.4 Documentar la conectividad con Azure SQL: causa del error de firewall y alternativas ordenadas de la más rápida a la más segura
- [ ] 8.5 (Opcional) Agregar Terraform para la programación y ejecución en AWS; verificar `terraform validate`

## 9. Tablero de Power BI (B6)

- [ ] 9.1 Exportar el hecho y las dimensiones a CSV/Parquet en `powerbi/datos/`; verificar que los totales coincidan con la base
- [ ] 9.2 Documentar el modelo, las relaciones y las medidas DAX de ventas, transacciones, ticket promedio y variación; verificar el caso de zona sin día anterior
- [ ] 9.3 Diseñar la página del tablero con tarjetas, comparación por zona/producto, filtros de fecha/zona/canal y RLS opcional; verificar contra los requisitos de la sección 7 del informe
- [ ] 9.4 Si hay acceso a Windows, construir `powerbi/tablero_ventas.pbix` y capturas; si no, documentar la limitación y entregar el diseño y los datos exportados

## 10. Informe y entrega

- [ ] 10.1 Responder las 10 preguntas de la Parte A con justificación y máximo 8 líneas por respuesta
- [ ] 10.2 Completar las secciones 1 a 8 del informe y compilar `INFORME_<nombre>.pdf` con máximo 25 páginas; verificar que el PDF abra y tenga todas las secciones
- [ ] 10.3 Documentar el uso de IA con herramientas, entre 3 y 5 prompts y al menos 2 correcciones o descartes
- [ ] 10.4 Actualizar el README con la estructura final, comandos de OpenSpec y del pipeline, y verificar que los enlaces no estén rotos

## 11. Integración y verificación final

- [ ] 11.1 Ejecutar el pipeline completo para el `2026-10-27` con y sin delta y comprobar base, Excel, `.eml`, log y códigos de salida
- [ ] 11.2 Ejecutar `pytest -q`, `ruff check .` y el workflow de CI; verificar que todo quede en verde
- [ ] 11.3 Revisar que no haya secretos ni `.env` versionados y que `.gitignore` cubra `db/`, `logs/` y `.venv/`

## Workflow follow-up

- Archivar el cambio con `openspec archive implementar-solucion-prueba-tecnica` cuando la implementación y el informe estén completos.
- Invitar a `Cristian-AS` como colaborador del repositorio privado al momento de la entrega.
