# Prueba Técnica — Solución de Arquitectura de Software | PagaRed S.A.S.

**Candidato:** Jhon E.

Repositorio de la solución a la prueba técnica de Desarrollador de Arquitectura
de Software. El caso pide automatizar el reporte diario de ventas de PagaRed,
persistir los datos para Power BI y operar el pipeline de forma confiable.

> Proyecto en construcción: la estructura y las convenciones base se crean en
> este commit; el análisis, el pipeline y los entregables se agregan en los
> siguientes.

## Estructura

```text
etl/        Pipeline de datos (B2)
tests/      Pruebas con pytest (B2)
sql/        Consultas (B3)
revision/   Revisión de código (B4)
infra/      Dockerfile y despliegue (B5)
powerbi/    Tablero y medidas DAX (B6)
salida/     Reportes generados
docs/       Informe y diagramas
datos/      Archivos de entrada del kit
```
