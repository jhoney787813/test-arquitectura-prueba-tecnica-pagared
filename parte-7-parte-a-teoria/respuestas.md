# Parte A — Componente teórico

> **En progreso:** A1 a A8 respondidas; A9 y A10 pendientes. Se procesa al
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

**Respuesta:** Se ejecuta a la **1:00 a. m.** de Colombia (06:00 UTC − 5 h),
no a las 6:00; el comentario es incorrecto. Para las 6:00 COT: (1) usar
`0 11 * * *` en UTC; (2) mantener `0 6 * * *` y declarar la zona con
`TZ=America/Bogota` en el trigger (`cron('TZ=America/Bogota\n0 6 * * *')`).
La primera es portable; la segunda deja la intención explícita. Colombia no
tiene horario de verano, así que 11:00 UTC son siempre las 6:00 COT. No
cambiaría la zona del servidor: afecta todos los jobs.

## A6. ETL — idempotencia y reintentos

**Respuesta:** El reintento duplica porque el cargue no es idempotente. La
tabla de hechos debe tener una clave natural (`id_transaccion`) con `UNIQUE`, y
el cargue debe hacer `UPSERT` (o borrar/insertar la fecha dentro de una
transacción) para que repetirlo deje el mismo resultado. Una columna de estado
sirve para auditar y decidir si se reprocesa, pero no evita duplicados si
quedaron filas parciales: el lote debe ser transaccional o usar staging + merge.
En Jenkins, `disableConcurrentBuilds()` y un lock evitan dos ejecuciones; no
mataría el proceso anterior a ciegas porque puede dejar escrituras a medias.

## A7. Seguridad y Git — secreto en el repositorio

**Respuesta:** No está resuelto: el commit conserva el secreto en el historial,
y también puede estar en clones, forks, cachés de CI y logs. Primero se rota y
revoca la contraseña de producción y se auditan accesos; luego se elimina del
historial con `git filter-repo` (o BFG) y se hace force-push coordinado,
sabiendo que hay que purgar copias y cachés. Después se previene: `.env` en
`.gitignore`, `.env.example`, escaneo de secretos (gitleaks/GitLab), permisos
mínimos y gestor de secretos. Un `rebase` no basta y no debe ser el primer paso.

## A8. Carga incremental — anulaciones tardías

**Respuesta:** Porque el incremental filtra por `fecha_transaccion`, no por la
fecha de modificación: una venta del día 10 anulada el 12 conserva su
`fecha_transaccion` del 10 y queda fuera del próximo cargue, así que el tablero
sigue mostrando el estado viejo. Rediseñaría con un watermark de
`fecha_actualizacion` (con ventana de solape), un `MERGE/UPSERT` por
`id_transaccion` que actualice solo si la modificación es más reciente, y el
delta/CDC del core como fuente de cambios. Agregaría control de cargas y una
reconciliación periódica contra el core para detectar cambios o borrados perdidos.

## A9. Modelado — historia de zonas

## A10. Criterio — automatizar un proceso manual
