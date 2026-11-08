#!/bin/bash
# T04: auditar, probar pinmux temporalmente y restaurar. Sin firmware.
set -u
export LC_ALL=C
umask 077
board=${1:-}
action=${2:-audit}
case "$board" in A|B) ;; *) echo 'Uso: bash t04-bbb.sh A|B audit|pin-test|clean-cache|headless'; exit 2;; esac
case "$action" in audit|pin-test|clean-cache|headless) ;; *) exit 2;; esac
model=$(tr -d '\000' </proc/device-tree/model 2>/dev/null || true)
case "$model" in *"AM335"*"BeagleBone Black"*) ;; *) echo "STOP: modelo no admitido: $model"; exit 2;; esac
run_dir=$(mktemp -d "${HOME}/T04-${board}-${action}-XXXXXX") || exit 2
exec > >(tee "$run_dir/resultado.txt") 2>&1
echo "PLACA declarada=$board ACCION=$action FECHA_BBB=$(date -Iseconds)"
echo "La fecha de la placa puede estar desajustada; anotar fecha real del PC."
echo "RESULTADOS=$run_dir"
run() { printf '\n---'; printf ' %q' "$@"; printf '\n'; timeout 35 "$@"; rc=$?; echo "SALIDA=$rc"; return 0; }
priv() { if [ "$(id -u)" = 0 ]; then run "$@"; else run sudo -n "$@"; fi; }
needroot() { if [ "$(id -u)" != 0 ] && ! sudo -n true 2>/dev/null; then echo 'STOP: ejecutar sudo -v en terminal y repetir; no se aplico cambio'; exit 3; fi; }
pins=(P8_11 P8_15 P8_16 P9_24 P9_27)
modes=(pruout pruin pruin pruin pruin)
statepath() {
 local p=$1
 find /sys/devices/platform -maxdepth 5 -path "*/ocp:${p}_pinmux/state" -print 2>/dev/null | head -n 1
}
pinctrl() {
 priv bash -c '
 seen=0
 for f in /sys/kernel/debug/pinctrl/*/pins /sys/kernel/debug/pinctrl/*/pinmux-pins; do
  [ -f "$f" ] || continue
  seen=1
  echo "PINCTRL=$f"
  grep -E "pin (13|14|15|18|94|95|97|105) |P8_11|P8_15|P8_16|P9_24|P9_27|P9_14|P9_19|P9_20" "$f" || true
 done
 [ "$seen" = 1 ] || echo "PINCTRL_PENDIENTE: debugfs no accesible o sin controlador"
 '
}

if [ "$action" = audit ]; then
 run cat /etc/os-release
 run uname -r
 run uname -m
 echo "MODELO=$model"
 run free -h
 run df -h /
 run lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
 run findmnt -no SOURCE,FSTYPE,OPTIONS /
 for f in /sys/class/block/mmcblk*/device/type; do [ -f "$f" ] && run cat "$f"; done
 run systemctl --failed --no-pager
 for service in ssh connman lightdm robotcontrol; do run systemctl is-active "$service"; run systemctl is-enabled "$service"; done
 priv journalctl -b -u lightdm --no-pager -n 12 -o cat
 # No volcar cmdline completa, hostname, serial EEPROM, claves, MAC o IP publicas.
 priv grep -E '^(uname_r|enable_uboot|uboot_overlay|disable_uboot)' /boot/uEnv.txt
 run ls -l /etc/resolv.conf
 run test -s /etc/resolv.conf
 run timeout 8 getent hosts deb.debian.org
 run sh -c "ip -br link | sed -E 's/([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}/[MAC omitida]/g'"
 run sh -c "ip -4 -o addr show | grep -E 'usb[01]|192\.168\.[67]\.' | sed -E 's/ valid_lft.*//'"
 run sh -c "ip route | grep -E '192\.168\.[67]\.|default' | sed -E 's/(via|src) [0-9.]+/\1 [IP omitida]/g'"
 run sh -c "ss -ltn | grep -E 'State|:22[[:space:]]'"
 for tool in python3 git ssh gcc g++ make config-pin dtc clpru lnkpru pru-gcc; do echo "HERRAMIENTA=$tool"; command -v "$tool" || true; done
 run python3 --version
 run gcc -dumpversion
 run git --version
 run sh -c "find /usr/share/ti /opt /usr/bin -maxdepth 5 -type f -name clpru -print 2>/dev/null"
 run sh -c "ls /lib/firmware/*pru* /lib/firmware/*PRU* 2>/dev/null"
 for r in /sys/class/remoteproc/remoteproc*; do
  [ -d "$r" ] || continue
  echo "REMOTEPROC=$r"
  run readlink -f "$r"
  run readlink -f "$r/device"
  for field in name state firmware; do [ -f "$r/$field" ] && run cat "$r/$field"; done
  run readlink -f "$r/device/driver"
 done
 run sh -c "lsmod | grep -E 'pru|pruss|remoteproc|rpmsg|pwm|i2c'"
 run sh -c "ls -d /dev/i2c-* /sys/class/pwm/pwmchip* /sys/class/gpio/gpiochip* 2>/dev/null"
 for r in /sys/class/pwm/pwmchip* /sys/class/i2c-adapter/i2c-*; do
  [ -d "$r" ] || continue
  run readlink -f "$r/device"
 done
 for p in "${pins[@]}" P9_14 P9_19 P9_20; do
  echo "PIN=$p"
  run config-pin -i "$p"
  run config-pin -l "$p"
  run config-pin -q "$p"
  f=$(statepath "$p"); [ -n "$f" ] && run cat "$f"
 done
 pinctrl
 priv sh -c "dmesg | grep -Ei 'pruss|remoteproc|pinmux|pinctrl|I/O error|EXT4-fs error' | tail -n 40"
 priv du -xhd1 /var /opt /usr /home
 priv du -sh /var/cache/apt/archives
 run journalctl --disk-usage
 if command -v dtc >/dev/null; then
  priv dtc -I fs -O dts -o "$run_dir/device-tree-local.dts" /proc/device-tree
  echo 'Device Tree completo SOLO LOCAL; revisar antes de compartir.'
 fi
 echo 'AUDITORIA_TERMINADA: salidas no cero indican comprobaciones pendientes, no aprobacion.'
elif [ "$action" = clean-cache ]; then
 needroot
 priv du -sh /var/cache/apt/archives
 run df -h /
 sudo -n apt-get clean || { echo "ERROR: limpieza no completada"; exit 5; }
 run df -h /
 echo 'Solo cache de paquetes descargados; no se desinstalaron programas.'
elif [ "$action" = headless ]; then
 needroot
 prior=$(systemctl is-enabled lightdm 2>/dev/null || true)
 printf '%s\n' "$prior" >"$run_dir/lightdm-enabled-antes.txt"
 run systemctl is-active lightdm
 if [ "$(systemctl is-failed lightdm 2>/dev/null || true)" != failed ]; then
  echo 'STOP: LightDM no esta fallando; no cambiar servicio.'; exit 4
 fi
 sudo -n systemctl disable --now lightdm || { echo "ERROR: no se deshabilito LightDM"; exit 5; }
 run systemctl is-enabled lightdm
 echo 'Se deshabilito el escritorio fallido, no SSH ni consola. No libera paquetes.'
 echo "Reversion: si antes era enabled, sudo systemctl enable lightdm; sudo systemctl start lightdm."
else
 needroot
 [ "${T04_SIN_CARGAS:-}" = SI ] || { echo 'STOP: requiere T04_SIN_CARGAS=SI y P8/P9 sin nada conectado'; exit 4; }
 command -v config-pin >/dev/null || { echo 'STOP: falta config-pin'; exit 4; }
 # Identificar ambos PRU por direccion, nunca por numero remoto fijo.
 seen0=0; seen1=0
 for r in /sys/class/remoteproc/remoteproc*; do
  [ -d "$r" ] || continue
  ident="$(readlink -f "$r") $(readlink -f "$r/device") $(cat "$r/name" 2>/dev/null || true)"
  case "$ident" in
   *4a334000*|*4a338000*)
    [ "$(cat "$r/state" 2>/dev/null)" = offline ] || { echo "STOP: PRU no detenido $r"; exit 4; }
    case "$ident" in *4a334000*) seen0=1;; esac
    case "$ident" in *4a338000*) seen1=1;; esac ;;
  esac
 done
 [ "$seen0$seen1" = 11 ] || { echo 'STOP: identidad de ambos PRU sin verificar'; exit 4; }
 declare -a paths old
 for i in "${!pins[@]}"; do
  p=${pins[$i]}; paths[$i]=$(statepath "$p")
  [ -n "${paths[$i]}" ] || { echo "STOP: falta estado sysfs de $p"; exit 4; }
  old[$i]=$(cat "${paths[$i]}") || exit 4
  case "${old[$i]}" in gpio|gpio_pu|gpio_pd|gpio_input|default|pruin|pruout) ;;
   *) echo "STOP: $p ocupado en ${old[$i]}; no cambiar UART/perifericos"; exit 4;; esac
  config-pin -l "$p" | tr ' ' '\n' | grep -qx "${modes[$i]}" || { echo "STOP: modo no publicado en $p"; exit 4; }
  printf '%s\t%s\t%s\n' "$p" "${old[$i]}" "${paths[$i]}" >>"$run_dir/estados-antes.tsv"
 done
 pinctrl
 changed=0
 restore() {
  local j bad=0
  trap - EXIT INT TERM HUP
  for ((j=changed-1;j>=0;j--)); do
   if sudo -n config-pin "${pins[$j]}" "${old[$j]}" && [ "$(cat "${paths[$j]}")" = "${old[$j]}" ]; then
    echo "RESTAURADO ${pins[$j]} ${old[$j]}"
   else echo "ERROR_RESTAURACION ${pins[$j]} revisar estados-antes.tsv"; bad=1; fi
  done
  [ "$bad" = 0 ] || echo 'STOP: no conectar cargas ni continuar T06.'
 }
 trap restore EXIT
 trap 'exit 130' INT
 trap 'exit 143' TERM HUP
 for i in "${!pins[@]}"; do
  changed=$((i+1))
  if ! sudo -n config-pin "${pins[$i]}" "${modes[$i]}"; then echo "CONFLICTO ${pins[$i]}"; exit 5; fi
  run config-pin -q "${pins[$i]}"
  [ "$(cat "${paths[$i]}")" = "${modes[$i]}" ] || { echo "CONFLICTO lectura ${pins[$i]}"; exit 5; }
  echo "MODO_SELECCIONADO ${pins[$i]} ${modes[$i]}"
 done
 pinctrl
 echo 'CINCO_MODOS_SELECCIONADOS: revisar registros/propietarios; NO prueba de firmware ni niveles.'
 echo 'Se restauran a continuacion los modos previos. No se instala persistencia.'
fi
echo "FIN_T04 $board $action"
