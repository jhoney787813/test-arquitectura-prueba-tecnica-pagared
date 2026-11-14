# Parte 5 — B5: Operación y despliegue

Empaquetado y operación del pipeline: Docker, programación antes de las 6:00
a. m., alertas, manejo de credenciales, análisis del incidente de recaudos y
conectividad con Azure SQL.

## Contenido

- `infra/Containerfile`: imagen Podman con usuario `etl` no root.
- `infra/entrypoint.sh` y `infra/demo.sh`: flujo ejecutable del demo.
- `infra/compose.yaml`: alternativa con `podman compose`.
- `features/operacion-etl.feature`: historia Gherkin de la operación.

## Ejecución

Desde la raíz:

```bash
make podman-build   # imagen pagared-etl:local
make podman-demo    # pipeline + delta + SQL + BI + envío B4
make podman-test    # 65 pruebas dentro del contenedor
```

El flujo del contenedor está en `infra/demo.sh` y los resultados numéricos en
[docs/RESULTADOS_EJECUCION.md](../../docs/RESULTADOS_EJECUCION.md).

## Entregable

La sección 6 del informe con la causa raíz del incidente, la corrección de los
datos, la propuesta de despliegue (Jenkins o AWS) y las alternativas de
conectividad con Azure.
