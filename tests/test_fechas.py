"""Pruebas de las utilidades de fecha y zona horaria."""

from __future__ import annotations

from datetime import date, datetime

import pytest
from etl.fechas import fecha_negocio, parsear_fecha, resolver_fecha_corte


@pytest.mark.parametrize(
    "texto",
    [
        "2026-10-27T13:45:00Z",
        "2026-10-27 13:45:00",
        "27/10/2026 13:45",
    ],
)
def test_parsear_fecha_formatos_del_core(texto: str) -> None:
    assert parsear_fecha(texto) == datetime(2026, 10, 27, 13, 45)


def test_parsear_fecha_rechaza_texto_invalido() -> None:
    with pytest.raises(ValueError):
        parsear_fecha("27-10-2026 13:45")


def test_fecha_negocio_cambia_de_dia_por_zona_horaria() -> None:
    # 03:00 UTC del 28/10 son las 22:00 del 27/10 en Colombia (UTC-5).
    assert fecha_negocio(datetime(2026, 10, 28, 3, 0)) == date(2026, 10, 27)
    # 05:00 UTC del 28/10 ya es medianoche del 28/10 en Colombia.
    assert fecha_negocio(datetime(2026, 10, 28, 5, 0)) == date(2026, 10, 28)


def test_resolver_fecha_corte_explicita() -> None:
    assert resolver_fecha_corte("2026-10-27") == date(2026, 10, 27)


def test_resolver_fecha_corte_por_defecto_es_ayer() -> None:
    assert resolver_fecha_corte(None, hoy=date(2026, 10, 28)) == date(2026, 10, 27)
