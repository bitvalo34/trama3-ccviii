# T06: PWM hardware y PRU0

Entrada operativa: [guía para ambas placas](../../documentacion/Guia_Completa_T06_T08.md).
Python 3.5+ y biblioteca estándar, Bash, gcc nativo, TI clpru/lnkpru con su runtime,
config-pin, sysfs PWM/remoteproc y debugfs. No se instalan paquetes ni se cambia boot.

```bash
python3 hardware/pruebas/t06/run.py preflight --board BBB-A
python3 hardware/pruebas/t06/build-report.py --board BBB-A
```

Sin `--active`, cualquier ensayo hace sólo auditoría. Para B usar `--board BBB-B`.
Los ensayos activos requieren sudo, checklist y fixture; no ejecutar antes de leer
la guía. Los wrappers .sh son equivalentes a las acciones de `run.py`.

| Archivo | Responsabilidad |
|---|---|
| firmware/main.c | Generación finita, captura de flancos, instantáneas R31, parada |
| firmware/abi.h | ABI ARM/PRU; buzón acotado y 1024 eventos |
| firmware/AM335x_PRU0.cmd | Memorias/enlazado PRU0, inicio C y resource table |
| src/host.c | Acceso exclusivo a SRAM compartida, barreras, timeout y salida JSON |
| resources.py | Detección por direcciones, propiedad, diario previo a cambios y restauración |
| analyze.py | Conteos, alto/bajo/período/frecuencia, muestras inválidas y tolerancia |
| toolchain.py | Inventario de compilador/runtime/interfaces; no instala |
| run.py | Argumentos, exclusividad, señales y resultados por placa/fecha |

## Contrato técnico

PRU0 usa R30.15 (P8_11), R31.15 (P8_15) y máscara común de bits 5/14/16
para P9_27/P8_16/P9_24. El nombre C0/C1/C2 del informe de instantáneas es el
orden de bits 5/14/16; **no es decodificación ni asignación matricial del protocolo**.
Usar tabla de pines al interpretarlo. El contador IEP nominal es 200 MHz;
resolución de 5 ns no significa esa precisión de detección por sondeo.

SRAM compartida PRU=0x10000, ARM=0x4a310000, ventana=12 KiB. ABI magic y versión
se verifican antes del comando. Estados READY/RUNNING/DONE/ERROR/STOPPED;
comandos TX/RX/LOOP/SNAPSHOT/STOP. Una muestra lee R31 una vez. Los resultados
se publican antes del estado final. Duración máxima 10 s, menor a media vuelta
del contador; se detecta overflow, retraso >10 µs y separación de muestras >10 µs.

Cada invocación carga firmware propio con nombre derivado del hash, preserva selector
anterior y sólo detiene lo adquirido. Ambos PRU offline y sin PTP son prerrequisitos
conservadores para usar IEP. /dev/mem inaccesible produce BLOCKED; no se relajan
permisos del kernel. El bloqueo coopera entre ejecuciones del paquete: no impide
que otro administrador modifique los mismos recursos. No ejecutar otros drivers
o herramientas de pinmux simultáneamente. Un cambio de propietario retiene el diario
y exige revisión antes de recuperación.

PWM se identifica por eHRPWM1 48302200, canal A/0; no por número pwmchip.
También se descarta uso del canal B porque comparte período. Lectura sysfs confirma
configuración, no señal. `pwm-capture` observa la señal por P8_15 dentro de la misma BBB;
comparte referencia de reloj, por lo que no sustituye calibración independiente.

Al terminar, duty cero, disable, desacoplar salida PRU, parar firmware propio,
restaurar pinmux/selector y unexport propio. No se promete nivel eléctrico de un PWM
deshabilitado. SIGINT/TERM/HUP invocan limpieza; SIGKILL y pérdida de alimentación
no permiten ejecutar finally. El diario ayuda a recuperar, no es un watchdog físico.

## Compilar y comprobar sin hardware

Desde la raíz del repositorio, Linux con gcc y Python:

```bash
python3 tests/hardware/test_hardware.py
gcc -std=c99 -O2 -Wall -Wextra -Werror hardware/pruebas/t06/src/host.c -o /tmp/trama3-host-check
gcc -std=c99 -O2 -Wall -Wextra -Wno-unknown-pragmas -Itests/hardware tests/hardware/test_firmware.c -o /tmp/trama3-firmware-model
/tmp/trama3-firmware-model
```

El modelo incluye el mismo main.c con registros simulados; no es un binario PRU
ni evidencia física. La compilación definitiva usa `build-report.py` en cada BBB,
que guarda versión, salida, código y resultado; `build.sh` no carga firmware.

Fuentes: [PRU cookbook](https://docs.beagleboard.org/books/pru-cookbook/03details/details.html),
[registros IEP TI](https://git.ti.com/cgit/pru-software-support-package/pru-software-support-package/plain/include/am335x/pru_iep.h),
[registros CFG TI](https://git.ti.com/cgit/pru-software-support-package/pru-software-support-package/plain/include/am335x/pru_cfg.h).
