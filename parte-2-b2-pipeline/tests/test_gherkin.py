"""Valida que cada parte tenga su historia Gherkin y que la sintaxis sea correcta."""

from __future__ import annotations

from pathlib import Path

import pytest
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

RAIZ = Path(__file__).resolve().parents[2]


def _features() -> list[Path]:
    return sorted(RAIZ.glob("parte-*/features/*.feature"))


def test_hay_al_menos_un_feature_por_parte() -> None:
    partes = {ruta.name for ruta in RAIZ.glob("parte-*") if ruta.is_dir()}
    con_feature = {ruta.parents[1].name for ruta in _features()}

    assert partes, "No se encontraron carpetas parte-*"
    assert partes == con_feature, f"Partes sin feature: {sorted(partes - con_feature)}"


@pytest.mark.parametrize("ruta", _features(), ids=lambda ruta: ruta.parent.parent.name)
def test_feature_gherkin_valido(ruta: Path) -> None:
    documento = Parser().parse(TokenScanner(ruta.read_text(encoding="utf-8")))

    assert documento["feature"]["name"], f"{ruta} no tiene Feature"
    assert documento["feature"]["children"], f"{ruta} no tiene escenarios"
