#!/bin/bash
# Separar bloques que exigen distinto cableado; nunca reconectar energizado.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
board=${1:-}; block=${2:-preparacion}
shift "$(( $# >= 2 ? 2 : $# ))"
case "$board" in BBB-A|BBB-B) ;; *) echo "Uso: bash ejecutar-bloque.sh BBB-A|BBB-B preparacion|compilar|pwm|pru|loopback|captura-pwm|alimentacion [opciones]"; exit 2;; esac
case "$block" in
 preparacion)
  python3 t08/inspeccion.py --board "$board" "$@"
  python3 t06/run.py preflight --board "$board" "$@"
  ;;
 compilar) python3 t06/build-report.py --board "$board" "$@" ;;
 pwm)
  for width in 1000 1500 2000; do
   python3 t06/run.py pwm --board "$board" --high-us "$width" "$@"
  done
  ;;
 pru) python3 t06/run.py pru-smoke --board "$board" "$@" ;;
 loopback) python3 t06/run.py loopback --board "$board" "$@" ;;
 captura-pwm)
  for width in 1000 1500 2000; do
   python3 t06/run.py pwm-capture --board "$board" --high-us "$width" "$@"
  done
  ;;
 alimentacion) python3 t08/inspeccion.py --board "$board" "$@" ;;
 *) echo "Bloque desconocido"; exit 2 ;;
esac
