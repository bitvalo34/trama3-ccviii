# Protocolo matricial de TRAMA 3

Erwin y Adrián · CC VIII · Revisión 102 · 08/11/2026
Esta revisión sustituye el reparto físico de la revisión 101. Conserva los tres medios y la trama lógica de 54 bits, pero codifica cada pareja de bits en nueve observaciones distribuidas entre tres canales y tres ticks. La validación se realiza al terminar cada bloque de tres ticks, antes de completar la trama. El CRC final sigue siendo una comprobación adicional.
El diseño se propone para implementación y revisión académica. La foto de clase muestra GPIO, canales, frecuencia y campos de trama, pero no permite transcribir una matriz de recuperación completa. Las matrices que siguen son una propuesta propia: no se atribuyen al auxiliar ni se afirma equivalencia demostrada con su caso base.
Se conserva el contexto visible de clase: bits y bytes, transmisión por varios canales, reloj, SYN/SFD, DATA, CRC y confirmaciones. Se implementa explícitamente una relación algebraica entre canales. Falta contrastar esta relación con el desarrollo completo de clase antes de anunciar cumplimiento académico definitivo.
Alcance
La referencia ejecutable adjunta verifica la codificación, recuperación, límites y recepción de un cuerpo de trama. No sustituye firmware PRU ni un simulador de sesiones completas. El simulador HTML 101 queda histórico y no demuestra la revisión 102.
Diagrama funcional
Texto → bytes → trama lógica → parejas de bits → matriz codificadora
                           ↓
             C0 luz | C1 sonido | C2 nylon
                           ↓
Muestras simultáneas → matriz recibida → validación por bloque
                           ↓
         reconstrucción → CRC final → ACK o NACK
No se promete corregir cualquier error. Se especifican las condiciones de recuperación y los casos en que se descarta o retransmite. No se envía texto por el reloj.

# Modelo matemático y transmisión híbrida

Se opera en GF(2): la suma es XOR y el producto es AND. Para cada bloque k, d=(a,b)ᵀ contiene dos bits consecutivos de la trama. p=a XOR b. La matriz X tiene filas temporales y columnas de canal:
Tick relativo       C0 luz      C1 sonido      C2 nylon
0                   a           b              p
1                   b           p              a
2                   p           a              b
Al apilar X por filas, c=Gd. G es de tamaño 9×2 y sus filas son:
(1,0), (0,1), (1,1), (0,1), (1,1), (1,0), (1,1), (1,0), (0,1).
Cada tick transporta tres valores relacionados. La recepción debe capturar conjuntamente C0/C1/C2 en una lectura de R31 y procesar una decisión común de bloque; no son tres mensajes seriales independientes. La sucesión temporal de las tres filas y de los bloques proporciona la parte serial. La dependencia algebraica, captura vectorial y decisión conjunta proporcionan el procesamiento paralelo propuesto.
En hardware, las órdenes de salida pueden prepararse secuencialmente, pero su asentamiento debe concluir dentro del calendario común antes de la captura. No llamar simultáneas a llamadas de Linux. La lectura PRU obtiene todos los bits del puerto y aplica la máscara de los tres pines en una sola captura.
Validación mediante matriz H
Se toman las dos primeras coordenadas como pivotes. Para i=2,…,8, la fila i−2 de H tiene 1 en posición i, G[i,0] en posición 0 y G[i,1] en posición 1; las otras posiciones valen cero. H es 7×9. Por construcción HG=0.
Con nueve muestras disponibles, s=Hr (módulo 2) es el síndrome. Si s≠0 hay inconsistencia. Si s=0 se recibió una palabra del código; eso no prueba ausencia de errores que hayan transformado una palabra válida en otra.
Ejemplo con a=1 y b=0
X=[1 0 1; 0 1 1; 1 1 0]. Si desaparece C0, las otras columnas conservan a, b y sus relaciones. Si sólo queda C2, se observan [p,a,b]=[1,1,0] y se comprueba p=a XOR b. La solución reconstruye a=1 y b=0.
La letra A es 01000001. Se codifican sus parejas 01,00,00,01 dentro de DATA, además de los demás campos de la trama. No confundir esos cuatro bloques con la trama completa.

# Recuperación y límites demostrables

Las cuatro palabras posibles son G(00), G(01), G(10) y G(11). Cualquier pareja difiere en seis posiciones: distancia mínima dmin=6. Con las nueve observaciones, el decodificador puede corregir hasta dos inversiones de bits. Más errores pueden producir rechazo o corrección equivocada; no se declara protección universal.
Un borrado es una posición explícitamente no utilizable, representada por ⊥. Un cero válido no es un borrado. Nunca se deduce un canal muerto porque sus datos sean cero.
Para las posiciones disponibles S se forma G_S y se resuelve G_S d=r_S. Se necesita rango(G_S)=2. La referencia enumera las cuatro soluciones posibles, lo cual equivale a resolver este sistema binario de dimensión dos y permite mostrar cada candidato en el log.
Para combinar errores y borrados se calcula δ_S, la distancia mínima entre las cuatro palabras restringidas a S. Si δ_S=0 falta información: rechazo por rango. Si hay un candidato único a distancia e y 2e<δ_S, se acepta bajo el modelo de hasta floor((δ_S−1)/2) errores. En otro caso se rechaza. La condición general 2e+s<6 es suficiente, pero las columnas completas perdidas tienen estructura especial y se evalúan con δ_S.
Tres canales: 9 muestras, δ=6, corrige hasta 2 errores.
Dos canales completos: 6 muestras, δ=4, corrige hasta 1 error.
Un canal completo: 3 muestras, δ=2, recupera los dos bits y detecta una inversión; no corrige esa inversión.
Cero canales: δ=0, no se entrega información.
Con un canal superviviente, dos errores pueden convertir la terna en otra válida. Con tres canales, cuatro errores pueden acercar una palabra a otra. El banco de pruebas incluye un contraejemplo de esta última situación; el CRC de trama reduce riesgo residual, pero también tiene colisiones.
No se cambia el significado ni el orden de las columnas cuando falla un medio. Esta redundancia evita necesitar un mapa nuevo para reconstruir el bloque. Los tres transmisores siguen enviando el calendario fijo; no hay envío serial de rescate ni texto por CLK. Si se pierde un canal durante el bloque sin una indicación fiable de borrado, sus lecturas se tratan como posibles errores, no como borrados conocidos.
La recuperación con un solo medio es un modo degradado temporal. No se presenta como funcionamiento paralelo observable: la demostración del carácter híbrido se realiza con tres o dos medios y la aprobación académica de la degradación sigue pendiente.

# Formato físico y calendario

La trama lógica conserva SYN12 + SFD6 + CONTROL4 + DATA8 + CRC8 + SEQ8 + SID8 = 54 bits. No se cambia por conveniencia un formato que forma parte del enunciado. Se mantienen los tipos y semántica de sesión de 101, con versión negociada 110 (decimal 6); un extremo 101 es incompatible.
Cada trama completa, incluyendo ACK, NACK y gestión, usa 27 bloques de dos bits: 81 ticks de cuerpo y 243 muestras binarias físicas. Se añaden seis ticks de pilotos: 010101 simultáneamente en las tres líneas. Total de emisión: 87 ticks, de los cuales 81 codifican el cuerpo. Una guarda previa de 2T deja 89T de ocupación por emisión. No hay relleno oculto ni control auxiliar de 17 bits.
Los pilotos son adicionales a SYN/SFD. Cada entrada se compara con el patrón conocido; una discrepancia la excluye para esa emisión y deja evidencia de canal. Es una prueba conservadora, no una identificación infalible de avería. Un ruido que imite el patrón puede pasar. Cada trama vuelve a probar las tres entradas, incluso las antes excluidas.
El reloj marca inicio mediante pulso 0.6T y los otros ticks mediante 0.2T. Se conservan bandas 0.55–0.65T y 0.15–0.25T y período T±5 %. Los pulsos 0.4T de control 101 dejan de tener significado en 102. Un marcador tras al menos 2T de reposo inicia piloto 0. Un marcador inesperado o período inválido aborta la recepción; sólo se acepta un nuevo inicio tras guarda. CLK no transporta texto, mapa ni CRC adicional.
La lectura de datos ocurre a 0.8T en cada tick. Se prepara la fila al inicio y se captura cuando hayan concluido las transiciones. El período se elige para que L_preparación + L_asentamiento + J + margen ≤0.8T y el tiempo de captura/cálculo termine antes del siguiente tick. READY acredita que se ordenó la salida, no que el servo se asentó. Un incumplimiento aborta el intento.
Cada dirección empieza a 1 Hz. Por bloque se registran tres capturas y se valida al final de la tercera: a 1 Hz, una decisión cada tres segundos. Es validación de bloques durante la trama, no detección instantánea de cualquier bit erróneo. Puede acumularse un prefijo correcto, pero nunca entregarse un mensaje incompleto al usuario.
El instante de validación del bloque k está antes de (6+3(k+1))T respecto del inicio. La referencia usa ese límite como timeEnd; no pretende simular el instante exacto de ejecución PRU.
Una trama DATA a 1 Hz tarda 87 s de señal; con guarda y ACK de igual longitud, el intercambio limpio ocupa 178 s. Una letra en una sesión abierta necesita también START, LEN_LO, LEN_HI y END: 5 intercambios =890 s. Hola requiere 8 intercambios =1424 s. No incluye apertura de sesión, negociación ni reintentos. Estos tiempos sustituyen los de 101 y no son mediciones físicas.

# Estados y respuesta a fallos

Recepción: ESPERAR_GUARDA → PILOTOS → BLOQUES → CRC_Y_CONTEXTO → CONFIRMAR. En PILOTOS se crea la máscara local de observaciones utilizables, que no cambia el reparto del transmisor. BLOQUES ejecuta 27 decisiones de matriz. Una decisión irresoluble invalida el intento; se puede continuar observando hasta su fin para diagnóstico, sin aceptar el cuerpo.
Errores de tiempo o pérdida de reloj: descartar el cuerpo, limpiar muestras y esperar guarda e inicio. No sustituir ticks ausentes por ceros. Si se pierde la sincronización no se confirma una identidad tomada de datos dañados.
Bloque inconsistente: marcar rechazo y descartar intento. NACK sólo con SID/SEQ esperadas y contexto de sesión fiable; en otro caso silencio y timeout. Una corrección dentro del radio se registra con sus posiciones estimadas; no equivale a diagnosticar sensor defectuoso.
CRC o SYN/SFD inválidos: descarte final aunque los bloques hayan pasado. ACK ajeno, secuencia inesperada o versión incompatible: no avanzar. ACK perdido: retransmitir misma SID/SEQ; receptor deduplica y vuelve a confirmar. Reinicio: nueva sesión y entrega previa incierta, sin garantía de exactamente una vez entre reinicios.
Se mantienen cuatro intentos totales. No reiniciar este contador al variar frecuencia o recuperar medios. Al agotarlo, detener mensaje y mostrar fallo o entrega incierta; no bucle infinito de retransmisiones.
ACK/NACK y gestión usan la misma codificación matricial 102, nunca copias seriales independientes por medio. El receptor reserva prioridad a respuestas al terminar una emisión local ya iniciada. Se admite como máximo una trama de aplicación pendiente por dirección.
Timeout desde fin TX: 2×89T_retorno + margen de procesamiento medido, considerando una emisión de retorno ya iniciada y la respuesta. Margen inicial de ensayo: 2 s; confirmar en firmware. No usar el período de ida para esperar un retorno lento.
Frecuencias por sentido independientes. La negociación QUIESCE/PERIOD_PART/PREPARED/COMMIT_RATE/READY_RATE/PROBE/ACTIVE_ACK/PING de 101 mantiene sus estados y usa ahora emisiones matriciales. Todas sus cotas deben recalcularse con 89T por trama, cuatro intentos por etapa y colas acotadas. No reutilizar sin análisis el vigilante de 8000 s.
Para el primer montaje sólo se habilita 1 Hz. Los perfiles superiores y la negociación no quedan implementados por la referencia matricial. Ante un perfil no medido se rechaza su activación. El protocolo especifica esa extensión; no se anuncia como validada.
La prueba de un canal falla si no reproduce los pilotos; eso identifica C0/C1/C2, no la causa física. Los errores desconocidos posteriores se reflejan en síndrome/rechazo; no permiten afirmar automáticamente qué medio murió. La siguiente trama vuelve a sondear y puede reincorporarlo.

# Medios y progreso físico

Se conservan dos BBB Black, PRU, tres medios no convencionales y un canal de reloj por sentido. El USB es terminal local. No se agregan UART/SPI/I2C entre nodos. I2C local al MCP23017 sigue permitido por esta arquitectura, no transporta el mensaje entre equipos.
C0: LED rojo, transistor y módulo LDR dentro de tubo opaco. Representa presencia/ausencia de luz. C1: buzzer activo, transistor, manguera y detector digital; la PRU determina presencia durante su ventana, no interpreta cada oscilación del tono como bit. C2: SG90, nylon, resorte y final de carrera; se representan tensión/liberación. Los tres deben reproducir cada fila en el calendario común.
Se mantiene el pinout ensayado en T04: P8_11 CLK TX; P8_15 CLK RX; P8_16 sonido; P9_24 mecánico; P9_27 óptico. P9_14 para PWM de servo; P9_19/P9_20 para I2C local. T04 valida selección/restauración, no ondas ni sensores.
No se exige comprar otros sensores para realizar los ensayos iniciales a 1 Hz. Tampoco se garantiza que los actuales lo alcancen: medir ambas transiciones y rebote. Si un medio no cumple, revisar mecanismo, acondicionamiento o sensor antes de aprobar el perfil; no ocultarlo excluyéndolo en la demostración nominal.
Los módulos de sonido recibidos tienen placas distintas: documentar individualmente VCC/GND/DO y compatibilidad 3.3 V. No usar el orden de pines del otro módulo. La recepción de componentes no acredita su velocidad.
Primeros ensayos: circuitos separados, sin señales conectadas a BBB hasta comprobar niveles; 00/01/10/11 y 010101; simultaneidad acústica y servo; luego pilotos y bloques 00,01,10,11. Registrar cada lectura, frecuencia, matriz, máscara local, distancia y decisión. Tensión de entrada BBB: comprobar compatibilidad 3.3 V; no alimentar servo desde GPIO.
Instrumentación: conseguir acceso prestado a osciloscopio o analizador lógico de entrada compatible. El multímetro no comprueba ancho de pulsos ni rebote. Medir el peor retardo, jitter y error de ancho bajo carga en ambos sentidos. La frecuencia máxima por dirección será la mayor que cumpla la desigualdad temporal y los ensayos de error definidos; no el máximo de la PRU.
Compras sólo si una medida las justifica: receptor óptico más rápido si LDR limita; acondicionamiento acústico si DO produce falsas detecciones; mecánica de menor recorrido o actuador alternativo si SG90 no asienta. Elegir referencia y adaptar esquema después del diagnóstico, no comprar una pieza genérica sin revisar niveles, consumo y respuesta.
La codificación matricial no requiere nuevos componentes electrónicos por sí misma: cambia software, duración y procesamiento. Permanecen los faltantes de montaje y alimentación del inventario. La espuma de sellado no debe tapar el aire en la manguera. El nylon sigue siendo el enlace mecánico no conductor.

# Verificación reproducible y aprobación

Ejecutar desde software/matrices102: node reference.cjs. No requiere paquetes externos. resultados.json conserva la ejecución del banco. La referencia codifica cualquier cuerpo de 54 bits, aplica pilotos, bloquea medios a cero, inyecta inversiones y procesa cada bloque antes del CRC final.
Pruebas: las cuatro parejas de entrada; los 512 subconjuntos de observaciones; corrección dentro del radio permitido por la distancia de cada subconjunto; los 256 bytes en las ocho combinaciones de canales bloqueados; detección de un error cuando sólo queda un medio; corte posterior al piloto; contraejemplo de corrección equivocada fuera del radio.
La batería comprueba que perder los tres medios impide entregar. Con uno o dos medios perdidos desde pilotos, reconstruye exactamente la trama en las hipótesis del modelo. No usa el texto original para decidir en el receptor: éste sólo recibe muestras y la máscara obtenida de pilotos. El banco sí conoce el original para comparar resultados.
No implementado por esta referencia: sesiones completas, ACK y pérdida de ACK, negociación de frecuencia, captura continua del reloj, adaptación analógica, cargas Linux y firmware. El HTML 101 cubre su versión anterior de gestión, pero no valida automáticamente esta nueva capa física. La integración de ambos es trabajo pendiente explícito antes de una demostración integral.
Criterios de aceptación física: comprobar 100 bloques de cada pareja a 1 Hz en cada sentido sin pérdida; repetir con uno y dos medios interrumpidos desde pilotos y durante el cuerpo; registrar rechazos y recuperación, nunca descartar resultados desfavorables. El ensayo no demuestra probabilidad nula de error. No declarar frecuencia máxima con una sola trama limpia.
Correspondencia con lo exigido
Paralelo y serial: captura vectorial, codificación conjunta y orden temporal, sección 2.
Validación durante transmisión: decisión matricial cada tres ticks, secciones 3 y 4.
Validación de canales: pilotos por canal y registro de discrepancias, secciones 4 y 5.
Recuperación: sistema G_S y distancia del código observado, sección 3.
LOG a 1 Hz: matriz y decisión por bloque, secciones 4 y 7.
Capacidad máxima: modelo temporal más medidas, sección 6.
Caso base: correspondencia parcial con la pizarra; validación académica pendiente.
Consulta concreta al auxiliar
“Conservamos luz, sonido y nylon. Cada dos bits se convierten en una matriz de tres canales por tres ticks, con paridades XOR. Recibimos los tres canales juntos y validamos cada bloque antes de terminar la trama; podemos reconstruirlo si queda un medio, con menor capacidad frente al ruido. Empezamos a 1 Hz. ¿Este desarrollo matricial corresponde al fundamento del caso base que debemos extender? ¿Acepta el funcionamiento temporal con un solo medio como recuperación, mostrando el modo híbrido con los tres?”
Referencias
Avisos del auxiliar y fotografía de pizarra aportados por el equipo el 08/11/2026. La pizarra no contiene una matriz legible suficiente para atribuirle G.
V. Guruswami, notas de teoría de códigos, sección 3.1: recuperación por sistemas lineales y borrados. https://www.cs.cmu.edu/~venkatg/teaching/codingtheory/notes/notes7.pdf
La matriz binaria específica de esta revisión es diseño propio; sus distancias se verifican exhaustivamente con reference.cjs. No es Reed–Solomon ni se presenta como tal.
La revisión 101 conserva como antecedentes el esquema eléctrico y las fuentes de los componentes; los cambios físicos y temporales de esta revisión prevalecen sobre su reparto y control de reloj.