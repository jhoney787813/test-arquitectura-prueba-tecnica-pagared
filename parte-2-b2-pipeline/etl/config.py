"""Configuración central del pipeline.

Concentra rutas, nombres de archivo, codificaciones y reglas de negocio para
evitar valores mágicos repartidos por el código. Las rutas se pueden
sobrescribir con variables de entorno (ver ``.env.example``).
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

RAIZ_REPOSITORIO = Path(os.getenv("PAGARED_ROOT") or Path(__file__).resolve().parents[2])


def _ruta_entorno(variable: str, defecto: Path) -> Path:
    """Devuelve la ruta configurada en ``variable`` o el valor por defecto."""
    valor = os.getenv(variable)
    return Path(valor).expanduser() if valor else defecto


DIR_DATOS = _ruta_entorno("PAGARED_DATOS_DIR", RAIZ_REPOSITORIO / "datos")
DIR_SALIDA = _ruta_entorno("PAGARED_SALIDA_DIR", RAIZ_REPOSITORIO / "salida")
DIR_LOGS = _ruta_entorno("PAGARED_LOGS_DIR", RAIZ_REPOSITORIO / "logs")
RUTA_DB = _ruta_entorno("PAGARED_DB_PATH", RAIZ_REPOSITORIO / "db" / "pagared.db")

# --- Archivos de entrada -----------------------------------------------------
ARCHIVO_TRANSACCIONES = "transacciones.csv"
ARCHIVO_DELTA = "transacciones_delta_20261028.csv"
ARCHIVO_PUNTOS = "puntos_venta.csv"

SEPARADOR_CSV = ";"
#: El core entrega UTF-8 con BOM; el maestro de puntos viene en Latin-1.
ENCODING_TRANSACCIONES = "utf-8-sig"
ENCODING_PUNTOS = "latin-1"

# --- Reglas de negocio (correo de Laura Restrepo) ----------------------------
#: Zona horaria de negocio. El core exporta en UTC y el día contable es Colombia.
ZONA_HORARIA = os.getenv("PAGARED_TZ", "America/Bogota")

#: Estados que cuentan como venta: lo aprobado y lo reversado (se cobró comisión).
ESTADOS_VENTA = frozenset({"APROBADA", "REVERSADA"})
ESTADOS_VALIDOS = frozenset({"APROBADA", "RECHAZADA", "ANULADA", "REVERSADA"})

PRODUCTOS_VALIDOS = frozenset({"RECARGA", "PAGO_SERVICIOS", "GIRO"})
CANALES_VALIDOS = frozenset({"POS", "WEB", "APP"})

#: Punto de pruebas de sistemas: se excluye de todos los reportes.
COD_PUNTO_PRUEBAS = "90001"

#: Zona asignada cuando el maestro no tiene zona (se informa, no se descarta).
ZONA_SIN_ASIGNAR = "SIN ZONA"

#: Zona asignada a ventas de puntos que no existen en el maestro (p. ej. 00199).
ZONA_NO_CATALOGADA = "NO CATALOGADO"

#: Fecha de corte de la prueba técnica.
FECHA_CORTE_PRUEBA = date(2026, 10, 27)
