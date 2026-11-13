# Aprobación AP-09 — Refactor por partes y Gherkin

- **Fecha:** 2026-11-13 18:39 (America/Bogota)
- **Solicitado por:** lead (agente)
- **Cambio:** `refactor-organizacion-por-partes`
- **Decisión:** APROBADO

## Alcance propuesto

1. Mover el código a carpetas `parte-1` a `parte-7`, conservando dentro de cada
   una la organización pedida por la prueba (`etl/`, `tests/`, `sql/`,
   `revision/`, `infra/`, `powerbi/`).
2. Dejar en la raíz solo OpenSpec, configuración y archivos que no son código
   (README, `pyproject.toml`, `Makefile`, datos y salidas compartidas, docs).
3. Agregar reglas y archivos `.feature` en formato Gherkin para las historias
   de usuario de cada parte.
4. Actualizar rutas, imports, `pyproject.toml`, Makefile, CI, README y
   referencias de OpenSpec.
5. Verificar con `pytest`, `ruff` y `openspec validate --strict`.

## Justificación del usuario

> “para que sea mas facil de comprender por el agente” y “para organizar de
> manera mas limpia el repositorio”.

## Condiciones

- No cambiar el comportamiento del pipeline ni de las pruebas.
- Mantener los datos de entrada y las salidas compartidas en la raíz.
- Documentar la desviación frente a la estructura literal del PDF y su motivo.

## Resultado

- Commit: `refactor: organizar el repositorio por partes y agregar Gherkin (AP-09)` en el historial de Git.
- Documento de justificación: [`docs/JUSTIFICACION_ESTRUCTURA.md`](../../../docs/JUSTIFICACION_ESTRUCTURA.md).
- Verificación: 58 pruebas (`pytest`), `ruff` y `openspec validate --changes --strict` en verde.
