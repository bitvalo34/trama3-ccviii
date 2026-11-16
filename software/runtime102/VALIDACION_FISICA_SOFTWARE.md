# Validación de la integración física C0/C1

**Resultado de software PC: PASS. Hardware nuevo: NOT_TESTED. Compilación TI PRU: BLOCKED por toolchain ausente. Compilación ARM: NOT_TESTED.**

La validación se ejecutó en Linux x86_64 (WSL Ubuntu), con Node 16.20.2 y Node 22.22.0, Python 3.12 y GCC del host. No se ejecutaron estas suites en Debian 9/10 ARM ni en una BeagleBone. Los perfiles de entrega permanecen PENDING, sin valores eléctricos o calibraciones inventados.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Matrices: 10252 comprobaciones matemáticas, 2264 de integración, 209 escenarios de sesión | PASS en Node16/22 | [node16.txt](validation-physical/node16.txt), [node22.txt](validation-physical/node22.txt) |
| Runtime original: 24 casos de protocolo, cuatro CRC, ACK perdido, NACK contextual, cuatro intentos, secuencia, epoch y tiempo | PASS | Mismos logs |
| Banco PR11 y preparación: ciclo TX/RX/timeout/limpieza, 30 comprobaciones de patrones, ventana y evidencia | PASS | Mismos logs |
| Nuevo camino físico mediante fixtures: C2 ausente aunque imite pilotos, distancia 4, corrección simple, cuatro CRC, polaridades, cuatro parejas, trama completa, ACK real en la interfaz de captura y guarda | PASS; datos sintéticos | `test-phy.cjs`, logs Node |
| Propietario/P2/preflight/calibración: 24 pruebas Python | PASS | Reinicio MCP, escritura fallida/ignorada, sin PWM, informes por receptor/ventana y preservación del original |
| Host C ABI4 | Compila con GCC x86, C99, `-Wall -Wextra -Werror` | Scripts y logs Node; no es binario ARM |
| Servicio PRU ejecutado como modelo C x86 | PASS | 90 s RX, wraps IEP, STOP, READY ausente, TX 87/3 ticks, guarda inicial/final, pulsos acústicos con muestra final LOW, overflow, hueco de polling y heartbeat |
| Recursos T06/T08 y netlist P2 | PASS; incluye 70 pruebas Python y modelo C diagnóstico | [p2-results.json](validation-physical/p2-results.json) |
| Compilación TI de firmware | BLOCKED: no se encontró un compilador TI único ni disponible | [ti-build.txt](validation-physical/ti-build.txt); salida 4 |
| Binario Node ARMv7 16.20.2 | Descargado y hash verificado contra publicación oficial; ejecución ARM pendiente | `prepare-offline.py`, NODE_SHASUMS256.txt del paquete |
| Primera señal/reloj/pareja/trama/ACK en BBB | NOT_TESTED | No se proporcionó una sesión de placas accesible; no hay nuevas capturas físicas |

Informe legible por máquina: [pc-results.json](validation-physical/pc-results.json). Las pruebas web existentes en Node16 necesitan `--experimental-fetch`, activado solo por el script de regresión; la CLI física no abre una red ni necesita ese indicador. Se conserva el código original de las pruebas web para comprobar regresiones; no se desarrolla otra interfaz web.

## Límites que deben resolverse en laboratorio

- Compilar ambos componentes ABI4 en las placas, revisar mapa TI/orden de publicación en ensamblador y validar sus hashes. Un build x86 no resuelve esto.
- Confirmar niveles/retornos P2 y polaridades por placa. El éxito previo del LED A no valida buzzer, entradas, B ni relojes.
- Medir ventana/umbral acústico con los módulos reales. La plantilla de observación no concede una decisión acústica para tramas.
- Confirmar que Node/Python/I²C cumplen 15 ms de preparación y PRU su polling/muestreo. Los timeouts abortan en lugar de inventar READY.
- Registrar 87 ticks reales completos, CRC y después retorno ACK. Dos medios conservan recuperación matemática; no cierran el requisito de tres medios.
- `recover-physical.py` conserva las comprobaciones de propiedad/boot/estado y no mata procesos; su uso con una transacción abandonada real sigue sin probar en hardware.

## Revisión de retransmisión anticipada

Se verificó el documento revisión 102 y `Endpoint.take`, `txDone`, `reject`, `PhysicalReceiver.ingest` y `service.c`. Hay rechazo por bloque antes del CRC final y NACK contextual. **No hay cancelación de TX ni reenvío de un bloque/trama antes de completar la emisión activa.** La integración conserva ese comportamiento. Las guardas y la identidad SID/SEQ se mantienen; la matriz no es un mecanismo de retransmisión parcial.
