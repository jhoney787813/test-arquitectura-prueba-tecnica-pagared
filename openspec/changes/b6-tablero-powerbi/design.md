# Design

## Context

Ver `proposal.md` y `specs/tablero-ventas/spec.md`. El modelo B2 ya tiene el
hecho y las dimensiones; Power BI Desktop no está disponible en macOS.

## Goals / Non-Goals

**Goals:** demostrar los indicadores y filtros del tablero con datos reales del
modelo y dejar las medidas DAX listas para Windows.

**Non-Goals:** generar un `.pbix` sin abrirlo ni validarlo en Power BI Desktop.

## Decisions

- **Datos**: CSV de `powerbi/datos/` generados por `make bi-export`.
- **DAX**: medidas de ventas, transacciones, ticket, día anterior y variación
  con `BLANK()` cuando no hay base.
- **Prototipo**: HTML autónomo generado desde SQLite, con filtros de fecha,
  zona y canal; no reemplaza al `.pbix`, lo valida.
- **Pages**: workflow que copia el HTML como `index.html`, adjunta el PDF y
  despliega con `actions/deploy-pages`.
- **Pendiente**: `.pbix`, capturas reales y RLS.

## Risks / Trade-offs

- El prototipo no es una captura de Power BI; se etiqueta como tal.
- El `.pbix` requiere Windows y una validación manual.
