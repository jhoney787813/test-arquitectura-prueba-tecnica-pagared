"""Pruebas de integración del pipeline: limpieza, idempotencia y delta."""

from __future__ import annotations

from datetime import date

import pandas as pd

from etl.limpieza import limpiar_puntos, limpiar_transacciones
from etl.modelo import (
    cargar_dimensiones,
    cargar_fact,
    conectar,
    crear_esquema,
    rango_fechas,
)


def _transaccion(
    id_transaccion: str,
    estado: str = "APROBADA",
    valor: str = "100.00",
    fecha: str = "2026-10-27 15:00:00",
    actualizacion: str | None = None,
    cod_punto: str = "00101",
) -> dict[str, str]:
    return {
        "id_transaccion": id_transaccion,
        "fecha_transaccion": fecha,
        "fecha_actualizacion": actualizacion or fecha,
        "cod_punto": cod_punto,
        "producto": "RECARGA",
        "valor": valor,
        "estado": estado,
        "canal": "POS",
    }


def _puntos() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "cod_punto": "00101",
                "nombre": "Punto Uno",
                "zona": "VALLE DE ABURRA",
                "activo": "S",
                "fecha_apertura": "2020-01-01",
                "archivo": "puntos_venta.csv",
                "fila": 2,
            },
            {
                "cod_punto": "00102",
                "nombre": "Punto Dos",
                "zona": "Oriente",
                "activo": "S",
                "fecha_apertura": "2021-01-01",
                "archivo": "puntos_venta.csv",
                "fila": 3,
            },
        ]
    )


def _base_montada(tmp_path, transacciones: list[dict[str, str]]):
    base = pd.DataFrame(transacciones)
    limpias, descartes, stats = limpiar_transacciones(base)
    puntos, _, _ = limpiar_puntos(_puntos())
    conexion = conectar(tmp_path / "pagared.db")
    crear_esquema(conexion)
    indice = cargar_dimensiones(
        conexion,
        puntos,
        set(limpias["cod_punto"]),
        rango_fechas(limpias, date(2026, 10, 27)),
    )
    return conexion, limpias, descartes, stats, indice


def test_limpieza_normaliza_codigo_fecha_y_excluye_punto_pruebas() -> None:
    base = pd.DataFrame(
        [
            _transaccion("TX000000001", fecha="2026-10-28T03:00:00Z"),
            _transaccion("TX000000002", cod_punto="131"),
            _transaccion("TX000000003", cod_punto="90001"),
            _transaccion("TX000000004", valor="N/A"),
        ]
    )

    limpias, descartes, stats = limpiar_transacciones(base)

    assert list(limpias["id_transaccion"]) == ["TX000000001", "TX000000002"]
    assert str(limpias.iloc[0]["fecha_negocio"]) == "2026-10-27"
    assert limpias.iloc[1]["cod_punto"] == "00131"
    assert set(descartes["motivo"]) == {"punto_pruebas", "valor_invalido"}
    assert stats["cargados"] == 2


def test_carga_idempotente_no_duplica(tmp_path) -> None:
    conexion, limpias, _, _, indice = _base_montada(
        tmp_path, [_transaccion("TX000000010", valor="100.00")]
    )
    try:
        primera = cargar_fact(conexion, limpias, indice)
        segunda = cargar_fact(conexion, limpias, indice)

        assert primera == (1, 0, 0)
        assert segunda == (0, 0, 1)
        assert conexion.execute("SELECT COUNT(*) FROM fact_transacciones").fetchone()[0] == 1
        assert (
            conexion.execute("SELECT SUM(valor_cop) FROM fact_transacciones").fetchone()[0] == 100
        )
    finally:
        conexion.close()


def test_delta_actualiza_estado_y_total(tmp_path) -> None:
    conexion, limpias, _, _, indice = _base_montada(
        tmp_path, [_transaccion("TX000000020", valor="100.00")]
    )
    try:
        cargar_fact(conexion, limpias, indice)

        delta = pd.DataFrame(
            [
                _transaccion(
                    "TX000000020",
                    estado="ANULADA",
                    actualizacion="2026-10-28 22:00:00",
                )
            ]
        )
        delta_limpia, _, _ = limpiar_transacciones(delta, "delta.csv")
        resultado = cargar_fact(conexion, delta_limpia, indice)

        assert resultado == (0, 1, 0)
        estado = conexion.execute(
            """
            SELECT e.estado
              FROM fact_transacciones f
              JOIN dim_estado e ON e.estado_sk = f.estado_sk
             WHERE f.id_transaccion = 'TX000000020'
            """
        ).fetchone()[0]
        assert estado == "ANULADA"
        ventas = conexion.execute(
            """
            SELECT COALESCE(SUM(f.valor_cop), 0)
              FROM fact_transacciones f
              JOIN dim_estado e ON e.estado_sk = f.estado_sk
             WHERE e.cuenta_como_venta = 1
            """
        ).fetchone()[0]
        assert ventas == 0
    finally:
        conexion.close()


def test_delta_obsoleto_se_ignora(tmp_path) -> None:
    conexion, limpias, _, _, indice = _base_montada(
        tmp_path, [_transaccion("TX000000030", actualizacion="2026-10-28 10:00:00")]
    )
    try:
        cargar_fact(conexion, limpias, indice)
        delta = pd.DataFrame(
            [
                _transaccion(
                    "TX000000030",
                    estado="ANULADA",
                    actualizacion="2026-10-27 09:00:00",
                )
            ]
        )
        delta_limpia, _, _ = limpiar_transacciones(delta, "delta.csv")
        resultado = cargar_fact(conexion, delta_limpia, indice)

        assert resultado == (0, 0, 1)
        estado = conexion.execute(
            """
            SELECT e.estado
              FROM fact_transacciones f
              JOIN dim_estado e ON e.estado_sk = f.estado_sk
             WHERE f.id_transaccion = 'TX000000030'
            """
        ).fetchone()[0]
        assert estado == "APROBADA"
    finally:
        conexion.close()
