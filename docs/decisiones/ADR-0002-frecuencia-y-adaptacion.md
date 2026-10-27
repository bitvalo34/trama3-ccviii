# ADR-0002 — Transmisión serial-paralela, frecuencia configurable y adaptación

**Registro:** 2026-10-27. **Estado:** especificación propuesta para revisión de Erwin y Adrián; sin implementación ni validación física. El usuario autoriza ahora actualizar el protocolo. Esta decisión amplía el alcance documental de T01 y define trabajo posterior; no acredita esas tareas como ejecutadas.

## 1. Evidencia y precedencia

El auxiliar pide poder bajar a **1 Hz** para observar registros, subir hasta el máximo declarado por el equipo y comprobar comportamiento ante interferencias. “1 kHz” aparece como ejemplo hipotético, no como mínimo exigido ni capacidad medida. También pide una transmisión híbrida. Fuentes: capturas aportadas por Erwin `codex-clipboard-1b643b4e-880c-4aa5-870b-6c46fd6bdb23.png`, `codex-clipboard-f94ec8af-16a4-4a6e-b250-25c629813050.png` y `codex-clipboard-288d611f-af0c-4dd8-a567-ab216a7107bb.png`. Registro de hoy; fecha calendario de mensajes no visible. No se publican capturas privadas.

Este ADR prevalece sobre v3.0 y ADR-0001 **sólo** en frecuencia, negociación, temporizadores y adaptación. Conserva medios, pines, frontera USB, cuatro capas, tres datos más reloj por dirección y marco de 54 bits. No modifica presupuesto ni originales PDF/Excel.

Cambios explícitos respecto a v3.0: se elimina la restricción exclusiva a T250/T500; bootstrap pasa a 1 Hz; se introduce negociación de período y recuperación dentro de la sesión. Ya no se excluye la adaptación automática de frecuencia. Cambian semántica de gestión y versión de protocolo; no fingir compatibilidad de software antiguo.

## 2. ¿Es híbrida?

Descripción precisa: **transmisión serial-paralela síncrona sobre tres medios heterogéneos**. Para vector de trama V[0..53], ciclo k de 0 a 17:

- C0 transmite V[3k]; C1 transmite V[3k+1]; C2 transmite V[3k+2].
- En un ciclo se transportan tres posiciones en paralelo; cada canal transporta su secuencia de posiciones a lo largo del tiempo.
- RX reconstruye V[3k+j] desde canal j. No identifica un byte completo con un único pulso.

Ejemplo de posiciones, no nueva trama:

| Ciclo k | Luz C0 | Sonido C1 | Nylon C2 |
|---|---|---|---|
| 0 | V0 | V1 | V2 |
| 1 | V3 | V4 | V5 |
| 2 | V6 | V7 | V8 |

Hay elementos seriales y paralelos; eso justifica “híbrida” en este sentido descriptivo. Muchos enlaces paralelos también secuencian palabras: no se presenta una nueva categoría física ni se afirma que el reloj variable elimine esa clasificación. R1, PDF oficial pp. 2–3, plantea transportar bytes con pocas líneas sin ajustarse estrictamente a serial o paralelo convencional. La aceptación académica de nuestro mecanismo exacto se demuestra con este reparto, reconstrucción, temporización y recuperación; la captura no constituye aprobación detallada de este ADR.

No hace falta cambiar el mapper para aparentar originalidad. No introducir reparto oportunista, tiempos independientes por medio ni supresión de un canal: necesitarían otro calendario y acuerdo de recepción.

## 3. Rango de frecuencia y materiales

Frecuencia de símbolo f = 1/T. El usuario puede solicitar un período entero en microsegundos **T_us entre T_min_validado y 1 000 000**, sujeto a aceptación de ambos nodos. La interfaz acepta Hz, convierte redondeando el período hacia arriba y muestra frecuencia efectiva, sin ocultar cuantización.

- 1 Hz / T=1 s: requisito de demostración y perfil de arranque/recuperación, **a validar físicamente**.
- 2 Hz / T=500 ms y 4 Hz / T=250 ms: candidatos históricos, no velocidades certificadas.
- f_max: máximo común medido de ambos sentidos con todos los medios activos y carga Linux. No se declara hoy un número.
- Aceptar sólo períodos con calibración válida. Se puede usar una lista de frecuencias ensayadas; no extrapolar toda una banda porque sus extremos pasaron. La UI rechaza frecuencias no verificadas y muestra la lista admitida.
- Ambos sentidos usan el mismo período de sesión para simplificar recuperación. Sus relojes físicos siguen siendo independientes en fase y generados por cada PRU, no un reloj eléctrico compartido.

Materiales actuales conservados. Servo/mecanismo y LDR pueden limitar la frecuencia; no atribuir todo el límite al software o al sonido. PRU más rápida no acelera la mecánica. Si ni 1 Hz funciona, no se declara conforme: corregir montaje/sensor antes de integración. Una sustitución se justifica con mediciones; no se compra por esta aclaración.

## 4. Temporización sin esperas añadidas arbitrarias

Cada perfil ensayado contiene T, plazo READY, retardo antes del flanco de captura, ancho CLK, ventana de cada receptor, margen y tolerancia de jitter. Debe cumplir:

`plazo_READY + peor_retardo_actualizacion + asentamiento_medio + margen <= instante_CLK`

`instante_CLK + ventana_RX_max + margen_final <= T`

Además CLK alto/bajo debe permitir recepción fiable por PC817. READY significa órdenes completadas, no servo asentado. Sin READY vigente, abortar TX sin paralizar RX. Para mantener actuación simultánea, la captura de sonido ocurre dentro del mismo ciclo y no añade un sleep posterior a los demás medios.

T=250 ms conserva como candidato de laboratorio el calendario anterior (READY <10 ms, CLK a190 ms); **no se divide todo proporcionalmente para velocidades mayores**. Los tiempos físicos se miden y la configuración se rechaza si no caben. Al bajar a 1 Hz se puede ampliar el reposo entre símbolos sin esperar innecesariamente para tomar una lectura ya estable. PWM servo continúa en su frecuencia propia prevista; f del protocolo no modifica el PWM ni el tono del buzzer.

Sonido: procesamiento por BBB admitido según Erwin. Durante la ventana del símbolo, pulsos válidos de una emisión producen un solo bit de presencia. Empezar con detección simple y añadir filtrado/conteo sólo si las mediciones lo requieren. Caracterizar ruido, 00/01/10/11 y memoria entre ventanas. Registrar pulsos puede servir al diagnóstico sin imponer esperar N pulsos. No convertir falta de CLK en bit 0.

## 5. Formato y versión

Conservar SYN12 + SFD6 + Control4 + DATA8 + CRC8 + SEQ8 + SID8 =54 bits, 18 ciclos, orden MSB primero y cálculo canónico de CRC de v3.0. No reusar un tipo reservado sin cambiar versión.

Nueva versión de configuración **010** (v3.0 usaba 001). HELLO conserva bits7–6 CRC y bit5 encoding; bits4–3 deben ser 00 y significan arranque a1 Hz en versión010. Un nodo antiguo o versión desconocida se rechaza visiblemente, sin adivinar el significado de bits. HELLO/HELLO_ACK/COMMIT/READY existentes siguen creando una sesión nueva sólo desconectados; ahora usan siempre T=1 s y CRC SMBUS. No borran una sesión activa por recibir un HELLO ajeno.

Después del arranque, un cambio de velocidad **conserva SID, SEQ de datos, buffers y filtro de duplicados**. No se reinicia el mensaje para esconder un fallo. Se reservan dos controles nuevos, usando los tres medios y el reloj igual que toda trama:

| Control | Nombre | DATA | SEQ |
|---|---|---|---|
| 0xE | PERIOD_PART | bits7–5 índice 0..3; bits4–0 fragmento de 5 bits | ID de transacción de cambio q |
| 0xF | RATE_CTRL | código de gestión siguiente | q; 0 sólo para petición de B |

T_us se transmite en cuatro fragmentos: `(T_us >> (15-5*i)) & 31`, i=0..3. Reconstrucción en orden MSB; rango representable 20 bits y máximo admitido 1 000 000. Índice4..7, T=0, fragmentos contradictorios o perfil no calibrado invalidan la propuesta. Un duplicado idéntico es idempotente. El receptor no aplica nada con bitmap incompleto. Cada fragmento lleva CRC y SID; cuatro fragmentos deben pertenecer al mismo q activo. No mezclarlos con una transacción anterior.

RATE_CTRL: 0x01 QUIESCE, 0x02 QUIESCED, 0x03 PREPARED, 0x04 COMMIT_RATE, 0x05 READY_RATE, 0x06 PROBE, 0x07 ACTIVE_ACK, 0x08 REJECT. Peticiones B con q=0: 0x10 REQUEST_SLOWER y 0x11 REQUEST_MANUAL; en esta versión B no elige el valor manual, se selecciona en terminal A. Otros valores se rechazan. 0xE/0xF usan CRC SMBUS, no ARQ de datos ni avance de SEQ de aplicación. Excepto PROBE/ACTIVE_ACK, se transmiten a1 Hz. La identificación es por Control, SID y q, no por número de pulsos CLK.

A es coordinador. Asigna q=1..255, estrictamente creciente dentro del SID; no se reutiliza tras rechazo. Antes de agotar q se requiere cierre explícito y nueva sesión, sin mensajes ambiguos. B mantiene última transacción y respuestas para duplicados. No hay dos cambios simultáneos; peticiones se agrupan o esperan.

## 6. Cambio coordinado de frecuencia

Secuencia propuesta, obligatoria para cambio manual y automático:

1. **Pausar admisión de nuevos envíos.** Finalizar la trama física en curso; no cortar una tripleta ni cambiar T en mitad de una trama. Guardar trama pendiente, contadores, SEQ y reensamblado. Antes de gestión no se deben seguir generando ACK o datos antiguos en segundo plano.
2. **Encuentro a1 Hz.** Tras guarda de2*max(T_actual,1s), A manda QUIESCE(q); B termina como máximo su trama en curso, congela colas y responde QUIESCED(q). Si la velocidad actual impide el control, el timeout de enlace conduce a modo recuperación que escucha1 Hz. B también puede entrar en recuperación por sus timeouts y emitir REQUEST_SLOWER a1 Hz; A termina su trama actual y coordina QUIESCE. No basar recuperación en recibir correctamente una petición a la velocidad que acaba de fallar. El detector reconoce entrenamiento SYN/SFD a1 Hz; durante transición puede aceptar el perfil actual o1 Hz, pero nunca cambia una trama parcialmente recibida. Un tren de CLK sin trama de gestión íntegra y CRC válido no autoriza reconfigurar.
3. **Preparar.** A envía las cuatro PERIOD_PART a1 Hz. B verifica perfil local, rango, versión y q (incluida su calibración RX/TX y el presupuesto temporal del perfil); devuelve PREPARED o REJECT. A conserva su perfil anterior. Un grupo incompleto se reenvía íntegro con el mismo q; no activa frecuencia.
4. **Comprometer.** A manda COMMIT_RATE; B guarda el candidato y devuelve READY_RATE todavía a1 Hz. B queda preparado para recibir candidato y control a1 Hz, pero no inicia mensajes propios en la frecuencia candidata.
5. **Probar activación.** Tras READY_RATE y guarda de `2*max(T_anterior,T_nuevo,1s)`, A manda PROBE(q) con el período candidato. B sólo responde ACTIVE_ACK(q) en ese período tras recibir PROBE íntegro. A confirma cambio tras ACTIVE_ACK válido. Esta prueba comprueba ambas direcciones en la frecuencia nueva. B puede atender retransmisiones de PROBE sin borrar estado; no libera datos de aplicación por un ACK de gestión.
6. **Reanudar.** A retoma la trama pendiente con su SID/SEQ originales. B permite tráfico propio tras observar la primera trama ordinaria válida de A en el candidato. Si A no tiene trama pendiente, envía PING existente como primera trama ordinaria. La deduplicación evita que la retransmisión de algo aceptado antes del cambio se entregue dos veces. La trama pendiente mantiene bits/CRC de datos; sólo cambia su calendario físico.

Pérdida de READY_RATE: A repite COMMIT_RATE a1 Hz, B vuelve a responderlo. Pérdida de ACTIVE_ACK: A repite PROBE en candidato, B repite ACTIVE_ACK. Ambos conservan recepción de gestión a1 Hz durante transición/recuperación; no suponer que el último ACK vuelve atómico un enlace falible. Si se pierde el estado de una BBB por reinicio, detener con error y nueva sesión: no prometer entrega exactamente una vez entre reinicios.

Cada etapa tiene timeout y hasta tres reintentos de gestión; después, estado visible RECOVERY_1HZ o LINK_FAULT, sin éxito falso. Un watchdog total de cambio de **1200 s** limita una negociación atascada; tráfico ajeno no lo reinicia. Es cota provisional generosa para la gestión lenta, que T28 debe verificar con pruebas de pérdida. Si el par no confirma el mismo q, no reanudar datos. Un extremo activo sin progreso por fallo de su par vuelve a recuperación tras timeout, conservando estado de sesión; al recuperar1 Hz se inicia un q nuevo. No hacer rollback silencioso que deje nodos en períodos distintos.

Durante transición congelar el timeout de reensamblado de aplicación, con el watchdog anterior como límite; al salir renovar el timeout normal. Registrar transacciones incompletas y motivo. El cambio es deliberadamente entre tramas y puede pausar un mensaje; no necesita descartarlo ni exigir reenviar manualmente todo su texto.

## 7. Política de adaptación y temporizadores

**Modo demostración manual:** A solicita una frecuencia validada; ambos confirman mediante §6. Se permite 1 Hz aunque sea lenta. Los registros no agregan pausa bloqueante por símbolo.

**Modo adaptativo:** después de dos fallos consecutivos de una misma trama de datos (NACK o timeout), suspender nuevos intentos y proponer el siguiente escalón menor validado en ambos nodos, nunca menos de1 Hz. B pide reducción por gestión; A coordina. Mantener el límite previo de cuatro intentos de datos (inicial+3), sin reiniciarlo cada vez que cambia la velocidad. Si se agota, LINK_FAULT. Si falla gestión o ya está a1 Hz, no entrar en un bucle infinito. No subir automáticamente: aumento manual y comprobado evita oscilación. Umbral de dos fallos es política de diseño, no resultado experimental.

No deducir el medio culpable de CRC: sólo identifica una trama dañada. Diagnóstico por línea y sensores puede orientar, sin alterar un bit para forzar CRC. Reducir velocidad puede ayudar a tiempos insuficientes o errores transitorios; **no repara un canal tapado, roto o sin alimentación**. Mantener tres medios; fallo persistente termina en pausa/error y requiere retirar la causa.

Con T común, duración de una trama =18T; con guarda mínima2T, servicio físico estimado20T. Mantener ACK prioritario sin interrumpir trama en curso. Timeout de ACK contado desde fin TX:

`tau_ACK = max(48*T, 40*T + margen_procesamiento_medido)`

Margen inicial de presupuesto =2 s, pendiente de medir bajo carga. A1 Hz resulta48 s y a4 Hz12 s. Para frecuencias mayores no reducir por debajo del procesamiento medido. Timeout de gestión con hasta cuatro tramas de parámetros: `tau_gestion = max(120 s, 100*T_boot + margen_procesamiento_medido)`, contado según etapa; reiniciar sólo ante progreso válido de esa transacción. Timeout normal de reensamblado `max(480*T, 2*tau_ACK)` renovado por progreso válido; suspendido durante cambio acotado. Guarda de SID/épocas antiguas `max(60 s, 240*T)` tras vaciar transmisiones; no confundirla con separación normal2T.

Todo temporizador se calcula al aceptar un perfil y queda registrado. Jitter5 ms y plazo READY10 ms de v3.0 no son constantes válidas a cualquier frecuencia: cada perfil debe justificar sus límites.

## 8. Rendimiento y observabilidad honestos

Ritmo bruto de datos físicos =3f bits/s; una trama54bits tarda18/f segundos, antes de guarda. No confundir Hz con bytes/s: una DATA contiene sólo8bits útiles, más tramas de control/ACK. A1 Hz la trama ocupa18 s y una DATA+ACK con guardas, idealmente40 s sin concurrencia ni procesamiento. A4 Hz son4,5 s y10 s respectivamente. 1 kHz sería18 ms por trama, pero **no se afirma que este hardware lo soporte**.

La negociación a1 Hz es lenta: QUIESCE/QUIESCED, cuatro parámetros, PREPARED, COMMIT_RATE y READY_RATE suman nueve tramas, aproximadamente180 s con guardas, más PROBE/ACTIVE_ACK y márgenes. Es sobrecarga de cambio, no delay añadido a cada bit. Se declara para evitar una promesa de adaptación instantánea. Optimizar gestión en el perfil actual puede estudiarse después; no incorporarlo sin rediseñar recuperación y probar pérdidas.

Logs mínimos: tiempo monotónico, dirección, SID/SEQ, Control, índice de símbolo, posiciones y bits C0/C1/C2, CLK previsto/observado, período solicitado/aceptado/medido, perfil, pulsos acústicos diagnósticos, READY y deadline, CRC, resultado, intentos, q/estado de cambio y causa. En UI: f solicitada, f efectiva, f máxima validada, modo y motivo del cambio. No afirmar diagnóstico de medio sólo por CRC.

## 9. Pruebas requeridas, todavía no ejecutadas

| Caso | Criterio verificable |
|---|---|
| Reparto serial-paralelo | 54 posiciones reconstruidas en18ciclos; 256 valores DATA y cruces de campos, con log por canal |
| 1 Hz | Ambos sentidos y todos los medios; no timeout falso por usar constantes de4 Hz |
| Barrido | Frecuencias ensayadas desde1 Hz; al menos1000símbolos/medio y100tramas/dirección en candidatos aceptados; registrar errores, reintentos y latencia |
| f_max | Mayor frecuencia que cumple criterios con carga Linux y simultaneidad; cero entregas corruptas observadas, sin presentar CRC8 como garantía absoluta |
| Interferencia transitoria | Perturbación física produce CRC/NACK o timeout, conserva SEQ, recuperación y una sola entrega |
| Adaptación | Dos fallos disparan propuesta inferior; acuerdo q y período en ambos; retransmisión conserva SID/SEQ; contador de intentos no vuelve a cero |
| Cambio manual | 1 Hz → perfil superior →1 Hz, sin cambio dentro de trama ni borrado de mensaje |
| Pérdidas en negociación | Perder cada fragmento, READY_RATE y ACTIVE_ACK; duplicados idempotentes; sin mezcla de q ni datos durante desacuerdo |
| Fallo persistente | Bloqueo de medio/reloj concluye en error acotado, sin éxito inventado ni enlace convencional |
| Reinicio | Nueva sesión visible; no prometer deduplicación a través de pérdida de estado |

Conservar criterio inicial de error crudo <=1 % como filtro de caracterización, pero documentar también tasa de fallo de trama y éxito final tras ARQ. No basta con cumplir BER para asegurar entrega: errores correlacionados pueden agotar reintentos. p99<150ms pertenece al candidato250ms; otros perfiles necesitan presupuesto propio y recuento de incumplimientos, no extrapolación.

## 10. Correspondencia con el tracker

Archivo consultado sin modificar: `CCVIII_Tracker_y_Cronograma.xlsx`, hoja `Tracker maestro`. Todas estas tareas continúan Pendiente en ese archivo. Este trabajo produce especificación anticipada, no ejecución de firmware/pruebas ni reprogramación de horas.

La tabla de [impacto por tarea](../planificacion/impacto-aclaraciones-frecuencia.md) conserva responsables, dependencias y criterios originales y propone los ajustes exactos. T01 registra frontera y requisitos; **T12 fija perfiles medidos; T16/T18 implementan tiempos; T25/T26 recuperación; T28 negociación; T30 logs; T38 valida adaptación**. No es razonable cargar toda esta implementación a la hora-persona de T01.

## 11. Referencias y estado final

PDF oficial pp.2–4: mecanismo híbrido, sincronización y pocas líneas; v3.0 caps.5A,9–11,14–19: reparto, trama, tiempos, ARQ, configuración y pruebas. Las nuevas capturas justifican1 Hz/f_max y respuesta a interferencias. La negociación, umbrales y extensión de versión aquí definidos son **propuestas de ingeniería**, no instrucciones literales del auxiliar.

No afirmar que el auxiliar aprobó el formato de gestión nuevo ni que ya se probó. Erwin/Adrián deben revisar el ADR y T28 debe verificar estados y pérdidas antes de firmware. No hay nueva compra obligatoria ni protocolo ejecutable en este commit.
