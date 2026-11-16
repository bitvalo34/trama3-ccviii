# Entregables y avance verificable de runtime102

Fuente: Proyecto_-_Capa_Fisica_ (1).pdf, 10 paginas, recibido el 15/11/2026,
especialmente pp.4-6 y 9. Esta matriz no modifica el tracker Excel ni sus fechas.
El Excel revision102 vigente no pudo materializarse en esta sesion; no se asignan
porcentajes ni cierres de filas cuyo criterio completo no se ha comprobado.

| Requisito de la guia | Evidencia disponible | Pendiente |
|---|---|---|
| Dos equipos bidireccionales | Endpoints independientes A/B en simulacion; T06 PASS ambas BBB | Aplicacion integrada y enlace fisico |
| SYN/SFD/Control/DATA/CRC | Referencia 102 compartida por runtime; DATA/CRC 8 bits | Firmware y recepcion fisica |
| Cuatro CRC seleccionables | API Endpoint crc y pruebas de los cuatro | Selector de chat y negociacion fisica |
| UTF-8 y Extended ASCII | Funciones de referencia y configuracion de Endpoint | Exponer selector, probar 1/2/3/4 bytes en runtime; CP1252 documentado como variante |
| ACK/NACK/retransmision | ACK perdido, deduplicacion, CRC->NACK contextual->reintento en software | Interferencia fisica presencial |
| LOG de tramas/CRC/control | RX_FRAME, RX_REJECT, TX_DONE, ACK_ACCEPTED, NACK_CONTEXT, NACK_ACCEPTED, ATTEMPT | Persistencia, exportacion y visualizacion web |
| Chat web | CLI y API de nodo como base | Servidor local, interfaz, cola y estados de entrega |
| Tres medios y reloj | Diseno P2 y mapeo de pines | Caracterizacion, ambas interfaces y comunicacion |
| Documentacion y ZIP | Protocolo, planos y ZIP de evidencia T06 | Manual integrado, instalador, fuentes y resultados finales |

## Orden de ejecucion

1. Consolidar contrato ABI ARM/PRU y temporizacion con READY por tick/epoch.
2. Adaptador PRU continuo: RX vectorial, TX de reloj, ring SPSC con barreras,
   watchdog, STOP y contadores extendidos. Compilar con TI en BBB antes de acreditar build.
3. Consumidor ARM y controladores P2: MCP23017, PWM, inicializacion OFF y configuracion
   por placa. Compartir interfaz con dispositivos simulados.
4. Integrar el endpoint con transporte real. Validar firmware en BBB sin P2 con
   fixture de diagnostico adecuado; los tests C de PC no acreditan esto.
5. Chat web local por nodo con seleccion de codificacion/CRC, estados
   pendiente/enviando/confirmado/fallido y registro descargable. HTTP no sera el
   transporte del mensaje entre nodos en modo hardware.
6. Gestion de perfiles y negociacion dinamica: el runtime actual solo admite
   1 Hz y rechaza cambios; la referencia simulada sigue disponible como oraculo.
7. Empaquetado offline y manuales. Inventariar Node y herramientas en ambas BBB:
   Node 18+ del PC no acredita compatibilidad con Debian 9/10 ARM.

## Calendarizacion

T06: cierre tecnico respaldado por evidencia de ambas placas.
T13/T16/T17/T57: avances de contrato/modelo; falta ABI y ejecucion ARM/PRU real.
T15/T56: referencia y pruebas disponibles; cierre sujeto al criterio exacto de fila.
T23/T24/T25: nucleo probado en PC; integracion fisica pendiente.
T18: controladores de runtime pendientes. T28: negociacion no portada al runtime.
T08/T09/T10/T11/T12: no cerrar con simulacion; requieren la evidencia fisica aplicable.

La guia exige calificacion presencial: el ZIP por si solo no acredita la entrega.
No escribir resultados fisicos esperados como si fueran observados. La demostracion
de error intencional debe mostrar el recorrido CRC/NACK/reintento sobre los medios.

## Avance de integracion supervisada

Implementado y probado en PC: contrato Endpoint/puente, confirmacion READY despues
de preparar salidas, parada ante errores, limpieza con errores visibles y log JSONL
por nodo. Banco de dos supervisores con cuatro CRC y fallos de IO inyectados.
ABI3 separa fin del cuerpo y fin de guarda. Host/firmware requieren recompilacion
conjunta y validacion TI/ARM; las pruebas C portables no acreditan esa compilacion.

Esto adelanta la integracion y el entregable de registro del protocolo. No cambia
el estado de cierre de T08, T18 ni T57. Faltan el lanzador con propiedad exclusiva
de recursos, enlace real al controlador P2, chat por nodo y pruebas fisicas.

## Avance del 16 de noviembre de 2026

El enlace Node/Python al controlador P2 ya se prueba con dos procesos persistentes
y backend simulado. Se propagan errores de preparacion y apagado. Hay perfiles
BBB-A/BBB-B con calibracion pendiente, y chat por nodo con sesion persistente,
cola acotada, estados de mensaje, CRC/codificacion elegibles al arrancar y logs.
Lo anterior sustituye los pendientes de software correspondientes del parrafo
anterior; no sustituye la conexion fisica al backend Linux y sus recursos.

| Entregable | Avance comprobable | Validacion restante |
| --- | --- | --- |
| Control de medios | Adaptador P2 y mismo controlador Python probado por proceso | MCP/PWM real, calibracion y asentamiento |
| Chat y registro | Dos vistas, mensajes sucesivos, UTF-8/CP1252, cuatro CRC en el nucleo, JSONL | Ejecucion por BBB y transporte fisico |
| Instalacion | Inventario de solo lectura y ZIP de fuentes con SHA256SUMS | Node/ABI3 TI/ARM en Debian de ambas BBB |
| Informe tecnico | Arquitectura y operacion documentadas | Resultados y evidencias de P2 y demo presencial |

Pruebas nuevas: test_integration.cjs (proceso Python, chat/API, codificaciones,
colas y registros) y test_p2.py (incluido fallo al apagar). Se conservan
test_supervisor.cjs y las 24 comprobaciones previas del protocolo. La comprobacion
web es de HTML/API; no se ha realizado inspeccion visual en un navegador.
No se modifican estados de cierre ni fechas del tracker original.

## Banco supervisado de fallos y base de informe

fault-suite.cjs agrega diez escenarios reproducibles con JSONL por nodo,
report.json (hashes de fuentes y verificaciones) y REPORTE.md. Comprueba perdida
de ACK, duplicados, CRC/NACK/reintento, perdida de enlace, salida del puente,
discontinuidad de captura y fallos/tardanza de IO. Un FAIL de sesion esperado
puede corresponder a un PASS del ensayo de parada.

El chat muestra reintentos, duplicados y diagnostico, y admite un escenario
de fallo al arrancar. Informe_Runtime102_Base.md documenta arquitectura, pruebas,
guion de demostracion en PC y pendientes fisicos. Ninguna de estas inyecciones
equivale a interferencia real sobre las placas.

## Preparacion del arranque por BBB

launcher.cjs y board_owner.py conectan el supervisor con un propietario de
recursos y el controlador P2 mediante proceso persistente. Once pruebas de
archivos simulados verifican restauracion/ocupacion; pruebas de procesos Node
verifican ready, ABI, timeout, caida y limpieza. El modo plan es de solo lectura;
mock no accede a dispositivos. La ruta hardware exige Linux y perfil calibrado.

Pendientes: compilar TI/ARM y validar deteccion, tiempos, I2C y restauracion en
cada BBB; acoplar el chat a un unico nodo fisico; verificar calibracion y medios.
ARRANQUE_BBB.md detalla limites ante corte de alimentacion y bloqueos residuales.
El lanzador no cambia los estados de cierre fisico de T08/T18/T57.
