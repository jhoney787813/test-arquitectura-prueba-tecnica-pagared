# Design

## Context

El análisis ya está redactado en `docs/informe.md` (sección 2) a partir del PDF
de la prueba y del correo de Laura. Esta feat lo ordena, lo valida contra los
datos reales y lo deja listo para el informe de máximo dos páginas.

## Goals / Non-Goals

**Goals:**

- Que cada requerimiento del correo tenga un identificador y un criterio de
  aceptación rastreable hacia B2-B6.
- Que las preguntas para Laura sean concretas y las respuestas pendientes no
  bloqueen la construcción.
- Que la arquitectura y el plan de fases se entiendan sin leer código.

**Non-Goals:**

- Implementar el pipeline o el tablero.
- Responder las preguntas de negocio por la Gerente Comercial.
- Escribir la Parte A, que se procesa al final.

## Decisions

- **Un documento fuente:** `docs/informe.md` es la fuente de la sección 2; el
  PDF se compila al final para no duplicar contenido.
- **Mermaid versionado:** los diagramas viven en `docs/` como texto para que se
  puedan revisar y versionar; el PDF los incluye como imagen.
- **Supuestos explícitos:** cada supuesto tiene su contrapartida en una pregunta
  o en una tarea de B2-B6, para que el evaluador vea la trazabilidad.
- **Corte de dos páginas:** la sección se recorta al final; el detalle técnico
  se delega en las especificaciones de B2 a B6.

## Risks / Trade-offs

- **Supuesto equivocado sobre el día contable** → se valida con los datos (652
  filas del 28 UTC pertenecen al 27 en Colombia) y se prueba en B2.
- **Preguntas sin respuesta** → se avanza con los supuestos documentados y se
  marcan como preguntas abiertas en el informe.
- **Sección demasiado larga para el PDF** → recorte final y enlaces a las
  especificaciones detalladas.

## Migration Plan

No aplica: es documentación. Se actualiza el informe y se recompila el PDF.

## Open Questions

- Nombre completo para `INFORME_<nombre>.pdf`.
- Confirmación de las preguntas 1 a 8 del informe por parte de Laura.
