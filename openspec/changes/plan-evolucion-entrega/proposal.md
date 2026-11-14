# Proposal

## Why

La solución técnica está implementada y verificada, pero quedan brechas de
cumplimiento formal y de trazabilidad que no se cerraron en esta entrega: B1
excede dos páginas, faltan diagramas renderizados en el PDF, la estructura
literal de la raíz no coincide, falta invitar al evaluador y OpenSpec necesita
cerrar tareas y cambios.

Este cambio no implementa esas mejoras: las deja planificadas y verificables
para futuras iteraciones.

## What Changes

- Planificar el recorte de B1 a dos páginas y la inclusión de los diagramas de
  arquitectura y modelo.
- Planificar la compatibilidad de la estructura raíz (`etl/`, `tests/`, `sql/`,
  `revision/`, `infra/`, `powerbi/`) y el `infra/Dockerfile` literal.
- Planificar la invitación de `Cristian-AS` al repositorio privado.
- Planificar la evidencia explícita de todos los archivos del incidente B5.
- Planificar el `.pbix`, las capturas reales y la RLS de B6.
- Planificar el cierre/archivo de los cambios OpenSpec completados.

## Capabilities

### New Capabilities

Ninguna: es un plan de evolución documental. El cambio declara
`skip_specs: true`.

### Modified Capabilities

Ninguna.

## Impact

- Informe PDF, README y OpenSpec.
- No cambia el comportamiento del pipeline ni del tablero publicado.
