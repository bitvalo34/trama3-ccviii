# T01 — Respuestas del auxiliar y actualización manual

Registro actualizado: **2026-10-27**. Responsable: Erwin. Revisor: Adrián.

## Confirmaciones recibidas

| Pregunta | Estado | Evidencia |
|---|---|---|
| 1. Par aislado de reloj por sentido | Aprobada | Confirmación de Erwin en esta conversación |
| 2. Manguera y nylon como uniones físicas | Aprobada | Confirmación de Erwin en esta conversación |
| 3. PC USB sólo terminal; protocolo en BBB | Aprobada | Erwin comunica: “Para la 3 me confirmó que sí” |
| 4. Interpretación de sonido | Aprobada la interpretación de múltiples pulsos en BBB para obtener un bit por ciclo | Captura inicial y posterior confirmación de Erwin: “listo, dijo que está bien” |
| Revisión interna del ADR | Pendiente | Falta revisión de Adrián y resolución de observaciones |

La fecha anterior es la del registro, no una fecha inventada de respuesta docente. La captura muestra horas pero no fecha calendario. No se adjunta la conversación privada al repositorio público.

## Respuesta acústica y alcance

El auxiliar indica: “lo más simple”, “1 pulso es 1”, “no pulso 0”, “en el ciclo de reloj”.

Regla adoptada: un pulso acústico válido durante el intervalo correspondiente al símbolo representa 1; su ausencia representa 0. Es el pulso del canal de sonido, no el del reloj. Si falta el reloj, hay un error de sincronización y no se puede inferir un bit 0.

Aclaración posterior registrada el 27/10/2026: tras explicar que una emisión puede producir varios pulsos en el KY-037 y consultar si la BeagleBone puede interpretarlos como un único bit, Erwin confirma que el auxiliar lo acepta. Por tanto, se admite procesar esos pulsos por programación, manteniendo un solo 0 o 1 por ciclo. No se exige agregar un circuito que entregue exactamente un pulso físico por pitido. Los valores de umbral y las ventanas de v3.0 son hipótesis de implementación por validar, no parámetros medidos ni aprobados individualmente. La BOM se conserva; cualquier ajuste posterior dependerá de las pruebas.

Todavía hay que medir el sensor y definir cómo sus posibles múltiples flancos producen un único evento válido, cómo se rechaza ruido y cómo se rearma para el siguiente ciclo. La ventana exacta y el circuito o programa que lo resuelve pertenecen a T09/T11/T12. Probar también bits 1 consecutivos. No se declaró ninguna prueba realizada ni se modificó la BOM.

No hace falta repetir las cuatro preguntas. Si una implementación futura introduce una nueva ambigüedad, consultarla entonces con una propuesta concreta.

## Actualización manual del tracker

**El Excel no se modificó.** Hoja `Tracker maestro`, fila **6**.

| Campo | Valor recomendado |
|---|---|
| K6 — Estado | `En revisión` |
| M6 — Avance | `95%` (valor 0,95; estimación documental) |
| G6/H6 — Inicio/Fin | Conservar `13/10/2026`, planificación histórica |
| Fecha real de trabajo | `27/10/2026`, registrar en Q6; aún no declarar fecha de cierre |
| O6 — Entregable | `ADR-0001 actualizado con respuestas del auxiliar, diagrama, README y repositorio TRAMA3-CCVIII.` |
| P6 — Criterio | Conservar `Confirmar BBB con PRU interno, 4 canales y USB solo como terminal local` |
| Criterio alcanzado | Frontera y USB aprobados; regla acústica documentada; pendiente revisión interna |
| Bloqueo de cierre | Revisión de Adrián y registro final por Erwin; no faltan respuestas a las cuatro consultas |

Texto recomendado para **Q6 — Observaciones**:

> 15/10: usuario confirma luz, sonido y tensión en nylon; placa perforada soldable preferida por auxiliar. 27/10/2026: ADR-0001 y repositorio preparados. Erwin confirma aprobación docente de preguntas 1–3 (reloj por sentido, manguera/nylon y PC USB sólo terminal). Captura de pregunta 4 indica pulso = 1 y ausencia = 0 en el ciclo de reloj; tras aclaración adicional, Erwin confirma que el auxiliar acepta interpretar los múltiples pulsos del sensor mediante la BeagleBone para obtener un único bit por ciclo. Materiales sin cambios; umbrales, ventanas y rearme por validar en tareas posteriores. Pendiente revisión de Adrián. En revisión, 95% orientativo. Sin pruebas físicas; se conserva planificación del 13/10.

Tras revisión de Adrián y resolución de observaciones, Erwin podrá registrar T01 completada al 100 % con fecha real de cierre. No exigir pruebas de otras tareas para cerrar esta decisión documental ni darlas por hechas. T02 sigue siendo la siguiente tarea disponible; no se inició aquí.

## Aclaraciones posteriores: frecuencia e interferencias

El auxiliar pide variar frecuencia desde1 Hz hasta el máximo demostrado y responder a interferencias. Se incorpora [ADR-0002](../decisiones/ADR-0002-frecuencia-y-adaptacion.md) y [asignación al tracker](../planificacion/impacto-aclaraciones-frecuencia.md). No se atribuye aprobación específica de la nueva negociación ni se afirma que variar frecuencia por sí solo haga híbrida una transmisión. Revisión de Adrián debe incluir esta ampliación antes de cerrar T01. La recomendación95% es documental; las tareas de implementación continúan pendientes.
