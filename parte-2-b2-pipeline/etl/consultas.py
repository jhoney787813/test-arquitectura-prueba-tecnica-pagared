"""Ejecución de las consultas de la Parte B3 sobre el modelo cargado."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from etl.config import DIR_SALIDA, RUTA_DB

RAIZ = Path(__file__).resolve().parents[2]
RUTA_SQL = RAIZ / "parte-3-b3-sql" / "sql" / "consultas.sql"
CONSULTAS_EJECUTABLES = {"top3", "puntos_sin_ventas", "variacion"}


def cargar_consultas(ruta: Path = RUTA_SQL) -> dict[str, str]:
    """Separa el archivo SQL por los marcadores ``-- @consulta: nombre``."""
    consultas: dict[str, str] = {}
    nombre: str | None = None
    lineas: list[str] = []

    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("-- @consulta:"):
            if nombre and lineas:
                consultas[nombre] = "\n".join(lineas).strip()
            nombre = linea.split(":", 1)[1].strip()
            lineas = []
        elif nombre:
            lineas.append(linea)

    if nombre and lineas:
        consultas[nombre] = "\n".join(lineas).strip()
    return consultas


def ejecutar_consultas(
    conexion: sqlite3.Connection,
    fecha: date,
    salida: Path | None = None,
) -> dict[str, pd.DataFrame]:
    consultas = cargar_consultas()
    parametros = {
        "fecha": fecha.isoformat(),
        "fecha_anterior": (fecha - timedelta(days=1)).isoformat(),
    }
    resultados: dict[str, pd.DataFrame] = {}
    for nombre in CONSULTAS_EJECUTABLES:
        if nombre not in consultas:
            continue
        resultados[nombre] = pd.read_sql_query(consultas[nombre], conexion, params=parametros)

    if salida:
        salida.parent.mkdir(parents=True, exist_ok=True)
        with salida.open("w", encoding="utf-8") as archivo:
            archivo.write(f"Consultas B3 — {fecha.isoformat()}\n")
            for nombre, df in resultados.items():
                archivo.write(f"\n## {nombre}\n")
                archivo.write(df.to_string(index=False))
                archivo.write("\n")
    return resultados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta las consultas de la Parte B3")
    parser.add_argument("--db", default=str(RUTA_DB), help="Ruta de la base SQLite")
    parser.add_argument("--fecha", default="2026-10-27", help="Fecha de corte YYYY-MM-DD")
    parser.add_argument(
        "--salida",
        default=None,
        help="Archivo de texto para los resultados (por defecto salida/consultas_YYYYMMDD.txt)",
    )
    args = parser.parse_args(argv)

    fecha = date.fromisoformat(args.fecha)
    salida = (
        Path(args.salida)
        if args.salida
        else DIR_SALIDA / f"consultas_{fecha.strftime('%Y%m%d')}.txt"
    )
    conexion = sqlite3.connect(args.db)
    try:
        resultados = ejecutar_consultas(conexion, fecha, salida)
    finally:
        conexion.close()

    for nombre, df in resultados.items():
        print(f"\n## {nombre}")
        print(df.to_string(index=False))
    print(f"\nResultados guardados en {salida}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
