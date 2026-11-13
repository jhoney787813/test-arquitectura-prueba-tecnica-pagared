@b3 @sql
Feature: Consultas SQL de ventas
  Como analista de negocio
  Quiero consultar el modelo dimensional
  Para responder preguntas de ventas y optimizar la consulta de producción

  Scenario: Top 3 de puntos por zona
    Given la fecha de corte 2026-10-27
    When se ejecuta la consulta de top 3
    Then devuelve máximo tres puntos por zona, ordenados por ventas

  Scenario: Puntos activos sin ventas
    Given el maestro de puntos y la fecha de corte
    When se ejecuta la consulta de puntos sin ventas
    Then aparecen los puntos activos sin ventas y no los inactivos

  Scenario: Variación por zona
    Given las ventas del 27 y del 26
    When se ejecuta la consulta de variación
    Then las zonas sin ventas previas devuelven variación nula

  Scenario: Consulta de producción optimizada
    Given la consulta original con funciones sobre la columna de fecha
    When se ejecuta la versión reescrita con rango de fechas
    Then devuelve el mismo resultado y usa el índice de fecha
