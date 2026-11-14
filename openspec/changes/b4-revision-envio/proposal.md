# Proposal

## Why

El script de envío actual falla de forma silenciosa, duplica correos y expone
credenciales. La Parte B4 exige revisar el código, explicar los síntomas y
entregar una versión corregida.

## What Changes

- Se documentan los hallazgos del script original por severidad, línea e
  impacto.
- Se explica por qué el correo se duplica, por qué a veces no llega y por qué
  Jenkins termina en verde.
- Se entrega `revision/enviar_reporte_v2.py` con validación, idempotencia,
  ledger, fallo visible y códigos de salida.
- Se agregan pruebas del modo `.eml`, idempotencia, reporte inexistente y fallo
  de SMTP.

## Capabilities

### New Capabilities

- `envio-reporte`: envío idempotente, observable y auditable de reportes.

### Modified Capabilities

Ninguna.

## Impact

- `parte-4-b4-revision/revision/` y sus pruebas.
- Sección 5 del informe consolidado.
- El demo de Podman ejecuta el envío dos veces contra un SMTP local.
