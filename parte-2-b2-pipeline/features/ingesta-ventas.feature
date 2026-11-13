@b2 @ingesta
Feature: Ingesta y limpieza de ventas
  Como analista de BI
  Quiero leer y normalizar los archivos del core
  Para que las ventas se calculen sin perder registros ni acentos

  Background:
    Given los archivos del kit están en datos/

  Scenario: Lectura de los tres archivos
    When el pipeline inicia la ingesta
    Then lee transacciones, delta y maestro con la codificación correcta

  Scenario: Normalización de fechas y estados
    Given una fila con fecha UTC 2026-10-28T03:00:00Z y estado " aprobada "
    When se limpia la fila
    Then el día contable es 2026-10-27 y el estado es APROBADA

  Scenario: Venta del punto de pruebas
    Given una venta aprobada del punto 90001
    When se aplican las reglas de negocio
    Then no suma ventas y queda registrada como excluida

  Scenario: Fila con valor inválido
    Given una fila con valor "N/A"
    When se limpia la fila
    Then se descarta con motivo valor_invalido y queda en la auditoría
