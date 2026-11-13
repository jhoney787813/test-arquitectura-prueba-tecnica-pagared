# Justificación de la estructura del repositorio

## 1. Propósito de este documento

La prueba pide una estructura raíz con `README.md`, `INFORME_<nombre>.pdf`,
`etl/`, `tests/`, `salida/`, `sql/consultas.sql`, `revision/`, `infra/` y
`powerbi/`. El repositorio conserva **todos** esos entregables, pero el código
de cada sección vive dentro de una carpeta `parte-N` para que la solución se
pueda leer, ejecutar y sustentar paso a paso.

Este documento explica qué hay en cada carpeta, para qué sirve, por qué se
distribuyó así y cómo se mantiene la correspondencia con la estructura pedida.
La decisión quedó aprobada por el usuario en **AP-09** y registrada en
[`openspec/aprobaciones.md`](../openspec/aprobaciones.md).

## 2. Estructura pedida frente a estructura adoptada

| Ruta pedida por la prueba | Dónde está en el repositorio | Qué se conserva |
| :--- | :--- | :--- |
| `README.md` | Raíz | Instrucciones de instalación, ejecución y mapa del repositorio |
| `INFORME_<nombre>.pdf` | Raíz (se compila al final) | Informe consolidado; la fuente está en `docs/informe.md` |
| `etl/` (B2) | `parte-2-b2-pipeline/etl/` | Paquete Python del pipeline |
| `tests/` (B2) | `parte-2-b2-pipeline/tests/` y `tests/` de cada parte | Pruebas de pytest junto al código que prueban |
| `salida/` | Raíz | Reporte Excel generado y borrador `.eml` |
| `sql/consultas.sql` (B3) | `parte-3-b3-sql/sql/consultas.sql` | Consultas de la parte B3 |
| `revision/enviar_reporte_v2.py` (B4) | `parte-4-b4-revision/revision/` | Revisión y versión corregida del envío |
| `infra/` (B5) | `parte-5-b5-operacion/infra/` | Dockerfile y Terraform opcional |
| `powerbi/` (B6) | `parte-6-b6-powerbi/powerbi/` | Diseño, DAX, datos exportados y capturas |

La adaptación no elimina entregables: cambia su ubicación para que cada uno
quede junto a su contexto, sus pruebas y su historia de usuario. El
`README.md`, el informe y `salida/` se mantienen en la raíz porque son puntos
de entrada y salidas compartidas por toda la solución.

## 3. Contenido y propósito de cada parte

### `parte-1-b1-analisis/` — B1: análisis del requerimiento

- `README.md`: resumen de la parte y enlaces al análisis.
- `features/analisis-requerimiento.feature`: historia Gherkin del análisis.
- El contenido completo vive en `docs/informe.md` (requerimientos, preguntas,
  supuestos, arquitectura y plan) y en los diagramas Mermaid de `docs/`.

**Para qué sirve:** entender el correo de Laura y el contexto del core antes de
construir; es la entrada de B2 a B6.

### `parte-2-b2-pipeline/` — B2: pipeline de ventas

- `etl/`: paquete Python (`config`, `fechas`, `limpieza` y las capas que se
  agregan en la implementación: lectura, negocio, carga, reporte y CLI).
- `tests/`: pruebas de contratos, fechas, limpieza, carga incremental y
  validación de Gherkin.
- `scripts/perfil_datos.py`: perfilado reproducible de los CSV.
- `features/`: historias de ingesta, almacén y reporte.

**Para qué sirve:** reemplazar el trabajo manual de Paola; es el núcleo técnico
de la prueba (25 puntos) y la fuente de datos de B3 a B6. Los CSV de entrada
(`datos/`) y las salidas (`salida/`, `db/`, `logs/`) se comparten desde la raíz
para no duplicarlos.

### `parte-3-b3-sql/` — B3: consultas SQL

- `sql/consultas.sql`: una consulta comentada por pregunta (top 3, puntos sin
  ventas, variación y optimización).
- `features/consultas-ventas.feature`: historia Gherkin de las consultas.
- `tests/` (se agrega con la implementación): ejecución sobre la base cargada.

**Para qué sirve:** demostrar que el modelo responde preguntas de negocio y que
la consulta de producción se puede optimizar sin cambiar su resultado.

### `parte-4-b4-revision/` — B4: revisión de código

- `revision/enviar_reporte_v2.py` (se agrega con la implementación): versión
  corregida del script de envío.
- `features/envio-reporte.feature`: historia Gherkin del envío idempotente.
- `tests/` (se agrega con la implementación): pruebas con SMTP falso.

**Para qué sirve:** explicar y corregir los problemas del script que hoy envía
correos duplicados o silencia fallas, sin mezclarlo con el pipeline B2.

### `parte-5-b5-operacion/` — B5: operación y despliegue

- `infra/`: Dockerfile y, si aplica, Terraform.
- `features/operacion-etl.feature`: historia Gherkin de la operación.
- El análisis del incidente, la programación, las alertas y la conectividad con
  Azure se documentan en la sección 6 del informe.

**Para qué sirve:** llevar la solución a ejecución diaria confiable (6:00 a. m.)
y demostrar criterio operativo, no solo de desarrollo.

### `parte-6-b6-powerbi/` — B6: tablero

- `powerbi/`: diseño, medidas DAX, datos exportados y capturas si hay Windows.
- `features/tablero-ventas.feature`: historia Gherkin del tablero.

**Para qué sirve:** cerrar el ciclo de valor para Laura: el dato cargado se
convierte en un tablero para decidir. Power BI Desktop no corre en macOS; la
limitación y el diseño se documentan.

### `parte-7-parte-a-teoria/` — Parte A: componente teórico

- `respuestas.md`: las 10 respuestas con justificación (pendiente).
- `features/componente-teorico.feature`: historia Gherkin del entregable.

**Para qué sirve:** responder el 30 % teórico de la prueba, al final, después de
haber construido y entendido la solución práctica.

## 4. Contenido de la raíz

| Elemento | Para qué sirve |
| :--- | :--- |
| `README.md` | Instrucciones de instalación, ejecución, estructura y enlaces |
| `pyproject.toml` | Empaquetado del `etl` desde `parte-2`, dependencias y configuración de pytest/ruff |
| `Makefile` | Atajos (`setup`, `test`, `lint`, `perfil`, `spec-validate`) |
| `openspec/` | Especificaciones, cambios, aprobaciones y trazabilidad |
| `.agents/skills/` | Skills de OpenSpec para DeepSeek Harness |
| `.github/workflows/` | CI con ruff y pytest |
| `datos/` | CSV de entrada compartidos, copiados del kit sin modificar |
| `salida/` | Reporte Excel y `.eml` generados (entregable) |
| `db/` y `logs/` | Base SQLite y logs de ejecución (generados, no versionados) |
| `docs/` | Informe consolidado y diagramas; documentación transversal |
| `INFORME_<nombre>.pdf` | Informe final, en la raíz |

La raíz funciona como **composition root**: solo reúne configuración, puntos de
entrada, documentación y recursos compartidos. El código de negocio no vive
allí.

## 5. Por qué se distribuyó así

### 5.1 Separación de responsabilidades

Cada parte tiene una responsabilidad distinta y un entregable verificable:
analizar (B1), construir el pipeline (B2), consultar (B3), revisar el envío
(B4), operar (B5), visualizar (B6) y responder la teoría (A). Tenerlas separadas
evita que un cambio en las consultas SQL obligue a tocar el ETL, o que la
revisión de B4 se mezcle con el pipeline B2.

### 5.2 Bajo acoplamiento y dependencias explícitas

Las dependencias van en una dirección: B1 alimenta a B2; B2 produce la base que
usan B3 y B6; B4 y B5 son transversales; A es independiente. El paquete `etl`
se importa desde `parte-2` y se instala con `package-dir`, sin que B3 o B6
importen código de B2: consumen la base o los datos exportados. Los recursos
compartidos (datos, salida, base) viven en la raíz, no se copian en cada parte.

### 5.3 Arquitectura limpia aplicada al entregable

No se trata de imponer capas ceremoniales, sino de aplicar sus principios:
responsabilidades separadas, dependencias unidireccionales, núcleo de negocio
aislado de la infraestructura y composición en la raíz. `etl/` contiene las
reglas y el modelo; `infra/` contiene el despliegue; `powerbi/` contiene la
capa de presentación. La raíz compone, no implementa. Esto permite cambiar el
motor de base, el orquestador o la herramienta de BI sin reescribir las reglas
de negocio.

### 5.4 Control del paso a paso y trazabilidad

La prueba se resuelve por etapas y se sustenta en vivo. Una carpeta por parte
permite:

- Asociar cada etapa a un cambio de OpenSpec (`b1-...`, `b2-...`, `b3-...`).
- Revisar y aprobar una etapa sin arrastrar las demás.
- Ejecutar y probar una parte de forma aislada.
- Hacer commits pequeños y revertir una etapa sin afectar el resto.
- Mostrar en la sustentación dónde está cada entregable en segundos.

La Parte A queda al final porque depende de haber entendido la solución
práctica; su carpeta existe desde ya para que el orden sea explícito.

### 5.5 Pruebas junto al código

`parte-2-b2-pipeline/tests/` prueba el pipeline que vive en
`parte-2-b2-pipeline/etl/`. Las pruebas de B3 y B4 se agregan en sus propias
partes. Así se evita un `tests/` raíz que mezcle responsabilidades y se cumple
el principio de que la prueba viaje con el código que valida.

### 5.6 Legibilidad para el agente y para el evaluador

Cada parte tiene un `README.md` corto, una historia Gherkin y un cambio de
OpenSpec. El agente puede cargar solo el contexto de la parte que va a
modificar; el evaluador puede seguir el hilo B1 → B2 → B3 → B4 → B5 → B6 → A sin
leer todo el repositorio. La raíz queda estable y predecible.

## 6. Trazabilidad con la prueba

| Parte | Carpeta | Entregable principal | Cambio OpenSpec | Estado |
| :---: | :--- | :--- | :--- | :--- |
| B1 | `parte-1-b1-analisis/` | Análisis y arquitectura | `b1-analisis-requerimiento` | Borrador |
| B2 | `parte-2-b2-pipeline/` | ETL, modelo, reporte y pruebas | `b2-pipeline-ventas` | En curso |
| B3 | `parte-3-b3-sql/` | `sql/consultas.sql` | `b3-consultas-sql` | Planificado |
| B4 | `parte-4-b4-revision/` | `revision/enviar_reporte_v2.py` | `b4-revision-envio` | Planificado |
| B5 | `parte-5-b5-operacion/` | Docker, incidente y Azure | (por crear) | Planificado |
| B6 | `parte-6-b6-powerbi/` | DAX, datos y tablero | (por crear) | Planificado |
| A | `parte-7-parte-a-teoria/` | 10 respuestas | (por crear, al final) | Pendiente |

## 7. Riesgos de la adaptación y mitigaciones

| Riesgo | Mitigación |
| :--- | :--- |
| El evaluador busca literalmente `etl/`, `sql/`, etc. en la raíz | El README y este documento incluyen la tabla de equivalencias; la estructura funcional está intacta dentro de cada parte. Si se exigiera la ruta literal, se pueden agregar wrappers o enlaces sin mover el código. |
| Imports rotos por mover `etl` | `pyproject.toml` mapea el paquete con `package-dir`; 58 pruebas y CI en verde lo verifican. |
| Enlaces o rutas obsoletas | Revisión automática de enlaces y referencias de OpenSpec; la raíz conserva datos y salidas compartidas. |
| Duplicación de requisitos entre Gherkin y OpenSpec | Gherkin es la vista de negocio; OpenSpec mantiene los requisitos detallados. Ambos se actualizan en el mismo cambio. |
| Pérdida del historial al mover archivos | Los movimientos se hicieron con `git mv`; el historial sigue a cada archivo. |

## 8. Cómo navegar el repositorio

1. Leer `README.md` para instalar y ejecutar.
2. Abrir `parte-1-b1-analisis/` para entender el problema.
3. Seguir `parte-2` a `parte-6` en orden; cada una tiene su README y su Gherkin.
4. Consultar `openspec/changes/` para el detalle de requisitos, diseño y tareas.
5. Revisar `openspec/aprobaciones.md` para las decisiones y su justificación.
6. Dejar `parte-7-parte-a-teoria/` para el final.

## 9. Conclusión

La estructura conserva el 100 % de los entregables que pide la prueba, pero los
agrupa por etapa para que la solución sea más legible, testeable y sustentable.
La raíz queda como punto de composición y configuración; el código y las
respuestas viven en la parte que les corresponde. Esta organización sigue los
principios de arquitectura limpia (responsabilidades separadas, dependencias
explícitas, composición en la raíz) y facilita controlar el avance de cada
etapa, que es exactamente lo que se necesita para construir y defender una
prueba técnica.
