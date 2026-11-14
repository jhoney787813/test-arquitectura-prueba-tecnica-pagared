# Tasks

## 1. Cumplimiento formal del informe

- [ ] 1.1 Recortar la sección B1 a máximo dos páginas y verificar el conteo al compilar el PDF
- [ ] 1.2 Renderizar `docs/arquitectura.mmd` y `docs/modelo_datos.mmd` a imágenes e incrustarlas en el PDF
- [ ] 1.3 Verificar que el PDF final siga por debajo de 25 páginas
- [ ] 1.4 Cerrar las preguntas abiertas de B1 con Laura y actualizar los supuestos

## 2. Estructura y Dockerfile

- [ ] 2.1 Agregar una capa de compatibilidad en la raíz para `etl/`, `tests/`, `sql/`, `revision/`, `infra/` y `powerbi/` sin duplicar código
- [ ] 2.2 Agregar `infra/Dockerfile` compatible con el `Containerfile` de Podman
- [ ] 2.3 Verificar que `pytest`, `make etl` y `make podman-demo` sigan funcionando

## 3. Evidencia y acceso

- [ ] 3.1 Citar explícitamente `listado_sftp.txt`, `configuracion_agente-etl.txt` e `historial_agente-etl.csv` en la sección B5
- [ ] 3.2 Invitar a `Cristian-AS` como colaborador del repositorio privado y verificar el acceso

## 4. B6 en Windows

- [ ] 4.1 Construir y validar `tablero_ventas.pbix` en Power BI Desktop
- [ ] 4.2 Capturar el tablero con el 27/10 y la vista de modelo
- [ ] 4.3 (Opcional) Configurar y probar RLS por zona

## 5. Cierre OpenSpec

- [ ] 5.1 Marcar como completadas las tareas pendientes de B2 y B3 que ya tienen implementación
- [ ] 5.2 Archivar los cambios completos (`b1`, `b2`, `b3`, `b4`, `b5`, `b6`, `parte-a`) cuando corresponda
- [ ] 5.3 Retirar el cambio paraguas y verificar `openspec validate --changes --strict`

## 6. Pendientes técnicos detectados en B2 y B3

- [ ] 6.1 Agregar a B2 la validación de frescura y archivo de control antes de cargar
- [ ] 6.2 Agregar a B2 pruebas automatizadas de las hojas del Excel y del `.eml`
- [ ] 6.3 Verificar en B3 la consulta legacy con `EXPLAIN` y agregar pruebas de las consultas
- [ ] 6.4 (Opcional) Exportar el hecho a Parquet particionado por fecha
