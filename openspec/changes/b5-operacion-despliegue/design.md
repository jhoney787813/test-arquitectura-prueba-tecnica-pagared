# Design

## Context

Ver `proposal.md` y `specs/operacion-etl/spec.md`. El kit entrega el Jenkinsfile,
el script, logs, `.ctl`, listado SFTP, configuración del agente e historial de
Power BI del incidente.

## Goals / Non-Goals

**Goals:** reproducir el pipeline en Podman, explicar el incidente con evidencia
y dejar una propuesta de operación segura.

**Non-Goals:** corregir el job de producción ni crear un Terraform funcional en
esta entrega.

## Decisions

- **Podman**: imagen `python:3.11-slim`, usuario `etl` no root, demo con
  `--userns=keep-id` en macOS y volúmenes para datos/salida.
- **Incidente**: la causa raíz es la selección de solo la última parte
  (`archivos[-1]`) sin validar el `.ctl`; el refresh de Power BI a las 5:30 leyó
  la tabla a medio cargar porque el build 211 terminó a las 5:41.
- **Prevención**: leer `partes`, `registros` y `valor_total`, carga atómica,
  `disableConcurrentBuilds`, agente dedicado, refresh posterior y alertas.
- **Azure**: firewall del servidor; alternativas de IP temporal, VPN/private
  endpoint y ejecución dentro de Azure.
- **Pendiente**: `infra/Dockerfile` literal y Terraform opcional.

## Risks / Trade-offs

- El demo usa un SMTP local y datos del kit; no toca producción.
- La corrección de los datos del incidente es un procedimiento documentado, no
  una ejecución sobre el core real.
