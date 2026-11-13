# Atajos de desarrollo del repositorio.
# En macOS el `python3` del sistema puede ser 3.9; por eso se prefiere 3.11/3.12.
PYTHON ?= $(shell command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3)
VENV ?= .venv
BIN := $(VENV)/bin
FECHA ?= 2026-10-27
DELTA ?= datos/transacciones_delta_20261028.csv

.DEFAULT_GOAL := ayuda

.PHONY: ayuda setup test lint fmt perfil spec spec-validate limpiar

ayuda:
	@echo "Objetivos disponibles:"
	@echo "  make setup       Crea .venv e instala el paquete con dependencias de desarrollo"
	@echo "  make test        Ejecuta pytest"
	@echo "  make lint        Ejecuta ruff"
	@echo "  make fmt         Formatea el código con ruff"
	@echo "  make perfil      Perfila los CSV de entrada"
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

spec:
	openspec list

spec-validate:
	openspec validate --changes --strict

limpiar:
	rm -rf .pytest_cache .ruff_cache
