"""Utilidades de fecha y zona horaria.

El core transaccional exporta en UTC, pero el negocio (y el correo de Laura)
habla de días calendario de Colombia. Todas las funciones de este módulo
trabajan con ``datetime`` *naive* en UTC y convierten a ``America/Bogota`` solo
cuando se necesita delimitar el día contable.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from etl.config import ZONA_HORARIA

_FORMATOS = (
    (re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"), "%Y-%m-%dT%H:%M:%SZ"),
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), "%Y-%m-%d %H:%M:%S"),
    (re.compile(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$"), "%d/%m/%Y %H:%M"),
)


def parsear_fecha(valor: str) -> datetime:
    """Convierte una fecha del core a ``datetime`` naive en UTC.

    Acepta los tres formatos que aparecen en los archivos del proveedor:
    ISO-8601 con ``Z``, ``YYYY-MM-DD HH:MM:SS`` y ``DD/MM/YYYY HH:MM``.

    Raises:
        ValueError: si el texto no corresponde a ninguno de los formatos.
    """
    texto = (valor or "").strip()
    for patron, formato in _FORMATOS:
        if patron.match(texto):
            return datetime.strptime(texto, formato)

    raise ValueError(f"Formato de fecha no reconocido: {valor!r}")


def a_zona_local(momento_utc: datetime, zona: str = ZONA_HORARIA) -> datetime:
    """Convierte un ``datetime`` naive UTC a la zona horaria de negocio."""
    return momento_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(zona))


def fecha_negocio(momento_utc: datetime, zona: str = ZONA_HORARIA) -> date:
    """Devuelve el día calendario de negocio de un instante UTC."""
    return a_zona_local(momento_utc, zona).date()


def resolver_fecha_corte(valor: str | None, hoy: date | None = None) -> date:
    """Resuelve ``--fecha-corte``.

    Sin valor explícito usa el día anterior en la zona de negocio (no en UTC),
    que es lo que necesita el reporte que se envía a las 6:00 a. m.
    """
    if valor:
        return date.fromisoformat(valor)

    hoy = hoy or datetime.now(ZoneInfo(ZONA_HORARIA)).date()
    return hoy - timedelta(days=1)
