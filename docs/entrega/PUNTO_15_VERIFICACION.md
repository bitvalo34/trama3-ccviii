# Punto 15 · Verificación presencial de TRAMA 3

**Estado al 16 de noviembre de 2026:** cadena CRC → NACK → reintento verificada en PC. Ensayo con interferencia física pendiente. En la página 9 de la guía, el criterio de este ensayo figura como la viñeta 13 de *Entrega*. El número 15 identifica esta acta en esta revisión. La [matriz de entregables](../../software/runtime102/ENTREGABLES_PREPARACION.md) reúne las referencias técnicas.

## 1. Referencia reproducible en PC

Desde la raíz del repositorio, generar un directorio nuevo con los dos registros independientes:

```bash
resultados="$(mktemp -d)"
node software/runtime102/fault-suite.cjs "$resultados/fallos"
```

El caso `crc-nack-retry` altera la primera DATA A→B y conserva su CRC original. El banco vuelve a codificar la trama alterada, de modo que el receptor reconstruye el cuerpo y alcanza el CRC. `report.json` identifica la ejecución como simulación. Los números de registro siguientes corresponden a la ejecución comprobada sobre `c02f3d3`, con Node 24.22.1.

| Paso | Registro observado |
| --- | --- |
| A inicia el intento 1 | A `2937` `ATTEMPT DATA`. A `3316` `TX_DONE DATA` con SID 1, SEQ 3 y CRC 183. |
| B detecta el error y responde | B `3109` `RX_REJECT` con `reason=CRC`. B `3110` `NACK_CONTEXT` y `3490` `TX_DONE NACK`, SID 1, SEQ 3. |
| A acepta el NACK y retransmite | A `3692–3694` `RX_FRAME NACK` válido, `NACK_ACCEPTED` e intento 2 de DATA. A `4072` `TX_DONE DATA` con la misma SID, SEQ y CRC. |
| B recibe y A confirma | B `3866` `RX_FRAME DATA` con CRC válido. B `4246` `TX_DONE ACK`. A `4448–4449` recibe y acepta ese ACK. |
| Termina el mensaje | B `6891` registra la única entrega de `Hola`. A `7474` registra `MESSAGE_CONFIRMED`. Ambos nodos registran `CLEANUP` con `errors=[]`. |

Los registros se encuentran en `$resultados/fallos/crc-nack-retry/A.jsonl` y `B.jsonl`. Cada nodo tiene su propio contador `record`. Para comparar trazas físicas se usan la dirección, SID, SEQ, orden dentro de cada nodo y la captura o vídeo del ensayo.

## 2. Ensayo presencial

1. Registrar ambas BBB, interfaces y montaje P2, perfiles, frecuencias, polaridades, commit y hashes de host y firmware ABI4. Completar la puesta en marcha, reloj, calibración y trama aislada de la [guía de primeras tramas](../../software/runtime102/PRIMERAS_TRAMAS_FISICAS.md). La respuesta ACK aislada comprueba el retorno. Para el NACK se necesita el contexto de una sesión completa.
2. En la consola de sesión, iniciar B y después A como coordinador. Esperar `CONNECTED` en ambas. Hacer un control limpio con `send A` desde A y `send B` desde B, de uno en uno. Conservar los registros de entrega y confirmación. Para el ensayo con interferencia, abrir una sesión con otro ID de registro y enviar `A` desde A. A 1 Hz, una letra requiere unos 890 s nominales en sesión abierta, antes de contar la interferencia y el reintento.
3. Aplicar y retirar la interferencia en el **medio físico de ida**, durante la primera trama DATA. Grabar qué medio se perturbó, cuándo y cómo. Usar el marcador CLK de esa trama como referencia temporal y contrastarlo con `ATTEMPT DATA` del emisor. Preservar el reloj, los pilotos, el encabezado, el CRC transmitido y el retorno. El criterio es producir un cuerpo reconstruible con datos alterados y CRC inválido. Si la matriz corrige el error, si reporta `MATRIX_SYNDROME`, o si se pierde el reloj, guardar ese resultado en el acta y ajustar el siguiente ensayo.
4. Confirmar B `RX_REJECT reason=CRC` → `NACK_CONTEXT` → `TX_DONE NACK`, seguido en A de `RX_FRAME NACK` válido y `NACK_ACCEPTED`. Correlacionar los dos `TX_DONE DATA` de A con la misma SID/SEQ/CRC y con el incremento de `ATTEMPT`. Confirmar B `RX_FRAME DATA` válido, retorno ACK, una única `DELIVERY` de `A` tras END y `MESSAGE_CONFIRMED` en A.
5. Cerrar con `stop` en ambas consolas, conservar `CLEANUP` y copiar sin editar los JSONL de ambos nodos. Adjuntar el vídeo o la captura sincronizada, el acta y un manifiesto SHA-256. Registrar cualquier intento fallido con su propio ID.

### Patrón de interferencia probado en el modelo

Para `A` (`0x41`), la primera pareja de DATA es `01`. Es el bloque 12 del cuerpo y ocupa los ticks **40–42** de la trama contando desde 1, incluidos los seis pilotos. Con `T=1 s`, son los tres ticks que comienzan a 39, 40 y 41 s desde el inicio de **esa trama DATA**. Sin interferencia, las filas C0/C1/C2 de ese bloque son `011`, `110`, `101`.

En PC, dejar C0 y C1 en cero lógico durante esas tres observaciones, conservando C2 cuando está habilitado, hizo que el receptor reconstruyera la pareja `00` y rechazara la trama por CRC. El patrón pasó en el modelo con C0/C1/CLK y con los tres medios. En laboratorio puede ensayarse bloqueando temporalmente el paso de luz y atenuando el trayecto acústico. La captura debe confirmar los ceros normalizados dentro del intervalo real de muestreo de luz y de la ventana acústica. Retirar la perturbación para que el reintento viaje limpio.

La campaña C0/C1 puede verificar este mecanismo en alcance parcial. Para acreditar los tres medios del diseño nominal se requiere su propia evidencia de funcionamiento. El [evaluador de entregas](../../software/runtime102/BANCO_MEDIOS.md#evaluacion-posterior-del-chat-real) comprueba entregas, confirmaciones y limpieza. El dictamen del ensayo se obtiene correlacionando los eventos de arriba con el registro de la interferencia física.

### Cronograma de la intervención

Usar el CLK A→B en el receptor, con analizador de lógica u osciloscopio referenciado al lado B, y una cámara que vea el obturador óptico y la atenuación acústica. El pulso de inicio mide `0.60T` normalizado. Contar esos inicios desde el envío de la letra: START, LEN_LO, LEN_HI y DATA son las primeras cuatro tramas de **ida**, siempre que el control previo haya confirmado que no hay reintentos. Si cambia la secuencia, verificar `TX_START DATA` en A y reiniciar el conteo sobre su pulso largo. El navegador solo presenta el registro y el estado.

| Flanco de subida de DATA a 1 Hz | Acción o señal | C0/C1 limpios |
| --- | --- | --- |
| 0 s, tick 1 | Pulso largo. Poner el contador de flancos en 1. | Pilotos en ticks 1–6 |
| 38 s, tick 39 | Conservar su muestra a 38.8 s. Preparar la intervención. | Sin cambio |
| 39 s, tick 40 | Aplicar después de 38.8 s y antes del inicio de la ventana acústica real del tick 40. | 01 |
| 40 s, tick 41 | Mantener la intervención durante la ventana acústica y la muestra. | 11 |
| 41 s, tick 42 | Mantener hasta completar la muestra de 41.8 s. | 10 |
| 42 s, tick 43 | Retirar antes de la ventana acústica de este tick. Conservar el resto del cuerpo y el CRC. | Sin cambio |

En los perfiles de ejemplo la ventana acústica es `0.20T–0.80T`. Ajustar el margen a la ventana medida, al retardo de los sensores y a la maniobra. Practicar el disparo en una pasada aparte con la misma referencia. Para repetirlo con precisión, usar un contador de flancos externo que sincronice el movimiento del obturador y el atenuador con el cuarto inicio. Guardar el CLK y la ventana de intervención en la misma captura. Mantener el retorno B→A despejado.

| Variante | Acción física | Resultado a registrar |
| --- | --- | --- |
| Principal C0/C1 | Obturador opaco en la ida y atenuador en el trayecto del buzzer de ida; comprobar ceros normalizados en B durante ticks 40–42. | En el modelo, `01 → 00` supera la matriz y falla CRC. Medir en las BBB. |
| Solo luz o solo sonido | Aplicar uno de los dos elementos al mismo bloque. | Puede corregirse, generar síndrome o llegar al CRC. Registrar el resultado observado. |
| Corte antes de pilotos o pérdida de CLK | Documentar por separado si ocurre durante otro diagnóstico. | Pilotos excluidos, pérdida de reloj, silencio o timeout se conservan con su propio dictamen. |

Para el ensayo guiado conservar un byte `A`, CRC SMBUS y UTF-8, con una sola transmisión de aplicación A→B. Tras cerrar los dos servidores, exportar originales, llenar el manifiesto y ejecutar los comandos de [CHECKLIST_GES.md](CHECKLIST_GES.md). El modo `interference` valida la cadena por orden local y SID/SEQ. El manifiesto exige acta y al menos una fotografía, vídeo o captura de instrumento con huella verificada. El operador confirma la correspondencia del material con el ensayo.

## 3. Acta por intento

Copiar este bloque para cada control o ensayo, incluidos los fallidos.

| Campo | Registro observado |
| --- | --- |
| ID · fecha y hora local del PC · operadores | |
| Placas A/B · revisión y montaje · sentido · medios activos | |
| Commit · ambiente ARM/TI/Node · hashes host y firmware · perfiles | |
| Frecuencia por sentido · CRC · codificación · texto esperado | |
| Medio perturbado · método físico · inicio y fin · instrumento o vídeo | |
| A intento inicial / B rechazo CRC | Archivo, número de registro, SID/SEQ del TX y motivo del rechazo |
| B NACK emitido / A NACK aceptado | Archivo, número de registro, SID/SEQ |
| A reintento / B DATA válida / A ACK aceptado | Archivo, número de registro, intento y SID/SEQ |
| B texto y número de entregas / A mensaje confirmado | Archivo, número de registro |
| Limpieza A/B · originales · hashes · incidencias | |
| Dictamen · responsable · fecha | **Pendiente de ejecución física** |

Marcar **Cumple** cuando los originales y la evidencia física acrediten la cadena completa y la entrega única. Marcar **No cumple** si se ejecutó el ensayo pero falta algún comportamiento exigido. Marcar **Pendiente** si la prueba física aún no se ejecutó.
