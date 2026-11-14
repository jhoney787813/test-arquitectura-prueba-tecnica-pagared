# Tasks

## 1. Contenedor y demo

- [x] 1.1 Crear `parte-5-b5-operacion/infra/Containerfile` con usuario no root y el entrypoint del pipeline
- [x] 1.2 Agregar `demo.sh` que ejecute tests, ETL base+delta, SQL, BI y envío B4
- [x] 1.3 Verificar `make podman-demo` y `make podman-test` con 65 pruebas

## 2. Incidente y operación

- [x] 2.1 Documentar la causa raíz del 26/10 y 27/10 con evidencia de logs, `.ctl`, Power BI e historial del agente
- [x] 2.2 Documentar la corrección de los datos afectados y su verificación
- [x] 2.3 Documentar la prevención: control de integridad, transacción, concurrencia y refresh posterior
- [x] 2.4 Documentar el despliegue Jenkins/AWS, credenciales, logs, alertas y almacenamiento
- [x] 2.5 Documentar la conectividad con Azure SQL y las alternativas ordenadas

## 3. Compatibilidad pendiente

- [ ] 3.1 Agregar `infra/Dockerfile` o una capa de compatibilidad en la raíz, sin romper la organización por partes
- [ ] 3.2 (Opcional) Agregar Terraform para la programación y ejecución en AWS
