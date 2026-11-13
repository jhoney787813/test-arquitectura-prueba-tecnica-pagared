#!/usr/bin/env python3
"""Perfilado reproducible de los archivos del kit (análisis previo a la limpieza).

No modifica datos: solo lee y reporta problemas de calidad para sustentar las
reglas de limpieza del informe. Uso:

    python scripts/perfil_datos.py
    python scripts/perfil_datos.py --detalle
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
from etl.config import (
    ARCHIVO_DELTA,
    ARCHIVO_PUNTOS,
    ARCHIVO_TRANSACCIONES,
    COD_PUNTO_PRUEBAS,
    DIR_DATOS,
    ENCODING_PUNTOS,
    ENCODING_TRANSACCIONES,
    SEPARADOR_CSV,
    ZONA_SIN_ASIGNAR,
)
from etl.fechas import fecha_negocio, parsear_fecha
from etl.limpieza import (
    normalizar_cod_punto,
    normalizar_estado,
    normalizar_zona,
    parsear_valor,
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


def detectar_encoding(ruta: Path) -> str:
    """Devuelve el primer encoding con el que el archivo decodifica completo."""
    contenido = ruta.read_bytes()
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            contenido.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar {ruta.name}")


def leer_csv(ruta: Path, encoding: str) -> pd.DataFrame:
    """Lee un CSV del core preservando los valores crudos como texto."""
    return pd.read_csv(
        ruta,
        sep=SEPARADOR_CSV,
        dtype=str,
        encoding=encoding,
        keep_default_na=False,
    )


def _titulo(texto: str) -> None:
    print(f"\n{'=' * 72}\n{texto}\n{'=' * 72}")


def resumen_archivo(nombre: str, ruta: Path, encoding: str, df: pd.DataFrame) -> None:
    print(f"\n- {nombre}: {len(df):,} filas x {len(df.columns)} columnas")
    print(f"  encoding: {encoding} | bytes: {ruta.stat().st_size:,} | sep: {SEPARADOR_CSV!r}")
    print(f"  columnas: {', '.join(df.columns)}")
    vacios = {col: int((df[col].astype(str).str.strip() == "").sum()) for col in df.columns}
    print(f"  vacíos por columna: {vacios}")


def perfilar_puntos(df: pd.DataFrame) -> None:
    _titulo("MAESTRO DE PUNTOS DE VENTA")
    print(f"puntos: {len(df)} | códigos únicos: {df['cod_punto'].nunique()}")
    print(f"activo: {df['activo'].value_counts().to_dict()}")
    print("\nVariantes de zona (crudo -> normalizado):")
    for crudo, cantidad in df["zona"].value_counts().items():
        print(f"  {crudo!r} ({cantidad}) -> {normalizar_zona(crudo)!r}")

    duplicados = df[df.duplicated("cod_punto", keep=False)].sort_values("cod_punto")
    if not duplicados.empty:
        print("\nCódigos duplicados en el maestro (posible cambio de zona/nombre):")
        print(duplicados.to_string(index=False))

    prueba = df[df["cod_punto"].str.strip() == COD_PUNTO_PRUEBAS]
    print(
        f"\nPunto de pruebas {COD_PUNTO_PRUEBAS}: {len(prueba)} registro(s) -> se excluye del reporte"
    )


def _formato_fecha(texto: str) -> str:
    """Etiqueta legible del formato de fecha encontrado en el archivo."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", texto):
        return "ISO-8601 con Z (UTC)"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", texto):
        return "YYYY-MM-DD HH:MM:SS"
    if re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", texto):
        return "DD/MM/YYYY HH:MM"
    return "desconocido"


def perfilar_transacciones(df: pd.DataFrame, nombre: str, codigos_maestro: set[str]) -> None:
    _titulo(f"TRANSACCIONES: {nombre}")

    formatos_fecha = Counter()
    errores_fecha = 0
    fechas_utc = []
    for valor in df["fecha_transaccion"]:
        try:
            momento = parsear_fecha(valor)
            formatos_fecha[_formato_fecha(valor.strip())] += 1
            fechas_utc.append(momento)
        except ValueError:
            errores_fecha += 1
    print(f"fechas no interpretables: {errores_fecha}")
    print(f"formatos: {dict(formatos_fecha)}")

    fechas = pd.Series(fechas_utc)
    print("\nDía calendario UTC vs día de negocio (America/Bogota):")
    print(f"  UTC:  {fechas.dt.date.value_counts().sort_index().to_dict()}")
    print(f"  COT:  {fechas.map(fecha_negocio).value_counts().sort_index().to_dict()}")

    estados_crudos = df["estado"].value_counts()
    print(f"\nestados crudos distintos: {len(estados_crudos)}")
    for estado, cantidad in estados_crudos.items():
        print(f"  {estado!r}: {cantidad}")
    normalizados = df["estado"].map(normalizar_estado)
    print(f"estados normalizados: {normalizados.value_counts(dropna=False).to_dict()}")
    print(f"estados inválidos: {int(normalizados.isna().sum())}")

    codigos = df["cod_punto"].map(normalizar_cod_punto)
    print(f"\ncódigos inválidos: {int(codigos.isna().sum())}")
    print(
        f"códigos corregidos (ceros a la izquierda): "
        f"{int((codigos.notna() & (df['cod_punto'].str.strip() != codigos)).sum())}"
    )
    print(
        f"punto de pruebas {COD_PUNTO_PRUEBAS}: {int((codigos == COD_PUNTO_PRUEBAS).sum())} filas"
    )

    huerfanos = sorted(set(codigos.dropna()) - codigos_maestro)
    filas_huerfanas = int(codigos.isin(huerfanos).sum())
    print(f"códigos fuera del maestro: {huerfanos} ({filas_huerfanas} filas)")

    valores = df["valor"].map(parsear_valor)
    print(f"\nvalores no interpretables: {int(valores.isna().sum())}")
    print(f"valores <= 0: {int((valores <= 0).sum())}")
    montos = [int(v) for v in valores.dropna()]
    print(f"suma de valores interpretables: {sum(montos):,} COP")

    duplicadas = int(df.duplicated(subset=COLUMNAS_TRANSACCION, keep="first").sum())
    print(f"\nfilas duplicadas exactas: {duplicadas}")
    print(f"ids únicos: {df['id_transaccion'].nunique()} de {len(df)} filas")
    print(f"ids con más de una versión: {int((df['id_transaccion'].value_counts() > 1).sum())}")


def perfilar_delta(base: pd.DataFrame, delta: pd.DataFrame) -> None:
    _titulo("CARGA INCREMENTAL (DELTA 2026-10-28)")
    ids_base = set(base["id_transaccion"])
    ids_delta = set(delta["id_transaccion"])
    print(f"filas delta: {len(delta)} | ids únicos: {len(ids_delta)}")
    print(f"ids que ya existían en la base: {len(ids_delta & ids_base)}")
    print(f"ids nuevos: {len(ids_delta - ids_base)}")

    base_estado = (
        base.assign(_e=base["estado"].map(normalizar_estado))
        .drop_duplicates("id_transaccion", keep="last")
        .set_index("id_transaccion")["_e"]
    )
    delta_estado = (
        delta.assign(_e=delta["estado"].map(normalizar_estado))
        .drop_duplicates("id_transaccion", keep="last")
        .set_index("id_transaccion")["_e"]
    )
    comunes = base_estado.index.intersection(delta_estado.index)
    cambios = int((base_estado.loc[comunes] != delta_estado.loc[comunes]).sum())
    print(f"ids comunes con cambio de estado: {cambios}")

    fechas = delta["fecha_actualizacion"].map(parsear_fecha)
    print(f"rango fecha_actualizacion: {fechas.min()} .. {fechas.max()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--detalle",
        action="store_true",
        help="Muestra ejemplos de los registros problemáticos.",
    )
    args = parser.parse_args(argv)

    archivos = {
        "transacciones": DIR_DATOS / ARCHIVO_TRANSACCIONES,
        "delta": DIR_DATOS / ARCHIVO_DELTA,
        "puntos": DIR_DATOS / ARCHIVO_PUNTOS,
    }
    faltantes = [ruta.name for ruta in archivos.values() if not ruta.exists()]
    if faltantes:
        print(f"ERROR: faltan archivos de entrada: {faltantes}", file=sys.stderr)
        return 2

    enc_tx = detectar_encoding(archivos["transacciones"])
    enc_delta = detectar_encoding(archivos["delta"])
    enc_puntos = detectar_encoding(archivos["puntos"])
    assert enc_tx == ENCODING_TRANSACCIONES
    assert enc_delta == ENCODING_TRANSACCIONES
    assert enc_puntos == ENCODING_PUNTOS

    base = leer_csv(archivos["transacciones"], enc_tx)
    delta = leer_csv(archivos["delta"], enc_delta)
    puntos = leer_csv(archivos["puntos"], enc_puntos)

    _titulo("RESUMEN GENERAL")
    resumen_archivo(ARCHIVO_TRANSACCIONES, archivos["transacciones"], enc_tx, base)
    resumen_archivo(ARCHIVO_DELTA, archivos["delta"], enc_delta, delta)
    resumen_archivo(ARCHIVO_PUNTOS, archivos["puntos"], enc_puntos, puntos)

    perfilar_puntos(puntos)
    codigos_maestro = set(puntos["cod_punto"].str.strip())
    perfilar_transacciones(base, ARCHIVO_TRANSACCIONES, codigos_maestro)
    perfilar_delta(base, delta)

    _titulo("HALLAZGOS PARA LAS REGLAS DE LIMPIEZA")
    hallazgos = [
        "El maestro de puntos viene en Latin-1 y el core en UTF-8 con BOM.",
        "Los estados tienen espacios y mayúsculas inconsistentes (24 variantes).",
        "Hay códigos de punto de 3 dígitos y 4 códigos vacíos.",
        "El punto 00199 aparece en 12 transacciones pero no está en el maestro.",
        "La columna valor mezcla '10000.00' con '522.500' (miles sin decimales).",
        "Las fechas usan tres formatos distintos, incluido ISO-8601 con Z.",
        "El archivo principal trae transacciones de madrugada del 28/10 (UTC).",
        "El delta incluye registros anteriores a la ventana declarada y cambios de estado.",
        "El maestro tiene el código 00117 duplicado con zona y nombre distintos.",
        "La zona del punto 00133 viene vacía y hay un punto de pruebas 90001.",
    ]
    for hallazgo in hallazgos:
        print(f"  - {hallazgo}")

    if args.detalle:
        _titulo("EJEMPLOS: FILAS CON PROBLEMAS")
        problemas = base[
            base["cod_punto"].map(normalizar_cod_punto).isna()
            | base["valor"].map(parsear_valor).isna()
            | base["estado"].map(normalizar_estado).isna()
        ]
        print(problemas.head(20).to_string(index=False))
        print(f"\nZonas sin asignar: {normalizar_zona('')!r} ({ZONA_SIN_ASIGNAR})")

    print("\nPerfilado completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
