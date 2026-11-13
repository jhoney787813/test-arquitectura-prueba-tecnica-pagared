# Spec Delta

## Purpose

Corregir el envío de reportes para que sea idempotente, verificable y falle de
forma visible cuando el correo no pueda entregarse.

## ADDED Requirements

### Requirement: Envío único por reporte

El emisor SHALL registrar una clave de idempotencia por reporte y fecha, y
SHALL negarse a reenviar un correo que ya fue entregado con esa clave.

#### Scenario: Reintento después de un envío exitoso

- **WHEN** el job se reintenta para el mismo reporte y la clave ya está en
  estado `ENVIADO`
- **THEN** no se envía un segundo correo y el proceso termina correctamente

#### Scenario: Reintento después de un fallo de SMTP

- **WHEN** el intento anterior quedó en estado `FALLIDO`
- **THEN** el reintento vuelve a intentar el envío con la misma clave

### Requirement: Fallo de envío visible

El emisor SHALL registrar el error, SHALL devolver código de salida distinto de
0 y SHALL evitar marcar el envío como exitoso cuando el SMTP rechaza la
conexión, la autenticación o el adjunto.

#### Scenario: SMTP rechaza la autenticación

- **WHEN** el servidor responde con error de autenticación
- **THEN** el intento queda `FALLIDO`, Jenkins marca el job en rojo y no se
  registra un envío exitoso

### Requirement: Validación de configuración y adjunto

El emisor SHALL validar destinatario, asunto y existencia del archivo adjunto
antes de abrir la conexión SMTP y SHALL fallar con un mensaje claro si falta
alguno.

#### Scenario: Reporte inexistente

- **WHEN** la ruta del Excel no existe
- **THEN** el proceso termina con error antes de conectarse al SMTP y registra
  el motivo

### Requirement: Registro de intentos de envío

El emisor SHALL registrar cada intento con fecha y hora, clave, destinatarios,
resultado y detalle del error, sin guardar credenciales.

#### Scenario: Consulta de auditoría

- **WHEN** se revisa la tabla de envíos después de dos intentos
- **THEN** aparecen ambos intentos con su estado y el segundo conserva la misma
  clave de idempotencia
