# Spec Delta

## Purpose

Ejecutar el pipeline de forma programada, segura y observable, con detección de
fallas, alertas y un despliegue reproducible.

## ADDED Requirements

### Requirement: Imagen Docker reproducible

El repositorio SHALL incluir un `Dockerfile` que construya una imagen con las
dependencias del pipeline y que ejecute el proceso con la fecha de corte y el
delta como parámetros.

#### Scenario: Ejecución en contenedor

- **WHEN** se construye la imagen y se ejecuta con los volúmenes de `datos/`,
  `salida/` y `db/`
- **THEN** genera el reporte y la base sin depender del Python del host

### Requirement: Programación diaria antes de las 6:00 a. m.

La operación SHALL programar el pipeline con la zona `America/Bogota` y SHALL
dejar el reporte disponible antes de las 6:00 a. m., con un tiempo máximo de
ejecución definido.

#### Scenario: Disparador en UTC

- **WHEN** Jenkins está configurado en UTC y el job debe correr a las 4:00 a. m.
  de Colombia
- **THEN** el cron usa `TZ=America/Bogota` o la hora UTC equivalente y el
  reporte queda listo antes de las 6:00 a. m.

### Requirement: Alerta por fallo o archivo faltante

La operación SHALL notificar a un responsable cuando el archivo no llega, el
layout no cumple el contrato o el pipeline termina con error, y SHALL evitar
marcar el job en verde en esos casos.

#### Scenario: Archivo del día ausente

- **WHEN** a la hora de ejecución no existe el archivo de transacciones
- **THEN** se envía una alerta con el motivo y el job termina con código
  distinto de 0

### Requirement: Validación de integridad de la carga

Antes de publicar el reporte, la operación SHALL comparar el archivo de control
del proveedor con lo cargado (conteo y valor) y SHALL fallar si la diferencia
supera la tolerancia definida.

#### Scenario: Carga parcial

- **WHEN** el archivo de control reporta 1.247 millones y la base cargó 512
  millones
- **THEN** el pipeline no publica el reporte, registra la diferencia y alerta

### Requirement: Manejo seguro de credenciales

La operación SHALL tomar las credenciales de variables de entorno o de un
gestor de secretos y SHALL impedir que se versionen en el repositorio.

#### Scenario: Arranque sin credenciales

- **WHEN** falta la cadena de conexión de la base
- **THEN** el proceso falla con un mensaje claro antes de intentar conectarse y
  no imprime el valor de la credencial

### Requirement: Conectividad con Azure SQL

El pipeline SHALL leer de Azure SQL usando una cadena de conexión segura y
SHALL reportar de forma accionable los errores de firewall o de autenticación.

#### Scenario: IP no autorizada en el firewall

- **WHEN** Azure responde que la IP del agente no está permitida
- **THEN** el error indica la IP y las alternativas de conexión, sin reintentos
  infinitos
