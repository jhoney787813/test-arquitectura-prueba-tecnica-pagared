# Parte 4 — B4: Revisión de código

Revisión del script `enviar_reporte.py` que corre en producción y entrega de
una versión corregida con envío idempotente, fallo visible y auditoría.

## Contenido

- `revision/enviar_reporte_v2.py`: versión corregida (se agrega con la
  implementación).
- `tests/`: pruebas con SMTP falso (se agregan con la implementación).
- `features/envio-reporte.feature`: historia Gherkin del envío.

## Entregable

Hallazgos por severidad con línea e impacto, explicación de los síntomas
(correo repetido, correo que no llega, Jenkins en verde) y el script v2.
