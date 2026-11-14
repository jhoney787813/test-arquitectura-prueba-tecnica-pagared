# Prueba Técnica — Solución de Arquitectura de Software | PagaRed S.A.S.

- **Candidato:** Jhon E.
- **Contexto:** prueba técnica de Desarrollador de Arquitectura de Software (Grupo Réditos — Dirección de Inteligencia Empresarial)
- **Fecha de corte de los resultados:** 27 de octubre de 2026
- **Fecha de entrega:** 14 de noviembre de 2026
- **Repositorio:** privado (se comparte con el evaluador al finalizar)

Solución al caso de PagaRed S.A.S.: automatizar el reporte diario de ventas que
hoy prepara Paola en Excel durante tres horas, dejarlo disponible para Power BI
y operarlo de forma confiable (idempotente, observable y con alertas).

> **Estado:** repositorio en construcción por fases. La estructura, las reglas
> de negocio, el perfilado de datos y el análisis del requerimiento (B1) ya
> están documentados; el pipeline (B2), las consultas (B3), la revisión de
> código (B4), la operación (B5) y el tablero (B6) se incorporan en los
> siguientes commits.

---

## 1. Estado de los entregables

| Parte | Entregable | Estado |
| :---: | :--- | :--- |
| A | Respuestas teóricas (10 preguntas) → [parte-7](parte-7-parte-a-teoria/) | Respondidas (10/10) |
| B1 | Análisis del requerimiento y arquitectura → [parte-1](parte-1-b1-analisis/) | Completo |
| B2 | Pipeline ETL, modelo dimensional, reporte y pruebas → [parte-2](parte-2-b2-pipeline/) | Implementado y probado |
| B3 | Consultas SQL → [parte-3](parte-3-b3-sql/) | Implementado |
| B4 | Revisión y envío corregido → [parte-4](parte-4-b4-revision/) | Implementado (v2 idempotente) |
| B5 | Operación, incidente y despliegue → [parte-5](parte-5-b5-operacion/) | Contenedor y demo; falta análisis del incidente |
| B6 | Tablero de Power BI → [parte-6](parte-6-b6-powerbi/) | Prototipo HTML + DAX + captura; `.pbix` pendiente (macOS) |
| — | Informe consolidado PDF | Pendiente de compilar |

---

## 2. Contexto en una frase

Cada madrugada el core exporta las transacciones en UTC; Laura necesita a las
6:00 a. m. (hora Colombia) un resumen del día anterior por zona y producto, con
comparativo contra el día previo, sin el punto de pruebas, sin duplicados y con
los datos persistidos para que BI construya el tablero mensual.

Reglas de negocio tomadas del correo de la Gerente Comercial:

- **Ventas** = transacciones `APROBADA` + `REVERSADA` (la reversada se cobró).
- **No cuentan** `ANULADA` ni `RECHAZADA`.
- Se excluye el punto de pruebas de sistemas (`90001`).
- Día contable = **00:00 a 23:59 de America/Bogota**, no UTC.
- Reporte por zona y producto, comparativo contra el día anterior.
- Si el archivo no llega, hay alerta; el correo no puede llegar dos veces.

---

## 3. Estructura del repositorio

```text
.
├── README.md
├── pyproject.toml              # configuración, dependencias, pytest y ruff
├── Makefile                    # atajos: setup, test, lint, perfil
├── datos/                      # CSV de entrada del kit (sin transformar)
├── salida/                     # reporte_ventas_YYYYMMDD.xlsx + .eml
├── db/                         # SQLite generada (no se versiona)
├── logs/                       # logs de ejecución (no se versionan)
├── docs/                       # informe, diagramas Mermaid y decisiones
├── openspec/                   # especificaciones, cambios y aprobaciones
├── .agents/skills/             # skills de OpenSpec para DeepSeek Harness
├── .github/workflows/          # CI con ruff + pytest
├── parte-1-b1-analisis/        # análisis, preguntas, supuestos y arquitectura
│   ├── README.md
│   └── features/analisis-requerimiento.feature
├── parte-2-b2-pipeline/        # pipeline ETL y pruebas
│   ├── etl/                    # paquete Python
│   ├── tests/                  # pytest
│   ├── scripts/                # perfilado de datos
│   └── features/               # ingesta, almacén y reporte
├── parte-3-b3-sql/             # consultas SQL
│   ├── sql/consultas.sql
│   └── features/consultas-ventas.feature
├── parte-4-b4-revision/        # revisión del script de envío
│   ├── revision/enviar_reporte_v2.py
│   └── features/envio-reporte.feature
├── parte-5-b5-operacion/       # Docker, despliegue, incidente y Azure
│   ├── infra/
│   └── features/operacion-etl.feature
├── parte-6-b6-powerbi/         # tablero, DAX y datos exportados
│   ├── powerbi/
│   └── features/tablero-ventas.feature
└── parte-7-parte-a-teoria/     # respuestas teóricas, al final
    ├── respuestas.md
    └── features/componente-teorico.feature
```

**Organización por partes.** El código, las pruebas y las respuestas de cada
sección viven en su carpeta `parte-N`. La raíz queda reservada para OpenSpec,
configuración, documentación, datos y salidas compartidas. El PDF pedía
`etl/`, `tests/`, `sql/`, `revision/`, `infra/` y `powerbi/` directamente en la
raíz; por decisión de legibilidad (AP-09) esas carpetas se conservan **dentro**
de su parte. El movimiento no cambia el comportamiento del pipeline.

La justificación completa de la estructura, el contenido de cada carpeta y su
correspondencia con la distribución pedida está en
[docs/JUSTIFICACION_ESTRUCTURA.md](docs/JUSTIFICACION_ESTRUCTURA.md). El
registro de uso de IA, contexto y prompts está en
[docs/USO_IA_Y_PROMPTS.md](docs/USO_IA_Y_PROMPTS.md).

Los archivos de `datos/` son copia byte a byte del kit entregado
(`md5` verificado). No se editan a mano: todas las correcciones quedan en el
pipeline y en la hoja **Calidad** del reporte.

---

## 4. Requisitos e instalación

- Python **3.10+** (probado con 3.11)
- Docker (opcional, para ejecutar el pipeline aislado)
- Power BI Desktop (solo Windows; en macOS se entrega el diseño y las medidas DAX)

```bash
# 1. Crear el entorno e instalar el paquete en modo editable
make setup            # usa python3.12/3.11 si existen; o: make setup PYTHON=python3.11

# 2. Verificar que todo esté sano
make test             # pytest
make lint             # ruff

# 3. Perfilar los datos de entrada (no modifica nada)
make perfil
```

Si no usa `make`:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

### 4.1 Especificaciones y flujo de trabajo (OpenSpec)

El proyecto usa [OpenSpec](https://openspec.dev) 2.x como capa de
especificaciones antes de escribir código. La instalación global es:

```bash
npm install -g @fission-ai/openspec@latest   # requiere Node.js 22.12+
```

El plan está dividido en un cambio por parte:

- `b1-analisis-requerimiento`: análisis, preguntas, supuestos y arquitectura.
- `b2-pipeline-ventas`: pipeline con las capacidades de ingesta, almacén y
  reporte.
- `b3-consultas-sql`: consultas y optimización.
- `b4-revision-envio`: revisión y corrección del envío.
- `refactor-organizacion-por-partes`: organización del repositorio y Gherkin.

B5, B6 y la Parte A se agregan como cambios independientes; la Parte A queda al
final, como se acordó. Cada cambio tiene `proposal.md`, `specs/`, `design.md`,
`tasks.md` y, cuando aplica, `aprobacion.md` con la justificación del usuario.

> El cambio `implementar-solucion-prueba-tecnica` es el plan paraguas original;
> queda temporalmente hasta crear B5 y B6 y se retira con la aprobación AP-08.

Comandos útiles:

```bash
make spec                        # lista los cambios activos
make spec-validate               # valida todos los cambios en modo estricto
openspec status --change b2-pipeline-ventas
openspec show b2-pipeline-ventas
```

Las skills de OpenSpec quedaron instaladas en `.agents/skills/` para que
DeepSeek Harness pueda proponer, aplicar y archivar cambios con
`/openspec-propose`, `/openspec-apply-change` y `/openspec-archive-change`.

### 4.2 Historias de usuario en Gherkin

Cada parte incluye una carpeta `features/` con sus historias en formato
Gherkin (palabras clave en inglés y texto en español):

```gherkin
Feature: Reporte diario de ventas
  Como Gerente Comercial
  Quiero recibir el reporte del día anterior por zona y producto
  Para tomar decisiones sin esperar el trabajo manual

  Scenario: Reporte del 27 de octubre
    Given la fecha de corte 2026-10-27
    When se genera el reporte
    Then existe reporte_ventas_20261027.xlsx con Resumen, Comparativo y Calidad
```

Los escenarios Gherkin son la vista de negocio de los requisitos de OpenSpec y
deben mantenerse alineados; el agente los usa para entender el alcance antes de
implementar. La regla quedó consignada en `openspec/config.yaml`.

### 4.3 Ejecución local y con Podman

**Local:**

```bash
make test          # 65 pruebas
make etl           # pipeline para 2026-10-27 (base)
make etl-delta     # pipeline + delta del 28/10
make consultas     # B3 sobre db/pagared.db
make bi-export     # CSV para Power BI en parte-6.../powerbi/datos
make b6            # datos + tablero HTML + captura del prototipo
```

**Podman:**

```bash
make podman-build  # construye pagared-etl:local
make podman-demo   # ejecuta el flujo completo y deja los artefactos en salida/
make podman-test   # 65 pruebas dentro del contenedor
```

El demo:

1. Ejecuta las 65 pruebas y `ruff` dentro del contenedor.
2. Borra la base y carga `transacciones.csv`.
3. Aplica `transacciones_delta_20261028.csv` sobre la misma base.
4. Genera reportes antes/después, ejecuta las consultas B3, exporta el modelo
   a CSV, genera el tablero HTML y envía el reporte por un SMTP local de
   prueba, comprobando que el segundo intento no duplica el correo.
5. Imprime los totales y deja los archivos en `salida/antes/`,
   `salida/despues/`, `salida/consultas_20261027.txt`, `salida/powerbi/`,
   `salida/smtp.log` y `salida/envios_smtp.json`.

Resultados del demo (fecha de corte 2026-10-27):

| Momento | Ventas | Transacciones |
| :--- | ---: | ---: |
| Antes del delta | $954.497.200 | 2.440 |
| Después del delta | $916.270.700 | 2.452 |

El delta insertó 2.005 transacciones, actualizó 52 e ignoró 53; la base base
descartó 314 filas por calidad y el delta 1 versión obsoleta.

La imagen define un usuario `etl` no root. Para que el demo escriba en los
volúmenes del host en macOS se ejecuta con `--userns=keep-id` y el UID del
usuario; en un servidor Linux se puede usar el usuario `etl` con volúmenes
propios. El detalle del flujo está en
[parte-5-b5-operacion/infra/](parte-5-b5-operacion/infra/). Los resultados
numéricos del demo están en
[docs/RESULTADOS_EJECUCION.md](docs/RESULTADOS_EJECUCION.md).

---

## 5. Perfilado de los datos entregados

| Archivo | Filas | Encoding | Separador | Observación |
| :--- | ---: | :--- | :---: | :--- |
| `datos/transacciones.csv` | 5.965 | UTF-8 con BOM | `;` | 3 formatos de fecha, 24 variantes de estado, 140 filas duplicadas |
| `datos/transacciones_delta_20261028.csv` | 2.111 | UTF-8 con BOM | `;` | 2.005 ids nuevos, 105 ya existentes, 82 cambios de estado |
| `datos/puntos_venta.csv` | 42 | Latin-1 | `;` | 00117 duplicado, 00133 sin zona, 00199 fuera del maestro, 90001 de pruebas |

Hallazgos que originan las reglas de limpieza (detalle en
[docs/informe.md](docs/informe.md)):

1. Los dos archivos del core vienen en **UTF-8 con BOM** y el maestro en
   **Latin-1**; leer todo como UTF-8 corrompe los acentos.
2. Hay **890 códigos de punto sin ceros a la izquierda** (`131` → `00131`) y
   4 registros con código vacío.
3. La columna `valor` mezcla `10000.00` con `522.500`; en COP el punto seguido
   de tres dígitos es separador de miles. No hay centavos distintos de `.00`.
4. Los estados aparecen con espacios y mayúsculas inconsistentes
   (`' aprobada '`, `'Aprobada'`), 24 variantes para 4 valores reales.
5. Las fechas usan tres formatos, incluido ISO-8601 con `Z` (UTC).
6. El archivo principal incluye transacciones del **28/10 entre 00:00 y 05:54
   UTC**, que en Colombia son la noche del 27/10: filtrar por fecha UTC
   perdería ventas del día de corte.
7. El delta trae registros anteriores a su ventana declarada (llegada tardía) y
   cambios de estado de transacciones ya cargadas.
8. El maestro tiene el código **00117 duplicado** con nombre, zona y fecha de
   apertura distintos, y la zona del punto **00133** vacía.
9. El punto **00199** aparece en 12 transacciones pero **no existe en el
   maestro**; no se puede atribuir a una zona.
10. El punto **90001** (`PUNTO PRUEBAS SISTEMAS - NO USAR`) registra 24 filas
    que deben excluirse de todos los reportes.

Día contable en Colombia frente al día UTC del archivo principal:

| Día | UTC | America/Bogota |
| :--- | ---: | ---: |
| 2026-10-25 | 0 | 291 |
| 2026-10-26 | 2.547 | 2.727 |
| 2026-10-27 | 2.756 | 2.937 |
| 2026-10-28 | 662 | 10 |

La diferencia demuestra por qué el pipeline convierte a `America/Bogota` antes
de delimitar el día: 652 de las 662 filas con fecha UTC del 28 pertenecen al 27
en el calendario del negocio.

---

## 6. Decisiones de diseño

| Tema | Decisión | Motivo |
| :--- | :--- | :--- |
| Motor | **SQLite** por defecto, con SQL compatible y ruta a PostgreSQL/Docker | Portabilidad y cero infraestructura para la sustentación; el modelo es el mismo |
| Zona horaria | UTC en el core → **America/Bogota** para el día contable | El correo pide “de 12 de la noche a 12 de la noche” |
| Idempotencia | `UNIQUE(id_transaccion)` + `UPSERT` y borrado/recarga por fecha de corte | Reintentos de Jenkins no duplican ventas (A6) |
| Incremental | Upsert por `id_transaccion`, gana la `fecha_actualizacion` más reciente | El delta puede reenviar filas y anulaciones tardías |
| Histórico de zonas | Dimensión de punto con vigencia (**SCD2**) | Evita que un cambio de zona reescriba los informes del pasado (A9) |
| Dinero | `Decimal` en Python y **pesos enteros** en la base | Evita el error de redondeo de `float` (A3) |
| Duplicados | Se descartan filas idénticas y se conserva la última versión por id | 140 filas exactas duplicadas en el archivo principal |
| Punto de pruebas | Excluido por código `90001` y registrado en Calidad | Regla explícita de Laura |
| Punto no catalogado | `00199` se reporta como `NO CATALOGADO`; la venta no se descarta | No se pierde dinero por un código ausente del maestro |
| Zona vacía | Se reporta como `SIN ZONA`, no se descarta la venta | No se pierde dinero por un dato faltante del maestro |
| Reporte | Excel con hojas **Resumen**, **Comparativo** y **Calidad** + `.eml` | Requisito B2.7 y ausencia de SMTP corporativo |
| Secretos | Variables de entorno / credenciales de Jenkins, `.env` ignorado | Nunca se versionan credenciales |

---

## 7. Modelo dimensional propuesto

```text
dim_fecha ──┐
dim_punto ──┼──< fact_transacciones >── dim_producto
dim_canal ──┤                     └──── dim_estado
             └── etl_cargas / etl_descartes (auditoría)
```

- `fact_transacciones`: grano = una fila por `id_transaccion`, con valor en
  pesos, fecha/hora UTC y local, estado y llaves a dimensiones.
- `dim_punto`: código, nombre, zona, activo y vigencia (`valido_desde`,
  `valido_hasta`) para resolver la zona histórica.
- `dim_fecha`: calendario con año, mes, día y fin de semana.
- `dim_producto`, `dim_canal`, `dim_estado`: catálogos normalizados.
- `etl_cargas` y `etl_descartes`: trazabilidad de cada ejecución (leídos,
  descartados por motivo, insertados, actualizados e ignorados).

Diagramas: [docs/arquitectura.mmd](docs/arquitectura.mmd) y
[docs/modelo_datos.mmd](docs/modelo_datos.mmd).

---

## 8. Hoja de ruta

- [x] Estructura del repositorio, datos y utilidades base
- [x] Análisis del requerimiento B1 y arquitectura (borrador)
- [x] Refactor por partes (B1 a B6 + Parte A al final) e historias Gherkin [AP-09](openspec/aprobaciones.md)
- [x] Pipeline B2: limpieza, modelo, carga idempotente, delta y reporte
- [x] Pruebas de limpieza e incremental (65 pruebas)
- [x] B3: consultas SQL y resultados
- [x] B4: revisión de `enviar_reporte.py` y versión corregida
- [x] B5: contenedor Podman, demo y flujo de ejecución
- [ ] B5: análisis del incidente, despliegue y conectividad Azure en el informe
- [x] B6: exportación de datos, medidas DAX, diseño y prototipo/captura
- [ ] B6: `.pbix` validado en Power BI Desktop (Windows)
- [ ] Informe consolidado en PDF y sustentación

---

## 9. Seguridad

- No se versionan `.env` ni credenciales; solo `.env.example`.
- Las credenciales de producción van en Jenkins Credentials o AWS Secrets
  Manager, nunca en el código.
- Los archivos de entrada y salida no contienen datos personales; aun así, el
  repositorio es privado.
- Cualquier secreto que haya estado en Git se considera comprometido y se rota
  (ver respuesta A7 del informe).

---

## 10. Autor

**Jhon E.** — aspirante a Desarrollador de Arquitectura de Software.
