# Runtime 102: base incremental

Estado: implementacion de software, sin validacion fisica nueva. No cargar como
firmware ni conectar P2 usando esta carpeta. T06 conserva sus evidencias; T08 sigue pendiente.

Entrada actual: [OPERACION.md](OPERACION.md). Incluye chat persistente por nodo
(node-web.cjs), adaptador P2 Node/Python, perfiles BBB-A/BBB-B, inventario de solo
lectura y empaquetador reproducible. web.cjs se conserva como banco inicial.

Preparacion de arranque: [ARRANQUE_BBB.md](ARRANQUE_BBB.md). launcher.cjs agrega
plan de solo lectura, arranque por nodo con procesos simulados y ruta Linux
experimental con perfiles calibrados. Sus pruebas PC no validan la ejecucion ARM.

## Ejecutar ahora en PC

Requiere Node 18+ y, para el modelo C, GCC. Sin paquetes externos.

```sh
node software/runtime102/test.cjs
node software/runtime102/cli.cjs simulate Hola Respuesta
gcc -std=c99 -Wall -Wextra -Werror software/runtime102/capture.c software/runtime102/test_capture.c -o test_capture
./test_capture
```

En Windows el ejecutable es test_capture.exe. La simulacion usa segundos virtuales;
no hay que esperar los minutos que requiere la transmision fisica a 1 Hz.
La salida JSON declara origin=simulation y physical_status=NOT_TESTED.

## Componentes implementados

- protocol.cjs: fachada sobre la referencia 102 existente, sin ejecutar simulacion
  al importar. Comparte tramas, CRC, matriz y parser; no es una nueva especificacion.
- endpoint.cjs: instancia independiente por nodo, HELLO/COMMIT, CRC negociado,
  envio bidireccional, colas acotadas, prioridad de respuestas, SID/SEQ,
  deduplicacion, cuatro intentos, temporizador desde fin TX y entrega tras END.
  Un reinicio detectado invalida la sesion: no se promete exactamente una vez.
- stream.cjs: receptor incremental de flancos/muestras, timestamps uint64 con
  BigInt, epoch/secuencia, control de captura 0.8T y matriz por bloque.
- virtual.cjs: conecta dos endpoints mediante eventos del formato de captura.
  Solo el banco conoce las perdidas inyectadas; el receptor observa las muestras.
- cli.cjs: simulacion y reproduccion de eventos JSONL. Replay no autentica origen
  fisico ni valida toda una sesion; requiere al menos una trama y ausencia de errores.
- capture.c: nucleo C continuo portable a 1 Hz, extension IEP, normalizacion R31,
  captura vectorial y ring acotado. Su API es de un solo hilo; NO es ABI compartida.

## Limites y trabajo siguiente

La negociacion dinamica de frecuencias del simulador de referencia NO se ha
portado al endpoint: este responde REJECT y opera solo a 1 Hz. El motor C aun
necesita adaptador PRU, watchdog independiente, publicacion release/acquire y
consumidor ARM integrados al protocolo. native/ contiene ahora los adaptadores
experimentales de PRU y ARM y un contrato separado; p2.py contiene el controlador
MCP/PWM con pruebas de IO simulado. Falta compilar TI/ARM y probar en BBB.
No existe todavia launcher de hardware. web.cjs ofrece un chat de prueba LOCAL
simulado, con seleccion de CRC y descarga de registro; no es el chat fisico final.
No debe confundirse el ring de prueba C con el contrato propuesto stream102.h.
Los tiempos de sondeo/asentamiento, ventana acustica y debounce reales no estan
caracterizados. Una muestra instantanea del comparador no sustituye esos filtros.

Siguiente integracion: contrato ABI definitivo, adaptadores ARM/PRU, controladores
P2 (MCP23017 GPA0/GPA1, PWM P9_14), perfiles por placa, pruebas en BBB sin P2 y luego
integracion fisica tras las comprobaciones correspondientes. TX clock P8_11;
RX clock P8_15; C0 P9_27, C1 P8_16, C2 P9_24. No modificar T06 para convertirlo
en un motor de sesiones largas. La configuracion de GPIO no acredita niveles electricos.

No se han actualizado estados del tracker ni publicado cambios remotos.

## Continuacion: compilacion y banco web

Desde la raiz del repositorio:

```sh
node software/runtime102/web.cjs
```

Abrir http://127.0.0.1:8080. El servidor solo escucha loopback; no mueve hardware.
Validacion: `node software/runtime102/test_web.cjs` y
`python software/runtime102/test_p2.py`. En Windows las pruebas inyectan fcntl;
el backend real requiere Linux y acceso exclusivo concedido por el supervisor.

native/build.sh compila el puente host y firmware TI cuando esten disponibles
gcc, clpru y runtime TI. No cambia pinmux ni carga firmware. Conservar log y mapa.
La prueba portable native/test_service.c cubre 90 s RX, varios wraps, STOP,
ausencia de READY y 87 ticks TX con guarda. No acredita tiempos reales PRU.

Pendientes concretos antes de usar P2: propietario real de recursos/restauracion,
conexion del controlador P2 al supervisor, comprobacion
de Node/alternativa en Debian ARM, compilacion TI/ARM, filtros y calibracion,
negociacion dinamica y seleccion de codificacion en UI. No se afirma plug-and-play.
En native/README.md se describen los precondicionantes del puente experimental.

## Supervisor y log persistente

`supervisor.cjs` une Endpoint, StreamDecoder y el contrato TX/READY del puente.
`bridge.cjs` adapta un proceso host ya creado. Ambos requieren un propietario
de recursos y un adaptador de salidas inyectados; no cargan firmware ni energizan P2.
El propietario debe llamar `pump()` periodicamente con reloj monotono en segundos,
detener el proceso nativo y restaurar recursos en `cleanup()`. Una operacion P2
pendiente al parar se reporta como limpieza no confirmada; no se declara segura.
READY solo se envia despues de aplicar las salidas dentro del presupuesto de 15 ms.
Ese presupuesto y los 20 ms de anticipacion son provisionales hasta medir hardware.

Prueba integrada sin placas, desde la carpeta cc8-trama3 (el destino debe ser nuevo):

```powershell
node .\repo\software\runtime102\supervised-simulation.cjs .\evidencias\runtime102-supervisado-01
```

Crea A.jsonl, B.jsonl y summary.json. El log incluye tramas, ACK/NACK, reintentos,
capturas, entregas y cierre. Se crea sin sobrescribir; limite 16 MiB por nodo.
La escritura es sincrona y se hace fsync al cierre; no garantiza persistencia ante
corte electrico durante la sesion. Saturacion/fallo del log detiene la sesion.
Todos estos resultados indican simulation / NOT_TESTED.

`node software/runtime102/test_supervisor.cjs` prueba ambos nodos, los cuatro CRC
(B arranca con SMBUS y aprende el negociado), fallos/tardanza/bloqueo de salidas,
salida del puente, orden invalido, limpieza, JSON fragmentado y proteccion del log.
El banco web inicial sigue usando virtual.cjs. node-web.cjs usa ahora sesiones
supervisadas persistentes con perfiles y logs por nodo. Los perfiles tienen
calibracion PENDING: conectar el lanzador de hardware sigue pendiente.
