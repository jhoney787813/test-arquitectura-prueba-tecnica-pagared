# Prueba Técnica — Solución de Arquitectura de Software | PagaRed S.A.S.

**Candidato:** Jhon E.  
**Contexto:** prueba técnica de Desarrollador de Arquitectura de Software (Grupo Réditos — Dirección de Inteligencia Empresarial)  
**Fecha de corte de los resultados:** 27 de octubre de 2026  
**Repositorio:** privado (se comparte con el evaluador al finalizar)

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
| A | Respuestas teóricas (10 preguntas) | Pendiente |
| B1 | Análisis del requerimiento y arquitectura → [docs/informe.md](docs/informe.md) | Borrador completo |
| B2 | Pipeline ETL, modelo dimensional, reporte y pruebas | En curso (utilidades de limpieza y fechas listas) |
| B3 | [sql/](sql/) (`consultas.sql`) | Pendiente |
| B4 | [revision/enviar_reporte_v2.py](revision/) | Pendiente |
| B5 | [infra/](infra/) y análisis del incidente | Pendiente |
| B6 | [powerbi/](powerbi/) | Pendiente (diseño DAX) |
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
├── pyproject.toml              # dependencias, pytest y ruff
├── Makefile                    # atajos: setup, test, lint, perfil
├── datos/                      # CSV de entrada del kit (sin transformar)
├── etl/                        # B2: lectura, limpieza, carga, reporte, CLI
│   ├── config.py               # rutas, encodings y reglas de negocio
│   ├── fechas.py               # parseo UTC y conversión a America/Bogota
│   └── limpieza.py             # normalización de estados, códigos, valores
├── tests/                      # B2: pytest (contratos, limpieza, incremental)
├── scripts/perfil_datos.py     # perfilado reproducible de los CSV
├── sql/consultas.sql           # B3
├── revision/                   # B4: enviar_reporte_v2.py
├── infra/                      # B5: Dockerfile y Terraform opcional
├── powerbi/                    # B6: .pbix, capturas y medidas DAX
├── salida/                     # reporte_ventas_YYYYMMDD.xlsx + .eml
├── db/                         # SQLite generada (no se versiona)
├── logs/                       # logs de ejecución (no se versionan)
└── docs/                       # informe, diagramas Mermaid y decisiones
```

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
- [ ] Pipeline B2: limpieza, modelo, carga idempotente, delta y reporte
- [ ] Pruebas de limpieza e incremental (mínimo 3, objetivo > 20)
- [ ] B3: consultas SQL y resultados
- [ ] B4: revisión de `enviar_reporte.py` y versión corregida
- [ ] B5: incidente, Dockerfile, despliegue y conectividad Azure
- [ ] B6: medidas DAX, diseño del tablero y capturas
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
