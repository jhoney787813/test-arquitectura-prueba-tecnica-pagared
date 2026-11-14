# Resultados de la ejecución en Podman

- **Fecha de ejecución:** 2026-11-13 (America/Bogota)
- **Imagen:** `pagared-etl:local`
- **Podman:** 5.8.3, máquina `podman-machine-default` (libkrun)
- **Comando principal:** `make podman-demo`

## 1. Flujo ejecutado

0. Ejecución de 65 pruebas y `ruff` dentro del contenedor.
1. Carga base de `datos/transacciones.csv` para la fecha de corte `2026-10-27`.
2. Carga incremental de `datos/transacciones_delta_20261028.csv` sobre la misma base.
3. Generación de los reportes antes y después del delta.
4. Ejecución de las consultas B3.
5. Exportación del modelo a CSV para Power BI.
6. Envío B4 por SMTP contra un servidor local de prueba, ejecutado dos veces
   para comprobar la idempotencia.

## 2. Resultados del pipeline

| Momento | Ventas COP | Transacciones |
| :--- | ---: | ---: |
| Antes del delta | 954.497.200 | 2.440 |
| Después del delta | 916.270.700 | 2.452 |

- Base: 5.965 filas leídas, 5.651 cargadas, 314 descartadas.
  - 140 duplicados exactos, 140 versiones obsoletas, 24 del punto de pruebas,
    6 valores inválidos y 4 códigos inválidos.
- Delta: 2.111 filas leídas, 2.110 cargadas, 1 versión obsoleta.
  - 2.005 insertadas, 52 actualizadas y 53 ignoradas.
- Hecho final: 7.656 transacciones; la reejecución de la base no inserta ni
  actualiza filas (idempotencia verificada).

## 3. Consultas B3

- **Top 3 por zona:** devuelve hasta tres puntos por zona, con desempate por
  código. Ejemplo: en Urabá lideran Turbo, Apartadó y Carepa.
- **Puntos activos sin ventas:** Castilla (00109), Andes (00125) y Yarumal
  (00131).
- **Variación por zona:** Urabá aparece con variación `N/A` porque no tuvo
  ventas el 26/10; el reporte no divide por cero.

El resultado completo está en `salida/consultas_20261027.txt`.

## 4. Reportes y artefactos

- `salida/antes/reporte_ventas_20261027.xlsx` y `.eml`
- `salida/despues/reporte_ventas_20261027.xlsx` y `.eml`
- `salida/reporte_ventas_20261027.xlsx` (copia final después del delta)
- `salida/consultas_20261027.txt`
- `salida/powerbi/*.csv` (hecho y dimensiones)
- `salida/smtp.log` y `salida/envios_smtp.json` (B4)

## 5. Envío idempotente B4

La primera ejecución envió el correo a un `DebuggingServer` local y registró
la clave de idempotencia. La segunda respondió:

```text
Ya registrado con la clave ...; no se envía de nuevo.
```

El servidor local recibió el asunto del reporte. Así se demuestra el envío real
sin depender de un SMTP corporativo y se evita el correo duplicado del script
original, sin ocultar fallas.

## 6. Pruebas

- `pytest`: 65 pruebas en verde (también dentro del contenedor).
- `ruff check .`: sin hallazgos (también dentro del contenedor).
- `openspec validate --changes --strict`: 6/6 cambios válidos.
- `make podman-test`: 65 pruebas dentro del contenedor.

## 7. Limitaciones

- El demo usa datos de prueba del kit; no toca producción.
- Power BI Desktop no está disponible en macOS: se exportan los CSV y se
  entrega el diseño/DAX; el `.pbix` queda pendiente de un equipo Windows.
- El SMTP del demo es un servidor local de prueba; no se envía a un servidor
  corporativo real. El modo `.eml` sigue disponible para entornos sin SMTP.
