# Diseño del tablero de Power BI (B6)

## 1. Limitación del entorno

Power BI Desktop solo funciona en Windows. El desarrollo de esta prueba se hizo
en macOS, por lo que **no se generó un `.pbix` ni capturas de Power BI
Desktop**. La prueba permite explícitamente este camino: entregar el diseño, las
medidas DAX y los datos exportados, e indicar la limitación en el informe.

Para demostrar que el modelo soporta el tablero, esta carpeta incluye un
**prototipo HTML funcional** generado desde `dw_pagared` con los mismos
indicadores, filtros y variación. No es un `.pbix`; es una maqueta ejecutable
del diseño.

## 2. Fuente de datos

- Opción A (recomendada para la sustentación): CSV exportados por
  `make bi-export` en `powerbi/datos/`:
  - `fact_transacciones.csv`
  - `dim_punto.csv`, `dim_fecha.csv`, `dim_producto.csv`, `dim_canal.csv`,
    `dim_estado.csv`
- Opción B: conexión directa a `db/pagared.db` con el conector ODBC de SQLite
  (si está disponible en Windows).

## 3. Modelo

Relaciones en estrella, todas de uno a muchos desde la dimensión al hecho:

```text
dim_fecha ──┐
dim_punto ──┼──< fact_transacciones >── dim_producto
dim_canal ──┤                     └──── dim_estado
             └── usuarios_zona (solo RLS)
```

- `fact_transacciones[valor_cop]` en pesos enteros.
- `dim_punto` conserva versiones SCD2 (`valido_desde`, `valido_hasta`,
  `es_actual`) para que la zona sea la vigente a la fecha de la venta.
- `dim_estado[cuenta_como_venta]` marca APROBADA y REVERSADA.
- Marcar `dim_fecha[fecha]` como **tabla de fechas** para que `DATEADD`
  funcione.

## 4. Página del tablero

Una sola página, pensada para Laura:

1. **Encabezado** con fecha seleccionada y nota de regla de negocio.
2. **Tres tarjetas KPI:** ventas del día, número de transacciones y ticket
   promedio.
3. **Barras por zona:** comparación directa entre territorios.
4. **Barras por producto:** RECARGA, PAGO_SERVICIOS y GIRO.
5. **Tabla de variación por zona:** ventas del día, del día anterior y
   variación porcentual; `N/A` cuando no hay base.
6. **Segmentaciones:** fecha, zona y canal, aplicadas a toda la página.

### Por qué estos visuales

Laura necesita responder “cómo vamos hoy contra ayer” y “qué zona/producto
explica el cambio”. Las tarjetas dan el pulso del día, las barras comparan
territorios y productos, y la tabla de variación evita que una zona nueva
(Urabá sin ventas el 26) rompa el cálculo con una división por cero.

## 5. Medidas DAX

Ver [`medidas.dax`](medidas.dax). Las principales:

- `Ventas`: suma con `dim_estado[cuenta_como_venta] = 1`.
- `Transacciones`: conteo de filas válidas.
- `TicketPromedio`: `DIVIDE([Ventas], [Transacciones])`.
- `VentasDiaAnterior`: `DATEADD(dim_fecha[fecha], -1, DAY)`.
- `VariacionVentas`: `BLANK()` si no hay base; evita dividir por cero.
- `VariacionTransacciones`: equivalente para el volumen.

## 6. Construcción en Windows

1. Abrir Power BI Desktop.
2. `Obtener datos` → `Texto/CSV` y cargar los seis CSV de `powerbi/datos/`.
3. Crear las relaciones del modelo en estrella.
4. Marcar `dim_fecha` como tabla de fechas.
5. Crear las medidas de `medidas.dax`.
6. Agregar las tarjetas, los dos gráficos de barras, la tabla y las
   segmentaciones.
7. Guardar como `powerbi/tablero_ventas.pbix`.
8. Tomar capturas del tablero con el 27/10 seleccionado y de la vista de modelo.

## 7. RLS opcional

Crear una tabla `usuarios_zona(email, zona)` y un rol `Zona`:

```dax
dim_punto[zona] =
LOOKUPVALUE(
    usuarios_zona[zona],
    usuarios_zona[email],
    USERPRINCIPALNAME()
)
```

Cada gerente verá solo su zona; el rol se prueba en Power BI Desktop con
“Ver como rol”.

## 8. Prototipo y captura

- `tablero_ventas.html`: prototipo autónomo (sin CDN) generado con
  `make b6-dashboard`.
- `capturas/tablero_20261027.png`: captura del prototipo con la fecha 27/10,
  claramente marcada como prototipo, no como Power BI.

El prototipo permite cambiar fecha, zona y canal; calcula ventas,
transacciones, ticket y variación contra el día anterior con la misma lógica
de las medidas DAX.
