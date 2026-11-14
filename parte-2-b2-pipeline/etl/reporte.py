"""Generación del reporte Excel y del borrador de correo."""

from __future__ import annotations

import os
import sqlite3
from datetime import date, timedelta
from email.message import EmailMessage
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from etl.config import DIR_SALIDA

ENCABEZADO = Font(bold=True, color="FFFFFF")
FONDO_ENCABEZADO = PatternFill("solid", fgColor="1F4E78")
FONDO_TOTAL = PatternFill("solid", fgColor="DDEBF7")
BORDE = Border(bottom=Side(style="thin", color="BFBFBF"))
FORMATO_MONEDA = "#,##0"
FORMATO_PORCENTAJE = "0.0%"


def _leer(conexion: sqlite3.Connection, sql: str, parametros: tuple[object, ...]) -> pd.DataFrame:
    return pd.read_sql_query(sql, conexion, params=parametros)


def resumen_por_zona_producto(conexion: sqlite3.Connection, fecha: date) -> pd.DataFrame:
    return _leer(
        conexion,
        """
        SELECT p.zona AS zona,
               pr.producto AS producto,
               SUM(f.valor_cop) AS ventas,
               COUNT(*) AS transacciones
          FROM fact_transacciones f
          JOIN dim_punto p ON p.punto_sk = f.punto_sk
          JOIN dim_producto pr ON pr.producto_sk = f.producto_sk
          JOIN dim_estado e ON e.estado_sk = f.estado_sk
          JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
         WHERE d.fecha = ? AND e.cuenta_como_venta = 1
         GROUP BY p.zona, pr.producto
         ORDER BY p.zona, ventas DESC
        """,
        (fecha.isoformat(),),
    )


def ventas_por_zona(conexion: sqlite3.Connection, fecha: date) -> pd.DataFrame:
    return _leer(
        conexion,
        """
        SELECT p.zona AS zona,
               SUM(f.valor_cop) AS ventas,
               COUNT(*) AS transacciones
          FROM fact_transacciones f
          JOIN dim_punto p ON p.punto_sk = f.punto_sk
          JOIN dim_estado e ON e.estado_sk = f.estado_sk
          JOIN dim_fecha d ON d.fecha_sk = f.fecha_sk
         WHERE d.fecha = ? AND e.cuenta_como_venta = 1
         GROUP BY p.zona
         ORDER BY ventas DESC
        """,
        (fecha.isoformat(),),
    )


def _comparativo(conexion: sqlite3.Connection, fecha: date) -> pd.DataFrame:
    actual = ventas_por_zona(conexion, fecha).set_index("zona")
    anterior = ventas_por_zona(conexion, fecha - timedelta(days=1)).set_index("zona")
    zonas = sorted(set(actual.index) | set(anterior.index))
    filas: list[dict[str, object]] = []
    for zona in zonas:
        ventas_actual = int(actual.loc[zona, "ventas"]) if zona in actual.index else 0
        ventas_anterior = int(anterior.loc[zona, "ventas"]) if zona in anterior.index else 0
        diferencia = ventas_actual - ventas_anterior
        porcentaje = diferencia / ventas_anterior if ventas_anterior else None
        filas.append(
            {
                "zona": zona,
                "ventas_actual": ventas_actual,
                "ventas_anterior": ventas_anterior,
                "variacion": diferencia,
                "variacion_pct": porcentaje,
            }
        )
    return pd.DataFrame(
        filas,
        columns=["zona", "ventas_actual", "ventas_anterior", "variacion", "variacion_pct"],
    )


def _descartes(conexion: sqlite3.Connection, id_carga: int) -> pd.DataFrame:
    return _leer(
        conexion,
        """
        SELECT archivo, fila, id_transaccion, motivo, detalle
          FROM etl_descartes
         WHERE id_carga = ?
         ORDER BY motivo, fila
        """,
        (id_carga,),
    )


def _encabezado(hoja, fila: int, titulos: list[str]) -> None:
    for columna, titulo in enumerate(titulos, start=1):
        celda = hoja.cell(row=fila, column=columna, value=titulo)
        celda.font = ENCABEZADO
        celda.fill = FONDO_ENCABEZADO
        celda.alignment = Alignment(horizontal="center")
        celda.border = BORDE


def _anchos(hoja, anchos: list[int]) -> None:
    for columna, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(columna)].width = ancho


def _escribir_resumen(hoja, datos: pd.DataFrame, fecha: date) -> None:
    hoja["A1"] = f"Reporte de ventas — {fecha.isoformat()}"
    hoja["A1"].font = Font(bold=True, size=14)
    hoja["A2"] = "Ventas = APROBADA + REVERSADA; excluye ANULADA, RECHAZADA y el punto 90001"
    hoja["A2"].font = Font(italic=True, size=9)

    _encabezado(hoja, 4, ["Zona", "Producto", "Ventas COP", "Transacciones"])
    fila = 5
    for _, registro in datos.iterrows():
        hoja.cell(row=fila, column=1, value=registro["zona"])
        hoja.cell(row=fila, column=2, value=registro["producto"])
        hoja.cell(row=fila, column=3, value=int(registro["ventas"]))
        hoja.cell(row=fila, column=4, value=int(registro["transacciones"]))
        hoja.cell(row=fila, column=3).number_format = FORMATO_MONEDA
        fila += 1

    hoja.cell(row=fila, column=1, value="TOTAL")
    hoja.cell(row=fila, column=2, value="")
    hoja.cell(row=fila, column=3, value=int(datos["ventas"].sum()) if not datos.empty else 0)
    hoja.cell(row=fila, column=4, value=int(datos["transacciones"].sum()) if not datos.empty else 0)
    hoja.cell(row=fila, column=3).number_format = FORMATO_MONEDA
    for columna in range(1, 5):
        hoja.cell(row=fila, column=columna).font = Font(bold=True)
        hoja.cell(row=fila, column=columna).fill = FONDO_TOTAL
    _anchos(hoja, [22, 18, 18, 15])
    hoja.freeze_panes = "A5"


def _escribir_comparativo(hoja, datos: pd.DataFrame, fecha: date) -> None:
    hoja["A1"] = "Comparativo contra el día anterior por zona"
    hoja["A1"].font = Font(bold=True, size=14)
    hoja["A2"] = f"Día {fecha.isoformat()} vs. {(fecha - timedelta(days=1)).isoformat()}"
    hoja["A2"].font = Font(italic=True, size=9)

    _encabezado(
        hoja,
        4,
        [
            "Zona",
            f"Ventas {fecha.isoformat()}",
            "Ventas día anterior",
            "Variación COP",
            "Variación %",
        ],
    )
    fila = 5
    for _, registro in datos.iterrows():
        hoja.cell(row=fila, column=1, value=registro["zona"])
        hoja.cell(row=fila, column=2, value=int(registro["ventas_actual"]))
        hoja.cell(row=fila, column=3, value=int(registro["ventas_anterior"]))
        hoja.cell(row=fila, column=4, value=int(registro["variacion"]))
        if registro["variacion_pct"] is None:
            hoja.cell(row=fila, column=5, value="N/A")
        else:
            celda = hoja.cell(row=fila, column=5, value=float(registro["variacion_pct"]))
            celda.number_format = FORMATO_PORCENTAJE
        hoja.cell(row=fila, column=2).number_format = FORMATO_MONEDA
        hoja.cell(row=fila, column=3).number_format = FORMATO_MONEDA
        hoja.cell(row=fila, column=4).number_format = FORMATO_MONEDA
        fila += 1
    _anchos(hoja, [22, 20, 20, 18, 14])
    hoja.freeze_panes = "A5"


def _escribir_calidad(
    hoja,
    descartes: pd.DataFrame,
    stats: dict[str, object],
    id_carga: int,
) -> None:
    hoja["A1"] = "Calidad del cargue"
    hoja["A1"].font = Font(bold=True, size=14)
    hoja["A2"] = (
        f"Carga #{id_carga} — leídos: {stats.get('leidos', 0)}; "
        f"cargados: {stats.get('cargados', 0)}; descartados: {stats.get('descartados', 0)}"
    )
    hoja["A2"].font = Font(italic=True, size=9)

    motivos = (
        descartes.groupby("motivo").size().reset_index(name="registros")
        if not descartes.empty
        else pd.DataFrame(columns=["motivo", "registros"])
    )
    hoja["A4"] = "Descartes por motivo"
    hoja["A4"].font = Font(bold=True)
    _encabezado(hoja, 5, ["Motivo", "Registros"])
    fila = 6
    for _, registro in motivos.iterrows():
        hoja.cell(row=fila, column=1, value=registro["motivo"])
        hoja.cell(row=fila, column=2, value=int(registro["registros"]))
        fila += 1

    fila += 1
    hoja.cell(row=fila, column=1, value="Correcciones aplicadas").font = Font(bold=True)
    fila += 1
    _encabezado(hoja, fila, ["Corrección", "Registros"])
    fila += 1
    corregidos = stats.get("corregidos", {}) or {}
    if not corregidos:
        hoja.cell(row=fila, column=1, value="Sin correcciones")
        fila += 1
    for nombre, cantidad in corregidos.items():
        hoja.cell(row=fila, column=1, value=nombre)
        hoja.cell(row=fila, column=2, value=int(cantidad))
        fila += 1

    fila += 1
    hoja.cell(row=fila, column=1, value="Detalle de descartes").font = Font(bold=True)
    fila += 1
    _encabezado(hoja, fila, ["Archivo", "Fila", "ID transacción", "Motivo", "Detalle"])
    fila += 1
    for _, registro in descartes.iterrows():
        hoja.cell(row=fila, column=1, value=registro["archivo"])
        hoja.cell(row=fila, column=2, value=int(registro["fila"]))
        hoja.cell(row=fila, column=3, value=registro["id_transaccion"])
        hoja.cell(row=fila, column=4, value=registro["motivo"])
        hoja.cell(row=fila, column=5, value=registro["detalle"])
        fila += 1
    _anchos(hoja, [28, 10, 18, 22, 60])
    hoja.freeze_panes = "A6"


def _generar_eml(ruta_xlsx: Path, fecha: date, resumen: pd.DataFrame) -> Path:
    destinatario = os.getenv("PAGARED_REPORTE_PARA", "laura.restrepo@pagared.com")
    total_ventas = int(resumen["ventas"].sum()) if not resumen.empty else 0
    total_transacciones = int(resumen["transacciones"].sum()) if not resumen.empty else 0

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Reporte de ventas {fecha.isoformat()}"
    mensaje["From"] = os.getenv("PAGARED_REPORTE_DE", "etl@pagared.com")
    mensaje["To"] = destinatario
    mensaje.set_content(
        "Hola Laura,\n\n"
        f"Adjunto el reporte de ventas del {fecha.isoformat()}.\n"
        f"Ventas: ${total_ventas:,.0f} COP en {total_transacciones:,} transacciones.\n\n"
        "El detalle por zona, producto y calidad está en el archivo adjunto.\n\n"
        "Equipo de Automatización"
    )
    mensaje.add_attachment(
        ruta_xlsx.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=ruta_xlsx.name,
    )
    ruta_eml = ruta_xlsx.with_suffix(".eml")
    ruta_eml.write_bytes(mensaje.as_bytes())
    return ruta_eml


def generar_reporte(
    conexion: sqlite3.Connection,
    id_carga: int,
    fecha: date,
    salida: Path | None = None,
    stats: dict[str, object] | None = None,
) -> dict[str, object]:
    """Genera el Excel, el `.eml` y devuelve los totales para consola."""
    salida = salida or DIR_SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    stats = stats or {}

    resumen = resumen_por_zona_producto(conexion, fecha)
    comparativo = _comparativo(conexion, fecha)
    descartes = _descartes(conexion, id_carga)

    libro = Workbook()
    hoja_resumen = libro.active
    hoja_resumen.title = "Resumen"
    _escribir_resumen(hoja_resumen, resumen, fecha)
    _escribir_comparativo(libro.create_sheet("Comparativo"), comparativo, fecha)
    _escribir_calidad(libro.create_sheet("Calidad"), descartes, stats, id_carga)

    ruta_xlsx = salida / f"reporte_ventas_{fecha.strftime('%Y%m%d')}.xlsx"
    libro.save(ruta_xlsx)
    ruta_eml = _generar_eml(ruta_xlsx, fecha, resumen)

    zonas = ventas_por_zona(conexion, fecha)
    return {
        "fecha": fecha.isoformat(),
        "ruta_xlsx": str(ruta_xlsx),
        "ruta_eml": str(ruta_eml),
        "total_ventas": int(resumen["ventas"].sum()) if not resumen.empty else 0,
        "total_transacciones": int(resumen["transacciones"].sum()) if not resumen.empty else 0,
        "zonas": zonas.to_dict(orient="records"),
    }
