# T01 — Respuestas del auxiliar y actualización manual

Registro actualizado: **2026-10-27**. Responsable: Erwin. Revisor: Adrián.

## Confirmaciones recibidas

| Pregunta | Estado | Evidencia |
|---|---|---|
| 1. Par aislado de reloj por sentido | Aprobada | Confirmación de Erwin en esta conversación |
| 2. Manguera y nylon como uniones físicas | Aprobada | Confirmación de Erwin en esta conversación |
| 3. PC USB sólo terminal; protocolo en BBB | Aprobada | Erwin comunica: “Para la 3 me confirmó que sí” |
| 4. Interpretación de sonido | Respondida; aplicar pulso/ausencia por ciclo | Captura aportada por Erwin |
| Revisión interna del ADR | Pendiente | Falta revisión de Adrián y resolución de observaciones |

La fecha anterior es la del registro, no una fecha inventada de respuesta docente. La captura muestra horas pero no fecha calendario. No se adjunta la conversación privada al repositorio público.

## Respuesta acústica y alcance

El auxiliar indica: “lo más simple”, “1 pulso es 1”, “no pulso 0”, “en el ciclo de reloj”.

Regla adoptada: un pulso acústico válido durante el intervalo correspondiente al símbolo representa 1; su ausencia representa 0. Es el pulso del canal de sonido, no el del reloj. Si falta el reloj, hay un error de sincronización y no se puede inferir un bit 0.

La respuesta resuelve la consulta, pero **no aprueba el esquema anterior de contar cierta cantidad de pulsos en dos ventanas**, ni obliga explícitamente a mantener un nivel estable todo el símbolo. El ADR cambia a presencia/ausencia de evento.

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

> 15/10: usuario confirma luz, sonido y tensión en nylon; placa perforada soldable preferida por auxiliar. 27/10/2026: ADR-0001 y repositorio preparados. Erwin confirma aprobación docente de preguntas 1–3 (reloj por sentido, manguera/nylon y PC USB sólo terminal). Captura de pregunta 4 indica pulso = 1 y ausencia = 0 en el ciclo de reloj; se sustituye el conteo acústico anterior por presencia/ausencia de evento, con acondicionamiento y rearme por validar en tareas posteriores. Pendiente revisión de Adrián. En revisión, 95% orientativo. Sin pruebas físicas; se conserva planificación del 13/10.

Tras revisión de Adrián y resolución de observaciones, Erwin podrá registrar T01 completada al 100 % con fecha real de cierre. No exigir pruebas de otras tareas para cerrar esta decisión documental ni darlas por hechas. T02 sigue siendo la siguiente tarea disponible; no se inició aquí.
