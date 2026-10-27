# Impacto de las aclaraciones en el tracker

**Consulta y propuesta: 2026-10-27.** Fuente: `CCVIII_Tracker_y_Cronograma.xlsx`, hoja `Tracker maestro`. El archivo se abrió en lectura; no se modificó. Todas las filas enumeradas están Pendiente y con avance0 en el archivo original, que aún no incorpora el trabajo documental de este chat.

## Qué se puede hacer ahora

Se actualiza la especificación mediante [ADR-0002](../decisiones/ADR-0002-frecuencia-y-adaptacion.md), aprovechando T01 como registro de requisitos. No se implementan T12/T16/T18/T25/T28 ni se acreditan ensayos. El tracker no tiene una tarea aislada llamada “transmisión híbrida”: el reparto ya corresponde a T17/T21 y su integración a T23/T24. La adaptación cruza varias tareas existentes.

La aclaración amplía el trabajo originalmente previsto en T28 (sólo dos perfiles y cambio desconectado). Revisar estimación de esfuerzo antes de iniciar esa implementación; no mantener ficticiamente el alcance anterior ni reprogramar fechas sin acuerdo. No se crea una tarea nueva ni se alteran dependencias en Excel.

## Ajustes propuestos por fila

Para actualización manual: conservar ID, responsables y dependencias; revisar Descripción(D), Entregable(O), Criterio(P) y Observaciones(Q) conforme a las ampliaciones. Las fechas históricas no son resultados de ejecución.

### T01 — Acordar frontera de equipo y reloj (fila 6)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **ninguna**.

Criterio actual: Confirmar BBB con PRU interno, 4 canales y USB solo como terminal local.

Ampliación propuesta: **Registrar aclaraciones de 1 Hz, máximo medido, combinación serial-paralela y adaptación. ADR-0002 y revisión de Adrián; no marcar implementación terminada.**

### T11 — Caracterizar sensores y simultaneidad (fila 20)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T53;T54**.

Criterio actual: 1000 bits/canal a T=250ms; errores <=1%; latencia p99 <150ms.

Ampliación propuesta: **Caracterizar 1 Hz y velocidades candidatas en ambos sentidos y simultáneamente. Mantener 1000 símbolos/medio y error crudo <=1%; medir latencia y definir márgenes por perfil. No exigir p99<150ms indiscriminadamente para todos los perfiles.**

### T12 — Validar PRU0 y fijar perfil físico (fila 21)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T53;T54**.

Criterio actual: 3 medios, conteo P8_16, latencia ARM_READY <=10ms y lecturas sin pérdidas.

Ampliación propuesta: **Validar perfil base1 Hz y catálogo de períodos ensayados; obtener f_max común medida, presupuestos de CLK/READY/ventanas y captura sin pérdidas. T250 es candidato, no única condición.**

### T13 — Definir interfaces y buffers en implementación futura (fila 22)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T11;T12**.

Criterio actual: Colas acotadas y contrato TX/RX documentado.

Ampliación propuesta: **Extender contrato con T_us, límites/calibración, q y estados de cambio; conservar buffers de mensaje, trama pendiente y deduplicación durante recuperación.**

### T15 — Preparar vectores de trama y CRC (fila 24)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T13**.

Criterio actual: 54 bits y 4 CRC cumplen vectores de referencia.

Ampliación propuesta: **Agregar vectores de versión010, controles E/F, fragmentos de período, CRC SMBUS de gestión y rechazo de versión001; conservar54bits/18ciclos y4CRC de datos.**

### T16 — Definir contrato ARM y PRU0 (fila 25)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T14**.

Criterio actual: Mensajes por índice y generación; fallo de deadline aborta TX sin frenar RX.

Ampliación propuesta: **Temporización parametrizada por perfil medido; READY indexado y captura concurrente; no escalar márgenes físicos automáticamente ni usar delay bloqueante.**

### T17 — Implementar ring buffer y mapper (fila 26)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T13;T15**.

Criterio actual: Sin pérdida ni duplicados al circular 256 entradas.

Ampliación propuesta: **Conservar mapper V[3k+j] y probar serialización/reconstrucción de54bits; congelar colas durante cambio sin perder ni duplicar descriptores.**

### T18 — Integrar driver PRU I2C PWM (fila 27)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T16**.

Criterio actual: Linux actualiza MCP/PWM; PRU emite reloj solo con READY vigente.

Ampliación propuesta: **Generación/captura a1 Hz y perfiles validados; PWM servo independiente; CLK sólo con READY vigente; cambio sólo entre tramas.**

### T22 — Ensayar carga Linux antes de integrar (fila 31)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T20**.

Criterio actual: CPU y servidor activos; ninguna trama falsa ante READY tardío.

Ampliación propuesta: **Medir todos los perfiles admitidos bajo carga Linux; rechazar perfiles sin margen, sin tramas falsas ante READY tardío.**

### T25 — Implementar Stop and Wait y duplicados (fila 34)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T23;T24**.

Criterio actual: ACK perdido no duplica entrega; límite 3 reintentos.

Ampliación propuesta: **Conservar límite3reintentos y SID/SEQ al bajar frecuencia; timeouts calculados por T; no resetear contador de intentos ni duplicar entrega tras cambio.**

### T26 — Ensayar interferencia y prioridad ACK (fila 35)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T23;T24**.

Criterio actual: NACK físico y timeout recuperan el mismo SEQ.

Ampliación propuesta: **Interferencia transitoria y persistente: diferenciar NACK de timeout, probar disparo de reducción y prioridad ACK; no inferir canal culpable sólo por CRC.**

### T28 — Implementar handshake de configuración (fila 37)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T26**.

Criterio actual: HELLO COMMIT idempotentes y CRC de arranque fijo.

Ampliación propuesta: **Implementar versión010, bootstrap1 Hz y transacción q de ADR-0002; fragmentos íntegros, confirmación de nuevo período, pérdida de respuestas y recuperación sin perfiles divergentes. Revisar máquina de estados antes de programar.**

### T29 — Montar servidor y chat en BeagleBone (fila 38)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T27**.

Criterio actual: Cuatro capas en BBB; PC es terminal web local, sin ruta A B.

Ampliación propuesta: **UI muestra frecuencia solicitada/efectiva/máxima validada, perfiles disponibles y modo manual/adaptativo. Petición local no modifica directamente CLK ni usa red A–B.**

### T30 — Añadir logs ARM PRU y medios (fila 39)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T28**.

Criterio actual: Distinguir error físico, deadline TX, desbordamiento RX y CRC.

Ampliación propuesta: **Logs por símbolo/canal y por transición de frecuencia: T medido, q, motivo, SID/SEQ, CRC, intentos y estado; sin bloqueos para animar UI.**

### T35 — Preparar guion de pruebas integrales (fila 44)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T33**.

Criterio actual: Casos de aceptación listos y mensajes cortos definidos.

Ampliación propuesta: **Agregar casos de1 Hz, barrido, f_max, transición manual, adaptación y pérdidas de negociación al guion, con tiempo previsto real.**

### T37 — Integrar chat bidireccional y configuración (fila 46)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T35;T36**.

Criterio actual: Dos usuarios envían simultáneamente sin duplicados.

Ampliación propuesta: **Cambio coordinado con dos usuarios; conservar mensajes/duplicados y evitar cambios simultáneos contradictorios.**

### T38 — Ejecutar matriz física de ruido y fallos (fila 47)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T35;T36**.

Criterio actual: CRC NACK retransmisión ACK observado y registrado.

Ampliación propuesta: **Demostrar error físico → recuperación/reducción coordinada → retransmisión → ACK; bloqueo persistente produce error acotado; no exigir que bajar velocidad elimine cualquier interferencia.**

### T39 — Pruebas prolongadas y correcciones (fila 48)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T37;T38**.

Criterio actual: 100 frames/dirección, 4 CRC, 0 duplicados entregados.

Ampliación propuesta: **Ejecutar campañas100tramas/dirección por perfiles aceptados, gestión con pérdidas y4CRC; registrar errores detectados, éxito final y ausencia de duplicados observados.**

### T43 — Revisar logs y evidencia de requisitos (fila 52)

Responsable: **Erwin**; revisor: Adrián. Dependencias: **T41**.

Criterio actual: Cada requisito enlazado a evidencia.

Ampliación propuesta: **Relacionar requisito híbrido con log de posiciones por medio/ciclo, y adaptación con trazas de ambos nodos a igual perfil y q.**

### T46 — Ensayar demostración física (fila 55)

Responsable: **Adrián**; revisor: Erwin. Dependencias: **T44**.

Criterio actual: Demostración de 2 direcciones e interferencia en tiempo disponible.

Ampliación propuesta: **Demostrar a1 Hz, aumentar a un perfil superior validado y mostrar interferencia/recuperación; declarar máximo medido y duración de negociación sin prometer1kHz.**

## Secuencia y estado

La siguiente ejecución física disponible sigue siendo T02, inspección de ambas BBB, sin dependencias; no se realiza aquí. T04 sigue a T02 y T06 a T04. T11/T12 requieren T53/T54; T16 requiere T14; T18 requiere T16; T25/T26 requieren T23/T24; T28 requiere T26; T30 requiere T28; T38 requiere T35/T36. No ejecutar implementación futura saltándose esas condiciones.

T01 puede conservar recomendación **En revisión, 95% documental orientativo**, ahora con revisión de Adrián incluyendo ADR-0002. Este porcentaje no aumenta por escribir trabajo de diseño de otras tareas. Actualización sugerida en Q6: “27/10: aclaraciones de frecuencia desde1 Hz, máximo medido y adaptación incorporadas en ADR-0002; implementación y pruebas asignadas a sus tareas, sin avance físico acreditado. Pendiente revisión interna”. Conservar observaciones históricas y aprobaciones previas.

El estado de las demás tareas no cambia por este documento. No declarar máxima frecuencia ni tiempos finales hasta disponer de evidencia.
