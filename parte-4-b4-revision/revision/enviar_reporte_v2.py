#!/usr/bin/env python3
"""Envío idempotente y observable de reportes (versión corregida de B4).

La versión original tenía credenciales en el código, `except: pass`, un envío
sin clave de idempotencia y un job que siempre terminaba en verde. Esta versión
valida la configuración, registra cada intento y solo envía una vez por clave.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

PARTE = Path(__file__).resolve().parents[1]
LEDGER_DEFECTO = PARTE / "envios.json"


def cargar_ledger(ruta: Path) -> dict[str, object]:
    if not ruta.exists():
        return {"envios": {}}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"envios": {}}
    if not isinstance(datos, dict):
        return {"envios": {}}
    datos.setdefault("envios", {})
    return datos


def guardar_ledger(ruta: Path, datos: dict[str, object]) -> None:
    """Escribe el ledger de forma atómica para no dejarlo a medias."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    os.replace(temporal, ruta)


def clave_por_contenido(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:24]


def _destinatarios(texto: str) -> list[str]:
    correos = [correo.strip() for correo in texto.split(",") if correo.strip()]
    if not correos or any("@" not in correo for correo in correos):
        raise ValueError("Los destinatarios deben ser correos separados por coma")
    return correos


def construir_mensaje(
    reporte: Path,
    destinatarios: list[str],
    asunto: str,
    remitente: str,
) -> EmailMessage:
    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = ", ".join(destinatarios)
    mensaje["Message-ID"] = make_msgid(domain="pagared.com")
    mensaje.set_content(
        "Hola,\n\n"
        f"Adjunto el reporte {reporte.name}.\n"
        "Este envío fue registrado con una clave de idempotencia para evitar duplicados.\n\n"
        "Equipo de Automatización"
    )
    mensaje.add_attachment(
        reporte.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if reporte.suffix.lower() == ".xlsx"
        else "octet-stream",
        filename=reporte.name,
    )
    return mensaje


def _registrar(
    ledger: dict[str, object],
    clave: str,
    estado: str,
    modo: str,
    detalle: str,
) -> None:
    envios = ledger.setdefault("envios", {})
    entrada = envios.setdefault(clave, {"estado": estado, "intentos": []})
    entrada["estado"] = estado
    entrada["intentos"].append(
        {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "modo": modo,
            "estado": estado,
            "detalle": detalle,
        }
    )


def enviar(
    reporte: Path,
    destinatarios: list[str],
    asunto: str,
    remitente: str,
    modo: str,
    ruta_eml: Path,
    ledger: dict[str, object],
    clave: str,
    smtp_host: str | None,
    smtp_port: int,
    usuario: str | None,
    password_env: str,
    timeout: int,
    usar_tls: bool,
) -> int:
    mensaje = construir_mensaje(reporte, destinatarios, asunto, remitente)

    if modo == "eml":
        ruta_eml.parent.mkdir(parents=True, exist_ok=True)
        ruta_eml.write_bytes(mensaje.as_bytes())
        _registrar(ledger, clave, "SIMULADO", modo, f"Borrador escrito en {ruta_eml}")
        return 0

    if not smtp_host:
        raise ValueError("--smtp-host es obligatorio en modo smtp")

    password = os.getenv(password_env, "")
    contexto = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as servidor:
        if usar_tls:
            servidor.starttls(context=contexto)
        if usuario:
            servidor.login(usuario, password)
        servidor.send_message(mensaje)
    _registrar(ledger, clave, "ENVIADO", modo, f"Enviado a {', '.join(destinatarios)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reporte", required=True, help="Archivo a enviar")
    parser.add_argument("--destinatarios", required=True, help="Correos separados por coma")
    parser.add_argument("--asunto", default=None, help="Asunto del correo")
    parser.add_argument("--remitente", default="etl@pagared.com")
    parser.add_argument(
        "--clave", default=None, help="Clave de idempotencia (por defecto, hash del archivo)"
    )
    parser.add_argument("--ledger", default=str(LEDGER_DEFECTO), help="JSON de control de envíos")
    parser.add_argument("--modo", choices=["eml", "smtp"], default="eml")
    parser.add_argument("--eml", default=None, help="Ruta del borrador en modo eml")
    parser.add_argument("--smtp-host", default=None)
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--usuario", default=None)
    parser.add_argument("--password-env", default="PAGARED_SMTP_PASSWORD")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument(
        "--sin-tls",
        action="store_true",
        help="No iniciar STARTTLS (solo para un servidor SMTP local de prueba)",
    )
    parser.add_argument("--forzar", action="store_true", help="Reenviar aunque la clave exista")
    args = parser.parse_args(argv)

    reporte = Path(args.reporte)
    if not reporte.is_file() or reporte.stat().st_size == 0:
        print(f"ERROR: no existe o está vacío el reporte {reporte}", file=sys.stderr)
        return 2

    try:
        destinatarios = _destinatarios(args.destinatarios)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    ruta_ledger = Path(args.ledger)
    ledger = cargar_ledger(ruta_ledger)
    clave = args.clave or clave_por_contenido(reporte)
    entrada = ledger.get("envios", {}).get(clave, {})
    if entrada.get("estado") in {"ENVIADO", "SIMULADO"} and not args.forzar:
        print(f"Ya registrado con la clave {clave}; no se envía de nuevo.")
        return 0

    asunto = args.asunto or f"Reporte {reporte.stem}"
    ruta_eml = Path(args.eml) if args.eml else reporte.with_suffix(".eml")
    try:
        codigo = enviar(
            reporte=reporte,
            destinatarios=destinatarios,
            asunto=asunto,
            remitente=args.remitente,
            modo=args.modo,
            ruta_eml=ruta_eml,
            ledger=ledger,
            clave=clave,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            usuario=args.usuario,
            password_env=args.password_env,
            timeout=args.timeout,
            usar_tls=not args.sin_tls,
        )
    except Exception as exc:  # noqa: BLE001 - el fallo debe quedar registrado
        _registrar(ledger, clave, "FALLIDO", args.modo, str(exc))
        guardar_ledger(ruta_ledger, ledger)
        print(f"ERROR de envío: {exc}", file=sys.stderr)
        return 1

    guardar_ledger(ruta_ledger, ledger)
    if args.modo == "eml":
        print(f"Borrador generado en {ruta_eml} (clave {clave}).")
    else:
        print(f"Correo enviado a {', '.join(destinatarios)} (clave {clave}).")
    return codigo


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
