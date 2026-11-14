# Parte A — Componente teórico

> **En progreso:** A1 a A4 respondidas; A5 a A10 pendientes. Se procesa al
> final, después de B1 a B6.

Cada respuesta debe incluir su justificación y no superar 8 líneas, como pide
la prueba. Esta sección alimenta la sección 1 del informe consolidado.

## A1. SQL — LEFT JOIN y filtro en WHERE

**Respuesta:** No cumple. El `OR t.valor = 0` no crea filas para los puntos
sin transacciones: `t.estado` y `t.valor` son NULL y `NULL = 'APROBADA' OR
NULL = 0` da UNKNOWN, así que el WHERE los elimina (y además incluye ceros no
aprobados). Se mueve el filtro al `ON` y se usa `COALESCE(SUM(t.valor), 0)`.

```sql
SELECT p.cod_punto, p.nombre, COALESCE(SUM(t.valor), 0) AS ventas
FROM puntos_venta p
LEFT JOIN transacciones t ON t.cod_punto = p.cod_punto AND t.estado = 'APROBADA'
GROUP BY p.cod_punto, p.nombre;
```

## A2. SQL — COUNT y NULL

**Respuesta:** La primera devuelve **700** y la segunda **0**. `estado <>
'ANULADA'` cuenta las 700 APROBADA; las 200 ANULADA no cumplen y las 100 NULL
quedan en UNKNOWN, que el `WHERE` descarta. En la segunda, `NOT IN ('ANULADA',
NULL)` equivale a `estado <> 'ANULADA' AND estado <> NULL`; como `x <> NULL` es
UNKNOWN para toda fila, ninguna pasa y el `COUNT` es 0.

**Para contar las 800 no anuladas incluyendo NULL:** `WHERE estado <> 'ANULADA'
OR estado IS NULL`. Para las 700 no nulas: `NOT IN ('ANULADA')`, sin el NULL.

## A3. Python — suma con float

**Respuesta:** No es solo redondeo: `float` usa binario y no representa exacto
valores como 0,10; al sumar miles el error se acumula. Se resuelve leyendo los
importes como texto y sumando con `Decimal` (o enteros de centavos), con
precisión y `ROUND_HALF_UP` solo al presentar; el separador decimal se
interpreta con el locale y los nulos se validan/normalizan antes de sumar.
**Otras capas:** parseo CSV, base (`FLOAT` vs `DECIMAL`), SQL, Excel/Power BI
y APIs/JSON que serializan como float.

## A4. RPA — Selenium y esperas

**Respuesta:** El `sleep(5)` espera tiempo, no al elemento: si el agente tarda
más, hay login/error, iframes/overlays o cambian los locators, el clic lanza
`NoSuchElementException`; también influyen headless, driver, red/VPN y sesión.
Se robustece con `WebDriverWait` + `expected_conditions`, locators estables,
reintentos con backoff, screenshot/logs y Chrome/driver fijados en contenedor.
No usaría RPA si el banco ofrece API/SFTP/DB, exige MFA/captcha no automatizable
o el volumen/frecuencia hacen el bot frágil; conviene integración o archivo
contratado.

## A5. Jenkins — zona horaria del cron

## A6. ETL — idempotencia y reintentos

## A7. Seguridad y Git — secreto en el repositorio

## A8. Carga incremental — anulaciones tardías

## A9. Modelado — historia de zonas

## A10. Criterio — automatizar un proceso manual
