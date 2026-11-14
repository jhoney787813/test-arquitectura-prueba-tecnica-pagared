# Ficha del entregable

| Campo | Valor |
| :--- | :--- |
| Candidato | Jhon E. |
| Empresa del caso | PagaRed S.A.S. — Grupo Réditos |
| Rol | Desarrollador de Arquitectura de Software |
| Fecha de corte | 27 de octubre de 2026 |
| Fecha de entrega | 14 de noviembre de 2026 |
| Repositorio | [github.com/jhoney787813/test-arquitectura-prueba-tecnica-pagared](https://github.com/jhoney787813/test-arquitectura-prueba-tecnica-pagared.git) |
| Tablero en vivo | [https://jhoney787813.github.io/test-arquitectura-prueba-tecnica-pagared/](https://jhoney787813.github.io/test-arquitectura-prueba-tecnica-pagared/) |
| Stack | Python 3.11, pandas, openpyxl, SQLite, pytest, ruff, Podman |
| Entregable | Pipeline ETL, modelo dimensional, SQL, revisión B4, operación B5 y diseño/prototipo B6 |

**Clonar y ejecutar:**

```bash
git clone https://github.com/jhoney787813/test-arquitectura-prueba-tecnica-pagared.git
cd test-arquitectura-prueba-tecnica-pagared
make setup        # Python 3.11 + dependencias
make test         # 65 pruebas
make podman-demo  # contenedor: tests, ETL, SQL, BI y envío B4
```

**Qué incluye:** informe, datos del kit, pipeline idempotente, reporte Excel,
consultas SQL, revisión y v2 del envío, contenedor Podman, DAX, prototipo del
tablero, captura y resultados de ejecución. La estructura está justificada en
`docs/JUSTIFICACION_ESTRUCTURA.md`.
