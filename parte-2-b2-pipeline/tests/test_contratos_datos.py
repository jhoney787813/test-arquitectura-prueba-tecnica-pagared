"""Pruebas de contrato de los archivos de entrada.

Si el proveedor cambia el layout, el encoding o el separador, el pipeline debe
fallar temprano y de forma explícita; estas pruebas son la primera barrera.
"""

from __future__ import annotations

import csv

import pytest

from etl.config import (
    ARCHIVO_DELTA,
    ARCHIVO_PUNTOS,
    ARCHIVO_TRANSACCIONES,
    COD_PUNTO_PRUEBAS,
    DIR_DATOS,
    ENCODING_PUNTOS,
    SEPARADOR_CSV,
)

COLUMNAS_TRANSACCION = [
    "id_transaccion",
    "fecha_transaccion",
    "fecha_actualizacion",
    "cod_punto",
    "producto",
    "valor",
    "estado",
    "canal",
]
COLUMNAS_PUNTOS = ["cod_punto", "nombre", "zona", "activo", "fecha_apertura"]


def _leer_encabezado(nombre: str, encoding: str) -> list[str]:
    with (DIR_DATOS / nombre).open(encoding=encoding, newline="") as archivo:
        return next(csv.reader(archivo, delimiter=SEPARADOR_CSV))


@pytest.mark.parametrize("nombre", [ARCHIVO_TRANSACCIONES, ARCHIVO_DELTA])
def test_encabezado_transacciones(nombre: str) -> None:
    assert _leer_encabezado(nombre, "utf-8-sig") == COLUMNAS_TRANSACCION


def test_encabezado_puntos_venta() -> None:
    assert _leer_encabezado(ARCHIVO_PUNTOS, ENCODING_PUNTOS) == COLUMNAS_PUNTOS


def test_transacciones_decodifica_utf8_con_bom() -> None:
    contenido = (DIR_DATOS / ARCHIVO_TRANSACCIONES).read_bytes()
    assert contenido.startswith(b"\xef\xbb\xbf")
    contenido.decode("utf-8-sig")


def test_maestro_puntos_no_es_utf8() -> None:
    # Documenta el hallazgo: si el proveedor lo reexporta en UTF-8, la prueba falla
    # y obliga a revisar la regla de encoding en lugar de corromper los acentos.
    contenido = (DIR_DATOS / ARCHIVO_PUNTOS).read_bytes()
    with pytest.raises(UnicodeDecodeError):
        contenido.decode("utf-8")


def test_volumen_minimo_de_datos() -> None:
    with (DIR_DATOS / ARCHIVO_TRANSACCIONES).open(encoding="utf-8-sig", newline="") as archivo:
        filas = sum(1 for _ in archivo) - 1
    assert filas > 1000


def test_el_maestro_incluye_el_punto_de_pruebas() -> None:
    with (DIR_DATOS / ARCHIVO_PUNTOS).open(encoding=ENCODING_PUNTOS, newline="") as archivo:
        codigos = {fila["cod_punto"] for fila in csv.DictReader(archivo, delimiter=SEPARADOR_CSV)}
    assert COD_PUNTO_PRUEBAS in codigos
