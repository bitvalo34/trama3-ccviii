# Referencia matricial 102

Ejecutar `node reference.cjs`. No requiere dependencias. La salida incluye 10252 comprobaciones y registros por bloque de la letra A con cero, uno, dos y tres medios bloqueados.

Cada bloque usa G de 9×2, codificación conjunta por tres canales y tres ticks. Los borrados se deducen de pilotos recibidos en el ensayo; los fallos inyectados no se pasan al decodificador como conocimiento privilegiado. La distancia mínima se recalcula para las posiciones disponibles. Las pruebas incluyen un contraejemplo fuera del radio de corrección.

Este programa es la referencia de la capa matricial, no el simulador completo de sesiones. No implementa negociación, ACK, firmware ni señales analógicas. El HTML en ../simulador corresponde exclusivamente a la revisión 101 y permanece histórico.

Especificación: ../../docs/protocolo/TRAMA3_Protocolo_Revision_102.md.
