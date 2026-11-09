# Simulador matricial de TRAMA3 revisión 102

Abrir **TRAMA3_Matricial_102.html** con Edge, Chrome o Firefox. Es autocontenido; no instala nada, no accede a las BBB y no requiere internet.

Se integró la matriz de la revisión 102 con las sesiones del motor anterior. La emisión completa tiene seis pilotos y 27 bloques de tres ticks; ACK, NACK y gestión usan el mismo formato matricial. El reloj transporta marcadores temporales, no el control de 17 bits de 101.

## Ejecutar las pruebas

Desde esta carpeta, con Node.js:

```sh
node test.cjs
node build-html.cjs
```

No hay dependencias externas. Node 18 o posterior recomendado. El HTML se regenera desde template.html, core.js y engine.js.

- **reference.cjs**: referencia matemática independiente y 10252 comprobaciones.
- **core.js**: codificador/decodificador compartido por navegador y motor.
- **engine.js**: sesiones, colas, trama, modelo de medios y reloj, negociación y fallos.
- **test.cjs**: 2264 comprobaciones de integración, incluyendo 209 escenarios de sesión.
- **resultados-integracion.json**: resultado completo de la batería.
- **ejemplo-corte-dos-medios.json**: registro de Hola con luz y sonido bloqueados durante 120 s desde el tick 8 de DATA.

Resultado de la ejecución del 08/11/2026: PASS. Se probó además el HTML en Edge: envío limpio, corte temporal de dos canales, selección de eventos, vistas de escritorio y móvil, sin errores JavaScript.

## Demostración sugerida

1. Dejar Hola, ambas frecuencias a 1 Hz y sin fallos. Pulsar Simular.
2. Ver CHANNEL_TEST y MATRIX_BLOCK. Cada bloque muestra nueve muestras, distancia y decisión; los bits se validan antes del CRC final.
3. Marcar C0 y C1 desde inicio. C2 permite recuperar los dos bits mediante tres observaciones por bloque. Es un modo degradado.
4. Cambiar a Durante primera DATA y duración 120 s. En el caso guardado hay un reintento y entrega exacta.
5. Marcar los tres medios o el reloj permanentemente: el protocolo no inventa bits ni reintenta sin límite.
6. Probar ACK perdido: se repite la confirmación sin duplicar el mensaje.
7. Probar un bit o dos bits invertidos: corrección matricial. Probar bloque válido equivocado: el caso falla por CRC y se retransmite.
8. Pedir frecuencias A=2 y B=4 para ver la negociación. Son perfiles hipotéticos, no frecuencias aprobadas para los sensores.
9. Cambiar retardo mecánico a 500 ms: que el mensaje llegue no acredita que nylon siga funcionando. Revisar los pilotos y la máscara.

Los filtros sólo limitan la tabla visible; Guardar registro JSON exporta todos los eventos. La probabilidad de inversión actúa sobre muestras de datos y pilotos, no representa una medición del sensor. Semilla fija para reproducibilidad.

## Resultados y límites

64 combinaciones de bloqueo por dirección: las 49 con al menos un medio vivo en cada sentido entregan los mensajes; las otras 15 terminan sin sesión operativa. Se cubren las cuatro variantes CRC, 16 parejas de frecuencia, cortes a nivel 0/1, temporales/permanentes antes y durante DATA, fallos de reloj, ACK, versión, sesión, UTF-8/CP1252 y vuelta de SEQ.

A 1 Hz y sin fallos: A tarda 1246 s virtuales; Hola 1780 s. Incluyen apertura y guardas. No esperar físicamente ese tiempo para ejecutar el simulador.

Un canal que pasa pilotos puede fallar después. El receptor no conoce la máscara de fallos del banco: opera sobre muestras, pilotos y distancia del código. Fuera del radio de corrección puede aceptar una palabra equivocada; existe un contraejemplo explícito. El CRC no elimina todas las colisiones.

El modelo no valida firmware, simultaneidad de capturas PRU, niveles eléctricos, interferencia cruzada analógica, rebote real ni frecuencia máxima. La captura de cada tick se representa como un vector; no se atribuye paralelismo físico a la ejecución JavaScript. La correspondencia académica con el caso de clase sigue pendiente de confirmación.

El motor 101 en software/simulador se conserva como histórico y no es la demostración de la revisión 102.
