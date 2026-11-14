# Design

## Context

Ver `proposal.md` y `specs/envio-reporte/spec.md`. El script original está en
`codigo/enviar_reporte.py` del kit y no se modifica; la versión corregida vive
en la parte 4.

## Goals / Non-Goals

**Goals:** envío único por reporte, fallo visible, validación previa y
auditoría de intentos.

**Non-Goals:** integrar un SMTP corporativo real en el entorno de la prueba.

## Decisions

- **Clave de idempotencia** por hash del archivo o `--clave`; el ledger JSON
  registra `ENVIADO`, `SIMULADO` y `FALLIDO`.
- **Validación antes de SMTP**: archivo existente, tamaño, destinatarios y
  configuración.
- **Modos**: `.eml` para entornos sin SMTP y `smtp` con TLS opcional para el
  servidor local del demo.
- **Códigos de salida**: 0 éxito/ya enviado, 1 fallo de envío, 2 configuración.
- **Sin credenciales en código**: contraseña desde `PAGARED_SMTP_PASSWORD`.

## Risks / Trade-offs

- El ledger local no coordina múltiples agentes; en producción se reemplaza por
  una tabla con clave única y bloqueo.
- `SIMULADO` bloquea un reenvío real salvo `--forzar`; se documenta.

## Migration Plan

El script v2 se prueba con `.eml` y SMTP local; en producción se configuran
credenciales y se reemplaza el ledger por la tabla de envíos.
