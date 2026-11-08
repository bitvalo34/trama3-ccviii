# TRAMA 3 revisión 101

Extracto textual; tablas y diagramas completos en el documento Word.

Protocolo y medios de transmisión de TRAMA 3

Erwin y Adrián
CC VIII
7 de noviembre de 2026 · Revisión 101

Conservamos la trama lógica de 54 bits y proponemos quitar los 40 ciclos previos de la revisión 011. El reloj mantendrá el ritmo y llevará información de control mediante el ancho de sus pulsos. La luz, el sonido y el nylon siguen transportando el mensaje. Si uno o dos medios dejan de responder, reorganizamos el siguiente intento por los disponibles.

El auxiliar aclaró el 7 de noviembre de 2026 que los pulsos pueden variar si el protocolo lo define, y que la lectura sigue el reloj recibido desde el otro dispositivo. Adoptamos la modulación por ancho de pulso bajo ese criterio y velocidades independientes por sentido. La revisión 101 queda como base de implementación; las señales, la frecuencia máxima y el rendimiento físico siguen pendientes de medición. No atribuimos al auxiliar la validación de nuestros campos, tolerancias ni pruebas de software.

1 Arquitectura de los dos nodos

Cada nodo tendrá una BeagleBone Black, una placa perforada soldable de interfaz y un transmisor y receptor de cada medio. Para enviar de A hacia B utilizaremos un LED, un buzzer y un servo en A, con una LDR, un micrófono y un final de carrera en B. El retorno repite esos componentes en el sentido contrario. Por tanto, son cuatro canales por sentido y ocho canales dirigidos en total.

Figura 1. Canales de datos y reloj en ambos sentidos. Cada flecha de retorno representa un montaje independiente.

El USB conecta cada computador con su placa como terminal local. El texto y las confirmaciones cruzan los medios del proyecto. Un ACK viaja como copia completa por cada medio de retorno. Para confirmarlo basta recibir una copia íntegra, aun cuando la ida y la vuelta conserven medios distintos.

Usaremos las dos BBB que ya tenemos. No hace falta agregar ESP32 al diseño: la BBB cuenta con el procesador ARM para Linux y con procesadores internos PRU para las tareas de tiempo preciso. Esto evita introducir otro controlador y otra comunicación interna.

2 Organización del protocolo

Figura 2. Funciones de las capas. Las tripletas de la capa física corresponden al caso en que se usan las tres líneas.

La aplicación recibe el texto y muestra su entrega. Presentación lo convierte en bytes UTF-8 o Windows-1252. Enlace agrega sesión, secuencia y CRC y espera confirmación. La capa física anuncia el mapa mediante el reloj, distribuye los bits entre los medios y reconstruye su orden en el receptor.

ARM/Linux prepara las salidas. Por I2C, el expansor MCP23017 maneja los drivers del LED y del buzzer; el servo utiliza PWM de hardware. La PRU controla el reloj de transmisión y las ventanas de recepción. El expansor permite separar la etapa de mando y reemplazarla si se daña, pero no constituye aislamiento galvánico ni protege por sí solo todas las entradas de la BBB.

ARM publica READY cuando terminó de emitir las órdenes del símbolo. La PRU acepta únicamente el índice y la generación que corresponden al ciclo actual. READY no significa que el servo ya llegó a su posición. Si la preparación se retrasa, se aborta la transmisión de esa trama sin bloquear la recepción local ni reutilizar datos anteriores.

3 Formato de trama y transmisión híbrida

La trama lógica contiene 54 bits, del más significativo al menos significativo de cada campo. Llamamos V0 al primero. Con tres medios, en el ciclo k repartimos V[3k], V[3k+1] y V[3k+2] entre luz, sonido y nylon. Se envían juntos y el siguiente grupo espera el siguiente ciclo. Con dos líneas agrupamos pares y con una enviamos un bit por ciclo.

El cuerpo ocupa 18, 27 o 54 ciclos con tres, dos o una línea. Ya no hay prefijo de 40 ciclos. En los primeros 18 ciclos se envía simultáneamente el control físico por CLK: un marcador inicial y 17 bits auxiliares. Por tanto, 54 es la longitud del cuerpo lógico; no es la suma de toda la información que circula por las cuatro líneas. No se añade relleno al cuerpo.

Por ejemplo, para enviar la letra A en una sesión ya abierta usamos Control 0x4, DATA 0x41, SEQ 0x03 y SID 0x01. El CRC-SMBUS se calcula sobre los bytes 04 41 03 01 y da 0x8D. El control se amplía a un byte sólo para calcular CRC; en la trama conserva cuatro bits. Este ejemplo se verificó por cálculo, no por una transmisión física.

Figura 3. Cuerpo de la trama de A con tres líneas activas. El ciclo 0 empieza junto con el marcador del reloj; no se esperan ciclos de prefijo.

Con tres medios, el receptor concatena C0, C1 y C2 en ese orden. DATA ocupa V22 a V29. En la figura comienza en C1 del ciclo 7 y termina en C2 del ciclo 9. Con otro reparto las posiciones lógicas son las mismas. Se verifica CRC después de recibir Control, DATA, SEQ y SID. SYN y SFD se comprueban por su patrón.

Una sesión se abre con HELLO, HELLO_ACK, COMMIT y READY. Para un mensaje se utilizan START, LEN_LO, LEN_HI, una trama DATA por byte y END. El límite previsto es de 1024 bytes. END permite comprobar la longitud y completar la decodificación antes de entregar el texto completo.

4 Medio óptico

El transmisor será un LED rojo de 5 mm y el receptor un módulo D6 con LDR y comparador LM393. Entre ellos colocaremos un tubo opaco de aproximadamente 30 cm con interior negro. Su función es mantener la alineación y reducir la luz ambiente que llega al sensor.

Figura 4. Cadena óptica. Entre LED y LDR la señal cruza como luz; las conexiones eléctricas son locales a cada nodo.

Para transmitir 1 encendemos el LED; para transmitir 0 lo apagamos. La LDR cambia de resistencia según la iluminación y el comparador entrega un estado digital al superar el umbral ajustado. Debemos calibrar la polaridad porque el nivel eléctrico bajo del módulo podría representar presencia de luz. La capa física convierte esa lectura al bit lógico correspondiente.

El circuito de salida propuesto parte de 5 V de actuadores, pasa por una resistencia de 330 ohm y el LED, y termina en el colector de un 2N2222. El emisor se conecta a tierra local. GPA0 del MCP23017 gobierna la base por una resistencia de 1 kiloohm, con 10 kiloohm entre base y tierra. La LDR se alimentará a 3.3 V y su salida DO llegará a P9_27 por una resistencia serie de 1 kiloohm. Los valores deben verificarse con los componentes reales antes de energizar.

Elegimos este medio porque permite ver la emisión y provocar una interferencia controlada tapando el tubo. La velocidad no estará limitada por el recorrido de la luz en 30 cm, sino principalmente por la respuesta del sensor y el circuito. Mediremos las transiciones de encendido y apagado y probaremos secuencias 0000, 1111 y 0101 para detectar persistencia o falsas lecturas.

5 Medio acústico

Aquí la información viaja como variaciones de presión en el aire. Un buzzer activo emite un tono cuando recibe alimentación y una manguera lo conduce hasta el micrófono KY-037. La propuesta usa una manguera PVC de 30 cm y diámetro interno de 10 a 12 mm. La espuma se coloca alrededor de las uniones para reducir fugas y vibración; no debe bloquear el paso del sonido.

Figura 5. Cadena acústica propuesta. Cada sentido utiliza su propio buzzer, manguera y sensor.

Podemos entenderlo como dos personas en los extremos de una manguera: una produce un sonido y la otra comprueba si lo escuchó durante su turno. El buzzer hace de emisor y el KY-037 de receptor. No enviamos corriente por la manguera ni utilizamos presión estática. La señal útil es la onda sonora que se propaga dentro del aire.

GPA1 del MCP23017 controlará un 2N2222 que conecta el buzzer a su alimentación externa de 5 V. Si el buzzer del lote es magnético, se debe verificar la protección frente a su carga inductiva. El KY-037 se utilizará con alimentación y salida compatibles con 3.3 V; DO entra por 1 kiloohm a P8_16. No conectaremos su salida analógica directamente al ADC de la BBB como parte de este diseño.

El micrófono convierte el sonido en una variación eléctrica. El comparador del módulo contrasta esa señal con un umbral ajustable. Una sola emisión puede cruzar el umbral varias veces y producir varios pulsos digitales. No significa que se hayan transmitido varios bits: esos pulsos pueden pertenecer al mismo sonido dentro del mismo ciclo.

Figura 6. Ejemplo conceptual de varios pulsos asociados a un único bit. La forma real debe medirse con el sensor del lote.

En cada ventana de recepción, la PRU rearma la detección. Si identifica presencia acústica válida, el resultado del ciclo es 1; si no encuentra presencia válida, es 0. La ausencia de reloj es un error de sincronización y no se interpreta como un cero. La aceptación de un evento debe distinguirse de un pulso de ruido; el umbral y el filtrado se fijarán con mediciones.

No proponemos esperar una cantidad arbitraria de pulsos antes de avanzar ni añadir una pausa después de cada bit. El procesamiento se realiza dentro del tiempo asignado al símbolo. Contar pulsos puede servir para diagnosticar el módulo, pero no es necesario convertir ese conteo en una espera obligatoria. La frecuencia del tono del buzzer es independiente de la frecuencia con que enviamos símbolos.

Elegimos el KY-037 porque forma parte de los componentes seleccionados y ofrece salida digital y sensibilidad ajustable. No identifica por sí solo nuestro tono ni elimina toda interferencia. Por eso se necesitan la manguera, el ajuste del umbral y pruebas con el servo y el canal acústico contrario activos. También se debe verificar el modelo recibido: la referencia comercial anterior mezclaba KY-037 y KY-038.

Probaremos 00, 01, 10 y 11. Dos unos consecutivos deben reconocerse como dos ciclos distintos, y el sonido residual del primero no debe producir un uno falso en el siguiente cero. No damos por hecho que dejar el buzzer encendido o usar cualquier módulo sin caracterización cumpla esta condición. La ventana y el patrón de emisión se ajustarán antes de integrar el protocolo.

6 Medio mecánico con nylon

El servo SG90 mueve una palanca que tira de un hilo de nylon. En el otro extremo, el movimiento acciona un final de carrera SPDT con rueda. Un resorte ligero devuelve el mecanismo al liberar la tensión. Usaremos nylon monofilamento de 0.4 a 0.6 mm de diámetro y unos 50 cm útiles por sentido, dejando longitud adicional para los nudos.

Figura 7. Transmisión mediante tensión y desplazamiento del hilo. Las conexiones eléctricas del switch pertenecen al receptor.

El bit 0 corresponde al hilo relajado y al contacto normalmente abierto sin accionar. El bit 1 corresponde a tensión suficiente para cerrar el contacto. Con COM conectado a tierra local del receptor y NO a una resistencia pull-up de 10 kiloohm hacia 3.3 V, el contacto cerrado produce nivel bajo. El programa normaliza ese nivel como un uno lógico.

La entrada propuesta incluye 100 nF a tierra y una resistencia serie de 1 kiloohm hacia P9_24. El filtro y las muestras sucesivas deben comprobarse frente al rebote del contacto. No debemos dar por válido un cambio que ocurra mientras el mecanismo aún está oscilando.

El SG90 recibe la señal PWM de P9_14 a través de la etapa con 2N3904 prevista en el diseño. Esta etapa invierte la señal, por lo que la polaridad debe verificarse antes de conectar el servo. El PWM previsto es de aproximadamente 50 Hz y los pulsos de posición se calibrarán; esta frecuencia no cambia automáticamente al modificar el reloj del protocolo. El servo se alimenta desde la fuente de actuadores, no desde un GPIO.

Elegimos nylon porque transmite fuerza sin crear una conexión eléctrica entre nodos y permite observar directamente la representación de cero y uno. Usaremos guías, topes y poco recorrido para reducir holgura y fricción. El resorte no debe mantener el servo bloqueado. Es probable que este mecanismo, junto con la LDR, limite la frecuencia del sistema; la PRU no puede acelerar físicamente un servo.

7 Canal de reloj y alimentación

Cada dirección conserva su propio reloj generado por la PRU y recibido mediante un PC817. El par de conductores lleva la ida y el retorno de corriente del LED del optoacoplador. Sigue siendo un canal físico por sentido; la propuesta le añade control por ancho de pulso.

Figura 8. Reloj de A hacia B. El PC817 está montado en B, pero sus pines LED pertenecen eléctricamente al dominio A.

La salida P8_11 de A excita el ánodo del PC817 a través de una resistencia propuesta de 390 ohm. El cátodo vuelve por el segundo conductor a GND A. El transistor del PC817 utiliza exclusivamente 3.3 V y GND B: colector con pull-up de 4.7 kiloohm, emisor a tierra local y entrada P8_15 por 1 kiloohm. No se conecta el cátodo a GND B. La réplica de B hacia A intercambia los dominios.

Cuando se enciende el LED del opto, el colector baja. Normalizamos esa inversión: medimos el tiempo de LED encendido, que aparece como tiempo bajo en el colector. Las subidas lógicas siguen separadas por T. Un ancho de 0.2T representa 0, 0.4T representa 1 y 0.6T marca inicio. El texto y los cuerpos ACK/NACK continúan por los medios; CLK anuncia versión, reparto y reporte de líneas.

El PC817 separa los dominios en este circuito, pero no garantiza el aislamiento de todo el montaje. Los USB, las fuentes o los instrumentos pueden unir las tierras por fuera. Esa situación debe comprobarse en la integración. La BOM propone fuentes reguladas de 5 V y 2 A para las BBB y fuentes de 5 V y 2.5 A para los actuadores; la disponibilidad y las etiquetas reales siguen pendientes de inventario.

8 Temporización de cada símbolo

Figura 9. Tres ciclos de ejemplo. El inicio del ciclo se reconoce por la subida lógica. El ancho transporta control y la captura de los medios se realiza después, normalmente a 0.8T. Es un calendario propuesto, no una medición.

La implementación debe preparar las salidas y validar READY sin depender de pausas impredecibles de Linux. El flanco inicial abre el ciclo de recepción. La PRU mide ambos flancos del reloj y captura los medios dentro del mismo período. El modelo reserva 5 ms para aplicar las salidas y sus retardos de asentamiento; no emula el intercambio ARM–PRU. Las seis primeras capturas también comprueban las líneas fuera del reparto con una secuencia de prueba.

El período T es el inverso de la frecuencia de símbolos f. El perfil debe permitir completar la preparación, el asentamiento, la captura y los márgenes. Se medirá el peor caso de ambas transiciones de cada medio; no dividiremos todos los retardos proporcionalmente al aumentar la frecuencia. Tampoco se puede confundir READY con asentamiento ni la precisión de la PRU con rapidez mecánica.

Arrancamos a 1 Hz. Un cuerpo de aplicación a tres líneas tarda 18 s. Junto con ACK de 54 ciclos y dos guardas de 2 ciclos, el intercambio limpio ocupa 76 s; con dos líneas, 85 s; con una, 112 s. Abrir la sesión suma 224 s en el modelo. La frecuencia máxima física queda pendiente de medición.

9 Integridad y retransmisión

El diseño contempla CRC-SMBUS, AUTOSAR, SAE J1850 y MAXIM-DOW como opciones de integridad; la gestión usa SMBUS. CRC detecta errores, pero no corrige la trama ni identifica automáticamente el medio que falló. También se revisan el tipo de control, la sesión y la secuencia. SYN y SFD no están cubiertos por CRC: si se dañan, puede ocurrir pérdida de sincronización o timeout.

Figura 10. Ejemplo de ACK perdido. La retransmisión conserva SID y SEQ, y el receptor evita duplicar la entrega.

Con stop-and-wait, el emisor conserva la trama hasta recibir una confirmación válida. Si se pierde el ACK, puede repetir la misma trama. El receptor reconoce una secuencia ya aceptada, vuelve a confirmar y no agrega de nuevo el byte. Se permiten cuatro intentos de datos en total, el inicial y tres reintentos.

Un control PWM inválido descarta el intento y no autoriza un mapa nuevo. Si el cuerpo falla pero el reloj y el contexto de recepción son válidos, se puede responder NACK con la SID y SEQ esperadas. Sin contexto fiable se espera timeout. El receptor nunca debe inventar una identidad a partir de bits dañados.

La deduplicación depende del estado de la sesión. Si una BBB se reinicia y pierde ese estado, se abre una sesión nueva y se informa la incertidumbre de entrega; no prometemos entrega exactamente una vez a través de reinicios.

10 Cambio de frecuencia y respuesta a interferencias

Cada sentido tiene su propio período: T_AB para A hacia B y T_BA para B hacia A. Ambos arrancan a 1 Hz. Después se negocia por separado el perfil de cada dirección. Tras dos intentos fallidos, se puede bajar un escalón en la dirección afectada manteniendo la velocidad configurada de la otra. El cambio pausa temporalmente nuevas emisiones de aplicación para negociar sin tramas en vuelo; no requiere igualar ambos períodos.

Figura 11. Cambio coordinado de la dirección seleccionada. Su emisor coordina; el otro período configurado se conserva. Las transacciones de ambas direcciones no se negocian simultáneamente.

Antes del cambio, ambos nodos terminan o suspenden ordenadamente los pendientes y guardan sus buffers. El emisor de la dirección que cambia inicia QUIESCE y espera QUIESCED usando gestión a 1 Hz. Envía el período en microsegundos en cuatro PERIOD_PART (0xE). El receptor verifica transacción, índices y período antes de PREPARED. La dirección se identifica por el enlace físico de la petición, no agregando bits al cuerpo.

Se intercambian COMMIT_RATE y READY_RATE a 1 Hz. PROBE viaja al período candidato por la dirección seleccionada; ACTIVE_ACK vuelve al período ya configurado del retorno. Cuando el candidato es 1 Hz, la respuesta de esta gestión se mantiene también a 1 Hz. Un PING final y su ACK confirman la reanudación. Sólo cambia el período seleccionado. Ambas direcciones conservan SID, SEQ, buffers y contadores. La negociación se serializa: una transacción de frecuencia cada vez.

Esta revisión usa versión binaria 101, equivalente a 5. Ambos extremos deben implementarla; no es compatible en el cable con las revisiones 011 y 100. HELLO anuncia versión, CRC de aplicación y codificación. El control PWM y la gestión usan CRC-8/SMBUS. Los fragmentos de período repetidos e iguales se admiten. Un perfil rechazado o una versión incompatible detienen la aplicación.

La gestión ocupa 54 ciclos por emisión. Conservamos 200 s de espera por etapa, cuatro intentos y vigilante de 8000 s para los perfiles virtuales de 1–4 Hz. En aplicación, el timeout se cuenta desde fin TX y vale 200 veces el período del retorno más 2 s. Así un ACK lento no se declara perdido usando el reloj rápido de ida. Incluye margen para una trama inversa en curso, respuesta replicada y guardas. Fuera de esos perfiles habrá que revisar las cotas.

Un bloqueo puede dejar el tubo oscuro sin afectar al reloj. El receptor compara patrones conocidos en cada medio y comunica lo observado mediante CLK. El emisor sólo aplica el reporte de una respuesta válida y correspondiente a la sesión. El mapa cambia al empezar otra trama, conservando el mensaje y los intentos consumidos.

11 Montaje sobre placa perforada

Cada nodo tendrá una placa perforada soldable de 9 por 15 cm, separada de la BBB mediante un arnés corto y rotulado. El MCP23017 irá en zócalo DIP28 para facilitar reemplazo. Se usarán borneras, separadores y fijaciones para evitar que el movimiento del servo o de los cables fuerce las soldaduras. No se soldará directamente sobre las BeagleBone.

Figura 12. Distribución funcional propuesta. No representa pistas terminadas ni sustituye la revisión eléctrica antes de energizar.

La zona de lógica trabaja a 3.3 V y tiene desacoplo cercano. Los drivers y la alimentación de actuadores se agrupan aparte. Las entradas conservan sus resistencias y filtros previstos. Los terminales del LED remoto del PC817 deben mantenerse separados del dominio eléctrico local. Las fuentes y tierras se unen únicamente donde corresponde dentro de cada nodo.

Para la réplica bidireccional se necesitan dos LED, dos LDR, dos buzzer, dos KY-037, dos SG90, dos switches, dos MCP23017 y dos PC817, además de sus drivers y elementos de montaje. Las dos BBB sí están confirmadas. El resto corresponde a la selección de la BOM; falta cerrar cantidades y variantes físicamente disponibles. Los pines son los propuestos en la documentación, todavía sujetos a verificación en T04.

12 Avance comprobado y pruebas pendientes

En A se eliminó la instalación remota de VS Code que ocupaba aproximadamente 1.1 GB. En B, la carpeta del usuario ocupa sólo 220 KB, por lo que no corresponde repetir esa limpieza. B presenta un fallo del entorno gráfico, pero sí permitió iniciar sesión y ejecutar consultas. Los LED de B se comportan como los de A y B no tiene microSD, según la observación realizada.

Las interfaces I2C y PWM son visibles en ambos sistemas. En A se identificaron los PRU detenidos. En B aparecen estados de remoteproc, pero no se pudieron leer sus archivos name. Estos resultados muestran soporte aparente; todavía no prueban ejecución de firmware PRU ni funcionamiento eléctrico de los pines. T02 se cerró el 07/11/2026 como inspección básica con observaciones; configuración y validación PRU pasan a T04.

En banco repetiremos los ensayos de las secciones 15 y 16. Mediremos bloqueo y respuesta de la LDR; falsos positivos y persistencia acústica; holgura y rebote del nylon; y deformación de los pulsos del PC817. También probaremos ambos sentidos a la vez bajo carga de Linux.

T04 recibirá las diferencias de sistema y los problemas de configuración. T09 a T12 cubrirán montaje y caracterización de los medios; T16 y T18, los tiempos de implementación; T25 y T26, recuperación; T28, negociación; y T38, validación de adaptación. Estos avances documentales no equivalen a completar esas pruebas ni cambian automáticamente el tracker.

13 Control por ancho de pulso

El reloj hace dos cosas en el mismo ciclo: marca cuándo empieza y, por la duración de su pulso, transmite una indicación. Es modulación por ancho de pulso, PWM. No conectamos el proyecto a la red eléctrica ni implementamos Powerline. La comparación sólo sirve para entender que un enlace puede transportar más de una función.

La subida lógica inicia el ciclo. El período entre subidas consecutivas permanece T = 1/f. La bajada permite medir el ancho. El receptor acepta 0 entre 0.15T y 0.25T, 1 entre 0.35T y 0.45T, e inicio S entre 0.55T y 0.65T. Los huecos entre bandas se rechazan. También rechaza un período fuera de T ± 5 %. No decide por “el valor más cercano” si el pulso cae fuera de una banda.

Antes de una emisión se exige reposo lógico bajo de al menos 2T. El marcador S ocupa el ciclo 0, que ya transmite bits del cuerpo. Los ciclos 1 a 17 llevan los 17 bits de control. En cuerpos de 27 o 54 ciclos, los demás pulsos son cortos, código 0. Un marcador dentro del cuerpo, un relleno incorrecto o un flanco adicional invalidan el intento. Una pausa no se interpreta como un bit cero.

Figura 13. Control de reloj y cuerpo de datos a tres líneas. El marcador y los 17 bits de control ocupan los mismos 18 ciclos que los 54 bits del cuerpo.

La palabra de nueve bits se forma como versión seguida de mapa y reporte, del bit más significativo al menos significativo. El CRC recibe primero el byte alto y luego el bajo: [palabra >> 8, palabra & 255]. Su resultado se transmite también de mayor a menor peso. Este CRC adicional protege el control físico; no sustituye ni aumenta el CRC de ocho bits del cuerpo.

Cómo se recibe el mapa sin conocerlo de antemano

El receptor guarda las tres muestras de cada ciclo mientras recibe el control PWM. Al completar el ciclo 17, verifica versión y CRC. Sólo entonces interpreta el mapa y ordena las muestras acumuladas. Con tres medios ya dispone de todo el cuerpo; con dos espera hasta el ciclo 26 y con uno hasta el 53. La memoria máxima de muestras de un intento es 54 por 3 bits, además de sus registros de tiempo y estado.

Si no valida el control, descarta esas muestras. La SID y la SEQ se mantienen en el cuerpo y se comprueban con su CRC y el estado de la sesión. El control PWM pertenece únicamente a la emisión iniciada por S después de la guarda: no se reutiliza una cabecera anterior.

14 Identificación y cambio de medios

Los identificadores no cambian: C0 es luz, C1 es sonido y C2 es tensión en nylon. Un mapa se escribe C2 C1 C0. Con w medios activos se toman grupos de w bits de V, respetando el índice ascendente de canal. El cambio afecta al reparto físico; el contenido de los 54 bits y la identidad del pendiente permanecen iguales.

Cómo comprobamos cada línea

Los primeros seis ciclos contienen bits conocidos de SYN y, con tres líneas, SFD. El receptor compara cada entrada con el patrón que corresponde al mapa. Una línea excluida envía 101010 durante esos seis ciclos y después cero; esa prueba va por capacidad libre del mismo período y no agrega ciclos. No pertenece al cuerpo V.

Esta comprobación distingue una línea fija en cero o uno de una que reproduce el patrón. No diagnostica la causa física: reporta que C0 no reprodujo lo esperado, no demuestra por sí sola que alguien tapó el tubo. Si falla después de la prueba, el CRC puede detectar el daño sin localizarlo; un nuevo intento vuelve a comprobar cada medio. Ruido que coincida con los patrones o colisiones de CRC siguen siendo posibles.

Cómo se acuerda la nueva distribución

START, LEN_LO, LEN_HI, DATA y END reparten el cuerpo entre los medios activos. HELLO, la gestión, ACK y NACK transmiten una copia completa por cada medio, con mapa 000. Basta una copia íntegra de control; si varias copias válidas discrepan, la respuesta se rechaza. Esto permite abrir y confirmar con un solo medio útil por sentido, aunque ida y vuelta utilicen medios distintos.

Cada extremo devuelve su observación en el control PWM de la siguiente respuesta. El otro extremo la utiliza únicamente si esa respuesta es válida y corresponde a la solicitud, SID, SEQ y tipo esperado. El mapa se aplica desde la próxima trama y se vuelve a anunciar en ella. Un reporte 000 no autoriza enviar el texto por CLK ni declara disponibles canales no comprobados.

Si el intento queda inválido, se retransmite desde V0, nunca desde una fracción elegida con el mapa nuevo. Un NACK con contexto válido o el timeout activa el reintento. Si ya se había aceptado el byte y se perdió su ACK, la SEQ evita incorporarlo otra vez. Las líneas excluidas siguen enviando la prueba para poder reincorporarse después de una observación válida.

Con tres medios el reparto mezcla envío paralelo dentro de cada ciclo y sucesión de grupos en el tiempo. Con dos conserva esa combinación. Con uno funciona temporalmente como transmisión serial degradada. El proyecto conserva instalados los tres medios; debe confirmarse con el auxiliar que acepta este modo de recuperación.

15 Simulación y resultados reproducibles

El HTML funciona localmente, sin instalar dependencias. Abra Simulador_TRAMA3.html, escriba Hola y prepare un ensayo a 1 Hz. “Ir a DATA” muestra los 54 bits; “Próximo cambio de líneas” muestra el reporte aceptado; “Ver resultado” permite comprobar la entrega. Los pulsos dibujados corresponden al código emitido y el valor inferior muestra el ancho recibido.

Son tiempos virtuales con una sesión nueva, un solo mensaje y retorno disponible. Incluyen HELLO, longitud, ACK, guardas y END. La reducción de 800 s para Hola a 1 Hz proviene de quitar 40 ciclos en sus 20 emisiones. No hemos aumentado la velocidad del servo ni de la LDR. El control permanece, pero se envía simultáneamente por CLK.

Si se bloquean luz y sonido durante 120 s a partir del ciclo 8 del primer DATA, Hola termina en 1020 s virtuales, con dos reintentos. El mapa pasa a 100 y luego vuelve a 111. El carácter pendiente conserva su identidad. Se puede exportar el registro JSON para observar las transiciones y el texto entregado.

Errores incluidos en la revisión

La batería automatizada tiene 42 pruebas: conserva codificación, los cuatro CRC, sesiones, duplicados, negociación y cambio de líneas, y añade diez pruebas específicas de PWM. Recorre los siete mapas de datos, las 256 posibilidades de byte y los cuatro algoritmos CRC. Comprueba todos los reportes y las inversiones de un bit en el control auxiliar.

Se inyectan ancho ambiguo, CRC de control alterado, marcador perdido, relleno incorrecto, período deformado, flanco extra, pulso perdido y trama truncada. También se prueban fronteras de tolerancia, recuperación tras guarda, retardo desigual entre flancos, variación aleatoria y ausencia de los tres medios con CLK funcionando. Un control inválido no habilita una entrega válida en esos ensayos.

Se conservan los casos de ACK perdido o ajeno, pérdida de ACK final, retorno bloqueado, cuatro intentos agotados, reinicio de sesión, READY tardío, rechazo de versión y frecuencia, fragmentos de período perdidos y reducción de frecuencia tras dos fallos. El cambio de frecuencia mantiene los intentos ya consumidos. La secuencia de aplicación puede volver a cero después de 255; la transacción de negociación no se reutiliza dentro de la sesión al agotarse su identificador.

Qué no demuestra la simulación

No existe una garantía de detectar todos los errores: un CRC de ocho bits tiene colisiones. Tampoco hay autenticación ni defensa contra señales maliciosas. El modelo trabaja con ventanas de emisión conocidas por el banco de pruebas; el receptor sí decodifica tiempos de flancos, aprende el mapa y reconstruye las muestras, pero no emula una PRU ni un circuito analógico continuo.

Las pruebas de sonido múltiple y rebote representan el resultado lógico del acondicionamiento, no una simulación electromecánica de cada componente. El reinicio invalida la sesión en el modelo; no sustituye ensayos de cortes de alimentación. Si la comunicación queda totalmente cortada, se informa fallo o entrega incierta; no se promete que un mensaje pendiente se recupere indefinidamente.

Los perfiles de 1, 2, 3 y 4 Hz son hipótesis. El comparador envía U* y *U en ambos sentidos. Con 300 ms de retardo mecánico, sólo hasta 2 Hz mantienen los tres medios sin reintentos en el modelo; a más frecuencia puede avanzar con menos líneas. Esto no establece la frecuencia máxima de las piezas reales. Ahora se prueban también los 16 pares posibles de velocidades de ida y vuelta, con los cuatro CRC. El escenario de ACK perdido se verifica con ida rápida y retorno lento; la bajada de A conserva la velocidad de B.

16 Materiales y validación del montaje

La BOM seleccionada ya incluye dos BeagleBone Black, dos PC817 DIP4, resistencias de 390 ohm y pull-ups de 4.7 kiloohm. Proponemos ensayar con ese mismo circuito a 1–4 Hz. No se requiere ESP32 ni un módem Powerline para esta modificación. Las dos BBB están confirmadas físicamente; las referencias y cantidades restantes deben cotejarse con las piezas recibidas.

Sharp publica tiempos típicos de subida y bajada de 4 y 3 microsegundos para el PC817, con máximos de 18 microsegundos bajo condiciones de prueba específicas: VCE de 2 V, IC de 2 mA y carga de 100 ohm. Nuestro pull-up de 4.7 kiloohm y la saturación cambian esas condiciones. No tomamos 18 microsegundos como un límite garantizado del circuito que construiremos. [1]

A 4 Hz, el pulso más corto propuesto dura 50 ms y la tolerancia de ancho es ±12.5 ms. Esa separación hace razonable ensayar el PC817 a baja frecuencia, pero no certifica el montaje. La resistencia de 390 ohm produce una corriente aproximada de unos 5 mA con 3.3 V y una caída LED cercana a 1.2 V; se debe verificar la caída real, el presupuesto del GPIO y el nivel bajo recibido antes de cerrar el diseño.

La PRU puede programar el reloj sin usar el mismo periférico PWM del servo. Las BBB incorporan dos PRU de 200 MHz; eso aporta control temporal, pero no confirma el pinmux ni el acceso a cada pin propuesto. T04 debe verificar P8_11/P8_15 y la forma de acceso desde PRU. [2] La modulación mantiene el período y cambia la duración activa, de acuerdo con el principio PWM. [3]

Compra condicional si las medidas la justifican

Si el colector del PC817 presenta flancos lentos con lecturas múltiples, se puede evaluar un SN74HC14N en encapsulado PDIP14 por nodo, alimentado a 3.3 V, más un capacitor cerámico de 100 nF por circuito. Son dos integrados y dos capacitores para los dos nodos; zócalos DIP14 si se desea reemplazo sencillo. El SN74HC14 admite 2–6 V y entradas Schmitt. Se debe contar su inversión y medir de nuevo el pulso. No acelera el propio PC817 ni garantiza corregir toda distorsión. [4]

No incluimos ese integrado como compra obligatoria. Si el GPIO no puede entregar la corriente elegida, hay que revisar el driver del LED del opto; los 2N3904 de la BOM ya están asignados al servo y no deben contarse como repuestos libres. Una mejora para frecuencias mayores se decidirá con medidas, no con el límite del simulador.

Prueba física que debe preceder a una afirmación de velocidad

Primero comprobar el reloj aislado: polaridad, corriente y niveles 0/3.3 V. Medir anchos 0.2T, 0.4T y 0.6T en ambos sentidos, empezando en 1 Hz y subiendo por pasos. Verificar que el peor error de ancho y de período queda dentro de ±0.05T con margen, incluyendo cables y variación bajo carga.

Después repetir patrones de los tres medios, cortes de uno y dos, reincorporación y tráfico simultáneo. Retirar CLK debe provocar descarte y recuperación, nunca bits cero inventados. Al medir los dominios aislados, revisar las tierras comunes de los instrumentos y USB para no puentear accidentalmente el PC817. Registrar los flancos reales junto con el log del protocolo.

17 Revisión frente al enunciado

La aclaración del auxiliar del 07/11/2026 admite pulsos de duración distinta cuando el protocolo lo amerite y explica que el receptor usa el reloj enlazado desde el otro dispositivo como referencia de lectura. Interpretamos esa respuesta, dada a la pregunta explícita sobre el aviso de canales, como autorización del principio de modulación propuesto. La revisión 101 sustituye la restricción anterior de CLK sólo para sincronización y añade frecuencia independiente por sentido.

El criterio del reloj queda aclarado para continuar el diseño. Su explicación no certifica los 17 bits auxiliares, los umbrales elegidos ni la implementación. Tampoco convierte 200 Hz en requisito o velocidad demostrada. La evaluación del funcionamiento temporal con menos de tres medios no fue confirmada expresamente en esta respuesta; el diseño conserva los tres instalados y documenta ese modo de recuperación.

Aclaración incorporada

No se repite la consulta sobre el reloj: queda incorporada su aclaración. Tick o quantum significa aquí un ciclo de la dirección correspondiente. Con un multiplicador entero m respecto de 1 Hz, f = m Hz y T = 1/m segundos. No multiplicamos el período por m. Cada log identifica dirección, trama, ciclo k y tiempo virtual; k vuelve a cero en cada trama. Recibir a 1 Hz y transmitir a 4 Hz son calendarios distintos dentro de la misma BBB.

Calendarios de transmisión y recepción

Ejemplo: A transmite a 4 Hz y B a 1 Hz. B lee C0/C1/C2 usando CLK_AB cada 250 ms; A lee el retorno usando CLK_BA cada segundo. El ancho PWM se interpreta como fracción del período recibido de esa dirección. En el firmware, la captura se agenda respecto al flanco recibido, no al reloj de salida local. El simulador utiliza el calendario nominal de cada dirección y modela distorsiones de flancos; sigue sin emular captura continua en una PRU.

El perfil solicitado por sentido se limita por ahora a 1, 2, 3 o 4 Hz. Hay selectores independientes en el HTML y parámetros hzA/hzB en el motor. El parámetro hz mantiene compatibilidad como valor común cuando no se especifican los dos anteriores. La trama lógica conserva 54 bits, el control PWM 17 bits y no vuelven los 40 ciclos de prefijo. Materiales y esquema de reloj no cambian por esta revisión.

Referencias

Base del proyecto: Proyecto de capa física, PDF entregado por el curso, páginas 2–4 y 7–9; aclaraciones del auxiliar compartidas en este chat; BOM CCVIII_Materiales_y_Compras.xlsx; ADR-0001 y ADR-0002 del repositorio. Consultados el 7 de noviembre de 2026. La restricción local de reloj sin control se identifica como decisión previa, no como una frase del enunciado.

[1] Sharp. PC817XxNSZ1B Series, hoja de datos de 15 de enero de 2018, tabla de características y curvas de respuesta. https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf

[2] BeagleBoard. BeagleBone Black y guía PRU. https://www.beagleboard.org/boards/beaglebone-black y https://docs.beagleboard.org/books/beaglebone-cookbook/08realtime/realtime.html

[3] Microchip. Pulse Width Modulation. https://developerhelp.microchip.com/xwiki/bin/view/products/mcu-mpu/8bit-pic/peripherals/ccp/pwm/

[4] Texas Instruments. SN74HC14. https://www.ti.com/product/SN74HC14

Microchip. MCP23017. https://www.microchip.com/en-us/product/mcp23017

Joy-IT. KY-037. https://sensorkit.joy-it.net/en/sensors/ky-037

Tower Pro. SG90. Las especificaciones del fabricante no certifican los clones. https://towerpro.com.tw/product/sg90-7/

Repositorio. https://github.com/bitvalo34/trama3-ccviii
