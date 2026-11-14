"""CLI del pipeline de ventas."""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from etl import __version__
from etl.config import (
    ARCHIVO_PUNTOS,
    ARCHIVO_TRANSACCIONES,
    DIR_LOGS,
    DIR_SALIDA,
    RUTA_DB,
    ZONA_HORARIA,
)
from etl.fechas import resolver_fecha_corte
from etl.lectura import ErrorDatos, leer_delta, leer_puntos, leer_transacciones
from etl.limpieza import limpiar_puntos, limpiar_transacciones
from etl.modelo import (
    cargar_dimensiones,
    cargar_fact,
    conectar,
    crear_esquema,
    finalizar_carga,
    iniciar_carga,
    rango_fechas,
    registrar_descartes,
)
from etl.reporte import generar_reporte

LOG = logging.getLogger("etl")


def _configurar_logging(nivel: str) -> Path:
    DIR_LOGS.mkdir(parents=True, exist_ok=True)
    ruta = DIR_LOGS / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    formato = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(
        level=getattr(logging, nivel.upper(), logging.INFO),
        format=formato,
        handlers=[logging.StreamHandler(), logging.FileHandler(ruta, encoding="utf-8")],
    )
    return ruta


def _sumar_stats(partes: list[dict[str, object]]) -> dict[str, object]:
    total: dict[str, object] = {
        "leidos": 0,
        "cargados": 0,
        "descartados": 0,
        "por_motivo": Counter(),
        "corregidos": Counter(),
    }
    for stats in partes:
        total["leidos"] += int(stats.get("leidos", 0))
        total["cargados"] += int(stats.get("cargados", 0))
        total["descartados"] += int(stats.get("descartados", 0))
        total["por_motivo"].update(stats.get("por_motivo", {}))
        total["corregidos"].update(stats.get("corregidos", {}))
    total["por_motivo"] = dict(total["por_motivo"])
    total["corregidos"] = dict(total["corregidos"])
    return total


def _imprimir_resumen(resultado: dict[str, object]) -> None:
    print(f"\nREPORTE {resultado['fecha']}")
    print(f"Ventas: ${resultado['total_ventas']:,.0f} COP")
    print(f"Transacciones: {resultado['total_transacciones']:,}")
    print(f"Excel: {resultado['ruta_xlsx']}")
    print(f"Correo: {resultado['ruta_eml']}")
    print("\nVentas por zona:")
    for zona in resultado["zonas"]:
        print(f"  {zona['zona']:<20} ${zona['ventas']:>14,.0f}  ({zona['transacciones']:,})")


def ejecutar(args: argparse.Namespace) -> int:
    fecha_corte = resolver_fecha_corte(args.fecha_corte)
    ruta_db = Path(args.db).expanduser() if args.db else RUTA_DB
    salida = Path(args.salida).expanduser() if args.salida else DIR_SALIDA
    ruta_log = _configurar_logging(args.log_level)

    LOG.info("Inicio del pipeline; fecha_corte=%s db=%s", fecha_corte, ruta_db)
    LOG.info("Archivo de log: %s", ruta_log)

    id_carga: int | None = None
    conexion = None
    try:
        base = leer_transacciones(Path(args.base).expanduser() if args.base else None)
        base_limpia, base_descartes, base_stats = limpiar_transacciones(base, ARCHIVO_TRANSACCIONES)
        LOG.info("Base: %s", base_stats)

        delta_limpia = None
        delta_descartes = None
        delta_stats: dict[str, object] = {}
        if args.delta:
            delta = leer_delta(Path(args.delta).expanduser())
            delta_limpia, delta_descartes, delta_stats = limpiar_transacciones(
                delta, Path(args.delta).name
            )
            LOG.info("Delta: %s", delta_stats)

        puntos = leer_puntos()
        puntos_limpios, puntos_descartes, puntos_stats = limpiar_puntos(puntos, ARCHIVO_PUNTOS)
        LOG.info("Maestro: %s", puntos_stats)

        conexion = conectar(ruta_db)
        crear_esquema(conexion)
        codigos_fact = set(base_limpia["cod_punto"]) if not base_limpia.empty else set()
        if delta_limpia is not None and not delta_limpia.empty:
            codigos_fact |= set(delta_limpia["cod_punto"])
        fechas = rango_fechas(base_limpia, fecha_corte)
        if delta_limpia is not None and not delta_limpia.empty:
            fechas = fechas | rango_fechas(delta_limpia, fecha_corte)
        indice_puntos = cargar_dimensiones(conexion, puntos_limpios, codigos_fact, fechas)

        archivo = ARCHIVO_TRANSACCIONES + (f" + {Path(args.delta).name}" if args.delta else "")
        id_carga = iniciar_carga(
            conexion, fecha_corte, archivo, "base+delta" if args.delta else "base"
        )

        insertados_base, actualizados_base, ignorados_base = cargar_fact(
            conexion, base_limpia, indice_puntos
        )
        insertados = insertados_base
        actualizados = actualizados_base
        ignorados = ignorados_base
        LOG.info(
            "Carga base: insertados=%s actualizados=%s ignorados=%s",
            insertados_base,
            actualizados_base,
            ignorados_base,
        )

        if delta_limpia is not None:
            insertados_delta, actualizados_delta, ignorados_delta = cargar_fact(
                conexion, delta_limpia, indice_puntos
            )
            insertados += insertados_delta
            actualizados += actualizados_delta
            ignorados += ignorados_delta
            LOG.info(
                "Carga delta: insertados=%s actualizados=%s ignorados=%s",
                insertados_delta,
                actualizados_delta,
                ignorados_delta,
            )

        descartes = [base_descartes]
        if delta_descartes is not None:
            descartes.append(delta_descartes)
        descartes_df = pd.concat(descartes, ignore_index=True) if descartes else pd.DataFrame()
        stats_transacciones = _sumar_stats(
            [base_stats, delta_stats] if delta_stats else [base_stats]
        )
        registrar_descartes(conexion, id_carga, descartes_df)
        finalizar_carga(
            conexion,
            id_carga,
            "OK",
            stats_transacciones,
            insertados=insertados,
            actualizados=actualizados,
            ignorados=ignorados,
        )

        resultado = generar_reporte(
            conexion, id_carga, fecha_corte, salida=salida, stats=stats_transacciones
        )
        LOG.info("Reporte generado: %s", resultado["ruta_xlsx"])
        _imprimir_resumen(resultado)
        LOG.info(
            "Fin OK: insertados=%s actualizados=%s ignorados=%s",
            insertados,
            actualizados,
            ignorados,
        )
        return 0
    except (ErrorDatos, ValueError, KeyError) as exc:
        LOG.error("Error de datos: %s", exc)
        if conexion is not None and id_carga is not None:
            finalizar_carga(conexion, id_carga, "FALLIDA", {})
        return 1
    except Exception as exc:  # noqa: BLE001 - el CLI debe reportar cualquier falla
        LOG.exception("Fallo inesperado: %s", exc)
        if conexion is not None and id_carga is not None:
            finalizar_carga(conexion, id_carga, "FALLIDA", {})
        return 1
    finally:
        if conexion is not None:
            conexion.close()


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pagared-etl",
        description="Pipeline ETL de ventas de PagaRed S.A.S.",
    )
    parser.add_argument(
        "--fecha-corte",
        help="Fecha de corte YYYY-MM-DD (por defecto, ayer en America/Bogota)",
    )
    parser.add_argument("--delta", help="Archivo incremental a aplicar después de la base")
    parser.add_argument("--base", help="Archivo principal (por defecto datos/transacciones.csv)")
    parser.add_argument("--db", help="Ruta de la base SQLite")
    parser.add_argument("--salida", help="Carpeta del reporte")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de log",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    if args.fecha_corte:
        try:
            date.fromisoformat(args.fecha_corte)
        except ValueError:
            parser.error("--fecha-corte debe tener formato YYYY-MM-DD")
    print(f"Zona horaria de negocio: {ZONA_HORARIA}")
    return ejecutar(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
