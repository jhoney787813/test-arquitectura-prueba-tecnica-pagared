# Informe consolidado — Prueba Técnica de Arquitectura de Software

**Candidato:** Jhon E.  
**Empresa (caso ficticio):** PagaRed S.A.S. — Grupo Réditos  
**Fecha de corte de los resultados:** 27 de octubre de 2026  
**Versión del documento:** borrador de trabajo (se compila a PDF al final)

> Este archivo es la fuente del informe `INFORME_Jhon_E.pdf`. Las secciones 1 y
> 3 a 7 se completan a medida que avanza la solución; la sección 2 (B1) ya está
> desarrollada porque es la entrada de las partes B2 a B6.

---

## 1. Componente teórico (Parte A)

> **En progreso:** A1 a A7 respondidas; A8 a A10 pendientes. El texto completo
> se redacta en [respuestas.md](../parte-7-parte-a-teoria/respuestas.md) y se
> incorpora a esta sección al compilar el PDF.

---

## 2. Análisis del requerimiento (B1)

### 2.1 Lectura del correo y del contexto

Laura pide reemplazar un proceso manual de tres horas por un reporte diario que
llegue a las 6:00 a. m. con las ventas del día anterior, por zona y producto.
El correo define tres reglas de negocio (qué cuenta como venta, exclusión del
punto de pruebas y comparativo contra el día anterior), dos requisitos
operativos (alertar si el archivo no llega y no enviar dos veces) y uno
estratégico (persistir los datos para el tablero de BI).

El contexto técnico agrega una restricción central: **el core exporta en UTC**,
mientras el negocio habla de días calendario de Colombia. Por eso el pipeline
no puede filtrar por la fecha “tal como viene”: debe convertir cada instante a
`America/Bogota` antes de asignar el día contable. En los datos del kit, 652 de
las 662 filas con fecha UTC del 28/10 pertenecen al 27/10 en Colombia; ignorar
la zona horaria perdería la venta de toda la tarde-noche del día de corte.

### 2.2 Requerimientos funcionales

| Id | Requerimiento | Criterio de aceptación |
| :--- | :--- | :--- |
| RF-01 | Leer transacciones y maestro de puntos del core | Acepta UTF-8 con BOM y Latin-1, separador `;` |
| RF-02 | Delimitar el día contable 00:00–23:59 en America/Bogota | El reporte del 27/10 incluye la noche del 27, no la madrugada UTC del 28 |
| RF-03 | Contar como venta `APROBADA` y `REVERSADA` | `ANULADA` y `RECHAZADA` no suman; la reversada sí |
| RF-04 | Excluir el punto de pruebas `90001` | No aparece en el reporte ni en los totales |
| RF-05 | Resumir ventas y número de transacciones por zona y producto | Cuadra contra el total del día |
| RF-06 | Comparar contra el día anterior por zona | Variación absoluta y porcentual; zona sin día previo no divide por cero |
| RF-07 | Generar `reporte_ventas_YYYYMMDD.xlsx` con 3 hojas | Resumen, Comparativo y Calidad con motivos |
| RF-08 | Persistir el resultado en un modelo dimensional | Power BI puede conectarse a hechos y dimensiones |
| RF-09 | Aplicar el delta del 28/10 sobre lo ya cargado | Inserta nuevas, actualiza cambiadas e ignora obsoletas |
| RF-10 | Permitir ejecutar N veces la misma fecha | No duplica filas ni totales |
| RF-11 | Alertar si el archivo no llega o el proceso falla | Notificación accionable y salida distinta de cero |
| RF-12 | Evitar el envío duplicado del correo | Una sola entrega por fecha y versión de reporte |
| RF-13 | Registrar leídos, descartados por motivo, cargados y cambios | Log + tablas de auditoría consultables |
| RF-14 | Dejar el correo listo sin servidor SMTP corporativo | Se genera un `.eml` con el reporte adjunto |

### 2.3 Requerimientos no funcionales

| Id | Requerimiento | Decisión |
| :--- | :--- | :--- |
| RNF-01 | Disponible antes de las 6:00 a. m. | Job a las 4:00 a. m. y SLA de 20 minutos; alerta si no termina |
| RNF-02 | Idempotente y recuperable | `UPSERT` por `id_transaccion`, control de cargas y *ledger* de envíos |
| RNF-03 | Auditable | Log estructurado + `etl_cargas`, `etl_descartes`, `etl_envios` |
| RNF-04 | Seguro | Credenciales solo en Jenkins/AWS; `.env` fuera del repositorio |
| RNF-05 | Portable | Contenedor Docker con Python 3.11 y SQLite/PostgreSQL |
| RNF-06 | Observable | Logs con contadores, exit code distinto de 0 y alerta por correo/Teams |
| RNF-07 | Exacto en dinero | `Decimal` en Python y pesos enteros en la base; nunca `float` para sumas |
| RNF-08 | Mantenible | `ruff`, `pytest`, CI y funciones pequeñas con docstring |
| RNF-09 | Privado | Repositorio privado; sin datos personales ni secretos |
| RNF-10 | Escalable en producción | Hechos por fecha, índices y camino a Parquet/Azure SQL |

### 2.4 Ambigüedades, riesgos y preguntas para Laura

| # | Ambigüedad o riesgo | Pregunta concreta |
| :---: | :--- | :--- |
| 1 | “Lo reversado sí cuenta” no dice si se suma el valor completo o solo la comisión; no hay campo de comisión en el archivo | ¿La venta reversada se reporta por el valor total de la transacción o solo por la comisión cobrada? |
| 2 | Solo se identifica el punto de pruebas por el nombre y el código `90001`; puede haber otros puntos internos | Además de `90001`, ¿qué códigos o nombres deben excluirse de los informes? |
| 3 | Las zonas cambian en el tiempo (caso A9); el reporte histórico puede reescribirse | Para un informe de 2024, ¿la zona debe ser la vigente en la fecha de la venta o la del maestro actual? |
| 4 | El delta llega a las 6:00 p. m.; las anulaciones posteriores no entran al reporte de la mañana siguiente | Si una transacción del 27 se anula el 29, ¿se reenvía una corrección del 27 o solo se refleja en el tablero? |
| 5 | “Que me avise” no define canal ni destinatario de la alerta | Si el archivo no llega a las 5:00 a. m., ¿a quién y por qué medio se alerta? ¿Se envía el reporte más tarde? |
| 6 | No se define el alcance del correo (solo Laura, copia a BI, adjunto o resumen en el cuerpo) | ¿Quiénes deben recibir el correo y prefieren el Excel adjunto o un resumen ejecutivo en el cuerpo? |
| 7 | El maestro no trae la zona “Sur” que menciona el caso A9 y tiene una zona vacía (00133) | ¿La zona “Sur” ya existe en producción? ¿Cómo se cargará y qué hacer con puntos sin zona? |
| 8 | El punto 00117 está duplicado en el maestro con zona distinta | ¿Es un traslado del punto o dos puntos distintos con el mismo código? |

Riesgos principales: archivo que no llega o llega incompleto (R1), delta
reenviado o incompleto (R2), cambios de estado posteriores al envío (R3),
maestro desactualizado (R4), error de zona horaria (R5), doble envío por
reintentos de Jenkins (R6) y dependencia del refresh de Power BI (R7).

### 2.5 Supuestos adoptados para avanzar

1. El día contable es `America/Bogota` y `fecha_transaccion` viene en UTC.
2. Ventas = `APROBADA` + `REVERSADA`; se suma el valor completo de la
   transacción porque no existe un campo de comisión.
3. Se excluye el punto `90001` por código; no hay otros puntos internos
   identificables en el kit.
4. Los valores están en pesos colombianos enteros; `522.500` significa
   $522.500 y no $522,50.
5. Gana la fila con `fecha_actualizacion` más reciente para cada
   `id_transaccion`; las filas idénticas se descartan.
6. El índice de zona es el vigente a la fecha de la transacción (SCD2). Para
   `00117` se interpreta como traslado: Oriente hasta 2024-03-03 y Valle de
   Aburrá desde 2024-03-04.
7. El punto `00199` (12 transacciones) no existe en el maestro: se reporta como
   `NO CATALOGADO` y se deja la venta visible. La zona vacía del `00133` se
   reporta como `SIN ZONA`; en ningún caso se descarta la venta.
8. Los puntos inactivos conservan sus ventas históricas; la lista de “puntos
   sin ventas” de B3 solo considera puntos activos.
9. El reporte “del 27/10” usa el estado más reciente disponible después del
   delta del 28/10 a las 6:00 p. m.
10. Sin SMTP corporativo, el entregable es el Excel más un borrador `.eml`
    listo para enviar.

### 2.6 Propuesta de solución

**Componentes.** Un job de Jenkins en el agente `agente-etl` dispara a las 4:00
a. m. (America/Bogota) un contenedor Python. El contenedor valida la llegada y
el layout de los archivos, limpia y normaliza, carga dimensiones y hechos en
`dw_pagared`, genera el Excel y deja el correo listo. Power BI consume el
modelo; el mismo job alimenta las alertas. El diagrama completo está en
[arquitectura.mmd](arquitectura.mmd).

**Dónde se ejecuta.** En el corto plazo, el agente Linux existente
(`agente-etl`, 1 ejecutor) con Docker; la base puede ser SQLite para la prueba
y PostgreSQL en el servidor. La misma imagen corre en AWS (ECS Fargate o Batch
+ EventBridge) si se quiere sacar del servidor on-premise.

**Modelo de datos.** Hecho `fact_transacciones` con grano por
`id_transaccion`, dimensiones `dim_fecha`, `dim_punto` (con vigencia SCD2),
`dim_producto`, `dim_canal` y `dim_estado`. Tablas de auditoría `etl_cargas`,
`etl_descartes` y `etl_envios`. Ver [modelo_datos.mmd](modelo_datos.mmd).

**Cómo evita duplicados en la carga.** `UNIQUE(id_transaccion)` en el hecho,
`INSERT ... ON CONFLICT DO UPDATE` para el delta y una tabla de control por
`fecha_corte` y archivo. Reejecutar el mismo día reemplaza el resultado de esa
fecha, no lo suma.

**Cómo evita el doble envío.** El envío se registra en `etl_envios` con una
clave única `(fecha_corte, tipo, version)`; si la clave ya está en estado
`ENVIADO`, el job no vuelve a enviar. Si el SMTP falla, queda `FALLIDO` y el
reintento es seguro. Además, `disableConcurrentBuilds()` evita dos ejecuciones
simultáneas del job.

**Cómo alerta.** Si el archivo no aparece, si el layout no cumple el contrato o
si el proceso termina con error, el job publica una alerta (correo/Teams) con
el motivo y el enlace al log, y termina con exit code distinto de 0. Un
`timeout` del pipeline evita que el reporte llegue después de las 6:00 sin
aviso.

### 2.7 Plan de entrega por fases

| Fase | Qué recibe Laura | Cuándo |
| :--- | :--- | :--- |
| 0. Preparación | Repositorio, perfilado de datos y este análisis | Día 1 |
| 1. MVP | Reporte del 27/10 generado por el pipeline, con las 3 hojas y el modelo cargado; pruebas y consultas | “El lunes” |
| 2. Operación | Job programado a las 4:00 a. m., alerta por archivo faltante, `.eml` y tablero de Power BI | Semana 1 |
| 3. Evolución | Envío SMTP real, RLS por zona, histórico SCD2 completo, Parquet/S3 y monitoreo | Semanas 2–4 |

---

## 3. Pipeline de datos (B2)

_Pendiente: reglas de limpieza, modelo implementado, resultados del 27/10 antes
y después del delta._

---

## 4. SQL (B3)

_Pendiente: consultas y resultados._

---

## 5. Revisión de código (B4)

_Pendiente: hallazgos por severidad y explicación de los síntomas._

---

## 6. Operación (B5)

_Pendiente: causa raíz del incidente, despliegue y conectividad con Azure._

---

## 7. Power BI (B6)

_Pendiente: medidas DAX, capturas y justificación._

---

## 8. Uso de IA

**Herramientas:** DeepSeek Harness (modelo `deepseek-flash`), OpenSpec 2.0,
GitHub Actions, `pytest` y `ruff`. El registro completo de la interacción, con
los prompts textuales y las evidencias, está en
[USO_IA_Y_PROMPTS.md](USO_IA_Y_PROMPTS.md).

### 8.1 Prompts relevantes

| # | Prompt (resumen) | Resultado verificable |
| :---: | :--- | :--- |
| 1 | “Creemos el proyecto que contendrá el repositorio de la solución” | Repositorio, perfilado de datos, 48 pruebas y análisis B1 |
| 2 | “Instala y configura OpenSpec según los requerimientos del PDF” | OpenSpec 2.0, skills DSH y plan con 7 capacidades |
| 3 | “Una feat por requerimiento; la Parte A al final” | Cambios B1-B4 separados y orden de trabajo explícito |
| 4 | “Pídeme autorización y registra mi justificación en OpenSpec” | Matriz de aprobaciones y AP-09 documentada |
| 5 | “Refactoriza por partes, raíz limpia y reglas Gherkin” | 7 carpetas `parte-*`, 9 `.feature` y 58 pruebas |

### 8.2 Correcciones o descartes de respuestas de la IA

1. **Plan monolítico descartado.** La IA propuso un único cambio con las 7
   capacidades y 45 tareas; se dividió en feats por parte para aprobar y
   sustentar cada etapa. Motivo: control del paso a paso y menor acoplamiento.
2. **Código en la raíz descartado.** Ante el conflicto con la estructura del
   PDF, la IA recomendó dejar el código en la raíz y usar `partes/` solo como
   índice; el usuario pidió empaquetarlo dentro de cada parte. Motivo:
   legibilidad y arquitectura limpia. Quedó en AP-09 y en
   [JUSTIFICACION_ESTRUCTURA.md](JUSTIFICACION_ESTRUCTURA.md).
3. **Gherkin faltante.** Los specs tenían requisitos y escenarios, pero no
   historias `.feature`; se agregaron 9 archivos, una regla en la configuración
   y una prueba de validación. Motivo: comprensión del agente y del evaluador.
4. **Ritmo sin autorización.** La IA venía ejecutando cambios de forma autónoma;
   el usuario exigió autorización previa y trazabilidad. Motivo: control humano
   y auditoría de decisiones.

### 8.3 Conclusión

La IA fue útil porque el contexto se entregó de forma explícita (PDF, CSV,
repositorio y validaciones) y porque cada instrucción definió un entregable
verificable. El juicio humano corrigió las decisiones que la IA optimizaba para
un criterio distinto (cumplir la letra del PDF) y las reemplazó por las que el
candidato podía sustentar. El resultado no es “código generado por IA”, sino un
repositorio con especificaciones, pruebas, CI, aprobaciones y decisiones
rastreables.
