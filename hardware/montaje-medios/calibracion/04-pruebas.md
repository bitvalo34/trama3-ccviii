# Calibración y comprobación T09 y T10

## Condiciones comunes y evidencia

Nada en este paquete acciona GPIO, I2C, PWM o PRU. T06/T08 serán adaptados posteriormente a T51, según instrucción de Erwin. Hasta que exista versión compatible y validación T52/T08 por placa, únicamente realizar medición dimensional, montaje seco y movimiento manual desenergizado. T09 requiere T08 y T06. T10 requiere T09 y T18; no dar por cumplida T18 porque exista un ejemplo PWM. La segunda placa puede montarse mecánicamente y cablearse apagada mientras se prepara software; no hay prueba bidireccional completa con sólo una interfaz validada.

Registrar fecha/hora del PC, nodo, revisión firmware y circuito, instrumento/modelo, incertidumbre, tensión, polaridad, ajuste, distancia, foto/captura y operador. Estado inicial de todas las filas: NO_PROBADO. Usar registros.csv y muestras.csv sin sustituir casillas vacías por cero. Guardar también intentos fallidos. Osciloscopio verifica amplitud y picos; analizador lógico de entrada compatible verifica tiempo después de verificar amplitud. Multímetro sirve para DC y continuidad, no para pulsos ni asentamiento. No unir masas de ambos nodos por el instrumento. Sin instrumento apropiado, registrar BLOQUEADO la medición correspondiente.

010101 a 1 Hz significa seis estados de 1 s cada uno. El patrón tiene cinco cambios internos; registrar nivel inicial, cinco transiciones y retorno final a reposo. Un reloj cuadrado de 1 Hz con 50% de duty cambia cada 0.5 s y no equivale al calendario de seis estados. Para revisión 102, T=1 s y captura de cada fila en 0.8T. Medir preparación, asentamiento yjitter; exigir Lprep+Lasent+J+margen<=0.8T por sentido. El margen es una decisión documentada de T11; no inventar valores para aprobar.

Etapa de calibración: reposo 10 s, activación/desactivación sostenida, diez repeticiones de 010101 (60 estados), luego 100 ciclos de activación/liberación de C2 y ensayos concurrentes. Estas cantidades son propuesta de banco T09/T10 y no sustituyen los 100 bloques por pareja del protocolo completo. Si una prueba falla, detener la aceptación, conservar evidencia, corregir sólo el ajuste identificado y repetir la prueba y las de diafonía afectadas.

## P01 Óptico A hacia B

Emisor LED-A por J2A; receptor LDR-B por J5B; observar TP5B y, sólo con niveles aprobados, P9_27B. Primero JP4B abierto y SW287 OFF. Con tubo X30 colocado y tapa opaca, medir salida en oscuridad tapando el LED, luego con LED activo por rutina T18 compatible. Registrar Vlow/Vhigh, corriente y polaridad presencia->0/1. Ajustar potenciómetro B entre estados claramente separados, no al borde del cambio. Repetir con luces del recinto apagadas/encendidas y mano alrededor de las juntas.

Verificados niveles 3.3 V y sin sobreimpulsos peligrosos, cerrar JP4B con alimentación retirada y volver a iniciar según T08. Generar 010101 a 1 Hz, registrar señal TX y RX en reloj/tiempo de referencia comparable, ambos retardos y falsas transiciones. Activar sólo LED-B del carril X75 mientras A está apagado: B no debe reportar presencia A. Repetir con sonido y servo cercanos. Aceptación: seis estados correctos por repetición, polaridad normalizada documentada, cero errores en muestra de banco y tiempos dentro del presupuesto medido. Si luz ambiente conmuta, reparar tapa; si no llega luz, alinear y revisar LED/DI antes de cambiar sensibilidad. Sin firmware compatible, preparar patrón en archivo pero no puentear driver para simular aprobación.

## P02 Óptico B hacia A

Emisor LED-B por J2B; receptor LDR-A por J5A, TP5A/P9_27A. Carrilglobal X75: TXB local 225, RXA75. Aplicar reposo 10 s, luz sostenida, ajuste del pot A y niveles con JP4A abierto. No copiar giro de pot ni polaridad registrada en B. Cerrar enlace sólo apagado y validado. Diez patrones 010101, medir subida/bajada, ruido y recuperación. Agresor LED-A del carril X30 activo con B apagado; luego sonido y ambos servos. Registrar en P02 con etiquetas propias. Mismos criterios y caminos de corrección de P01; un PASSA->B no acredita B->A.

## P03 Acústico A hacia B

Buzzer-A por J3A; MIC-B por J6B, TP6B/P8_16B. Carril X120, manguera 480 mm. Identificar VCC/GND/DO/AO de MIC-B independientemente. JP5B abierto. Alimentación 3.3 V del módulo y driver 5 V del buzzer según P2 validado. Medir 10 s de silencio y 10 s de emisión; ajustar sensibilidad hasta distinguirlos sin golpear ni tocar el sensor. Repetir con conversación ambiental, mesa rozada y servo del propio B operando descargado.

Capturar DO a tasa suficiente para resolver su pulso más corto observado; registrar resolución, ancho mínimo, conteo de flancos y hueco máximo durante tono. DO puede oscilar a frecuencia relacionada con el buzzer: **cada flanco no es un bit**. La adquisición debe estimar presencia dentro de una ventana autorizada por T18/T57, conservando la captura conjunta del vector en 0.8T. Caracterizar ventana y umbral con datos de silencio/tono: cualquier filtro o retención debe liberar antes del siguiente 0. No fijar RC ni ventana numérica arbitraria en esta entrega. Si el firmware aún sólo toma un valor instantáneo crudo y el tono produce tren de pulsos, registrar BLOQUEADO la aceptación lógica y entregar trazas a Adrián.

Con acondicionamiento de presencia compatible y JP5 cerrado tras validar niveles, ejecutar diez 010101; guardar crudo y presencia normalizada, latencia de entrada y de salida. Agresor principal buzzer-B con A apagado: medir falsos positivos en MIC-B; después ambos buzzer y servo. Si hay diafonía, sellar fugas alrededor (no dentro) del conducto, aislar apoyos, separar cámaras y reducir sensibilidad sin perder señal propia. No atribuir transmisión por manguera si funciona igual al desconectarla: hacer control con boca bloqueada y fuente separada, anotando ruido aéreo residual.

## P04 Acústico B hacia A

Buzzer-B por J3B; MIC-A por J6A, TP6A/P8_16A, carril X160. Crear tabla de pines y ajuste de MIC-A propios. Repetir silencio/tono 10 s, niveles 3.3 V, tren de pulsos y ventana de presencia. No copiar la correspondencia física de MIC-B. Ensayar diez 010101 y agresor buzzer-A con B apagado, con y sin movimiento de ambos servos. Comparar primero crudo, luego presencia; registrar también falsos negativos, no sólo falsos positivos. Si permanece activo tras cortar tono, bajar retención/sensibilidad sólo después de medir el decaimiento. T09 cierra sólo con P01-P04 completos y revisión de Adrián, sin sustituir el canal difícil por uno eléctrico.

## P05 Mecánico A hacia B

SG90-A/J4A transmite; SW2-B/J7B recibe; TP7B/P9_24B. Carril X215. Primero sin energía y sin brazo acoplado al servo: tirar suavemente del nylon y comprobar continuidad COM-NO, liberación y ausencia de atasco. Registrar carrera, fuerza en punto de amarre, precarga, k medida y elongaciones. Después de T08/T06/T18 compatible, retirar nylon del brazo, mantener SW287 OFF, establecer PWM de centro y verificar señal; habilitar servo sin carga y comprobar carrera pequeña. No copiar anchos 1/2 ms de ensayo T06 como extremos del mecanismo.

Apagar, conectar brazo y nylon con retorno libre. Reactivar con pulsos cortos y pequeña excursión medida; observar que el switch cierre antes de un tope. Medir tensión de servo bajo carga, corriente y temperatura cualitativa; cortar ante zumbido persistente, golpe o no retorno. Comprobar OFF del SW287-A: no mueve ni se mantiene señal activamente alta; restablecer sin tirón con hilo descargado.

Ensayar reposo 10 s,10 accionamientos lentos y 100 ciclos. Registrar tiempos de cierre/apertura, rebote crudo y tiempo hasta último flanco, errores y desplazamiento de MDF. Con entrada segura cerrar JP6B y probar 010101 a 1 Hz en diez series. Agresor servo-B moviendo su línea, luego ambos; verificar que SW2B no cambie por vibración cuando su línea está en reposo. Criterio: retorno estable y estados correctos sin bloqueo; la frecuencia se acredita sólo con registro. Corregir fricción, holgura o brazo antes de aumentarpar/giro.

## P06 Mecánico B hacia A

SG90-B/J4B -> SW2-A/J7A, TP7A/P9_24A, carril X275. En local B el eje TX está X25, guía X33; RXA está X275. Repetir todas las etapas de P05 con medidas propias del resorte B->A. Fotografiar nudo, posición de brazo y punto de amarre en SW2A. Comprobar OFF de SW287-B,100 ciclos y diez 010101; servo-A es agresor. Registrar histéresis: desplazamiento de cierre menos desplazamiento de apertura medidos en la misma dirección de aproximación. Si la cuerda se afloja y sale de guía, usar ojo cerrado y corregir tensión inicial; no resolver con precarga que impida reposo. No afirmar 100 ciclos si sólo se dibujó la trayectoria.

## P07 Reloj A hacia B

Con alimentación retirada, continuidad J9A.1->J8B.1 y J9A.2->J8B.2; comprobar que no se añadió GND común y que la isla óptica no toca retorno B. Revisar polaridad LED/antiparalelo. Con P2 aprobada y generador/receptor compatibles, emitir una secuencia finita a 1 Hz con marcador 0.6T y pulsos ordinarios 0.2T, guarda 2T. Receptor B observa TP8B/P8_15B; transmisión TP10A/P8_11A. Usar instrumentos aislados/diferenciales apropiados si se comparan dos nodos; no unir sus masas con sondas comunes.

Normalizar inversión del opto: pulso TX alto produce RX bajo. Registrar anchoalto/bajo crudo, período, retardo, recuperación, pulsos perdidos/extra y saturación. Referencias 102: marcador 0.55..0.65T, ordinario 0.15..0.25T, período±5%. Repetir con todos los actuadores funcionando y dos relojes simultáneos a su calendario independiente. El cable físicamente instalado no acredita captura PRU. Si no hay firmware compatible con 1 s, el resultado es BLOQUEADO y se conservan las conexiones apagadas; no llamar a T06 con argumentos fuera de su rango.

## P08 Reloj B hacia A

Par J9B->J8A por bordeglobal X295. Aplicar inspección apagada y medición de P07 con TP10B, TP8A/P8_15A. Verificar recepción correcta cuando AB emite simultáneamente; no usar un solo pulso compartido como evidencia de ambos. Desconectar sólo este par con energía retirada y comprobar, al reanudar ensayo, ausencia de captura en RXA mientras RXB sigue operativo. Documentar que los datos únicamente circulan por C0/C1/C2 y que no hay USB/Ethernet/UART/I2C entre equipos. T10 requiere P05-P08 además de T09/T18, revisión de Adrián y evidencia de ambas placas.

## Herramientas y comandos preparados

Desde raíz del repositorio, sólo auditoría existente (no acciona hardware):

```bash
python3 hardware/pruebas/t06/run.py preflight --board BBB-A
python3 hardware/pruebas/t08/inspeccion.py --board BBB-A
```

Repetir con BBB-B. Estos informes no validan P2. La compilación y los ensayos activos se ejecutarán con las instrucciones de la revisión T06/T08 adaptada, sin reutilizar el formulario antiguo. No se reescribe PRU. Limitaciones constatadas: run.py acepta período 1000..100000 us; no 1000000 us. inputs usa fixture de resistencias, no captura lógica de tres medios; ventana máxima 10 s no sirve para trama 102 de 87 ticks. T18 debe generar salidas de forma segura; T57 debe aportar captura continua y presencia acústica válida. Estos son contratos pendientes, no funciones prometidas por el script adjunto.

Se entrega `registro.py`, utilidad offline Python 3.5+, para preparar patrón y comprobar registros sin tocar hardware:

```bash
python3 hardware/montaje-medios/calibracion/registro.py plan --output plan-010101.csv
python3 hardware/montaje-medios/calibracion/registro.py evaluar --input hardware/montaje-medios/calibracion/muestras.csv --output evaluacion.json
```

El plan sólo contiene tiempos esperados ybits, no los emite. En muestras.csv anotar seis filas por ensayo con bit observado normalizado, flancos, retardos, tensión, polaridad, evidencias y resolución. El evaluador comprueba completitud y coincidenciabit a bit; devuelve NO_PROBADO si faltan datos. No certifica amplitud, calibración, autenticidad ni cumplimiento del mecanismo, y nunca cierra T09/T10 automáticamente. Usar protocolo de laboratorio y firma además del CSV.

## Matriz de interferencia

Para cada receptor C0/C1/C2 en A y B: mantener su emisor apagado, activar por separado emisor contrario del mismo medio, los otros dos medios locales y ambos servos; luego transmitir 010101 propio con cada agresor. Registrar número de ventanas, falsos positivos, falsos negativos, flancos adicionales, ajuste y captura. No sumar intentos diferentes como un único ensayo limpio. Repetir después de mover espuma, cerrar bridas, ajustar fuentes o cambiar software.

Adrián revisa evidencia y criterios, Erwin ejecuta yregistra. Los resultados físicos quedan pendientes. T11 recoge el presupuesto de tiempos y decide el perfil permitido, sin imponer 4 Hz ni 150 ms de una planificación anterior.
