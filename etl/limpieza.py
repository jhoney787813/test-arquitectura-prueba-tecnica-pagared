"""Limpieza y normalización de los datos que entrega el core.

Las reglas de este módulo están justificadas en el informe (sección 3) y se
aplican tanto al archivo principal como al delta, para que una transacción se
normalice igual sin importar de cuál de los dos venga.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

from etl.config import (
    CANALES_VALIDOS,
    ESTADOS_VALIDOS,
    PRODUCTOS_VALIDOS,
    ZONA_SIN_ASIGNAR,
)

#: Zonas del maestro tal como deben quedar en el modelo (nombre canónico).
ZONAS_CANONICAS = {
    "valle de aburra": "Valle de Aburrá",
    "oriente": "Oriente",
    "suroeste": "Suroeste",
    "norte": "Norte",
    "uraba": "Urabá",
}

_RE_MILES_PUNTO = re.compile(r"^\d{1,3}(\.\d{3})+$")
_RE_MILES_COMA = re.compile(r"^\d{1,3}(,\d{3})+(\.\d{1,2})?$")
_RE_DECIMAL_PUNTO = re.compile(r"^\d+(\.\d{1,2})?$")
_RE_DECIMAL_COMA = re.compile(r"^\d+(,\d{1,2})?$")


def normalizar_texto(valor: object) -> str:
    """Convierte a texto, elimina espacios extremos y colapsa espacios internos."""
    return " ".join(str(valor if valor is not None else "").split())


def normalizar_estado(valor: object) -> str | None:
    """Normaliza el estado (mayúsculas y espacios) y descarta valores inválidos.

    El archivo trae 24 variantes como ``' aprobada '``, ``'Aprobada'`` o
    ``'ANULADA '``; todas deben mapear a los cuatro estados del diccionario.
    """
    texto = normalizar_texto(valor).upper()
    return texto if texto in ESTADOS_VALIDOS else None


def normalizar_producto(valor: object) -> str | None:
    """Normaliza el producto y descarta valores fuera del catálogo."""
    texto = normalizar_texto(valor).upper()
    return texto if texto in PRODUCTOS_VALIDOS else None


def normalizar_canal(valor: object) -> str | None:
    """Normaliza el canal y descarta valores fuera del catálogo."""
    texto = normalizar_texto(valor).upper()
    return texto if texto in CANALES_VALIDOS else None


def normalizar_cod_punto(valor: object) -> str | None:
    """Deja el código de punto en 5 dígitos.

    El core exporta algunos códigos sin ceros a la izquierda (``131`` en lugar
    de ``00131``) y usa ``00000`` como comodín inválido. Ambos casos se
    resuelven aquí para que el cruce con el maestro sea confiable.
    """
    texto = normalizar_texto(valor)
    if not texto.isdigit() or len(texto) > 5:
        return None

    codigo = texto.zfill(5)
    return None if codigo == "00000" else codigo


def normalizar_zona(valor: object) -> str:
    """Mapea las variantes de zona del maestro a su nombre canónico.

    El maestro trae ``VALLE DE ABURRA``, ``oriente `` y una zona vacía; sin
    esta normalización, ``GROUP BY zona`` partiría el mismo territorio en dos
    filas del reporte.
    """
    texto = normalizar_texto(valor)
    if not texto:
        return ZONA_SIN_ASIGNAR

    clave = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    ).lower()
    return ZONAS_CANONICAS.get(clave, texto)


def parsear_valor(valor: object) -> Decimal | None:
    """Interpreta un valor monetario en COP y lo devuelve como ``Decimal``.

    El archivo mezcla dos convenciones: ``10000.00`` (punto decimal) y
    ``522.500`` (punto de miles, sin decimales). En COP no circulan centavos,
    por lo que tres dígitos después del punto se interpretan como miles.

    Returns:
        El monto como ``Decimal`` o ``None`` si el texto no es interpretable.
    """
    texto = normalizar_texto(valor).replace("$", "").replace(" ", "")
    if not texto:
        return None

    if _RE_MILES_PUNTO.match(texto):
        texto = texto.replace(".", "")
    elif _RE_MILES_COMA.match(texto):
        texto = texto.replace(",", "").replace(".", "")
    elif _RE_DECIMAL_PUNTO.match(texto):
        pass
    elif _RE_DECIMAL_COMA.match(texto):
        texto = texto.replace(",", ".")
    else:
        return None

    try:
        return Decimal(texto)
    except InvalidOperation:  # pragma: no cover - cubierto por el patrón
        return None


def a_pesos_enteros(monto: Decimal) -> int:
    """Convierte un monto a pesos enteros, rechazando centavos.

    El modelo guarda pesos enteros (``INTEGER``) para que las sumas sean
    exactas y no hereden el error de redondeo de ``float`` (pregunta A3).
    """
    if monto != monto.to_integral_value():
        raise ValueError(f"El monto {monto} tiene centavos y no es representable en pesos")
    return int(monto)
