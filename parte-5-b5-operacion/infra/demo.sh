#!/bin/sh
set -eu

FECHA="${FECHA:-2026-10-27}"
FECHA_COMPACTA=$(echo "$FECHA" | tr -d "-")
DB="/app/db/pagared.db"
DELTA="/app/datos/transacciones_delta_20261028.csv"
REPORTE="/app/salida/despues/reporte_ventas_${FECHA_COMPACTA}.xlsx"

cd /app
rm -f "$DB"
rm -rf /app/salida/antes /app/salida/despues /app/salida/powerbi
rm -f /app/salida/envio.eml /app/salida/envios.json /app/salida/envios_smtp.json /app/salida/smtp.log
mkdir -p /app/db /app/salida/antes /app/salida/despues

echo "== 0. Pruebas y lint =="
python -m pytest -q -p no:cacheprovider
python -m ruff check --no-cache .

echo
echo "== 1. Carga base (antes del delta) =="
python -m etl --fecha-corte "$FECHA" --db "$DB" --salida /app/salida/antes

echo
echo "== 2. Carga incremental (después del delta) =="
python -m etl --fecha-corte "$FECHA" --delta "$DELTA" --db "$DB" --salida /app/salida/despues

echo
echo "== 3. Consultas B3 =="
python -m etl.consultas --db "$DB" --fecha "$FECHA" --salida /app/salida/consultas_${FECHA_COMPACTA}.txt

echo
echo "== 4. Exportación para Power BI =="
python /app/parte-6-b6-powerbi/scripts/exportar_datos.py --db "$DB" --destino /app/salida/powerbi
python /app/parte-6-b6-powerbi/scripts/generar_tablero.py \
  --db "$DB" \
  --salida /app/salida/powerbi/tablero_ventas.html \
  --fecha "$FECHA"

echo
echo "== 5. Envío B4 idempotente (SMTP local de prueba) =="
cp "$REPORTE" /app/salida/reporte_ventas_${FECHA_COMPACTA}.xlsx
cp "/app/salida/despues/reporte_ventas_${FECHA_COMPACTA}.eml" /app/salida/reporte_ventas_${FECHA_COMPACTA}.eml
python -m smtpd -n -c DebuggingServer 127.0.0.1:1025 > /app/salida/smtp.log 2>&1 &
SMTP_PID=$!
trap 'kill "$SMTP_PID" 2>/dev/null || true' EXIT INT TERM
sleep 1

python /app/parte-4-b4-revision/revision/enviar_reporte_v2.py \
  --reporte "$REPORTE" \
  --destinatarios laura.restrepo@pagared.com \
  --modo smtp \
  --smtp-host 127.0.0.1 \
  --smtp-port 1025 \
  --sin-tls \
  --ledger /app/salida/envios_smtp.json
python /app/parte-4-b4-revision/revision/enviar_reporte_v2.py \
  --reporte "$REPORTE" \
  --destinatarios laura.restrepo@pagared.com \
  --modo smtp \
  --smtp-host 127.0.0.1 \
  --smtp-port 1025 \
  --sin-tls \
  --ledger /app/salida/envios_smtp.json

kill "$SMTP_PID" 2>/dev/null || true
wait "$SMTP_PID" 2>/dev/null || true
trap - EXIT INT TERM
echo "Servidor SMTP local recibió:"
grep -m1 "Subject:" /app/salida/smtp.log || true

echo
echo "== 6. Artefactos generados =="
find /app/salida -maxdepth 3 -type f | sort
