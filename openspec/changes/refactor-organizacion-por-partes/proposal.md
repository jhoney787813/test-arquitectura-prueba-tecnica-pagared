# Proposal

## Why

El repositorio tiene el código repartido entre la raíz (`etl/`, `tests/`,
`sql/`, `revision/`, `infra/`, `powerbi/`) y el plan de la prueba está separado
en cambios de OpenSpec. Para el agente y para quien sustenta la prueba es más
fácil navegar si cada parte de la prueba tiene su propia carpeta con su código,
sus respuestas y sus historias Gherkin, y si la raíz queda reservada para
OpenSpec, configuración y archivos compartidos que no son código.

## What Changes

- Se crean las carpetas `parte-1-b1-analisis` a `parte-7-parte-a-teoria`.
- Se mueve el código a la parte que corresponde: `etl/`, `tests/` y `scripts/`
  a la parte 2; `sql/` a la 3; `revision/` a la 4; `infra/` a la 5; `powerbi/`
  a la 6.
- La raíz conserva solo `openspec/`, `.agents/`, configuración (`pyproject.toml`,
  `Makefile`, `.github/`, `.env.example`, `.gitignore`, `.editorconfig`),
  documentación (`docs/`), datos (`datos/`) y salidas compartidas (`salida/`,
  `db/`, `logs/`).
- Se agrega un archivo `.feature` por capacidad en la carpeta `features/` de su
  parte, con historia de usuario y escenarios Gherkin.
- Se actualizan `pyproject.toml`, Makefile, CI, README, rutas de configuración y
  referencias de OpenSpec.
- Se documenta la desviación frente a la estructura literal del PDF, el
  contenido de cada parte y su justificación en
  `docs/JUSTIFICACION_ESTRUCTURA.md`.

## Capabilities

### New Capabilities

Ninguna: es un refactor de organización y documentación, sin cambio de
comportamiento observable. El cambio declara `skip_specs: true`.

### Modified Capabilities

Ninguna.

## Impact

- Rutas de código, imports, empaquetado, pruebas, CI y documentación.
- No cambia el modelo de datos, las reglas de negocio ni los resultados.
- La estructura del PDF se conserva dentro de cada parte (`etl/`, `tests/`,
  `sql/`, etc.), pero deja de estar en la raíz; se explica en el README.
