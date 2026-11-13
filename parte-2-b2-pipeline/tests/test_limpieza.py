"""Pruebas de limpieza y normalización (Parte B2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from etl.limpieza import (
    a_pesos_enteros,
    normalizar_canal,
    normalizar_cod_punto,
    normalizar_estado,
    normalizar_producto,
    normalizar_zona,
    parsear_valor,
)


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("APROBADA", "APROBADA"),
        (" aprobada ", "APROBADA"),
        ("Aprobada", "APROBADA"),
        ("\tAnulada\n", "ANULADA"),
        ("REVERSADA ", "REVERSADA"),
        ("desconocido", None),
        ("", None),
    ],
)
def test_normalizar_estado(crudo: str, esperado: str | None) -> None:
    assert normalizar_estado(crudo) == esperado


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("131", "00131"),
        ("00131", "00131"),
        (" 90001 ", "90001"),
        ("00000", None),
        ("", None),
        ("12A4", None),
        ("123456", None),
    ],
)
def test_normalizar_cod_punto(crudo: str, esperado: str | None) -> None:
    assert normalizar_cod_punto(crudo) == esperado


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("VALLE DE ABURRA", "Valle de Aburrá"),
        ("valle de aburrá", "Valle de Aburrá"),
        ("oriente ", "Oriente"),
        ("URABA", "Urabá"),
        ("", "SIN ZONA"),
        ("Occidente", "Occidente"),
    ],
)
def test_normalizar_zona(crudo: str, esperado: str) -> None:
    assert normalizar_zona(crudo) == esperado


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("10000.00", Decimal("10000.00")),
        ("522.500", Decimal("522500")),
        ("1.247.000", Decimal("1247000")),
        ("$ 15.000", Decimal("15000")),
        ("2000", Decimal("2000")),
        ("", None),
        (None, None),
        ("N/A", None),
        ("-5000", None),
    ],
)
def test_parsear_valor(crudo: object, esperado: Decimal | None) -> None:
    assert parsear_valor(crudo) == esperado


def test_a_pesos_enteros_rechaza_centavos() -> None:
    assert a_pesos_enteros(Decimal("15000.00")) == 15000
    with pytest.raises(ValueError):
        a_pesos_enteros(Decimal("15000.50"))


@pytest.mark.parametrize(
    ("funcion", "entrada", "esperado"),
    [
        (normalizar_producto, " pago_servicios ", "PAGO_SERVICIOS"),
        (normalizar_producto, "OTRO", None),
        (normalizar_canal, "app", "APP"),
        (normalizar_canal, "CALLE", None),
    ],
)
def test_normalizar_catalogos(funcion, entrada: str, esperado: str | None) -> None:
    assert funcion(entrada) == esperado
