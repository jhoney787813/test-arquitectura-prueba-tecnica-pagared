#!/bin/sh
set -eu

case "${1:-demo}" in
  demo)
    exec sh /app/parte-5-b5-operacion/infra/demo.sh
    ;;
  test)
    exec python -m pytest -q
    ;;
  etl)
    shift
    exec python -m etl "$@"
    ;;
  consultas)
    shift
    exec python -m etl.consultas "$@"
    ;;
  *)
    exec python -m etl "$@"
    ;;
esac
