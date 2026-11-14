# Parte 6 — B6: Tablero de Power BI

Diseño del tablero de una página para Laura, con indicadores del día,
comparación por zona y producto, variación contra el día anterior, filtros y
medidas DAX explícitas.

## Contenido

- `powerbi/`: diseño, medidas DAX y capturas si hay acceso a Windows.
- `scripts/exportar_datos.py`: exporta el hecho y las dimensiones a CSV para
  conectarlos desde Power BI en macOS.
- `features/tablero-ventas.feature`: historia Gherkin del tablero.

## Exportación de datos

```bash
make bi-export   # CSV del hecho y las dimensiones en powerbi/datos/
```

El demo de Podman también los deja en `salida/powerbi/`.

## Limitación

Power BI Desktop solo funciona en Windows. En macOS se entrega el diseño, las
medidas DAX y los datos exportados; la limitación se documenta en la sección 7
del informe.
