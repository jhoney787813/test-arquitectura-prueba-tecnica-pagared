"""Modelo dimensional, carga idempotente y auditoría del pipeline."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from etl.config import (
    CANALES_VALIDOS,
    COD_PUNTO_PRUEBAS,
    ESTADOS_VALIDOS,
    PRODUCTOS_VALIDOS,
    ZONA_NO_CATALOGADA,
    ZONA_SIN_ASIGNAR,
)

ESQUEMA = """
CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_sk INTEGER PRIMARY KEY,
    fecha TEXT NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    nombre_mes TEXT NOT NULL,
    es_fin_semana INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_punto (
    punto_sk INTEGER PRIMARY KEY,
    cod_punto TEXT NOT NULL,
    nombre TEXT NOT NULL,
    zona TEXT NOT NULL,
    activo TEXT NOT NULL,
    valido_desde TEXT NOT NULL,
    valido_hasta TEXT NOT NULL,
    es_actual INTEGER NOT NULL,
    UNIQUE (cod_punto, valido_desde)
);

CREATE TABLE IF NOT EXISTS dim_producto (
    producto_sk INTEGER PRIMARY KEY,
    producto TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_canal (
    canal_sk INTEGER PRIMARY KEY,
    canal TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_estado (
    estado_sk INTEGER PRIMARY KEY,
    estado TEXT NOT NULL UNIQUE,
    cuenta_como_venta INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_transacciones (
    id_transaccion TEXT PRIMARY KEY,
    fecha_sk INTEGER NOT NULL REFERENCES dim_fecha(fecha_sk),
    punto_sk INTEGER NOT NULL REFERENCES dim_punto(punto_sk),
    producto_sk INTEGER NOT NULL REFERENCES dim_producto(producto_sk),
    canal_sk INTEGER NOT NULL REFERENCES dim_canal(canal_sk),
    estado_sk INTEGER NOT NULL REFERENCES dim_estado(estado_sk),
    valor_cop INTEGER NOT NULL,
    fecha_hora_utc TEXT NOT NULL,
    fecha_hora_local TEXT NOT NULL,
    fecha_actualizacion_utc TEXT NOT NULL,
    cargado_en TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_fecha ON fact_transacciones (fecha_sk);
CREATE INDEX IF NOT EXISTS idx_fact_punto ON fact_transacciones (punto_sk);
CREATE INDEX IF NOT EXISTS idx_fact_estado ON fact_transacciones (estado_sk);

CREATE TABLE IF NOT EXISTS etl_cargas (
    id_carga INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_corte TEXT NOT NULL,
    archivo TEXT NOT NULL,
    modo TEXT NOT NULL,
    leidos INTEGER NOT NULL DEFAULT 0,
    descartados INTEGER NOT NULL DEFAULT 0,
    cargados INTEGER NOT NULL DEFAULT 0,
    insertados INTEGER NOT NULL DEFAULT 0,
    actualizados INTEGER NOT NULL DEFAULT 0,
    ignorados INTEGER NOT NULL DEFAULT 0,
    estado TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fin TEXT
);

CREATE TABLE IF NOT EXISTS etl_descartes (
    id_descarte INTEGER PRIMARY KEY AUTOINCREMENT,
    id_carga INTEGER NOT NULL REFERENCES etl_cargas(id_carga),
    archivo TEXT NOT NULL,
    fila INTEGER NOT NULL,
    id_transaccion TEXT,
    motivo TEXT NOT NULL,
    detalle TEXT
);
"""

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

PRODUCTOS_SK = {producto: i + 1 for i, producto in enumerate(sorted(PRODUCTOS_VALIDOS))}
CANALES_SK = {canal: i + 1 for i, canal in enumerate(sorted(CANALES_VALIDOS))}
ESTADOS_SK = {estado: i + 1 for i, estado in enumerate(sorted(ESTADOS_VALIDOS))}


def conectar(ruta: Path) -> sqlite3.Connection:
    """Abre (y crea si hace falta) la base SQLite con claves foráneas activas."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(ESQUEMA)
    conexion.commit()


def _insertar_catalogos(conexion: sqlite3.Connection) -> None:
    for producto, sk in PRODUCTOS_SK.items():
        conexion.execute(
            "INSERT OR IGNORE INTO dim_producto (producto_sk, producto) VALUES (?, ?)",
            (sk, producto),
        )
    for canal, sk in CANALES_SK.items():
        conexion.execute(
            "INSERT OR IGNORE INTO dim_canal (canal_sk, canal) VALUES (?, ?)",
            (sk, canal),
        )
    for estado, sk in ESTADOS_SK.items():
        conexion.execute(
            "INSERT OR IGNORE INTO dim_estado (estado_sk, estado, cuenta_como_venta) VALUES (?, ?, ?)",
            (sk, estado, int(estado in {"APROBADA", "REVERSADA"})),
        )


def _insertar_fechas(conexion: sqlite3.Connection, fechas: set[date]) -> None:
    for fecha in sorted(fechas):
        conexion.execute(
            """
            INSERT OR IGNORE INTO dim_fecha
                (fecha_sk, fecha, anio, mes, dia, dia_semana, nombre_mes, es_fin_semana)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(fecha.strftime("%Y%m%d")),
                fecha.isoformat(),
                fecha.year,
                fecha.month,
                fecha.day,
                fecha.weekday(),
                MESES[fecha.month - 1],
                int(fecha.weekday() >= 5),
            ),
        )


def construir_versiones_punto(
    puntos: pd.DataFrame,
    codigos_fact: set[str],
) -> tuple[list[dict[str, object]], dict[str, list[tuple[date, date, int]]]]:
    """Construye la dimensión SCD2 y la tabla de búsqueda por código y fecha."""
    versiones: list[dict[str, object]] = []
    indice: dict[str, list[tuple[date, date, int]]] = {}

    puntos = puntos[puntos["cod_punto"] != COD_PUNTO_PRUEBAS].sort_values(
        ["cod_punto", "fecha_apertura", "fila"], kind="stable"
    )

    for cod_punto, grupo in puntos.groupby("cod_punto", sort=True):
        grupo = grupo.drop_duplicates("fecha_apertura", keep="last").reset_index(drop=True)
        for posicion, fila in grupo.iterrows():
            desde = fila["fecha_apertura"]
            if posicion + 1 < len(grupo):
                hasta = grupo.iloc[posicion + 1]["fecha_apertura"] - timedelta(days=1)
            else:
                hasta = date(9999, 12, 31)
            sk = int(cod_punto) * 100 + posicion
            versiones.append(
                {
                    "punto_sk": sk,
                    "cod_punto": cod_punto,
                    "nombre": fila["nombre"],
                    "zona": fila["zona"] if fila["zona"] else ZONA_SIN_ASIGNAR,
                    "activo": fila["activo"],
                    "valido_desde": desde.isoformat(),
                    "valido_hasta": hasta.isoformat(),
                    "es_actual": int(posicion + 1 == len(grupo)),
                }
            )
            indice.setdefault(cod_punto, []).append((desde, hasta, sk))

    # Puntos que aparecen en el hecho pero no en el maestro.
    for cod_punto in sorted(codigos_fact - set(indice)):
        sk = int(cod_punto) * 100 + 99
        versiones.append(
            {
                "punto_sk": sk,
                "cod_punto": cod_punto,
                "nombre": f"Punto no catalogado {cod_punto}",
                "zona": ZONA_NO_CATALOGADA,
                "activo": "N",
                "valido_desde": "1900-01-01",
                "valido_hasta": "9999-12-31",
                "es_actual": 1,
            }
        )
        indice[cod_punto] = [(date(1900, 1, 1), date(9999, 12, 31), sk)]

    return versiones, indice


def resolver_punto_sk(
    indice: dict[str, list[tuple[date, date, int]]],
    cod_punto: str,
    fecha: date,
) -> int:
    """Devuelve el `punto_sk` vigente para un código y una fecha de negocio."""
    opciones = indice[cod_punto]
    for desde, hasta, sk in opciones:
        if desde <= fecha <= hasta:
            return sk
    return opciones[-1][2] if fecha > opciones[-1][1] else opciones[0][2]


def cargar_dimensiones(
    conexion: sqlite3.Connection,
    puntos: pd.DataFrame,
    codigos_fact: set[str],
    fechas: set[date],
) -> dict[str, list[tuple[date, date, int]]]:
    """Carga catálogos, calendario y la dimensión de punto con SCD2."""
    _insertar_catalogos(conexion)
    _insertar_fechas(conexion, fechas)

    existentes = conexion.execute("SELECT COUNT(*) FROM dim_punto").fetchone()[0]
    versiones, indice = construir_versiones_punto(puntos, codigos_fact)
    if existentes == 0:
        conexion.executemany(
            """
            INSERT OR IGNORE INTO dim_punto
                (punto_sk, cod_punto, nombre, zona, activo, valido_desde, valido_hasta, es_actual)
            VALUES (:punto_sk, :cod_punto, :nombre, :zona, :activo, :valido_desde, :valido_hasta, :es_actual)
            """,
            versiones,
        )
    conexion.commit()
    return indice


def iniciar_carga(
    conexion: sqlite3.Connection,
    fecha_corte: date,
    archivo: str,
    modo: str,
) -> int:
    cursor = conexion.execute(
        """
        INSERT INTO etl_cargas (fecha_corte, archivo, modo, estado, inicio)
        VALUES (?, ?, ?, 'EN_PROCESO', ?)
        """,
        (fecha_corte.isoformat(), archivo, modo, datetime.now().isoformat(timespec="seconds")),
    )
    conexion.commit()
    return int(cursor.lastrowid)


def finalizar_carga(
    conexion: sqlite3.Connection,
    id_carga: int,
    estado: str,
    stats: dict[str, object],
    insertados: int = 0,
    actualizados: int = 0,
    ignorados: int = 0,
) -> None:
    conexion.execute(
        """
        UPDATE etl_cargas
           SET leidos = ?, descartados = ?, cargados = ?,
               insertados = ?, actualizados = ?, ignorados = ?,
               estado = ?, fin = ?
         WHERE id_carga = ?
        """,
        (
            int(stats.get("leidos", 0)),
            int(stats.get("descartados", 0)),
            int(stats.get("cargados", 0)),
            insertados,
            actualizados,
            ignorados,
            estado,
            datetime.now().isoformat(timespec="seconds"),
            id_carga,
        ),
    )
    conexion.commit()


def registrar_descartes(
    conexion: sqlite3.Connection,
    id_carga: int,
    descartes: pd.DataFrame,
) -> None:
    if descartes.empty:
        return
    filas = [
        (
            id_carga,
            str(fila["archivo"]),
            int(fila["fila"]),
            str(fila["id_transaccion"]),
            str(fila["motivo"]),
            str(fila["detalle"]),
        )
        for _, fila in descartes.iterrows()
    ]
    conexion.executemany(
        """
        INSERT INTO etl_descartes
            (id_carga, archivo, fila, id_transaccion, motivo, detalle)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        filas,
    )
    conexion.commit()


def _formato_fecha(momento: object) -> str:
    if isinstance(momento, datetime):
        return momento.isoformat(sep=" ", timespec="seconds")
    return str(momento)


def cargar_fact(
    conexion: sqlite3.Connection,
    transacciones: pd.DataFrame,
    indice_puntos: dict[str, list[tuple[date, date, int]]],
) -> tuple[int, int, int]:
    """Inserta o actualiza el hecho; devuelve (insertados, actualizados, ignorados)."""
    existentes = {
        fila["id_transaccion"]: fila["fecha_actualizacion_utc"]
        for fila in conexion.execute(
            "SELECT id_transaccion, fecha_actualizacion_utc FROM fact_transacciones"
        )
    }
    _insertar_fechas(conexion, set(transacciones["fecha_negocio"].tolist()))
    insertar: list[tuple[object, ...]] = []
    actualizar: list[tuple[object, ...]] = []
    ignorados = 0
    ahora = datetime.now().isoformat(timespec="seconds")

    for fila in transacciones.itertuples(index=False):
        fecha = fila.fecha_negocio
        fa = _formato_fecha(fila.fecha_actualizacion_utc)
        punto_sk = resolver_punto_sk(indice_puntos, fila.cod_punto, fecha)
        fecha_sk = int(fecha.strftime("%Y%m%d"))
        valores = (
            fecha_sk,
            punto_sk,
            PRODUCTOS_SK[fila.producto],
            CANALES_SK[fila.canal],
            ESTADOS_SK[fila.estado],
            int(fila.valor_cop),
            _formato_fecha(fila.fecha_transaccion_utc),
            _formato_fecha(fila.fecha_hora_local),
            fa,
            ahora,
            fila.id_transaccion,
        )
        anterior = existentes.get(fila.id_transaccion)
        if anterior is None:
            insertar.append((fila.id_transaccion, *valores[:-1]))
        elif fa > anterior:
            actualizar.append(valores)
        else:
            ignorados += 1

    if insertar:
        conexion.executemany(
            """
            INSERT INTO fact_transacciones
                (id_transaccion, fecha_sk, punto_sk, producto_sk, canal_sk, estado_sk,
                 valor_cop, fecha_hora_utc, fecha_hora_local, fecha_actualizacion_utc, cargado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            insertar,
        )
    if actualizar:
        conexion.executemany(
            """
            UPDATE fact_transacciones
               SET fecha_sk = ?, punto_sk = ?, producto_sk = ?, canal_sk = ?, estado_sk = ?,
                   valor_cop = ?, fecha_hora_utc = ?, fecha_hora_local = ?,
                   fecha_actualizacion_utc = ?, cargado_en = ?
             WHERE id_transaccion = ?
            """,
            actualizar,
        )
    conexion.commit()
    return len(insertar), len(actualizar), ignorados


def rango_fechas(transacciones: pd.DataFrame, fecha_corte: date) -> set[date]:
    """Genera el calendario necesario, incluido el día anterior al corte."""
    fechas = set(transacciones["fecha_negocio"].tolist())
    fechas.add(fecha_corte)
    fechas.add(fecha_corte - timedelta(days=1))
    if not fechas:
        return {fecha_corte}
    inicio = min(fechas) - timedelta(days=1)
    fin = max(fechas) + timedelta(days=1)
    total = (fin - inicio).days + 1
    return {inicio + timedelta(days=i) for i in range(total)}
