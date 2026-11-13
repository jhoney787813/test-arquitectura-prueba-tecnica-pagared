@b2 @almacen
Feature: Almacén dimensional de ventas
  Como área de BI
  Quiero un modelo dimensional idempotente
  Para conectar Power BI y recalcular sin duplicar

  Scenario: Carga repetida del mismo día
    Given la fecha 2026-10-27 ya cargada
    When se ejecuta la carga otra vez
    Then no cambian el conteo ni el total de ventas

  Scenario: Delta que anula una transacción
    Given una transacción aprobada y un delta con fecha_actualizacion posterior
    When se aplica el delta
    Then la transacción queda ANULADA, hay una sola fila y deja de sumar

  Scenario: Zona histórica del punto 00117
    Given el punto 00117 con versiones en Oriente y Valle de Aburrá
    When se carga una venta de 2026
    Then la venta se asocia a Valle de Aburrá
