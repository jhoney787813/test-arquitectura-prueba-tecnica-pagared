# Proposal

## Why

La Parte B5 exige operar el pipeline de forma confiable: diagnosticar el
incidente de recaudos, proponer el despliegue diario y resolver la conectividad
con Azure SQL. Además, el pipeline debe ejecutarse en un contenedor reproducible.

## What Changes

- Se agrega la imagen Podman (`Containerfile`), el entrypoint y el demo completo.
- Se documenta la causa raíz del incidente de `carga_recaudos_bi` con evidencia
  de logs, archivos de control, SFTP, agente y Power BI.
- Se documentan la corrección de datos, la prevención, el despliegue
  Jenkins/AWS y las alternativas de conectividad con Azure.
- Se deja como pendiente la compatibilidad literal `infra/Dockerfile` y el
  Terraform opcional.

## Capabilities

### New Capabilities

- `operacion-etl`: ejecución programada, segura y observable del pipeline.

### Modified Capabilities

Ninguna.

## Impact

- `parte-5-b5-operacion/infra/` y el demo de Podman.
- Sección 6 del informe consolidado.
- No se modifica el job de producción del kit: el incidente se analiza.
