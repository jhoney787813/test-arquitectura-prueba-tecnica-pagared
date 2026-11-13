# Uso de IA, contexto e ingeniería de prompts

## 1. Objetivo de este registro

Este documento deja trazabilidad de cómo se usó la IA durante la solución de la
prueba técnica de PagaRed: qué herramientas se emplearon, qué contexto se le
entregó, cuáles fueron los prompts principales y en qué casos se corrigió o
descartó una respuesta del modelo. También explica por qué la ingeniería de
prompts fue útil para llegar a un repositorio verificable y no a una colección
de respuestas sueltas.

El registro es una síntesis curada de la conversación completa. No se incluye
la transcripción cruda porque contenía un token de GitHub que fue redactado y
porque el objetivo es mostrar las decisiones, no el ruido de la sesión.

## 2. Herramientas y fuentes de contexto

| Herramienta / fuente | Uso |
| :--- | :--- |
| DeepSeek Harness (modelo `deepseek-flash`) | Agente que inspecciona archivos, ejecuta comandos, escribe código y documentación |
| PDF de la prueba (`Prueba_Tecnica_...pdf`) | Fuente de verdad de requisitos, puntajes y entregables; se extrajo a texto con `pypdf` |
| Kit `prueba_tecnica_kit/` | CSV reales, script de envío e incidente de recaudos |
| `git` + GitHub | Historial de commits, push, CI con GitHub Actions |
| [OpenSpec](https://openspec.dev) 2.x | Especificaciones, cambios, tareas y aprobaciones en el repositorio |
| Skills `.agents/skills/` | Flujo `/openspec-propose`, `/openspec-apply-change`, `/openspec-archive-change` en DeepSeek Harness |
| `pytest` + `ruff` | Verificación automática de comportamiento y estilo |
| Perfilador `parte-2-b2-pipeline/scripts/perfil_datos.py` | Evidencia reproducible de la calidad de los datos |

## 3. Línea de tiempo de la interacción

| # | Instrucción del usuario | Contexto que leyó el agente | Resultado verificable |
| :---: | :--- | :--- | :--- |
| 1 | “Creemos el proyecto que contendrá el repositorio de la solución” | PDF, kit, estructura del workspace | Repositorio, 3 commits, 48 pruebas, perfilado y análisis B1 |
| 2 | Configurar el token y hacer el primer push | Estado de Git, API de GitHub | `main` publicado, CI en verde |
| 3 | Instalar y configurar OpenSpec según los requisitos | PDF, CLI de OpenSpec | OpenSpec 2.0, skills DSH y cambio con 7 capacidades y 45 tareas |
| 4 | Una feat por requerimiento, Parte A al final | Cambio paraguas, requisitos B1-B6 | Cambios `b1` a `b4`; B5, B6 y A pendientes |
| 5 | Pedir autorización antes de cambiar y registrar la justificación | Estado del repositorio, OpenSpec | Matriz AP-01 a AP-08 y registro de aprobaciones |
| 6 | Refactorizar por partes y limpiar la raíz | Estructura actual, PDF, imports, tests | 7 carpetas `parte-*`, 58 pruebas, CI |
| 7 | Agregar reglas e historias Gherkin | Specs de OpenSpec, requisitos | 9 `.feature`, parser oficial y prueba automatizada |
| 8 | Justificar la estructura por arquitectura limpia | Estructura adoptada, PDF | `docs/JUSTIFICACION_ESTRUCTURA.md` y AP-09 |
| 9 | Revisar los chats y documentar la ingeniería de prompts | Conversación completa, commits, evidencias | Este documento |

## 4. Prompts principales

Se seleccionaron cinco instrucciones que cambiaron el rumbo del trabajo. Se
citan textualmente (se corrigieron solo espacios para legibilidad).

### P1. Crear el proyecto y entender el caso

> “creemos el proyecto que contendra el repositorio de la solucion de la prueba
> tecnica”

**Intención:** arrancar el repositorio, no escribir código a ciegas.
**Contexto usado:** PDF completo, kit de datos, estado del workspace.
**Resultado:** estructura base, copia de los CSV, perfilado de calidad, 48
pruebas, análisis B1 y tres commits (`17c035c`, `8210907`, `b228244`).
**Por qué funcionó:** el agente pudo convertir un enunciado breve en un plan
concreto porque leyó las fuentes antes de proponer.

### P2. Instalar y configurar OpenSpec

> “empecemos a solucionar la prueba para eso, instala en el proyecto y configura
> segun los requerimientos de la prueba tecnica que esta en el pdf...
> `npm install -g @fission-ai/openspec@latest`”

**Intención:** usar una capa de especificaciones, no prompts sueltos.
**Contexto usado:** PDF, requisitos B1-B6, CLI de OpenSpec.
**Resultado:** OpenSpec 2.0.0, integración `dsh`, `openspec/config.yaml` con el
contexto del caso, cambio con 7 capacidades y 45 tareas (commit `7c3c13b`).
**Por qué funcionó:** se pidió una herramienta y un resultado, no un tutorial;
el agente verificó la instalación y la validación estricta.

### P3. Una feat por parte y la teoría al final

> “ahora analiza lo que solicitan y creemos por cada requerimiento una feat que
> sera procesada con open spec, dejar de ultimo el punto 3. PARTE A. COMPONENTE
> TEÓRICO (30 PUNTOS). crea las reglas para los otros”

**Intención:** dividir el trabajo en unidades aprobables y dejar la teoría al
final.
**Contexto usado:** cambio paraguas, requisitos y orden de la prueba.
**Resultado:** cambios `b1-analisis-requerimiento`, `b2-pipeline-ventas`,
`b3-consultas-sql` y `b4-revision-envio`; B5, B6 y A quedaron para después.
**Por qué funcionó:** el prompt fijó el orden y el formato de trabajo; el agente
dejó de tratar la prueba como un bloque monolítico.

### P4. Autorización y trazabilidad

> “de aqui en adelante dejame o pideme autorizacion de los cambios que
> realizaras para yo aprobarlos, y de aprobarlos deja consignado los cambios
> con open spec como trazabilidad, donde yo justifique por que si y por que no”

**Intención:** que el humano controle el cambio y que la decisión quede
auditada.
**Contexto usado:** estado del repositorio, cambios activos.
**Resultado:** matriz AP-01 a AP-08, registro en
[`openspec/aprobaciones.md`](../openspec/aprobaciones.md) y el formato
`aprobacion.md` por cambio; AP-09 quedó aprobada con la justificación del
usuario.
**Por qué funcionó:** convirtió una preferencia (“avísame”) en un contrato
verificable: propuesta → decisión → justificación → commit.

### P5. Refactor por partes, raíz limpia y Gherkin

> “refactoriza el repositorio donde pongas codigo con las respuestas
> encarpetados con cada seccion es decir parte1 a parte N para mayor legibiidad”
>
> “agreguemos las reglas para que los requerimientos solicitados queden
> consignados en formato Gherkin ... para que en la raiz del proyecto solo quede
> lo de openspec, configuracion o archivos que no son netamente del codigo”

**Intención:** legibilidad por etapas, raíz como punto de composición y
historias de usuario legibles por el agente.
**Contexto usado:** estructura actual, PDF, imports, tests.
**Resultado:** 7 carpetas `parte-*`, 9 `.feature` validados, 58 pruebas, CI en
verde y AP-09 documentada (commits `18a1df8` y `4fb9762`).
**Por qué funcionó:** el prompt dio restricciones concretas (qué va en la raíz,
qué va en cada parte, formato Gherkin) y una justificación; el agente pudo
verificar el resultado con pruebas y validaciones.

## 5. Correcciones y descartes de respuestas de la IA

### Caso 1. Se descartó el plan monolítico de OpenSpec

La IA creó primero un único cambio `implementar-solucion-prueba-tecnica` con las
7 capacidades y 45 tareas. Era correcto en contenido, pero difícil de aprobar y
de sustentar por etapas. Con el prompt P3 se descartó como unidad de trabajo y
se dividió en cambios por parte.

**Motivo:** control del paso a paso, aprobación independiente y menor
acoplamiento entre entregables. El cambio paraguas queda temporalmente hasta
crear B5 y B6 y se retirará con AP-08.

### Caso 2. Se descartó la recomendación de dejar el código en la raíz

Ante el conflicto con la estructura literal del PDF, la IA propuso tres
opciones y recomendó la opción 1: dejar el código en `etl/`, `sql/`, etc. y usar
`partes/` solo como índice. El usuario insistió en que el código debe estar
empaquetado dentro de cada parte y que la raíz solo conserve configuración,
OpenSpec y archivos no-code.

**Motivo:** legibilidad por etapas y organización más limpia. La decisión se
registró como AP-09 y se mitigó el riesgo con la tabla de equivalencias y
[docs/JUSTIFICACION_ESTRUCTURA.md](JUSTIFICACION_ESTRUCTURA.md).

### Caso 3. Se corrigió la ausencia de Gherkin

Los specs de OpenSpec ya tenían requisitos y escenarios, pero no existían
archivos `.feature` con historias de usuario. El usuario pidió agregar esa capa
explícitamente.

**Motivo:** que el agente y el evaluador entiendan el negocio sin interpretar
solo el código. Resultado: 9 `.feature`, regla en `openspec/config.yaml` y una
prueba que valida sintaxis y cobertura por parte.

### Caso 4. Se corrigió el ritmo de trabajo sin autorización

La IA venía creando cambios y commits de forma autónoma. El usuario estableció
que, desde ese momento, debía pedir autorización y registrar su justificación.

**Motivo:** control humano y trazabilidad de decisiones. Resultado: matriz de
aprobaciones, AP-09 documentada y commits que referencian la aprobación.

## 6. Patrones de ingeniería de prompts que se usaron

| Patrón | Ejemplo en esta interacción | Efecto |
| :--- | :--- | :--- |
| Contexto + objetivo | “según los requerimientos del PDF”, adjuntando el PDF | Menos suposiciones; el agente lee la fuente |
| Restricciones medibles | “raíz solo OpenSpec/config”, “código en parte-1 a parte-N” | Resultado verificable, no ambiguo |
| Contrato de salida | “una feat por requerimiento”, “Gherkin”, “commit” | Formato predecible y repetible |
| Verificación exigida | tests, `openspec validate --strict`, CI | La IA no se autoevalúa: se comprueba |
| Gate humano | “pídeme autorización y registra mi justificación” | Control y auditoría |
| Iteración correctiva | “no; el código va dentro de las partes” | La IA ajusta el rumbo con evidencia |
| Seguridad | token redactado, `.env` ignorado, rotación | No se filtran credenciales |

## 7. Por qué la ingeniería de prompts fue útil

1. **Redujo la ambigüedad.** El PDF tiene reglas que se cruzan (UTC vs.
   Colombia, reversadas, punto de pruebas); pedir que se leyera y se documentara
   evitó decisiones inventadas.
2. **Hizo verificable el resultado.** Cada prompt relevante terminó en un
   artefacto concreto: commits, specs, features, pruebas y CI.
3. **Permitió dividir el problema.** Una prueba de 6 partes se convirtió en
   cambios independientes, aprobables y sustentables por separado.
4. **Dejó trazabilidad.** Las decisiones y sus motivos quedaron en OpenSpec y
   en AP-09, no solo en el chat.
5. **Aprovechó el contexto real.** Los números y reglas salieron del PDF y de
   los CSV, no de la memoria del modelo.
6. **Mantuvo el control humano.** El usuario corrigió el rumbo cuando la IA
   priorizó una opción distinta (plan monolítico, código en la raíz).

## 8. Límites y riesgos del uso de IA

- **La IA no sustituye la validación:** los 58 tests, el parser Gherkin y
  `openspec validate` son la red de seguridad; sin ellos, el refactor podría
  haber roto imports o rutas.
- **La IA puede optimizar para lo local:** recomendó mantener el código en la
  raíz para cumplir el PDF, pero el usuario priorizó la legibilidad; la decisión
  humana quedó documentada.
- **Los supuestos siguen abiertos:** el punto `00117` (traslado o dos puntos) y
  el valor de las reversadas necesitan confirmación de negocio.
- **Power BI no se puede validar en macOS:** se entrega diseño, DAX y datos; no
  se inventa un `.pbix`.
- **Seguridad:** se compartió un token en el chat al inicio; se usó solo para el
  push, no se guardó en el repositorio y se recomendó rotarlo. En este documento
  aparece redactado.

## 9. Evidencia verificable

| Evidencia | Resultado |
| :--- | :--- |
| Commits | `17c035c`, `8210907`, `b228244`, `7c3c13b`, `cc563d7`, `18a1df8`, `4fb9762` |
| Pruebas | 58 pruebas con `pytest` en verde |
| Estilo | `ruff check .` sin hallazgos |
| OpenSpec | 6/6 cambios válidos con `openspec validate --changes --strict` |
| Gherkin | 9 `.feature` validados con `gherkin-official` |
| CI | GitHub Actions en verde para el último commit |
| Aprobaciones | AP-09 en `openspec/aprobaciones.md` con justificación del usuario |
| Documentación | README, `docs/informe.md`, `docs/JUSTIFICACION_ESTRUCTURA.md` y este archivo |

## 10. Relación con el informe

Este documento es la fuente de la sección 8 del informe consolidado. La versión
del PDF incluirá los cinco prompts, los casos de corrección y una conclusión
breve; el detalle completo queda en el repositorio para que el evaluador pueda
auditar la interacción.
