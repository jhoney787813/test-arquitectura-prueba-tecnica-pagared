#!/bin/sh
set -eu

FECHA="${FECHA:-2026-10-27}"
FECHA_COMPACTA=$(echo "$FECHA" | tr -d "-")
DB="/app/db/pagared.db"
DELTA="/app/datos/transacciones_delta_20261028.csv"

cd /app
rm -f "$DB"
rm -rf /app/salida/antes /app/salida/despues /app/salida/powerbi /app/salida/envio.eml /app/salida/envios.json
mkdir -p /app/db /app/salida/antes /app/salida/despues

echo "== 1. Carga base (antes del delta) =="
python -m etl --fecha-corte "$FECHA" --db "$DB" --salida /app/salida/antes

echo
echo "== 2. Carga incremental (después del delta) =="
python -m etl --fecha-corte "$FECHA" --delta "$DELTA" --db "$DB" --salida /app/salida/despues

echo
echo "== 3. Consultas B3 =="
python -m etl.consultas --db "$DB" --fecha "$FECHA" --salida /app/salida/consultas_20261027.txt

echo
echo "== 4. Exportación para Power BI =="
python /app/parte-6-b6-powerbi/scripts/exportar_datos.py --db "$DB" --destino /app/salida/powerbi

echo
echo "== 5. Envío B4 idempotente =="
REPORTE="/app/salida/despues/reporte_ventas_${FECHA_COMPACTA}.xlsx"
cp "$REPORTE" /app/salida/reporte_ventas_${FECHA_COMPACTA}.xlsx
cp "/app/salida/despues/reporte_ventas_${FECHA_COMPACTA}.eml" /app/salida/reporte_ventas_${FECHA_COMPACTA}.eml
python /app/parte-4-b4-revision/revision/enviar_reporte_v2.py \
  --reporte "$REPORTE" \
  --destinatarios laura.restrepo@pagared.com \
  --modo eml \
  --eml /app/salida/envio.eml \
  --ledger /app/salida/envios.json
python /app/parte-4-b4-revision/revision/enviar_reporte_v2.py \
  --reporte "$REPORTE" \
  --destinatarios laura.restrepo@pagared.com \
  --modo eml \
  --eml /app/salida/envio.eml \
  --ledger /app/salida/envios.json

echo
echo "== 6. Artefactos generados =="
find /app/salida -maxdepth 3 -type f | sort
