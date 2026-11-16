#!/bin/bash
# Build only. No pinmux, firmware loading, network or privileged operations.
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p build
cc="${CLPRU:-$(command -v clpru)}"
paths=$(PYTHONPATH=../../../hardware/pruebas python3 ../../../hardware/pruebas/t06/toolchain.py "$cc") || exit 4
mapfile -t layout <<< "$paths"
[ "${#layout[@]}" -eq 2 ] || { echo 'Toolchain unavailable'; exit 4; }
cc=${layout[0]}; root=${layout[1]}
gcc -std=c99 -O2 -Wall -Wextra -Werror host.c -o build/runtime102-host
"$cc" --silicon_version=3 --hardware_mac=on --endian=little --opt_level=2 --include_path="$root/include" --include_path=. --obj_directory=build --compile_only firmware.c
"$cc" --silicon_version=3 --run_linker --output_file=build/runtime102-pru0.out --map_file=build/runtime102-pru0.map ../../../hardware/pruebas/t06/firmware/AM335x_PRU0.cmd build/firmware.obj --search_path="$root/lib" --library=libc.a
sha256sum build/runtime102-host build/runtime102-pru0.out > build/SHA256SUMS
echo 'Build finished; review map/assembly. No hardware test performed.'
