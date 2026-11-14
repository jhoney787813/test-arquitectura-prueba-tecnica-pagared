# Atajos de desarrollo del repositorio.
# En macOS el `python3` del sistema puede ser 3.9; por eso se prefiere 3.11/3.12.
PYTHON ?= $(shell command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3)
VENV ?= .venv
BIN := $(VENV)/bin
FECHA ?= 2026-10-27
DELTA ?= datos/transacciones_delta_20261028.csv
PODMAN ?= podman
IMAGEN ?= pagared-etl:local
CHROME ?= /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
FECHA_COMPACTA = $(shell echo $(FECHA) | tr -d -)

.DEFAULT_GOAL := ayuda

.PHONY: ayuda setup test lint fmt perfil etl etl-delta consultas bi-export b6 b6-dashboard b6-captura informe podman-build podman-demo podman-test spec spec-validate limpiar

ayuda:
	@echo "Objetivos disponibles:"
	@echo "  make setup       Crea .venv e instala el paquete con dependencias de desarrollo"
	@echo "  make test        Ejecuta pytest"
	@echo "  make lint        Ejecuta ruff"
	@echo "  make fmt         Formatea el código con ruff"
	@echo "  make perfil      Perfila los CSV de entrada"
	@echo "  make etl         Ejecuta el pipeline para la fecha de corte"
	@echo "  make etl-delta   Ejecuta el pipeline y aplica el delta"
	@echo "  make consultas   Ejecuta las consultas B3"
	@echo "  make bi-export   Exporta el modelo a CSV para Power BI"
	@echo "  make b6          Genera tablero HTML, captura y datos de Power BI"
	@echo "  make informe     Compila el informe consolidado en PDF"
	@echo "  make podman-build  Construye la imagen con Podman"
	@echo "  make podman-demo   Ejecuta el demo completo en un contenedor"
	@echo "  make podman-test   Ejecuta pytest dentro del contenedor"
	@echo "  make spec        Lista los cambios de OpenSpec"
	@echo "  make spec-validate  Valida el cambio OpenSpec en modo estricto"
	@echo "  make limpiar     Borra cachés locales"

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"

test:
	$(BIN)/pytest -q

lint:
	$(BIN)/ruff check .

fmt:
	$(BIN)/ruff format .

perfil:
	$(BIN)/python parte-2-b2-pipeline/scripts/perfil_datos.py --detalle

etl:
	$(BIN)/python -m etl --fecha-corte $(FECHA)

etl-delta:
	$(BIN)/python -m etl --fecha-corte $(FECHA) --delta $(DELTA)

consultas:
	$(BIN)/python -m etl.consultas --fecha $(FECHA)

bi-export:
	$(BIN)/python parte-6-b6-powerbi/scripts/exportar_datos.py

b6: etl-delta bi-export b6-captura

b6-dashboard: etl-delta
	$(BIN)/python parte-6-b6-powerbi/scripts/generar_tablero.py \
		--db db/pagared.db \
		--salida parte-6-b6-powerbi/powerbi/tablero_ventas.html \
		--fecha $(FECHA)

b6-captura: b6-dashboard
	"$(CHROME)" --headless=new --disable-gpu --hide-scrollbars \
		--no-first-run --no-default-browser-check \
		--user-data-dir=/tmp/pagared-chrome-b6 \
		--window-size=1440,1000 --virtual-time-budget=4000 \
		--screenshot="$(CURDIR)/parte-6-b6-powerbi/powerbi/capturas/tablero_$(FECHA_COMPACTA).png" \
		"file://$(CURDIR)/parte-6-b6-powerbi/powerbi/tablero_ventas.html"

informe:
	$(BIN)/python parte-5-b5-operacion/scripts/generar_informe.py

podman-build:
	$(PODMAN) build -t $(IMAGEN) -f parte-5-b5-operacion/infra/Containerfile .

podman-demo: podman-build
	$(PODMAN) run --rm \
		--userns=keep-id --user "$$(id -u):$$(id -g)" \
		-v "$(CURDIR)/datos:/app/datos:ro" \
		-v "$(CURDIR)/db:/app/db" \
		-v "$(CURDIR)/salida:/app/salida" \
		-v "$(CURDIR)/logs:/app/logs" \
		$(IMAGEN) demo

podman-test: podman-build
	$(PODMAN) run --rm $(IMAGEN) test

spec:
	openspec list

spec-validate:
	openspec validate --changes --strict

limpiar:
	rm -rf .pytest_cache .ruff_cache
