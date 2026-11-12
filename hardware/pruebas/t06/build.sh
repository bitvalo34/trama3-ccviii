#!/bin/bash
# Compila sin cargar firmware ni cambiar pinmux. Sin Internet.
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p build
exec > >(tee build/build.log) 2>&1
cc="${CLPRU:-}"
if [ -z "$cc" ]; then
 cc=$(command -v clpru || true)
fi
if [ -z "$cc" ]; then
 mapfile -t choices < <(find /usr/share/ti /usr/lib/ti /opt -maxdepth 6 -type f -name clpru 2>/dev/null || true)
 [ "${#choices[@]}" = 1 ] || { echo "BLOCKED: especificar CLPRU=/ruta/real/bin/clpru"; exit 4; }
 cc=${choices[0]}
fi
cc=$(readlink -f -- "$cc")
root=$(cd -- "$(dirname -- "$cc")/.." && pwd)
[ -x "$cc" ] && [ -x "$root/bin/lnkpru" ] && [ -f "$root/include/stdint.h" ] || { echo "BLOCKED: toolchain TI incompleto"; exit 4; }
[ -f "$root/lib/libc.a" ] || { echo "BLOCKED: falta runtime TI libc.a"; exit 4; }
"$cc" --compiler_revision
command -v gcc
gcc --version | head -n 1
gcc -std=c99 -O2 -Wall -Wextra -Werror src/host.c -o build/trama3-t06-host
"$cc" --silicon_version=3 --hardware_mac=on --endian=little --opt_level=2 --include_path="$root/include" --include_path=firmware --obj_directory=build --compile_only firmware/main.c
"$cc" --silicon_version=3 --run_linker --output_file=build/trama3-t06-pru0.out --map_file=build/trama3-t06-pru0.map firmware/AM335x_PRU0.cmd build/main.obj --search_path="$root/lib" --library=libc.a
test -s build/trama3-t06-pru0.out
sha256sum build/trama3-t06-pru0.out build/trama3-t06-host > build/SHA256SUMS
echo "BUILD_OK: no equivale a prueba fisica. Revisar mapa: IRAM <=8192 bytes."
