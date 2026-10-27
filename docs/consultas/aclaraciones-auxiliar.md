# T01 — Consultas y actualización manual

Fecha: **2026-10-27**. Responsable Erwin; revisor Adrián. **Preguntas 1 y 2 aprobadas por el auxiliar, según confirmación de Erwin en esta conversación.** Fecha de registro: 2026-10-27; no se atribuye una fecha ni cita literal a la respuesta original. Preguntas 3 y 4 pendientes; nuevo borrador preparado, no enviado.

## Mensaje para copiar en WhatsApp

Hola, auxiliar. Gracias por confirmar lo del reloj y el uso de la manguera y el nylon. Sólo nos quedan dos dudas:

**3. Uso de la computadora:** ¿Podemos conectar una computadora por USB a cada BeagleBone sólo para escribir y leer los mensajes? Todo el protocolo funcionaría en las BeagleBone, y los mensajes entre los dos equipos viajarían únicamente por los medios del proyecto.

**4. Lectura del sonido:** El sensor puede dar varios pulsos cuando escucha el sonido. ¿Podemos programar la BeagleBone para contar esos pulsos y decidir si recibió un 0 o un 1, o el circuito debe entregar directamente un 0 o un 1 estable?

## Registro de confirmaciones

La réplica general ya es obligatoria según el PDF p. 8. Erwin confirma que el auxiliar aprobó la pregunta 1 (par aislado y reloj por sentido) y la 2 (manguera y nylon). Esta aprobación del diseño no equivale a validación física. La pregunta acústica resuelve la ambigüedad reconocida en v3.0 cap. 8 y no cambia el medio.

| Confirmación | Estado | Evidencia para cerrar |
|---|---|---|
| Revisión de Adrián | Pendiente | Fecha, observaciones y resolución |
| Par aislado y reloj por sentido | Aprobado por el auxiliar | Confirmación de Erwin en esta conversación, registrada el 27/10/2026 |
| Manguera y nylon | Aprobado por el auxiliar | Confirmación de Erwin en esta conversación, registrada el 27/10/2026 |
| PC USB terminal local | Pendiente | Respuesta y condiciones |
| Conteo acústico | Pendiente | Conteo admitido o exigencia de nivel estable |

Registrar aquí las respuestas de las preguntas 3 y 4 cuando existan. No inferir aprobación del silencio. Si una condición cambia arquitectura, actualizar ADR y evaluar impacto antes de cerrar T01. Las pruebas físicas pertenecen a otras tareas.

## Actualización manual del tracker

**El Excel no se modificó.** Hoja `Tracker maestro`, fila **6**.

| Campo | Valor recomendado |
|---|---|
| K6 — Estado | `En revisión` |
| M6 — Avance | `85%` (valor 0,85; estimación documental, no medición de horas) |
| G6/H6 — Inicio/Fin | Conservar `13/10/2026`, fechas planificadas históricas |
| Fecha real de trabajo | `27/10/2026`; registrar en Q6 porque no hay columna de fecha real |
| O6 — Entregable | `ADR-0001-frontera-nodos-y-reloj.md, README y repositorio local TRAMA3-CCVIII; diagrama y consulta al auxiliar preparados.` |
| P6 — Criterio de aceptación | Conservar `Confirmar BBB con PRU interno, 4 canales y USB solo como terminal local` |
| Criterio alcanzado | Frontera, reparto funcional, cuatro canales por sentido y USB local documentados; confirmación definitiva pendiente |
| Bloqueos de cierre | Revisión de Adrián y respuestas del auxiliar sobre USB e interpretación acústica |

Texto exacto recomendado para **Q6 — Observaciones**, conservando antecedente:

> 15/10: usuario confirma luz, sonido y tensión en nylon; placa perforada soldable preferida por auxiliar. 27/10/2026: ADR-0001 y estructura local preparados; dos BBB con PRU0 interno, C0/C1/C2 más CLK por sentido y USB sólo local documentados. Revisión documental realizada, sin pruebas físicas. Erwin confirma aprobación docente de las preguntas 1 y 2: par de reloj por sentido y uniones manguera/nylon. Pendientes revisión de Adrián y aprobación de frontera USB e interpretación acústica. Mensaje preparado, no enviado. Avance orientativo 85%; no cerrado. Repositorio local preparado; remoto creado por Erwin. Se encontró identidad Git y autenticación existentes en Ubuntu/WSL para publicar la documentación. Se conserva planificación del 13/10.

No registrar fin real hasta aceptación ni cambiar horas estimadas, dependencias u otras filas. El 85 % reconoce el entregable disponible sin atribuir acuerdo humano. Un 90 % sería razonable tras revisión interna si sólo resta respuesta externa. T02 es la siguiente tarea disponible; no se inició.
