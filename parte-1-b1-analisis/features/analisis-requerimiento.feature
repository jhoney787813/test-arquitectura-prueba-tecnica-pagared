@b1 @analisis
Feature: Análisis del requerimiento de ventas
  Como responsable de la solución
  Quiero comprender el correo de Laura y las reglas del core
  Para construir el pipeline sin ambigüedades

  Scenario: Requerimientos identificados
    Given el correo de la Gerente Comercial y el PDF de la prueba
    When se analiza el caso
    Then existen requerimientos funcionales y no funcionales con criterios de aceptación

  Scenario: Preguntas y supuestos
    Given las ambigüedades del correo
    When se documenta el análisis
    Then hay al menos cinco preguntas concretas y supuestos explícitos

  Scenario: Arquitectura y plan
    Given los requerimientos identificados
    When se propone la solución
    Then hay diagrama de arquitectura, modelo de datos y plan por fases
