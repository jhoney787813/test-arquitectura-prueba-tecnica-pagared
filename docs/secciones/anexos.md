# Anexo A. Repositorio, ejecución y evidencia

## A.1 Repositorio

```bash
git clone https://github.com/jhoney787813/test-arquitectura-prueba-tecnica-pagared.git
cd test-arquitectura-prueba-tecnica-pagared
```

La rama `main` contiene el historial completo. El repositorio es privado y se
comparte con el evaluador.

## A.2 Organización

| Parte | Carpeta | Contenido |
| :---: | :--- | :--- |
| B1 | `parte-1-b1-analisis/` | Análisis, preguntas, supuestos y arquitectura |
| B2 | `parte-2-b2-pipeline/` | ETL, modelo, reporte, tests y CLI |
| B3 | `parte-3-b3-sql/` | `sql/consultas.sql` |
| B4 | `parte-4-b4-revision/` | `revision/enviar_reporte_v2.py` y tests |
| B5 | `parte-5-b5-operacion/` | `infra/Containerfile`, demo Podman y operación |
| B6 | `parte-6-b6-powerbi/` | DAX, diseño, HTML, captura y CSV |
| A | `parte-7-parte-a-teoria/` | Respuestas teóricas |
| — | `openspec/` | Especificaciones, cambios y aprobaciones |
| — | `salida/` | Reporte Excel y `.eml` finales |

La raíz conserva OpenSpec, configuración, documentación, datos y salidas
compartidas; el código vive en la parte que le corresponde. La decisión y su
justificación están en `docs/JUSTIFICACION_ESTRUCTURA.md` y en la aprobación
AP-09.

## A.3 Comandos de verificación

```bash
make setup
make test
make lint
make etl-delta
make consultas
make b6
make podman-demo
make podman-test
```

`make podman-demo` ejecuta dentro del contenedor: 65 pruebas, ruff, carga base,
delta, reportes, SQL, exportación BI, tablero HTML y envío B4 con SMTP local.
Los resultados quedan en `salida/` y en `docs/RESULTADOS_EJECUCION.md`.

## A.4 Evidencia

| Evidencia | Resultado |
| :--- | :--- |
| Pruebas | 65 en local y 65 dentro del contenedor |
| Estilo | `ruff check .` sin hallazgos |
| OpenSpec | 6/6 cambios válidos con `openspec validate --changes --strict` |
| Datos | 5.651 transacciones base + 2.005 del delta; 7.656 en el hecho |
| Reporte | `salida/reporte_ventas_20261027.xlsx` y `.eml` |
| SQL | `salida/consultas_20261027.txt` |
| BI | `parte-6-b6-powerbi/powerbi/tablero_ventas.html` y captura |
| CI | GitHub Actions en verde |
| Podman | `pagared-etl:local`, demo completo |

## A.5 Limitaciones declaradas

- Power BI Desktop no corre en macOS: no se generó un `.pbix`; se entrega el
  diseño, las medidas DAX, los CSV y un prototipo funcional, como permite la
  prueba.
- El SMTP del demo es local; el envío corporativo real requiere credenciales y
  red autorizada.
- El análisis del incidente B5 es documental; no se modificó el job de
  producción del kit.
