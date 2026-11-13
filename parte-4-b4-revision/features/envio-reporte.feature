@b4 @envio
Feature: Envío idempotente de reportes
  Como responsable de automatización
  Quiero que el correo se envíe una sola vez y falle de forma visible
  Para que Laura no reciba duplicados ni se quede sin reporte

  Scenario: Primer envío del día
    Given un reporte generado y una clave de envío nueva
    When se ejecuta el envío
    Then el correo se envía una vez y queda registrado como ENVIADO

  Scenario: Reintento tras un envío exitoso
    Given una clave de envío ya registrada como ENVIADO
    When el job se reintenta
    Then no se envía un segundo correo

  Scenario: Fallo de autenticación SMTP
    Given un servidor SMTP que rechaza las credenciales
    When se intenta enviar el reporte
    Then el intento queda FALLIDO, el job sale con código distinto de 0 y no se marca como exitoso
