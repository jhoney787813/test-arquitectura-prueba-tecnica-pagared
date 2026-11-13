# Power BI — Tablero de ventas (B6)

## Limitación del entorno

El equipo de trabajo es **macOS** y Power BI Desktop solo funciona en Windows.
Por eso el repositorio entregará:

1. El **diseño del tablero** y las **medidas DAX** documentadas.
2. Los **datos del modelo** exportados a CSV/Parquet para que el tablero se
   pueda abrir o reconstruir en Windows sin depender de la base local.
3. Las **capturas** del tablero y de la vista de modelo cuando se ejecute en un
   equipo Windows (o la indicación explícita de esta limitación en el informe,
   como permite la prueba).

El archivo `tablero_ventas.pbix` se agrega únicamente si se cuenta con Power BI
Desktop; no se inventa un `.pbix` que no haya sido abierto y validado.

## Fuente de datos prevista

- Opción A: conexión directa a `dw_pagared` (PostgreSQL o SQLite con el
  controlador ODBC correspondiente).
- Opción B: conexión a los CSV/Parquet exportados desde el modelo
  (`powerbi/datos/`), que es la ruta recomendada para la sustentación en macOS.

## Modelo en estrella

`fact_transacciones` se relaciona con `dim_fecha`, `dim_punto` (zona),
`dim_producto`, `dim_canal` y `dim_estado`. La vigencia SCD2 de `dim_punto`
evita que un cambio de zona reescriba el pasado.

## Medidas DAX (borrador)

```dax
Ventas =
CALCULATE(
    SUM(fact_transacciones[valor_cop]),
    dim_estado[cuenta_como_venta] = 1
)

Transacciones =
CALCULATE(
    COUNTROWS(fact_transacciones),
    dim_estado[cuenta_como_venta] = 1
)

Ticket promedio = DIVIDE([Ventas], [Transacciones])

Ventas día anterior =
CALCULATE(
    [Ventas],
    DATEADD(dim_fecha[fecha], -1, DAY)
)

Variación vs día anterior =
VAR Anterior = [Ventas día anterior]
RETURN
    IF(
        ISBLANK(Anterior) || Anterior = 0,
        BLANK(),
        DIVIDE([Ventas] - Anterior, Anterior)
    )
```

`Variación vs día anterior` devuelve vacío cuando la zona no tenía ventas el
día previo (por ejemplo, los puntos nuevos de Urabá abiertos el 27/10), en
lugar de dividir por cero.

## Seguridad por filas (opcional)

RLS sobre `dim_punto[zona]` con una tabla de usuarios por zona; cada gerente ve
solo su zona. Se documentará el rol y la expresión DAX `[zona] = USERPRINCIPALNAME()`
en la sección 7 del informe.

## Pendientes

- [ ] Exportar hechos y dimensiones a `powerbi/datos/`
- [ ] Validar las medidas en Power BI Desktop (Windows)
- [ ] Capturas del tablero (27/10) y de la vista de modelo
- [ ] RLS y publicación en el servicio (si aplica)
