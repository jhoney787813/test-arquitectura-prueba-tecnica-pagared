"""Pruebas del envío idempotente de B4."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "revision" / "enviar_reporte_v2.py"
spec = importlib.util.spec_from_file_location("enviar_reporte_v2", RUTA)
modulo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(modulo)


def _reporte(tmp_path: Path) -> Path:
    ruta = tmp_path / "reporte_ventas_20261027.xlsx"
    ruta.write_bytes(b"PK\x03\x04reporte-de-prueba")
    return ruta


def test_modo_eml_es_idempotente(tmp_path, capsys) -> None:
    reporte = _reporte(tmp_path)
    ledger = tmp_path / "envios.json"
    eml = tmp_path / "salida.eml"
    argumentos = [
        "--reporte",
        str(reporte),
        "--destinatarios",
        "laura@pagared.com",
        "--ledger",
        str(ledger),
        "--eml",
        str(eml),
    ]

    assert modulo.main(argumentos) == 0
    assert eml.exists()
    datos = json.loads(ledger.read_text())
    clave = next(iter(datos["envios"]))
    assert datos["envios"][clave]["estado"] == "SIMULADO"

    assert modulo.main(argumentos) == 0
    datos = json.loads(ledger.read_text())
    assert len(datos["envios"][clave]["intentos"]) == 1
    assert "no se envía de nuevo" in capsys.readouterr().out


def test_reporte_inexistente_devuelve_dos(tmp_path) -> None:
    codigo = modulo.main(
        ["--reporte", str(tmp_path / "no-existe.xlsx"), "--destinatarios", "laura@pagared.com"]
    )
    assert codigo == 2


def test_smtp_fallido_queda_registrado(tmp_path) -> None:
    reporte = _reporte(tmp_path)
    ledger = tmp_path / "envios.json"
    codigo = modulo.main(
        [
            "--reporte",
            str(reporte),
            "--destinatarios",
            "laura@pagared.com",
            "--ledger",
            str(ledger),
            "--modo",
            "smtp",
            "--smtp-host",
            "127.0.0.1",
            "--smtp-port",
            "1",
            "--timeout",
            "1",
        ]
    )
    assert codigo == 1
    datos = json.loads(ledger.read_text())
    clave = next(iter(datos["envios"]))
    assert datos["envios"][clave]["estado"] == "FALLIDO"
