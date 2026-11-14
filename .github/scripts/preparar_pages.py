"""Copia el tablero como index y agrega el enlace al informe PDF."""

from pathlib import Path

pagina = Path("site/index.html")
html = pagina.read_text(encoding="utf-8")
boton = (
    '<a class="badge" style="text-decoration:none;color:#fff" '
    'href="INFORME_Jhon_E.pdf">Informe PDF</a>'
)
reemplazo = (
    '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
    + boton
    + '<div class="badge">Prototipo funcional · .pbix pendiente (Windows)</div></div>'
)
original = '<div class="badge">Prototipo funcional · .pbix pendiente (Windows)</div>'
if original not in html:
    raise SystemExit("No se encontró el badge esperado en el tablero")
pagina.write_text(html.replace(original, reemplazo), encoding="utf-8")
print("Sitio preparado con el enlace al informe")
