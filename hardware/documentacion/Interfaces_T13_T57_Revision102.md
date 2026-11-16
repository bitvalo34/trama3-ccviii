# Interfaces reutilizables y limites de T06
T06 ABI1 es diagnostico finito, 1024 eventos, <=10 s, periodos 1..100 ms;
no cambiar solo timeout para una trama 102. A 200 MHz el contador 32 bit envuelve
cada 21.47483648 s. 87 ticks a 1 Hz mas guarda 2T requieren tiempo extendido.

## Contratos para tareas siguientes
| Tarea | Reutiliza | Debe implementar/verificar |
|---|---|---|
| T09 | R31 crudo, C0 bit5/C1 bit14, captura finita, XOR explicito | Polaridad por lote, ventanas acusticas, retardos, modulos a 3.3 V |
| T10 | PWM 50 Hz 1/1.5/2 ms y P8_11/P8_15 | Mecanica descargada, SW287, PC817, relojes por sentido |
| T13 | ABI1, mapeo compartido y hashes | ABI2 separado, version/capacidades/epoch y barreras SPSC |
| T18 | Deteccion/exclusividad/restauracion | Salidas MCP inicializadas OFF antes de direction; servo seguro; no escribir desde T06 bare |
| T24 | R31 unico por muestra, timestamps y pines reloj | Muestreo nominal 0.8T, normalizacion PC817, pulsos 0.6T inicio/0.2T ordinarios |
| T56 | Referencia software/matrices102 | Reusar G/H y pruebas existentes, no duplicarlas aqui |
| T57 | interfaces/stream102.h y stream102.py (modelo) | Motor continuo real PRU/ARM, ring, watchdog, integracion/ensayo fisico |

Tres canales x tres ticks codifican dos bits; 27 bloques de cuerpo=81 ticks,
6 pilotos=87 ticks, guarda 2T. Frecuencia inicial 1 Hz, independiente por sentido.
T06 no reproduce una trama ni el temporizado de recepcion 0.8T.

## Propuesta de motor continuo, no desplegada
ABI2 separado; magic/version diferentes de ABI1. Ring SPSC de 256 entradas y 28 bytes
cada una, indices monotónicos uint32, distancia productor-consumidor <=capacidad.
PRU es unico escritor producer; ARM unico escritor consumer. PRU escribe datos y
publica indice tras barrera; ARM copia slot tras acquire y publica consumo tras barrera.
No leer ticks_hi/lo concurrentemente de un slot sin publicacion estable.
El header cabe en 12 KiB compartidos; requiere comprobar alineacion/orden en compiladores destino.

Epoch identifica reinicios; sequence identifica perdidas. Overflow no sobrescribe:
FAULT, salida segura, notificacion ARM, resincronizacion explicita con epoch nuevo.
Muestras vectoriales y flancos son tipos distintos; cada muestra hace una lectura R31.
Conservar raw y normalized con mascara de polaridad configurada/medida.
Cada bloque de 3 muestras se entrega al decodificador existente; no usar ring como
almacen ilimitado de toda sesion. Registrar retraso de muestra respecto 0.8T.
La ventana acustica y debounce mecanico se caracterizan en T09/T11; una muestra
instantanea del comparador no demuestra presencia de tono durante la ventana.

Timestamp extendido: leer IEP continuamente, acumular delta uint32 en contador 64.
La lectura debe ocurrir antes de un wrap, incluso sin flancos. Un silencio de 87 s
no permite extender timestamps tomando solo los dos extremos. Vigilar max_gap,
heartbeat y plazo externo; si se pierde garantia temporal, invalidar epoch.
El modelo Python requiere elapsed_ns como cota independiente por llamada y rechaza
intervalo >=wrap. No es un controlador de watchdog PRU ni lectura hardware.
ARM lento debe producir backpressure/FAULT acotado, no detener muestreo de forma silenciosa.
STOP debe dejar TX bajo antes de publicar STOPPED; cancelar timers y liberar solo recursos propios.

Pruebas pendientes T57: >=89 s, varios wraps, cargas ARM, pausa consumidor, overflow,
reinicio de cada lado, secuencias/epoch, pérdida de reloj y limpieza. Las pruebas de PC
verifican contratos/modelos; no cierran T57 ni acreditan retardo de PC817.
