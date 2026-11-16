# ABI3 experimental y adaptadores

magic=0x52313032, abi=3, bytes=7592. El magic distingue el contrato anterior
propuesto en interfaces/stream102.h. Ring SPSC 256 x 28 bytes en SRAM compartida.
ARM es unico consumidor; PRU unico productor. No ejecutar dos hosts.

TX: ARM publica 87 vectores congelados y tx_id. PRU solicita cada vector 20 ms
antes del flanco programado; ARM aplica las salidas y confirma id/index. READY
no acredita asentamiento. A 1 Hz se captura RX a 0.8T y CLK usa 0.6T/0.2T.
tx_body_done se publica al terminar el cuerpo y tx_done tras la guarda 2T.
El host emite body_done antes de done; el supervisor conserva la hora de recepcion
del primer aviso para el timeout. La latencia de entrega host/Node queda pendiente
de medir en BBB: no se presenta esa hora como timestamp fisico exacto.
ABI3 cambia el layout: recompilar host y firmware juntos, no mezclar con ABI2.

STOP/FAULT desactiva CLK; no apaga automaticamente MCP/servo: el supervisor debe
desactivar sus controladores y detener remoteproc. Heartbeat ARM: 500 ms.
Pausa PRU superior a un wrap requiere watchdog externo ARM: el IEP solo no puede
detectar todos los silencios ambiguos. El host comprueba heartbeat PRU con cota
de 500 ms; falta integrar el supervisor y verificarlo sobre ARM.

## Preparacion sin BBB

`service.c` se ejecuta en PC con test_service.c. `firmware.c` es el adaptador TI;
`host.c` es Linux ARM y accede /dev/mem. No estan compilados/verificados en BBB.
La barrera PRU y layout deben revisarse en ensamblador TI; maximo IRAM 8 KiB.

Cuando se disponga de BBB se puede ejecutar solo `bash build.sh` sin energizar P2.
No hay launcher autorizado de pruebas fisicas: antes hacen falta supervision,
exclusion de recursos IEP/PRU/PWM, checklist, pinmux y restauracion. No copiar
estos binarios a /lib/firmware ni arrancarlos manualmente a partir de este README.

El protocolo del puente host es JSONL de salida y comandos TX/READY/STOP por stdin.
Es una interfaz interna, no CLI del usuario ni transporte entre nodos. El runtime
Node dispone de ProcessBridge y Supervisor para este contrato, probados con un
puente simulado. launcher.cjs conecta el propietario de recursos y controlador P2;
hay pruebas de procesos y archivos simulados y una ruta Linux experimental,
todavia no validada en Debian ARM. El host lee stdin sin esperar una
linea completa, conservando el heartbeat aunque llegue un comando fragmentado.

El host ahora emite ready (ABI3/epoch) al observar RUNNING. El lanzador no conecta
el pin de reloj hasta recibirlo. Recompilar el host; no mezclar ejecutables de
entregas anteriores que no emitan esta confirmacion.
