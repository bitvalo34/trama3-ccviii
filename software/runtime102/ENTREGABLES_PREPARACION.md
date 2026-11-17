# Entregables 2 al 10 de TRAMA 3

Corte del 16 de noviembre de 2026. La numeración 2–10 sigue el orden de las viñetas de la sección **Entrega**, página 9 de la guía *Proyecto Final: Capa Física No Convencional*. La [verificación presencial](../../docs/entrega/PUNTO_15_VERIFICACION.md) usa el identificador **15** solicitado para esta revisión. En el orden de la guía, la interferencia física aparece en la viñeta 13 y la documentación técnica en la 15.

Base del software revisado: [`c02f3d3`](https://github.com/bitvalo34/trama3-ccviii/commit/c02f3d361a677ce4cd5d3aadc99985a1214cdd67), que incorpora el runtime 102, el banco de patrones y la ruta experimental C0/C1. Los documentos sobre el montaje y la placa A también se consultaron en las ramas de los PR #7 y #10.

## Matriz de entregables

| Punto | Qué cubren el repositorio y las pruebas | Evidencia para el cierre |
| --- | --- | --- |
| **2. Dos equipos funcionales y bidireccionales** | T06 registra pruebas de las dos BBB por separado. El runtime intercambió mensajes en ambos sentidos entre dos nodos simulados. [Resultados T06](../../hardware/documentacion/evaluacion-T06-2026-11-15.json) · [Validación en PC](VALIDACION_FISICA_SOFTWARE.md) | Ejecutar el enlace A→B y B→A con ambas placas y guardar los mensajes y registros de la misma sesión. |
| **3. De tres a ocho canales físicos, incluido el reloj** | El diseño usa cuatro canales por sentido: C0 luz, C1 sonido, C2 nylon y CLK por PC817. El perfil experimental habilita C0/C1/CLK con C2 declarado ausente. [Diseño P2](../../hardware/documentacion/fuentes-P2/diseno-electrico.md) · [Primera trama](PRIMERAS_TRAMAS_FISICAS.md) | Registrar el montaje efectivo, pinout, polaridades y señal de reloj en ambos sentidos. |
| **4. Tres medios físicos no convencionales** | El diseño y montaje describen luz por LED/LDR, sonido por buzzer/KY-037 y tensión de nylon por servo/final de carrera. En la placa A se documentaron el LED, cambios de sensor reportados y una incidencia I²C abierta. [Montaje](https://github.com/bitvalo34/trama3-ccviii/tree/9ba0bcaa271740effe206ec1ef79b72c070168e6/hardware/montaje-medios) · [Evidencia placa A](https://github.com/bitvalo34/trama3-ccviii/tree/8702cfa410404c5331f371a5e49405ce3ea7556f/hardware/inspecciones/avance-placa-A-2026-11-16) | Probar los tres medios sobre las dos interfaces del montaje real. La campaña C0/C1 acredita un alcance parcial cuando se ejecute. |
| **5. PHY con SYN, SFD, Control, DATA y CRC** | El serializador y receptor comparten el formato de revisión 102. La trama completa se reconstruyó en PC a partir de muestras sintéticas. [Formato y estados](../../docs/protocolo/TRAMA3_Protocolo_Revision_102.md#formato-físico-y-calendario) · [Prueba](test-phy.cjs) | Mostrar una trama física decodificada y los resultados de pilotos, bloques, campos y CRC. |
| **6. DATA y CRC de 8 bits por trama** | La trama lógica de 54 bits lleva DATA8 y CRC8. Un carácter UTF-8 de varios bytes ocupa una trama DATA por byte. [Formato](../../docs/protocolo/TRAMA3_Protocolo_Revision_102.md#formato-físico-y-calendario) · [Codec compartido](../matrices102/engine.js) | Identificar ambos campos en el volcado de la trama física del punto 5. |
| **7. Cuatro CRC seleccionables** | CRC-8/SMBUS, AUTOSAR, SAE-J1850 y MAXIM-DOW lograron negociación e intercambio en pruebas de PC. El chat de simulación permite elegir CRC. [Ensayos del runtime](test.cjs) · [Chat simulado](web.cjs) | Mostrar la selección y una recepción válida por variante en el programa con enlace físico. La consola de hardware actual usa SMBUS por defecto y carece de opción de selección. |
| **8. UTF-8 de 1 a 4 bytes y Extended ASCII** | UTF-8 y Windows-1252 están implementados. En PC se comprobó el intercambio exacto de `Añ€😀` en UTF-8 y `Añ€` en Windows-1252. [Pruebas de integración](test_integration.cjs) · [Codec](../matrices102/engine.js) | Guardar los bytes y el texto reconstruido en cada modo en el enlace físico. La consola de hardware usa UTF-8 por defecto y carece de selector. |
| **9. ACK, NACK y retransmisión** | Stop-and-Wait conservó SID/SEQ, aceptó NACK contextual y entregó el mensaje una vez en PC. El límite es tres reintentos después del intento inicial. [Banco de fallos](fault-suite.cjs) · [Trazabilidad y acta](../../docs/entrega/PUNTO_15_VERIFICACION.md) | Abrir una sesión real, provocar un error físico y conservar rechazo CRC, NACK, reintento de la misma trama, ACK y entrega. |
| **10. Sincronización y reconstrucción al recibir** | La captura usa CLK para inicio y muestreo. La revisión 102 aplica seis pilotos de canal y 27 bloques de tres ticks. El receptor y el modelo C pasaron en PC. [Validación](VALIDACION_FISICA_SOFTWARE.md) · [Banco de medios](BANCO_MEDIOS.md) | Guardar capturas de reloj y datos con 87 ticks, pilotos y 54 bits reconstruidos en ambos sentidos. La campaña nominal de la revisión 102 pide al menos 100 bloques por pareja y sentido, más ensayos con medios interrumpidos. |

## Referencia técnica común

| Elemento | Diseño usado |
| --- | --- |
| Aplicación y presentación | Chat en PC sobre dos nodos simulados. Consola local por BBB para el enlace físico. UTF-8 o Windows-1252 convierte texto a bytes. |
| Enlace de datos | Trama lógica `SYN12 + SFD6 + CONTROL4 + DATA8 + CRC8 + SEQ8 + SID8`. Stop-and-Wait valida CRC y contexto, confirma y reintenta conservando SID/SEQ. |
| PHY | PRU0 emite y mide CLK, y muestrea los datos. Cada pareja lógica se codifica por paridad XOR en tres ticks. Linux gestiona la sesión y prepara las salidas P2 con el controlador local. |
| C0 / luz | LED por U1 GPA0 y J2. Receptor LDR en J5, DO hacia P9_27. |
| C1 / sonido | Buzzer por U1 GPA1 y J3. Receptor KY-037 en J6, DO hacia P8_16. La ventana acústica reduce sus pulsos a una decisión por tick. |
| C2 / nylon | Servo SG90 en J4 con PWM en P9_14. Final de carrera en J7, entrada P9_24. |
| CLK / sincronización | P8_11 hacia el par J9 TX. J8 RX con PC817 hacia P8_15. Cada sentido tiene su propio par. |
| Interfaces locales | USB para consola de cada BBB. P9_19/P9_20 para I²C local al MCP23017. |

[Arquitectura del runtime](../../docs/planificacion/Informe_Runtime102_Base.md) · [Conexiones y componentes P2](../../hardware/documentacion/fuentes-P2/diseno-electrico.md) · [Planos y cableado del montaje P2](https://github.com/bitvalo34/trama3-ccviii/blob/9ba0bcaa271740effe206ec1ef79b72c070168e6/hardware/montaje-medios/construccion/03-cableado-P2.md)

## Validación y entrega

- En PC Linux x86_64 con Node 24.22.1 y GCC 14.2 se ejecutaron `bash software/runtime102/test-physical.sh` y `python3 tests/hardware/verify_pc.py --output RUTA_NUEVA`. Pasaron 10 252 comprobaciones matemáticas, 2 264 de integración matricial (209 sesiones), las suites del runtime, diez escenarios del banco de fallos, 24 pruebas Python del runtime, el modelo C ABI4 y las verificaciones de P2/T06/T08 en PC.
- Para presentación, `Añ€😀` en UTF-8 da `41 C3 B1 E2 82 AC F0 9F 98 80`. `Añ€` en Windows-1252 da `41 F1 80`. La campaña física debe conservar la configuración usada junto a los resultados.
- El ZIP final reúne código y pruebas de un commit fijo, los documentos de arquitectura y conexiones P2, [la operación del runtime](OPERACION.md), [el arranque por BBB](ARRANQUE_BBB.md), perfiles efectivamente usados, actas, evidencias originales y un manifiesto de versiones y hashes. El [paquete offline](PRIMERAS_TRAMAS_FISICAS.md) cubre el despliegue de laboratorio. El expediente final se entrega por GES y la verificación se demuestra presencialmente.
- Quedan pendientes la compilación ARM/TI del runtime ABI4, la campaña nominal con tres medios, la integración del chat web al nodo físico y el registro del montaje efectivo en ambas interfaces. Los [formularios T08](../../hardware/pruebas/t08/README.md) recogen las mediciones P2.
