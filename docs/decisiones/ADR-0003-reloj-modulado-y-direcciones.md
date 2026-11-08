# ADR 0003 Reloj modulado y frecuencias por sentido

Fecha: 07/11/2026. Base de implementación, pendiente de validación física.

El auxiliar respondió a la consulta explícita sobre pulsos de distinta duración para avisar canales: pueden durar distinto si el protocolo lo amerita, y la lectura utiliza el reloj enlazado desde el otro dispositivo. Interpretamos esta respuesta como aceptación del principio de modulación, no como certificación de nuestros campos ni firmware. No necesitamos repetir esa consulta.

## Decisión

La revisión binaria 101 conserva cuerpo de 54 bits y control PWM de 17 bits simultáneos. Reemplaza la restricción de CLK exclusivamente para sincronización de ADR-0001 y la hipótesis de período común de ADR-0002. Se conservan la frontera de nodos y los restantes criterios compatibles.

A→B y B→A tienen períodos independientes y parten de 1 Hz. El receptor lee con el reloj recibido; su reloj de salida no determina esa captura. Un tick es un ciclo de la dirección. Para un multiplicador m de 1 Hz: f=m Hz y T=1/m s. Los logs incluyen dirección, trama, ciclo y tiempo.

Se serializan las negociaciones y se pausan nuevas emisiones de aplicación para drenar pendientes. El emisor de la dirección seleccionada coordina la gestión a 1 Hz. El PROBE prueba su período candidato; ACTIVE_ACK usa el período configurado de retorno, excepto candidato 1 Hz, que conserva gestión a 1 Hz. PING/ACK confirma reanudación. Sólo cambia el período seleccionado.

ACK/NACK de aplicación usan la frecuencia del retorno. Su timeout desde fin TX es 200*T_retorno+2 s, conservador para los perfiles 1–4 Hz del modelo. Una bajada tras dos fallos conserva el período de la otra dirección, los bits pendientes y los intentos consumidos.

El simulador ofrece dos selectores; 42 pruebas cubren también 16 pares de frecuencia por cuatro CRC, retorno lento y fallos asimétricos. No equivale a firmware ni medición física. Los 200 Hz mencionados por el auxiliar son un ejemplo, no un objetivo certificado.

No cambia la lista de componentes por esta revisión. Sigue pendiente medir PC817, sensores, pinmux y PRU. El funcionamiento temporal con menos medios no fue aprobado expresamente en esta respuesta; conservamos tres instalados y describimos el comportamiento degradado.

La revisión 100 se conserva como histórico. El documento de referencia actual es docs/protocolo/TRAMA3_Protocolo_y_Medios_Revision_101.docx.
