@b6 @powerbi
Feature: Tablero de ventas
  Como Gerente Comercial
  Quiero ver los indicadores del día y comparar zonas y productos
  Para tomar decisiones comerciales con datos confiables

  Scenario: Indicadores del 27 de octubre
    Given el tablero abierto con la fecha 2026-10-27
    When se cargan los visuales
    Then muestran ventas, número de transacciones y ticket promedio del día

  Scenario: Variación de una zona nueva
    Given una zona con ventas el 27 pero sin ventas el 26
    When se calcula la variación
    Then se muestra vacía o N/A, sin error de DAX

  Scenario: Filtros combinados
    Given una zona y el canal APP seleccionados
    When se aplican los filtros
    Then todos los visuales se recalculan con esa combinación

  Scenario: Medidas DAX reutilizables
    Given un visual nuevo
    When se usan las medidas de ventas y transacciones
    Then el resultado coincide con el Resumen del reporte Excel
