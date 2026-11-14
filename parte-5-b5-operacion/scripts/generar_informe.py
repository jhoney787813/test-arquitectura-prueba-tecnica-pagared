#!/usr/bin/env python3
"""Compila el informe consolidado en Markdown, HTML y PDF.

Requiere Google Chrome para imprimir el HTML a PDF. El contenido se arma con
las secciones ya redactadas en docs/ y docs/secciones/.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import markdown
from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"
SECCIONES = DOCS / "secciones"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SALIDA_MD = DOCS / "informe_consolidado.md"
SALIDA_HTML = DOCS / "informe_consolidado.html"
SALIDA_PDF = RAIZ / "INFORME_Jhon_E.pdf"
REPO = "https://github.com/jhoney787813/test-arquitectura-prueba-tecnica-pagared.git"

CSS = """
@page { size: A4; margin: 14mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body {
  margin: 0; color: #1c2a3a; background: #fff;
  font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
  font-size: 9.5pt; line-height: 1.34;
}
h1 {
  font-size: 16pt; color: #123a63; margin: 0 0 8px;
  padding-bottom: 4px; border-bottom: 2px solid #123a63;
  page-break-after: avoid;
}
h2 { font-size: 11.8pt; color: #1f5c94; margin: 11px 0 4px; page-break-after: avoid; }
h3 { font-size: 10.2pt; color: #123a63; margin: 8px 0 3px; page-break-after: avoid; }
p { margin: 3px 0 5px; text-align: justify; }
ul, ol { margin: 3px 0 6px 18px; padding: 0; }
li { margin: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 5px 0 9px; font-size: 7.9pt; page-break-inside: avoid; }
th { background: #123a63; color: #fff; text-align: left; padding: 3px 4px; font-weight: 600; }
td { border-bottom: 1px solid #dbe3ee; padding: 2.5px 4px; vertical-align: top; }
tr:nth-child(even) td { background: #f7f9fc; }
code { font-family: Menlo, Consolas, monospace; font-size: 8pt; background: #f1f4f8; padding: 1px 2px; border-radius: 2px; }
pre { background: #f6f8fb; border-left: 3px solid #1f5c94; padding: 6px 8px; margin: 5px 0 9px; page-break-inside: avoid; }
pre code { background: transparent; padding: 0; font-size: 7.3pt; line-height: 1.22; }
blockquote { border-left: 3px solid #62a7d9; margin: 6px 0; padding: 3px 9px; color: #40506a; background: #f6fafd; }
img { max-width: 100%; height: auto; display: block; margin: 8px auto 4px; page-break-inside: avoid; }
em { color: #40506a; }
a { color: #1f5c94; text-decoration: none; }
.pagebreak { page-break-before: always; height: 0; }
.cover { height: 252mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }
.cover .brand { color: #1f5c94; font-size: 10pt; letter-spacing: .16em; text-transform: uppercase; margin-bottom: 18px; }
.cover h1 { font-size: 31pt; line-height: 1.08; border: none; margin: 0 0 10px; color: #123a63; }
.cover .subtitle { font-size: 15pt; color: #1f5c94; margin-bottom: 34px; }
.cover .meta { font-size: 10pt; line-height: 1.7; color: #33445c; }
.cover .meta strong { color: #123a63; }
.cover .repo { margin-top: 26px; padding: 14px 16px; background: #eef4fa; border-left: 4px solid #1f5c94; font-size: 9.2pt; line-height: 1.6; }
.cover .repo code { font-size: 8.4pt; }
.cover .nota { margin-top: 26px; color: #75859b; font-size: 8pt; }
.toc { columns: 2; column-gap: 24px; font-size: 9pt; }
"""


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def recorte(texto: str, inicio: str, fin: str | None = None) -> str:
    i = texto.index(inicio)
    j = texto.index(fin, i) if fin else len(texto)
    return texto[i:j].strip()


def componer() -> str:
    respuestas = leer(RAIZ / "parte-7-parte-a-teoria" / "respuestas.md")
    a = recorte(respuestas, "## A1.")
    informe = leer(DOCS / "informe.md")
    b1 = recorte(informe, "## 2.", "## 3.")
    b6 = recorte(informe, "## 7.", "## 8.")
    ai = recorte(informe, "## 8.")
    b1 = b1.replace("## 2.", "# 2.", 1)
    b6 = b6.replace("## 7.", "# 7.", 1)
    ai = ai.replace("## 8.", "# 8.", 1)

    portada = f"""
<div class="cover">
  <div class="brand">PagaRed S.A.S. · Grupo Réditos</div>
  <h1>Informe consolidado</h1>
  <div class="subtitle">Prueba Técnica — Desarrollador de Arquitectura de Software</div>
  <div class="meta">
    <strong>Candidato:</strong> Jhon E.<br>
    <strong>Fecha de corte:</strong> 27 de octubre de 2026<br>
    <strong>Entrega:</strong> 14 de noviembre de 2026<br>
    <strong>Rol:</strong> Desarrollador de Arquitectura de Software
  </div>
  <div class="repo">
    <strong>Repositorio</strong><br>
    <code>{REPO}</code><br><br>
    <strong>Clonar</strong><br>
    <code>git clone {REPO}</code>
  </div>
  <div class="nota">Documento confidencial · uso exclusivo del proceso de selección</div>
</div>
"""

    indice = """
## Contenido

<div class="toc">

1. Componente teórico (Parte A)
2. Análisis del requerimiento (B1)
3. Pipeline de datos (B2)
4. Consultas SQL (B3)
5. Revisión de código (B4)
6. Operación y despliegue (B5)
7. Power BI (B6)
8. Uso de IA
Anexo A. Repositorio, ejecución y evidencia

</div>
"""

    partes = [
        portada,
        leer(SECCIONES / "conclusion.md"),
        leer(SECCIONES / "ficha.md"),
        indice,
        '<div class="pagebreak"></div>',
        "# 1. Componente teórico (Parte A)\n\n" + a,
        '<div class="pagebreak"></div>',
        b1,
        '<div class="pagebreak"></div>',
        leer(SECCIONES / "b2.md"),
        '<div class="pagebreak"></div>',
        leer(SECCIONES / "b3.md"),
        '<div class="pagebreak"></div>',
        leer(SECCIONES / "b4.md"),
        '<div class="pagebreak"></div>',
        leer(SECCIONES / "b5.md"),
        '<div class="pagebreak"></div>',
        b6,
        '<div class="pagebreak"></div>',
        ai,
        '<div class="pagebreak"></div>',
        leer(SECCIONES / "anexos.md"),
    ]
    texto = "\n\n".join(partes)
    SALIDA_MD.write_text(texto, encoding="utf-8")
    return texto


def main() -> int:
    texto = componer()
    html_cuerpo = markdown.markdown(
        texto,
        extensions=["tables", "fenced_code", "sane_lists", "md_in_html"],
    )
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Informe consolidado — Prueba Técnica PagaRed</title>
<style>{CSS}</style>
</head>
<body>
{html_cuerpo}
</body>
</html>
"""
    SALIDA_HTML.write_text(html, encoding="utf-8")

    if not CHROME.exists():
        print(f"No se encontró Chrome en {CHROME}; el HTML quedó generado.")
        return 2

    comando = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--user-data-dir=/tmp/pagared-chrome-informe",
        "--no-pdf-header-footer",
        f"--print-to-pdf={SALIDA_PDF}",
        "--virtual-time-budget=6000",
        f"file://{SALIDA_HTML}",
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(resultado.stderr[-2000:])
        return 1

    lector = PdfReader(str(SALIDA_PDF))
    paginas = len(lector.pages)
    print(f"PDF generado: {SALIDA_PDF} ({paginas} páginas)")
    if paginas > 25:
        print(f"ADVERTENCIA: el informe supera 25 páginas ({paginas})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
