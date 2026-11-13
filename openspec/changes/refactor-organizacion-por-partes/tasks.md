# Tasks

## 1. Mover el código a las partes

- [x] 1.1 Mover `etl/`, `tests/` y `scripts/` a `parte-2-b2-pipeline/` con `git mv`; verificar que no queden archivos de código en la raíz
- [x] 1.2 Mover `sql/` a `parte-3-b3-sql/`, `revision/` a `parte-4-b4-revision/`, `infra/` a `parte-5-b5-operacion/` y `powerbi/` a `parte-6-b6-powerbi/`; verificar el árbol
- [x] 1.3 Crear `parte-1-b1-analisis/` y `parte-7-parte-a-teoria/` con su README y contenido de documentación

## 2. Ajustar empaquetado y rutas

- [x] 2.1 Configurar `package-dir` y `packages.find` en `pyproject.toml` y `testpaths` de pytest; verificar `pip install -e ".[dev]"`
- [x] 2.2 Actualizar `etl/config.py` para calcular la raíz desde `parte-2-b2-pipeline`; verificar que `DIR_DATOS` apunte a `datos/` de la raíz
- [x] 2.3 Actualizar el Makefile (`perfil`, rutas) y verificar `make test`, `make lint` y `make perfil`
- [x] 2.4 Verificar que CI siga funcionando con `pip install -e .`, `pytest` y `ruff` sobre las nuevas rutas

## 3. Documentación por parte y Gherkin

- [x] 3.1 Crear `README.md` en cada parte con propósito, contenido y comandos; verificar que los enlaces relativos existan
- [x] 3.2 Crear `features/*.feature` para ingesta, almacén, reporte, consultas, envío, operación, tablero, análisis y componente teórico; verificar sintaxis Gherkin
- [x] 3.3 Agregar en `openspec/config.yaml` la regla de que cada capacidad tenga su `.feature` y que Gherkin sea la vista de historia de usuario

## 4. Actualizar referencias

- [x] 4.1 Actualizar el README raíz con la nueva estructura, el motivo y la desviación frente al PDF
- [x] 4.2 Actualizar `docs/informe.md` y los diagramas para las nuevas rutas
- [x] 4.3 Actualizar las referencias de rutas en los cambios de OpenSpec (`etl/`, `tests/`, `sql/`, `revision/`, `infra/`, `powerbi/`)

## 5. Verificación y cierre

- [x] 5.1 Ejecutar `pytest -q`, `ruff check .`, `make perfil` y `openspec validate` de todos los cambios; verificar que todo quede en verde
- [x] 5.2 Revisar que la raíz solo tenga OpenSpec, configuración, documentación, datos y salidas compartidas
- [x] 5.3 Commit y push del refactor, con referencia a AP-09
