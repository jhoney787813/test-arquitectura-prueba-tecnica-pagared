"""Lectura y validación de los archivos de entrada del core."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from etl.config import (
    ARCHIVO_DELTA,
    ARCHIVO_PUNTOS,
    ARCHIVO_TRANSACCIONES,
    DIR_DATOS,
    ENCODING_PUNTOS,
    ENCODING_TRANSACCIONES,
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


class ErrorDatos(RuntimeError):
    """Error de contrato en un archivo de entrada."""


def detectar_encoding(ruta: Path) -> str:
    """Devuelve el primer encoding con el que el archivo decodifica completo."""
    contenido = ruta.read_bytes()
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            contenido.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ErrorDatos(f"No se pudo decodificar {ruta.name}")


def _leer_csv(ruta: Path, columnas: list[str]) -> pd.DataFrame:
    if not ruta.exists():
        raise ErrorDatos(f"No existe el archivo {ruta}")

    if ruta.stat().st_size == 0:
        raise ErrorDatos(f"El archivo {ruta.name} está vacío")

    encoding = detectar_encoding(ruta)
    try:
        df = pd.read_csv(
            ruta,
            sep=SEPARADOR_CSV,
            dtype=str,
            encoding=encoding,
            keep_default_na=False,
        )
    except Exception as exc:  # noqa: BLE001 - se reporta como error de datos
        raise ErrorDatos(f"No se pudo leer {ruta.name}: {exc}") from exc

    faltantes = [columna for columna in columnas if columna not in df.columns]
    if faltantes:
        raise ErrorDatos(f"{ruta.name} no tiene las columnas: {faltantes}")

    if df.empty:
        raise ErrorDatos(f"{ruta.name} no tiene filas de datos")

    return df


def leer_transacciones(ruta: Path | None = None) -> pd.DataFrame:
    """Lee el archivo principal o el delta conservando los valores crudos."""
    return _leer_csv(ruta or DIR_DATOS / ARCHIVO_TRANSACCIONES, COLUMNAS_TRANSACCION)


def leer_delta(ruta: Path | None = None) -> pd.DataFrame:
    """Lee el archivo incremental del 28/10."""
    return _leer_csv(ruta or DIR_DATOS / ARCHIVO_DELTA, COLUMNAS_TRANSACCION)


def leer_puntos(ruta: Path | None = None) -> pd.DataFrame:
    """Lee el maestro de puntos (Latin-1)."""
    ruta = ruta or DIR_DATOS / ARCHIVO_PUNTOS
    if not ruta.exists():
        raise ErrorDatos(f"No existe el archivo {ruta}")
    if ruta.stat().st_size == 0:
        raise ErrorDatos(f"El archivo {ruta.name} está vacío")

    try:
        df = pd.read_csv(
            ruta,
            sep=SEPARADOR_CSV,
            dtype=str,
            encoding=ENCODING_PUNTOS,
            keep_default_na=False,
        )
    except Exception as exc:  # noqa: BLE001
        raise ErrorDatos(f"No se pudo leer {ruta.name}: {exc}") from exc

    faltantes = [columna for columna in COLUMNAS_PUNTOS if columna not in df.columns]
    if faltantes:
        raise ErrorDatos(f"{ruta.name} no tiene las columnas: {faltantes}")

    if df.empty:
        raise ErrorDatos(f"{ruta.name} no tiene filas de datos")

    return df


# Constantes expuestas para pruebas y compatibilidad.
__all__ = [
    "COLUMNAS_PUNTOS",
    "COLUMNAS_TRANSACCION",
    "ENCODING_PUNTOS",
    "ENCODING_TRANSACCIONES",
    "ErrorDatos",
    "detectar_encoding",
    "leer_delta",
    "leer_puntos",
    "leer_transacciones",
]
