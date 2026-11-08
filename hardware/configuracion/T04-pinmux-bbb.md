# T04 — Pines de BeagleBone Black

Preparación documental: 08/11/2026. Protocolo 101. **Selección y restauración verificadas en ambas placas: [resultados](T04-resultados.md). No es prueba eléctrica ni de firmware.**

## Correspondencia que debe verificarse en A y B

| Pin | Función futura | AM335x / modo mux | Selección esperada | Comprobar conflicto |
|---|---|---|---|---|
| P8_11 | CLK TX | PRU0 R30 bit 15 / modo 6 | pruout | GPIO1_13, eQEP; salida sin cargas |
| P8_15 | CLK RX | PRU0 R31 bit 15 / modo 6 | pruin | GPIO1_15, eQEP, PRU eCAP |
| P8_16 | Sonido RX | PRU0 R31 bit 14 / modo 6 | pruin | GPIO1_14, eQEP |
| P9_24 | Mecánico RX | PRU0 R31 bit 16 / modo 6 | pruin | UART1 TX, PRU UART, CAN, I2C1 |
| P9_27 | Óptico RX | PRU0 R31 bit 5 / modo 6 | pruin | GPIO3_19, eQEP |
| P9_14 | Servo | eHRPWM1A / modo 6 | pwm, sólo consultar en T04 | GPIO1_18 y PWM ya exportado/activo |
| P9_19 | I2C SCL | I2C2_SCL / modo 3 | controlador I2C2 | I2C activo, no liberar su propietario |
| P9_20 | I2C SDA | I2C2_SDA / modo 3 | controlador I2C2 | I2C activo, no escanear periféricos |

Los nombres son los expuestos por config-pin de BeagleBoard. No se escriben registros a mano. El modo 6 es la función alternativa del multiplexor, no un número de GPIO. R30 corresponde a salida PRU y R31 a entrada; compartir el índice 15 entre TX y RX no significa compartir un conductor.

Los cinco pines propuestos no pertenecen a los pines físicos ocupados por eMMC en la BBB. Que una función alternativa se llame MMC no significa que ese pin esté conectado a la eMMC de esta placa. No deshabilitar eMMC. Tampoco deshabilitar HDMI a ciegas por una advertencia de arranque: comprobar el pad concreto y su dueño. P9_27 no es el pin HDMI de audio P9_25.

## Evidencia por niveles

1. Tabla/documentación: confirma que el silicio dispone de la función.
2. config-pin -l/-i: confirma que la imagen ofrece la selección.
3. config-pin -q y archivo state: confirman el estado seleccionado.
4. debugfs pinctrl: identifica propietario, grupo y registro aplicado.
5. Firmware/medición: prueba transmisión/lectura real. **Fuera de T04**, corresponde a T06.

Un retorno cero de config-pin no sustituye los pasos 3 y 4. Si debugfs no está accesible, marcar corroboración de registro pendiente, no afirmar prueba eléctrica.

Índices de pad en el controlador pinctrl-single de AM335x: P8_11=13, P8_15=15, P8_16=14, P9_24=97, P9_27=105, P9_14=18, P9_19=95, P9_20=94. Direcciones pad: 0x44e10834, 83c, 838, 984, 9a4, 848, 97c y 978 respectivamente (los últimos sufijos comparten base 0x44e10000). En el registro, bits 2:0 seleccionan el modo; entradas PRU requieren RXACTIVE (bit 5). Los pull-ups/down y slew deben conservarse según overlay real, no copiar una palabra hexadecimal genérica.

## Procedimiento y recuperación

[t04-bbb.sh](t04-bbb.sh), modo pin-test, exige BBB AM335x Black, confirmación física de pines sin cargas, ambos PRU identificados por su dirección y detenidos, modo actual reversible y modo requerido publicado. Si detecta UART u otro periférico seleccionado, se detiene **antes de cambiar cualquier pin**. No detiene drivers o PRU desconocidos.

Guarda el estado de los cinco pines antes de escribir, selecciona los cinco modos, consulta el estado y pinctrl, y restaura lo anterior al terminar o ante error/Ctrl+C. Un apagón o SIGKILL no ejecuta la restauración: conservar la placa sin cargas, recuperar acceso y revisar los archivos estados-antes.tsv. No conectar componentes sólo porque el script terminó.

El resultado «CINCO_MODOS_SELECCIONADOS» acredita selección temporal, pendiente de interpretar pinctrl. «RESTAURADO» acredita el retorno de cada estado lógico. No instala servicio de arranque, no modifica uEnv y no carga firmware.

Persistencia: se aplaza deliberadamente hasta T06 para no activar CLK TX al arrancar sin firmware que inicialice R30. Repetir audit tras reiniciar acredita los modos de arranque, no que la selección temporal persistió. La futura inicialización deberá verificar el mux antes de arrancar PRU y abortar si falla.

## Conflictos

| Resultado | Qué hacer en esta tarea |
|---|---|
| Falta config-pin o state | Sólo auditoría. Registrar imagen/DT; no descargar scripts de otra versión para forzar. |
| Modo pruin/pruout ausente | No pasar número de modo ni usar devmem. Guardar -i/-l y árbol de dispositivos. |
| P9_24 en uart o propietario serial | Conservar consola USB ttyGS0; no detener UART desconocida. Revisar overlay/servicio antes de liberar. |
| Pin ya solicitado por otro driver | Guardar propietario. No usar unbind ni deshabilitar eMMC/HDMI globalmente. |
| PRU en running o identidad incierta | No detener ni cargar firmware. Documentar nombre, device y estado. |
| Cambio falla | El script intenta restaurar todos los pines tocados. Revisar los cinco estados; queda bloqueo si no se restaura. |
| I2C sin config-pin | Puede ser normal porque su driver posee P9_19/P9_20. Corroborar controlador/pinctrl; no cambiar a GPIO. |
| P9_14 ofrece pwm | Disponible documentalmente; no demuestra onda de 50 Hz. Sin export/enable de PWM en T04. |

## Referencias técnicas

- [BeagleBoard: implementación oficial de config-pin](https://github.com/beagleboard/bb.org-overlays/blob/master/tools/beaglebone-universal-io/config-pin), correspondencias P8/P9 y modos simbólicos; consultar además la copia instalada.
- [BeagleBoard: conectores BBB](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html), tablas de pads y alternativas AM335x.
- [PRU Cookbook: configurar pines y compiladores](https://docs.beagleboard.org/books/pru-cookbook/03details/details.html). GCC para ARM no es clpru.
- [TI AM335x, hoja técnica SPRS717L, tabla 4-2](https://www.ti.com/lit/ds/symlink/am3358.pdf), funciones y modos de pads. TRM disponible en la página oficial AM3358.

La selección efectiva y los registros pinctrl en ambas placas se corroboraron el 08/11/2026; véase T04-resultados.md.
