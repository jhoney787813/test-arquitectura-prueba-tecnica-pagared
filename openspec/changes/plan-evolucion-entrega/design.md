# Design

## Context

Ver el análisis de brechas y `README.md`. Las prioridades son: cumplimiento
formal del PDF, estructura exigida, acceso del evaluador y trazabilidad
OpenSpec. B6 `.pbix` depende de un equipo Windows.

## Goals / Non-Goals

**Goals:** cerrar las brechas de entrega sin rehacer el pipeline.

**Non-Goals:** cambiar reglas de negocio, cargar datos de producción o generar
un `.pbix` sin Windows.

## Decisions

- **B1**: recortar tablas redundantes y enlazar el detalle; renderizar Mermaid
  a PNG y embeberlo en el PDF.
- **Estructura**: usar enlaces o wrappers en la raíz para cumplir la ruta
  literal sin duplicar código; agregar `Dockerfile` compatible.
- **B5**: citar `listado_sftp.txt`, `configuracion_agente-etl.txt` e
  `historial_agente-etl.csv` en la tabla de evidencia.
- **B6**: construir el `.pbix` en Windows con el diseño y DAX ya entregados.
- **OpenSpec**: archivar los cambios completos y retirar el paraguas.

## Risks / Trade-offs

- Los enlaces raíz pueden no funcionar en Windows; se documenta la alternativa
  de copia o wrapper.
- El `.pbix` no se puede validar sin Windows.
