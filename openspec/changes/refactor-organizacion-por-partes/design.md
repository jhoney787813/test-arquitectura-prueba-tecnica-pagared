# Design

## Context

Ver `proposal.md` y la aprobación AP-09. El código funciona y las 48 pruebas
pasan; el refactor no debe cambiar comportamiento. La estructura literal del
PDF (`etl/`, `tests/`, `sql/`, `revision/`, `infra/`, `powerbi/` en la raíz) se
reemplaza por una organización por partes, decisión explícita del usuario para
mejorar la legibilidad. La estructura funcional se conserva **dentro** de cada
parte.

## Goals / Non-Goals

**Goals:**

- Una carpeta por parte con su código, respuestas y features.
- Raíz limpia: OpenSpec, configuración, documentación, datos y salidas.
- Gherkin como lenguaje común de historias de usuario para el agente.
- Pruebas, lint y CI en verde después del movimiento.

**Non-Goals:**

- Cambiar reglas de negocio, esquema o resultados.
- Implementar el pipeline o los entregables pendientes.
- Reorganizar los cambios de OpenSpec más allá de sus referencias.

## Target Structure

```text
.
├── README.md
├── pyproject.toml
├── Makefile
├── .env.example
├── .github/
├── .agents/
├── openspec/
├── docs/                      # informe y diagramas (no es código)
├── datos/                     # entrada compartida
├── salida/                    # reporte generado
├── db/                        # SQLite generada
├── logs/                      # logs generados
├── parte-1-b1-analisis/
│   ├── README.md
│   └── features/analisis-requerimiento.feature
├── parte-2-b2-pipeline/
│   ├── README.md
│   ├── etl/
│   ├── tests/
│   ├── scripts/
│   └── features/{ingesta,almacen,reporte}.feature
├── parte-3-b3-sql/
│   ├── README.md
│   ├── sql/consultas.sql
│   ├── tests/
│   └── features/consultas-ventas.feature
├── parte-4-b4-revision/
│   ├── README.md
│   ├── revision/
│   ├── tests/
│   └── features/envio-reporte.feature
├── parte-5-b5-operacion/
│   ├── README.md
│   ├── infra/
│   └── features/operacion-etl.feature
├── parte-6-b6-powerbi/
│   ├── README.md
│   ├── powerbi/
│   └── features/tablero-ventas.feature
└── parte-7-parte-a-teoria/
    ├── README.md
    ├── respuestas.md
    └── features/componente-teorico.feature
```

## Decisions

### 1. Partes numeradas en el orden de la prueba

`parte-1` a `parte-6` corresponden a B1 a B6; `parte-7` es la Parte A, que se
procesa al final. Los nombres incluyen la sección (`b1`, `b2`, …) para que no
haya ambigüedad entre el número de carpeta y el número de la prueba.

### 2. La raíz conserva lo compartido y lo no-code

`datos/`, `salida/`, `db/`, `logs/` y `docs/` se quedan en la raíz porque son
entradas, salidas o documentación compartida entre partes; no son código.
`openspec/`, `.agents/`, `.github/` y los archivos de configuración también se
quedan. El código de cada entregable vive en su parte.

### 3. Empaquetado de Python con `package-dir`

El paquete `etl` se mueve a `parte-2-b2-pipeline/etl`. Para que `pip install -e`
siga funcionando se configura:

```toml
[tool.setuptools]
package-dir = {"" = "parte-2-b2-pipeline"}

[tool.setuptools.packages.find]
where = ["parte-2-b2-pipeline"]
include = ["etl*"]
```

`pytest` apunta a `parte-2-b2-pipeline/tests` y el script de perfilado se ejecuta
desde `parte-2-b2-pipeline/scripts`. Las rutas de datos y salida se calculan
desde la raíz con `parents[2]` en `parte-2-b2-pipeline/etl/config.py`.

### 4. Gherkin en la parte, no en OpenSpec

Cada parte incluye `features/*.feature` con una historia de usuario:

```gherkin
Feature: <capacidad>
  Como <rol>
  Quiero <acción>
  Para <beneficio>

  Scenario: <nombre>
    Given ...
    When ...
    Then ...
```

Se usan palabras clave en inglés (`Feature`, `Scenario`, `Given`, `When`,
`Then`) y texto en español, para que cualquier parser Gherkin lo entienda. Los
escenarios son la vista de negocio de los requisitos que ya están en
`openspec/changes/*/specs/`; si cambia un requisito, se actualizan ambos. La
Parte A usa un `Scenario Outline` con las 10 preguntas.

### 5. Referencias actualizadas

Se actualizan README, `docs/informe.md`, Makefile, CI, `pyproject.toml` y las
rutas de los cambios de OpenSpec. Los enlaces relativos se revisan al final.

## Risks / Trade-offs

- **Desviación de la estructura literal del PDF** → se documenta en el README y
  en el informe; la estructura funcional se conserva dentro de cada parte.
- **Imports rotos tras mover `etl`** → `package-dir` y reinstalación editable;
  las 48 pruebas son la red de seguridad.
- **Rutas de datos/salida** → `config.py` calcula la raíz dos niveles arriba y
  las pruebas de contrato validan que los archivos se encuentren.
- **Duplicación Gherkin/OpenSpec** → Gherkin es la vista de historia de usuario;
  los escenarios se mantienen alineados y se revisan en el mismo commit.
- **Enlaces relativos** → revisión automática de enlaces en README e informe.

## Migration Plan

1. Mover carpetas con `git mv` para conservar historial.
2. Ajustar empaquetado y rutas.
3. Reinstalar el paquete editable y ejecutar pruebas.
4. Actualizar documentación y referencias.
5. Validar OpenSpec y CI.
6. Revertir con `git revert` si algo falla; no hay migración de datos.

## Open Questions

Ninguna que cambie el alcance; la ubicación de las salidas compartidas en la
raíz queda documentada.
