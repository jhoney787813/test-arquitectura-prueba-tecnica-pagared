#!/usr/bin/env python3
"""Exporta el modelo a CSV para conectarlo desde Power BI en macOS."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

PARTE = Path(__file__).resolve().parents[1]
DESTINO_DEFECTO = PARTE / "powerbi" / "datos"


def exportar(db: Path, destino: Path) -> dict[str, int]:
    destino.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(db)
    try:
        consultas = {
            "fact_transacciones": """
                SELECT f.id_transaccion, d.fecha, p.cod_punto, p.nombre AS punto,
                       p.zona, pr.producto, c.canal, e.estado,
                       e.cuenta_como_venta, f.valor_cop,
                       f.fecha_hora_utc, f.fecha_hora_local
                  FROM fact_transacciones f
                  JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
                  JOIN dim_punto p ON p.punto_sk = f.punto_sk
                  JOIN dim_producto pr ON pr.producto_sk = f.producto_sk
                  JOIN dim_canal c ON c.canal_sk = f.canal_sk
                  JOIN dim_estado e ON e.estado_sk = f.estado_sk
                 ORDER BY d.fecha, f.id_transaccion
            """,
            "dim_punto": "SELECT * FROM dim_punto ORDER BY punto_sk",
            "dim_fecha": "SELECT * FROM dim_fecha ORDER BY fecha",
            "dim_producto": "SELECT * FROM dim_producto ORDER BY producto_sk",
            "dim_canal": "SELECT * FROM dim_canal ORDER BY canal_sk",
            "dim_estado": "SELECT * FROM dim_estado ORDER BY estado_sk",
        }
        conteos: dict[str, int] = {}
        for nombre, sql in consultas.items():
            df = pd.read_sql_query(sql, conexion)
            df.to_csv(destino / f"{nombre}.csv", index=False, encoding="utf-8-sig")
            conteos[nombre] = len(df)
        return conteos
    finally:
        conexion.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="db/pagared.db", help="Base SQLite")
    parser.add_argument(
        "--destino",
        default=str(DESTINO_DEFECTO),
        help="Carpeta de salida para los CSV de Power BI",
    )
    args = parser.parse_args()
    conteos = exportar(Path(args.db), Path(args.destino))
    for nombre, cantidad in conteos.items():
        print(f"{nombre}: {cantidad:,} filas")
    print(f"CSV exportados en {args.destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
