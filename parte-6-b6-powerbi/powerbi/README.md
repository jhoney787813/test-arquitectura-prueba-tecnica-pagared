# Power BI — Tablero de ventas (B6)

## Limitación del entorno

El equipo de trabajo es **macOS** y Power BI Desktop solo funciona en Windows.
La prueba permite este escenario: entregar el **diseño**, las **medidas DAX** y
los **datos exportados**, e indicar la limitación en el informe. No se inventa
un `.pbix` que no haya sido abierto y validado.

## Entregado

- `DISENO_TABLERO.md`: modelo, página, visuales, filtros, RLS y pasos para
  construirlo en Windows.
- `medidas.dax`: ventas, transacciones, ticket, día anterior y variación.
- `datos/`: hecho y dimensiones exportados a CSV (`make bi-export`).
- `tablero_ventas.html`: **prototipo funcional** generado desde `dw_pagared`
  con filtros de fecha, zona y canal, KPIs y variación (`make b6-dashboard`).
- `capturas/tablero_20261027.png`: captura del prototipo con el 27/10. Está
  marcada como prototipo, no como Power BI Desktop.

## Comandos

```bash
make b6            # datos + HTML + captura
make b6-dashboard  # solo el HTML
make bi-export     # solo los CSV
```

## Pendiente (requiere Windows)

- [ ] Construir y validar `tablero_ventas.pbix` en Power BI Desktop.
- [ ] Capturas reales del tablero y de la vista de modelo.
- [ ] Probar RLS con “Ver como rol”.
- [ ] Publicar en el servicio si aplica.
