@b5 @operacion
Feature: Operación programada del pipeline
  Como equipo de automatización
  Quiero ejecutar el pipeline de forma segura y observable
  Para que el reporte llegue antes de las 6:00 a. m. y las fallas se detecten

  Scenario: Ejecución en contenedor
    Given la imagen Docker construida
    When se ejecuta con los volúmenes de datos y salida
    Then genera el reporte sin depender del Python del host

  Scenario: Programación antes de las 6:00 a. m.
    Given Jenkins configurado en UTC
    When se programa el job para las 4:00 a. m. de Colombia
    Then el reporte queda listo antes de las 6:00 a. m.

  Scenario: Archivo del día ausente
    Given que no llega el archivo de transacciones
    When se ejecuta el job
    Then se envía una alerta y el job termina con código distinto de 0

  Scenario: Carga parcial contra el archivo de control
    Given un archivo de control con un total mayor al cargado
    When se valida la integridad
    Then el pipeline no publica el reporte y alerta la diferencia
