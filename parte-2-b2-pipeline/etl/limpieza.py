"""Limpieza y normalización de los datos que entrega el core.

Las reglas de este módulo están justificadas en el informe (sección 3) y se
aplican tanto al archivo principal como al delta, para que una transacción se
normalice igual sin importar de cuál de los dos venga.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd

from etl.config import (
    CANALES_VALIDOS,
    COD_PUNTO_PRUEBAS,
    ESTADOS_VALIDOS,
    PRODUCTOS_VALIDOS,
    ZONA_SIN_ASIGNAR,
)
from etl.fechas import a_zona_local, fecha_negocio, parsear_fecha

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


def _descarte(
    archivo: str,
    fila: int,
    id_transaccion: str,
    motivo: str,
    detalle: str = "",
) -> dict[str, object]:
    return {
        "archivo": archivo,
        "fila": fila,
        "id_transaccion": id_transaccion,
        "motivo": motivo,
        "detalle": detalle,
    }


def limpiar_transacciones(
    df: pd.DataFrame,
    archivo: str = "transacciones.csv",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Aplica las reglas de ingesta a un archivo de transacciones.

    Returns:
        ``(limpias, descartes, stats)`` donde ``limpias`` tiene una fila por
        ``id_transaccion`` vigente y ``stats`` resume leídos, descartes y
        correcciones.
    """
    descartes: list[dict[str, object]] = []
    limpios: list[dict[str, object]] = []
    motivos: Counter[str] = Counter()
    corregidos: Counter[str] = Counter()

    for offset, row in enumerate(df.itertuples(index=False), start=2):
        datos = row._asdict()
        id_transaccion = normalizar_texto(datos["id_transaccion"]).upper()

        if not re.fullmatch(r"TX\d{9}", id_transaccion):
            motivo = "id_invalido"
            descartes.append(
                _descarte(
                    archivo, offset, id_transaccion, motivo, "id fuera del patrón TX#########"
                )
            )
            motivos[motivo] += 1
            continue

        try:
            fecha_utc = parsear_fecha(datos["fecha_transaccion"])
            actualizacion_utc = parsear_fecha(datos["fecha_actualizacion"])
        except ValueError as exc:
            motivo = "fecha_invalida"
            descartes.append(_descarte(archivo, offset, id_transaccion, motivo, str(exc)))
            motivos[motivo] += 1
            continue

        cod_punto = normalizar_cod_punto(datos["cod_punto"])
        if cod_punto is None:
            motivo = "cod_punto_invalido"
            descartes.append(
                _descarte(archivo, offset, id_transaccion, motivo, repr(datos["cod_punto"]))
            )
            motivos[motivo] += 1
            continue

        if cod_punto == COD_PUNTO_PRUEBAS:
            motivo = "punto_pruebas"
            descartes.append(
                _descarte(
                    archivo,
                    offset,
                    id_transaccion,
                    motivo,
                    "Punto de pruebas de sistemas excluido del reporte",
                )
            )
            motivos[motivo] += 1
            continue

        estado = normalizar_estado(datos["estado"])
        producto = normalizar_producto(datos["producto"])
        canal = normalizar_canal(datos["canal"])

        if estado is None:
            motivo = "estado_invalido"
            descartes.append(
                _descarte(archivo, offset, id_transaccion, motivo, repr(datos["estado"]))
            )
            motivos[motivo] += 1
            continue
        if producto is None:
            motivo = "producto_invalido"
            descartes.append(
                _descarte(archivo, offset, id_transaccion, motivo, repr(datos["producto"]))
            )
            motivos[motivo] += 1
            continue
        if canal is None:
            motivo = "canal_invalido"
            descartes.append(
                _descarte(archivo, offset, id_transaccion, motivo, repr(datos["canal"]))
            )
            motivos[motivo] += 1
            continue

        monto = parsear_valor(datos["valor"])
        if monto is None:
            motivo = "valor_invalido"
            descartes.append(
                _descarte(archivo, offset, id_transaccion, motivo, repr(datos["valor"]))
            )
            motivos[motivo] += 1
            continue
        if monto <= 0:
            motivo = "valor_no_positivo"
            descartes.append(_descarte(archivo, offset, id_transaccion, motivo, str(monto)))
            motivos[motivo] += 1
            continue
        try:
            valor_cop = a_pesos_enteros(monto)
        except ValueError:
            motivo = "valor_con_centavos"
            descartes.append(_descarte(archivo, offset, id_transaccion, motivo, str(monto)))
            motivos[motivo] += 1
            continue

        if normalizar_texto(datos["cod_punto"]) != cod_punto:
            corregidos["cod_punto"] += 1
        if normalizar_texto(datos["estado"]) != estado:
            corregidos["estado"] += 1

        local = a_zona_local(fecha_utc)
        limpios.append(
            {
                "id_transaccion": id_transaccion,
                "fecha_transaccion_utc": fecha_utc,
                "fecha_actualizacion_utc": actualizacion_utc,
                "fecha_negocio": fecha_negocio(fecha_utc),
                "fecha_hora_local": local,
                "cod_punto": cod_punto,
                "producto": producto,
                "estado": estado,
                "canal": canal,
                "valor_cop": valor_cop,
                "archivo": archivo,
                "fila": offset,
            }
        )

    columnas = [
        "id_transaccion",
        "fecha_transaccion_utc",
        "fecha_actualizacion_utc",
        "fecha_negocio",
        "fecha_hora_local",
        "cod_punto",
        "producto",
        "estado",
        "canal",
        "valor_cop",
        "archivo",
        "fila",
    ]
    if not limpios:
        vacio = pd.DataFrame(columns=columnas)
        return (
            vacio,
            pd.DataFrame(descartes),
            {
                "leidos": len(df),
                "cargados": 0,
                "descartados": len(descartes),
                "por_motivo": dict(motivos),
                "corregidos": dict(corregidos),
            },
        )

    limpias = pd.DataFrame(limpios)

    # 1) Filas exactamente repetidas: se conserva la primera.
    columnas_negocio = [
        "id_transaccion",
        "fecha_transaccion_utc",
        "fecha_actualizacion_utc",
        "cod_punto",
        "producto",
        "estado",
        "canal",
        "valor_cop",
    ]
    duplicadas = limpias.duplicated(subset=columnas_negocio, keep="first")
    for _, fila in limpias[duplicadas].iterrows():
        descartes.append(
            _descarte(
                archivo,
                int(fila["fila"]),
                str(fila["id_transaccion"]),
                "duplicado_exacto",
                "Fila idéntica repetida en el archivo",
            )
        )
        motivos["duplicado_exacto"] += 1
    limpias = limpias[~duplicadas].copy()

    # 2) Varias versiones de una transacción: gana la actualización más reciente.
    limpias = limpias.sort_values(
        ["id_transaccion", "fecha_actualizacion_utc", "fila"], kind="stable"
    )
    vigentes = limpias.drop_duplicates("id_transaccion", keep="last")
    obsoletas = limpias.loc[~limpias.index.isin(vigentes.index)]
    for _, fila in obsoletas.iterrows():
        descartes.append(
            _descarte(
                archivo,
                int(fila["fila"]),
                str(fila["id_transaccion"]),
                "version_obsoleta",
                "Existe una versión con fecha_actualizacion mayor",
            )
        )
        motivos["version_obsoleta"] += 1

    limpias = vigentes.sort_values("id_transaccion").reset_index(drop=True)

    stats = {
        "leidos": len(df),
        "cargados": len(limpias),
        "descartados": len(descartes),
        "por_motivo": dict(motivos),
        "corregidos": dict(corregidos),
    }
    return limpias, pd.DataFrame(descartes), stats


def limpiar_puntos(
    df: pd.DataFrame,
    archivo: str = "puntos_venta.csv",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Normaliza el maestro de puntos y conserva las versiones por apertura."""
    descartes: list[dict[str, object]] = []
    limpios: list[dict[str, object]] = []
    motivos: Counter[str] = Counter()
    corregidos: Counter[str] = Counter()

    for offset, row in enumerate(df.itertuples(index=False), start=2):
        datos = row._asdict()
        cod_punto = normalizar_cod_punto(datos["cod_punto"])
        if cod_punto is None:
            motivo = "cod_punto_invalido"
            descartes.append(_descarte(archivo, offset, "", motivo, repr(datos["cod_punto"])))
            motivos[motivo] += 1
            continue

        nombre = normalizar_texto(datos["nombre"])
        if not nombre:
            motivo = "nombre_invalido"
            descartes.append(_descarte(archivo, offset, cod_punto, motivo, ""))
            motivos[motivo] += 1
            continue

        try:
            fecha_apertura = date.fromisoformat(normalizar_texto(datos["fecha_apertura"]))
        except ValueError:
            motivo = "fecha_apertura_invalida"
            descartes.append(
                _descarte(archivo, offset, cod_punto, motivo, repr(datos["fecha_apertura"]))
            )
            motivos[motivo] += 1
            continue

        activo = normalizar_texto(datos["activo"]).upper()
        if activo not in {"S", "N"}:
            motivo = "activo_invalido"
            descartes.append(_descarte(archivo, offset, cod_punto, motivo, repr(datos["activo"])))
            motivos[motivo] += 1
            continue

        zona = normalizar_zona(datos["zona"])
        if normalizar_texto(datos["cod_punto"]) != cod_punto:
            corregidos["cod_punto"] += 1
        if normalizar_texto(datos["zona"]) != zona:
            corregidos["zona"] += 1

        limpios.append(
            {
                "cod_punto": cod_punto,
                "nombre": nombre,
                "zona": zona,
                "activo": activo,
                "fecha_apertura": fecha_apertura,
                "archivo": archivo,
                "fila": offset,
            }
        )

    if not limpios:
        vacio = pd.DataFrame(columns=["cod_punto", "nombre", "zona", "activo", "fecha_apertura"])
        return (
            vacio,
            pd.DataFrame(descartes),
            {
                "leidos": len(df),
                "cargados": 0,
                "descartados": len(descartes),
                "por_motivo": dict(motivos),
                "corregidos": dict(corregidos),
            },
        )

    puntos = pd.DataFrame(limpios)
    exactas = puntos.duplicated(
        subset=["cod_punto", "nombre", "zona", "activo", "fecha_apertura"], keep="first"
    )
    for _, fila in puntos[exactas].iterrows():
        descartes.append(
            _descarte(
                archivo,
                int(fila["fila"]),
                str(fila["cod_punto"]),
                "duplicado_exacto",
                "Fila idéntica repetida en el maestro",
            )
        )
        motivos["duplicado_exacto"] += 1
    puntos = puntos[~exactas].copy()

    # Un mismo código puede tener varias vigencias (p. ej. 00117).
    puntos = puntos.sort_values(["cod_punto", "fecha_apertura", "fila"], kind="stable")
    puntos = puntos.drop_duplicates(["cod_punto", "fecha_apertura"], keep="last")
    puntos = puntos.sort_values(["cod_punto", "fecha_apertura"]).reset_index(drop=True)

    stats = {
        "leidos": len(df),
        "cargados": len(puntos),
        "descartados": len(descartes),
        "por_motivo": dict(motivos),
        "corregidos": dict(corregidos),
    }
    return puntos, pd.DataFrame(descartes), stats
