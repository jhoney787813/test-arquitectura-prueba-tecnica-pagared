# Proposal

## Why

El correo de Laura contiene reglas de negocio incompletas y supuestos que
afectan todo el pipeline: qué estados cuentan como venta, cómo se delimita el
día, qué pasa con los puntos sin zona y cómo se evita el doble envío. Antes de
construir B2 a B6 hay que dejar explícito qué se entendió, qué se preguntó y
qué se asumió.

## What Changes

- Se documentan los requerimientos funcionales y no funcionales del correo y
  del contexto de la prueba.
- Se listan las ambigüedades y riesgos con al menos cinco preguntas concretas
  para Laura.
- Se registran los supuestos adoptados para avanzar sin sus respuestas.
- Se publica la propuesta de solución con diagrama de arquitectura, modelo de
  datos, estrategia de alertas, idempotencia y control de doble envío.
- Se define el plan de entrega por fases, con lo que Laura recibe el lunes y lo
  que queda para después.

No se modifica comportamiento de software: esta feat produce el análisis y los
diagramas que alimentan el informe y las demás feats.

## Capabilities

### New Capabilities

Ninguna. Es una feat de documentación y análisis; por eso el cambio declara
`skip_specs: true`. Las capacidades de software se especifican en B2 a B6.

### Modified Capabilities

Ninguna.

## Impact

- `docs/informe.md` (sección 2).
- `docs/arquitectura.mmd` y `docs/modelo_datos.mmd`.
- `README.md` y el futuro informe PDF.
- No toca código, datos ni infraestructura.
