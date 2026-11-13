@b2 @reporte
Feature: Reporte diario de ventas
  Como Gerente Comercial
  Quiero recibir el reporte del día anterior por zona y producto
  Para tomar decisiones sin esperar el trabajo manual

  Scenario: Reporte del 27 de octubre
    Given la fecha de corte 2026-10-27
    When se genera el reporte
    Then existe reporte_ventas_20261027.xlsx con Resumen, Comparativo y Calidad

  Scenario: Zona sin ventas el día anterior
    Given una zona que solo tiene ventas el 27
    When se calcula el comparativo
    Then la variación es N/A y no hay división por cero

  Scenario: Correo listo sin SMTP
    Given un entorno sin servidor SMTP
    When termina el pipeline
    Then se genera un .eml con el Excel adjunto
