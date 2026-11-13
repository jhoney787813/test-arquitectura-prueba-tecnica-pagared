@parte-a @teoria
Feature: Componente teórico de la prueba
  Como evaluador
  Quiero respuestas justificadas a las 10 preguntas
  Para verificar el criterio técnico del candidato

  Scenario Outline: Responder la pregunta <id>
    Given la pregunta <id> del componente teórico
    When se redacta la respuesta
    Then incluye justificación y no supera 8 líneas

    Examples:
      | id |
      | A1 |
      | A2 |
      | A3 |
      | A4 |
      | A5 |
      | A6 |
      | A7 |
      | A8 |
      | A9 |
      | A10 |
