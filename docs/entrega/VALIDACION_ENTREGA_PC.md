# Validación en PC de la preparación GES

**Origen · software y simulación. Estado físico · PREPARADO.** Comprobaciones ejecutadas el 17 de noviembre de 2026 en Ubuntu x86_64 con Node 22.22.0 y Node 16.20.2, Python 3.12.3 y GCC 13.3.0. El modelo C y el host de estas pruebas son para PC.

| Prueba ejecutada | Resultado |
| --- | --- |
| Matrices y sesiones | 10 252 comprobaciones matemáticas y 2 264 de integración, con 209 escenarios de sesión. |
| Runtime y parser | Suite completa. Cuatro CRC, pérdida de ACK, NACK contextual, reintentos, deduplicación, vuelta de SEQ y errores de reloj. |
| Chat y HTTP | Envío y recepción en simulación, UTF-8 de varios bytes y CP1252. Interfaz por nodo B con endpoint local de prueba, estados pendiente → transmisión → espera → confirmado, y entrega incierta al interrumpir. HTTP 400, 403, 409 y 413, filtro ACK y descarga comprobados. |
| P2 y ABI4 | 24 pruebas Python del runtime, compilación del host x86 y modelo C (captura RX de 90 s, vueltas, READY, ventana acústica y apagado). Regresión P2/T06/T08 con evaluación en PC. |
| Banco de fallos | 10 escenarios conformes con su expectativa, incluidos fallos protectores y limpieza. |
| Ventana de interferencia | Muestras sintéticas C0/C1 con C2 ausente. En DATA de `0x41`, las filas de ticks 40–42 son `011 / 110 / 101`. Forzar C0/C1 a cero reconstruyó `0x01` con CRC recibido distinto del calculado. |
| Evaluador | `crc-nack-retry` pasó con SID 1 y SEQ 3. B registró un CRC inválido, un NACK enviado y una entrega. A aceptó el NACK, reenvió DATA, aceptó el ACK y confirmó el mensaje. El control sin interferencia falló el criterio de cadena como se esperaba. |
| Documentación | DOCX editable y PDF de cinco páginas exportado desde Word, con revisión de páginas. |

### Reproducir

~~~bash
bash software/runtime102/test-physical.sh
python3 tests/hardware/verify_pc.py --output "$(mktemp -d)/p2"
~~~

La [lista GES](CHECKLIST_GES.md) contiene los comandos del banco y evaluador. Los números de registro dependen de la versión y del escenario. El [acta del punto 15](PUNTO_15_VERIFICACION.md) conserva como antecedente los números de la corrida de la PR #13.

Pendientes físicos en A/B: perfiles medidos, compilación TI/ARM, retorno y sesión del chat, interferencia sobre el montaje y aceptación nominal de tres medios. La PR #10 conserva las comprobaciones previas sobre la placa A.
