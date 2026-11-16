# Source from Bash: source software/runtime102/lab-env.sh BBB-A
# Defines local commands only; does not acquire resources or energize anything.
case "${1:-}" in BBB-A|BBB-B) export BOARD="$1";; *) echo 'Specify BBB-A or BBB-B'; return 2;; esac
export PHY_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PHY_PROFILE="$HOME/trama3-lab/$BOARD.json"
export PHY_RESULTS="$HOME/trama3-lab/results/$BOARD"
export PHY_NODE="$(command -v node)"
mkdir -p "$PHY_RESULTS"
phy() {
  if [ "$#" -lt 3 ]; then echo 'phy send|receive c0|c1|clock|i2c|pair|frame RUN_ID [options]'; return 2; fi
  local action="$1" kind="$2" run="$3"; shift 3
  sudo "$PHY_NODE" "$PHY_ROOT/phy-cli.cjs" "$action" --kind "$kind" --run "$run" \
    --profile "$PHY_PROFILE" --directory "$PHY_RESULTS/$run" "$@"
}
phycheck() { "$PHY_NODE" "$PHY_ROOT/phy-cli.cjs" check --profile "$PHY_PROFILE" --kind "${1:-clock}"; }
