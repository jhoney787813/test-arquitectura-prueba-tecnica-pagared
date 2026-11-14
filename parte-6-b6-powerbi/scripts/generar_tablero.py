#!/usr/bin/env python3
"""Genera un prototipo HTML del tablero B6 a partir de dw_pagared.

El objetivo no es reemplazar Power BI: es demostrar, en macOS, que el modelo
tiene los datos y las medidas necesarias. El `.pbix` se construye en Windows
siguiendo el diseño y las medidas DAX de esta carpeta.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

PARTE = Path(__file__).resolve().parents[1]
SALIDA_DEFECTO = PARTE / "powerbi" / "tablero_ventas.html"
PLANTILLA = PARTE / "powerbi" / "plantilla_tablero.html"


def _filas(conexion: sqlite3.Connection) -> list[dict[str, object]]:
    cursor = conexion.execute(
        """
        SELECT d.fecha AS fecha,
               p.zona AS zona,
               pr.producto AS producto,
               c.canal AS canal,
               SUM(f.valor_cop) AS ventas,
               COUNT(*) AS transacciones
          FROM fact_transacciones f
          JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
          JOIN dim_punto p ON p.punto_sk = f.punto_sk
          JOIN dim_producto pr ON pr.producto_sk = f.producto_sk
          JOIN dim_canal c ON c.canal_sk = f.canal_sk
          JOIN dim_estado e ON e.estado_sk = f.estado_sk
         WHERE e.cuenta_como_venta = 1
         GROUP BY d.fecha, p.zona, pr.producto, c.canal
         ORDER BY d.fecha, p.zona, pr.producto, c.canal
        """
    )
    return [
        {
            "fecha": fila["fecha"],
            "zona": fila["zona"],
            "producto": fila["producto"],
            "canal": fila["canal"],
            "ventas": int(fila["ventas"]),
            "transacciones": int(fila["transacciones"]),
        }
        for fila in cursor
    ]


def generar(db: Path, salida: Path, fecha_inicial: date) -> dict[str, object]:
    conexion = sqlite3.connect(db)
    conexion.row_factory = sqlite3.Row
    try:
        filas = _filas(conexion)
    finally:
        conexion.close()

    fechas = sorted({str(fila["fecha"]) for fila in filas})
    datos: dict[str, list[dict[str, object]]] = {fecha: [] for fecha in fechas}
    for fila in filas:
        datos[str(fila["fecha"])].append(
            {
                "zona": fila["zona"],
                "producto": fila["producto"],
                "canal": fila["canal"],
                "ventas": fila["ventas"],
                "transacciones": fila["transacciones"],
            }
        )

    if fecha_inicial.isoformat() not in datos and fechas:
        fecha_inicial = date.fromisoformat(fechas[-1])

    contenido = {
        "fechas": fechas,
        "fecha_inicial": fecha_inicial.isoformat(),
        "datos": datos,
        "meta": {
            "generado": datetime.now().isoformat(timespec="seconds"),
            "fuente": "dw_pagared (SQLite)",
        },
    }
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    html = plantilla.replace("__DATOS__", json.dumps(contenido, ensure_ascii=False))
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    return {"salida": str(salida), "fechas": fechas, "filas": len(filas)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="db/pagared.db")
    parser.add_argument("--salida", default=str(SALIDA_DEFECTO))
    parser.add_argument("--fecha", default="2026-10-27")
    args = parser.parse_args()

    resultado = generar(Path(args.db), Path(args.salida), date.fromisoformat(args.fecha))
    print(f"Tablero generado en {resultado['salida']}")
    print(f"Fechas disponibles: {', '.join(resultado['fechas'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
