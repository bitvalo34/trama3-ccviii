#!/bin/bash
# Separar bloques que exigen distinto cableado; nunca reconectar energizado.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
board=${1:-}; block=${2:-preparacion}
shift "$(( $# >= 2 ? 2 : $# ))"
case "$board" in BBB-A|BBB-B) ;; t08-fuentes|t08-interfaz-p2|t08-gpio)
  echo "Formulario manual P2; no energiza. Registrar puntos de la etapa segun guia."
  python3 t08/registrar-mediciones.py --board "$board" "$@" ;;
 report) python3 evaluar.py "$@" ;;
 *) echo "Uso: bash ejecutar-bloque.sh BBB-A|BBB-B preparacion|compilar|pwm|pru|loopback|captura-pwm|alimentacion [opciones]"; exit 2;; esac
case "$block" in
 preflight|preparacion)
  python3 t08/inspeccion.py --board "$board" "$@"
  python3 t06/run.py preflight --board "$board" "$@"
  ;;
 build|compilar) python3 t06/build-report.py --board "$board" "$@" ;;
 pwm)
  for width in 1000 1500 2000; do
   python3 t06/run.py pwm --board "$board" --high-us "$width" "$@"
  done
  ;;
 pru-smoke|pru) python3 t06/run.py pru-smoke --board "$board" "$@" ;;
 loopback) python3 t06/run.py loopback --board "$board" "$@" ;;
 pwm-capture|captura-pwm)
  for width in 1000 1500 2000; do
   python3 t06/run.py pwm-capture --board "$board" --high-us "$width" "$@"
  done
  ;;
 pru-tx|pru-rx|inputs|cleanup) python3 t06/run.py "$block" --board "$board" "$@" ;;
 t08-bbb|alimentacion) python3 t08/inspeccion.py --board "$board" "$@" ;;
 t08-fuentes|t08-interfaz-p2|t08-gpio)
  echo "Formulario manual P2; no energiza. Registrar puntos de la etapa segun guia."
  python3 t08/registrar-mediciones.py --board "$board" "$@" ;;
 report) python3 evaluar.py "$@" ;;
 *) echo "Bloque desconocido"; exit 2 ;;
esac
