# Diseño eléctrico T51-P1

Referencia funcional: TRAMA 3 revisión 102. No se cambia la trama lógica de 54 bits, las matrices ni el tratamiento de fallos del protocolo. A y B usan este mismo circuito. No se ha generado firmware ni ensayado hardware.

## Alimentación, retornos y estados iniciales

BBB se alimenta por su conexión propia. J10.1 recibe 3.3 V de P9_3 y J10.2 la referencia P9_1. No se lleva 5 V de BBB a actuadores y no se inyecta una fuente exterior en P9_3. La fuente de actuadores de 5 V/2.5 A entra por J1.1 positivo y J1.2 retorno. El conector real de esa fuente sigue pendiente de identificación; comprar un adaptador sólo cuando se conozcan su tipo y polaridad.

Ruta positiva: J1 → portafusible F1 mediante J14 → D de Q6 → S de Q6 → +5V_ACT. Q6 es IRLML6402 de canal P, G=1, S=2, D=3, montado en adaptador SOT23. R30=100 kΩ lleva G a GND_ACT. Para esta protección inversa, **D va a la entrada y S a la salida**: no invertirlos por copiar un interruptor MOSFET convencional. La etapa evita la caída permanente de una protección serie por diodo. No bloquea necesariamente retorno de una salida alimentada externamente; sólo debe existir una fuente en J1/J11.

C1=1000 µF/16 V y C2=100 nF desacoplan +5V_ACT. C3=100 nF desacopla el riel conmutado del servo. El capacitor no sustituye una fuente suficiente: ΔV=I·Δt/C; 0.5 A durante 1 ms ya produce 0.5 V sobre 1000 µF ideal, sin contar ESR.

GND_ACT recibe servo y drivers. GND_LOGIC recibe sensores, MCP y BBB. **NT1, un puente corto de 22 AWG entre sus dos pads, es la única unión intencional entre ambos retornos dentro de cada interfaz.** No añadir puentes en los arneses. El retorno de potencia recorre cable 22 AWG, no una cadena de gotas de estaño. Las conexiones superiores son terminales de componentes; los enlaces eléctricos inferiores son los cables W001–W134. El cobre de las islas por sí solo no une perforaciones vecinas.

J11 permite el adaptador Micro USB como alternativa de banco de baja carga, máximo provisional 0.5 A y servo desconectado. No es la entrada de potencia para SG90 y no se conecta a la vez que J1. Su volumen externo es una reserva geométrica; no se certifica la corriente de su PCB.

F1 de 1 A se conserva como **valor provisional pendiente T08**, no como selección aprobada para el servo. Falta tipo rápido/lento, curva, consumo en reposo/movimiento/arranque y corriente de bloqueo del lote. No aumentar el fusible porque se funda: antes verificar cable, borneras, adaptador Q6, fuente y curva I²t. A 1 A y RDS=0.065 Ω, Q6 disipa 0.065 W; a 2.5 A, 0.406 W. La cifra de corriente de la hoja de datos no acredita disipación en un adaptador pequeño. La placa no queda calificada para 2.5 A por tener una fuente de esa capacidad.

Presupuesto preliminar del riel BBB: reservar 20 mA por cada módulo receptor, 5 mA para MCP, hasta 10 mA para LED del reloj, 5 mA para bases TX y 15 mA para pull-ups, entradas y margen: **75 mA de reserva de diseño**. El límite documentado de expansión 3.3 V es 250 mA, sujeto al sistema completo. Los 75 mA son un presupuesto, no mediciones de los módulos. Si una placa excede la reserva, resolver antes de integrar. Los módulos y GPIO se alimentan desde el mismo 3.3 V para evitar mantener entradas activas con BBB apagada; no conectar señales externas energizadas a una BBB sin alimentación.

## Control MCP23017 e I2C

U1 DIP28 estrecho de paso transversal 7.62 mm, zócalo extraíble, muesca hacia fila A. Pin 9 VDD=3.3 V; 10 VSS=GND_LOGIC; 12 SCL=P9_19; 13 SDA=P9_20; 15/16/17 A0/A1/A2=GND, dirección 0x20. RESET pin18 tiene R1=10 kΩ a 3.3 V y JP1 normalmente abierto a tierra. C4=100 nF se coloca junto al sector VDD/VSS. NC11/14, interrupciones19/20 y puertos no usados no se conectan. No confundir la numeración vista desde arriba con la cara de soldadura.

GPA0 pin21 controla luz; GPA1 pin22 controla buzzer. Tras reset los puertos son entradas; R5/R8 mantienen apagados los transistores. La inicialización futura debe escribir estado apagado antes de habilitar salidas, sin añadir aquí firmware.

R2/R3=4.7 kΩ y JP2/JP3 son **DNP/abiertos por defecto**, reservas para pull-up I2C. Primero comprobar los pull-ups existentes en BBB y la resistencia equivalente. No montar otros en paralelo sin calcular corriente de hundimiento y tiempo de subida. Para un bus RC, tr≈0.8473·Rp·Cb; 4.7 kΩ con 100 pF da unos 398 ns. Esto no certifica la velocidad del bus real. El bus I2C local no sustituye los medios del protocolo.

## C0: luz

TX: GPA0 → R4=1 kΩ → base Q1 2N2222; R5=10 kΩ base-emisor; emisor a GND_ACT. +5V_ACT → R6=330 Ω → J2.1 ánodo LED; J2.2 cátodo → colector Q1. A 5 V, Vf≈2 V y VCE≈0.1 V, ILED≈8.8 mA. Con fuente ±5 %, R ±5 %, Vf entre 1.8–2.2 V y VCE entre 0.1–0.2 V: 6.8–10.7 mA; R6 disipa menos de 0.036 W bajo esas hipótesis. Resistencia 1/4 W suficiente para este cálculo.

Q1/Q2 tienen pads **1=E, 2=B, 3=C en este diseño**. Eso no identifica el orden físico del transistor recibido. Algunos P2N2222A son C-B-E; confirmar fabricante/marcado, doblar las patas con aislamiento o corregir la huella. No basta mirar la cara plana.

RX: J5.1=3.3 V, J5.2=GND_LOGIC, J5.3=DO del módulo LDR; AO libre. R17=10 kΩ fija DO alto cuando la salida es colector abierto. TP5 permite medir DO antes de cerrar JP4 hacia P9_27. EN_C0 selecciona DO o cero; R20=1 kΩ limita corriente accidental, **no convierte 5 V a 3.3 V ni constituye aislamiento**. Alimentar exclusivamente el módulo a 3.3 V en esta revisión. Que el IC sea LM393 no demuestra el funcionamiento de toda la placa a esa tensión. Si el módulo no conmuta correctamente a 3.3 V, detener esta rama y diseñar adaptación de nivel o sustituir el módulo: no elevar su alimentación a 5 V con JP4 cerrado. Registrar si luz corresponde a DO alto o bajo para normalización futura.

## C1: sonido

TX: GPA1 → R7=1 kΩ → base Q2; R8=10 kΩ base-emisor; emisor a GND_ACT; colector a J3.2; J3.1 a +5V_ACT. Buzzer activo, con polaridad verificada. D1=1N5819 entre colector y +5V_ACT, ánodo en colector y banda/cátodo en positivo, proporciona camino de rueda libre si la carga es electromagnética. No se usa ese diodo sobre el servo.

La etapa queda condicionada a un buzzer de **5 V y consumo ≤20 mA**. Con base aproximada 2.5 mA se dispone de margen para β forzada próxima a 10; el VOH real del MCP se debe comprobar bajo carga. Si el buzzer consume más, no asumir saturación de Q2: recalcular o usar un driver adecuado. El 1N4148 existente se reserva al optoacoplador, no se propone como protección universal de actuadores.

RX: J6.1=3.3 V, J6.2=GND_LOGIC, J6.3=DO; R18=10 kΩ pull-up; TP6=DO; EN_C1 → R21=1 kΩ → JP5 → P8_16. AO no se conecta. Las fotos muestran variantes distintas de módulo acústico; mapear cada serigrafía, no copiar el orden de los pines del módulo A al B. Puede haber varios pulsos ante una emisión, por el comparador y la oscilación acústica. Este diseño no añade un retardo RC arbitrario al sonido; la interpretación temporal corresponde al receptor de revisión102 y debe caracterizarse con analizador/osciloscopio. La salida DO no demuestra por sí misma qué pulsos representan sonido válido.

## C2: servo y final de carrera

P9_14 entrega PWM_BBB de 3.3 V. Se desconoce el umbral garantizado de los SG90 recibidos: se usa adaptación a 5 V con **dos inversiones**, sin cambiar la polaridad lógica del PWM.

R10=4.7 kΩ alimenta base Q3; R11=47 kΩ la mantiene baja. Q3 invierte con R12=4.7 kΩ a +5V_SERVO. R13=4.7 kΩ lleva PWM_INV a base Q4 y R14=47 kΩ la descarga. Q4 invierte de nuevo; R15=2.2 kΩ eleva PWM_5V a +5V_SERVO; R16=47 kΩ mantiene baja SERVO_SIG. Ambos emisores a GND_ACT. Entrada baja estable: Q3 apagado, Q4 encendido, salida baja. Entrada alta: Q3 encendido, Q4 apagado, salida alta. R10 proporciona aproximadamente (3.3−0.8)/4.7k=0.53 mA; Q3 hunde cerca de 1 mA. Q4 recibe del orden de (5−0.8)/(R12+R13)=0.45 mA y hunde unos 2.3 mA. Comprobar tiempos de borde/capacitancia con el arnés real. No se acredita PWM funcional porque T04 verificara otros pines.

SW1 es un DPDT ON-ON externo, de al menos 3 A DC/12 V en su especificación. ON une 1–2 y 4–5; OFF une 2–3 y 5–6; pin3 aislado. Polo1 desconecta +5V_SERVO. Polo2 pone SERVO_SIG a GND_ACT en OFF. Todas las resistencias que elevan el PWM a 5 V se alimentan del riel **conmutado**, evitando señal de 5 V con servo deliberadamente apagado. J13 es un conjunto de puntos de soldadura para este arnés, no un conector Dupont de potencia. J4 es bornera GND/+5V_SERVO/SIG, con adaptador de cable a tres pines macho 2.54 mm para la hembra del SG90. Identificar marrón/negro, rojo y naranja/amarillo en la pieza real.

No se garantiza ausencia de transitorios de encendido, rebotes de SW1 o movimientos del servo por este análisis estático. Encender con SW1 OFF; sólo habilitar después de establecer PWM válido y comprobar señal, con mecanismo descargado. Abrir EN_C2 no detiene el servo: para mantenimiento usar SW1 y retirar alimentación. Nunca poner un interruptor en el retorno del servo dejando su señal activa.

RX: final de carrera SW2 COM → J7.1 GND_LOGIC; NO → J7.2 MECH_RAW; NC libre. R19=4.7 kΩ a 3.3 V y C5=100 nF a tierra dan τ=0.47 ms. Reposo/abierto alto; contacto cerrado bajo. TP7 permite medir. EN_C2 → R22=1 kΩ → JP6 → P9_24. El RC atenúa rebotes rápidos, no garantiza eliminarlos ni sustituye la validación temporal. No se ha diseñado la mecánica del nylon.

## Reloj aislado, un circuito por sentido

P8_11 → R28=2.2 kΩ → base Q5 2N3904; R29=47 kΩ base-emisor a GND_LOGIC. Q5 hunde corriente del LED remoto. +3V3_LOGIC → R31=270 Ω → J9.1 CLK_TX+; J9.2 CLK_TX− → colector Q5. **Se envían dos conductores**, ida y retorno del LED; ninguno se conecta al GND de la placa receptora.

Conexión A→B: J9.A.1 → J8.B.1; J9.A.2 → J8.B.2. B→A análoga, en otro par. En cada RX, J8.1 va al ánodo U2.1 y J8.2 al cátodo U2.2. D2=1N4148 antiparalelo: ánodo en U2.2 y banda en U2.1. U2.3 emisor a GND_LOGIC local; U2.4 colector a R26=4.7 kΩ a 3.3 V. Colector → R27=1 kΩ → JP7 → P8_15, con TP8 antes del enlace. TP10 muestra el CLK TX original. Reposo Q5 apagado → RX alto; pulso luminoso → RX bajo. El receptor debe normalizar esa inversión.

Con 3.3 V ±5 %, R31 ±5 %, Vf LED 1.0–1.4 V y VCE 0.1–0.2 V, IF de diseño es 5.4–9.2 mA. El GPIO alimenta la base (~1.14 mA nominal), no el LED directamente. R28=2.2 kΩ proporciona aproximadamente 0.97 mA de base incluso con VOH=3.135 V, VBE=0.85 V y resistencia +5 %, descontando R29; así el objetivo de β forzada permanece por debajo de 10 frente a 9.2 mA. Comprobar VOH real del GPIO antes de aceptar esa hipótesis. R26 exige aproximadamente 0.66 mA en bajo. El CTR de catálogo del PC817 se especifica bajo condiciones concretas; no certifica saturación y tiempos a 3.3 V en este montaje. Medir ancho mínimo, retardo y recuperación antes de aumentar frecuencia.

El reloj de revisión102 empieza a 1 Hz y usa anchos relativos al período; esas funciones no obligan a modular una alimentación de red ni a añadir Powerline. Este circuito transporta el reloj lógico aislado y su duración. No lleva el texto. El límite de frecuencia se obtiene de la suma/máximo pertinente de retardos reales y márgenes, no de la frecuencia nominal del PRU.

La isla remota de U2/D2/J8 no recibe cobre o cable local. La placa no está diseñada para red eléctrica ni se certifica aislamiento de seguridad. **Si ambas BBB se conectan por USB al mismo PC, sus tierras pueden unirse a través del PC**: el opto sigue aislando el camino de señal, pero no se puede afirmar aislamiento galvánico total del sistema. No añadir además un cable GND entre nodos.

## Selectores EN y enlaces de prueba

JP10=EN_C0, JP11=EN_C1, JP12=EN_C2: pin1 RAW, pin2 seleccionado, pin3 GND_LOGIC. Puente 1–2 = habilitado; puente 2–3 = deshabilitado. Sin puente, R23/R24/R25=100 kΩ mantienen seleccionado bajo. No se une RAW a tierra: se desconecta RAW del GPIO y se fija sólo la entrada seleccionada. Las resistencias de 1 kΩ quedan entre selección y enlace GPIO. Usar capuchones de puente aislados, no puntas sueltas durante funcionamiento.

Estos selectores permiten probar por separado los ocho estados de tres entradas y no afectan el reloj. En A deshabilitan recepción B→A; en B, A→B. Para bloquear un medio en ambos sentidos, actuar en ambos nodos. Un nivel fijo no equivale inmediatamente a “canal muerto”: la validación matricial/pilotos de revisión102 debe detectar la falta de patrón. Con entrada activa baja, cero puede representar actividad permanente; los patrones variables siguen distinguiendo el fallo. No se promete detección instantánea ni resultado de protocolo a partir del selector solamente.

JP4/JP5/JP6/JP7 son enlaces GPIO que se dejan **abiertos antes de medir niveles**. No cumplen la misma función que EN. Los valores estables en el conector de la BBB sólo están definidos cuando se cierran esos enlaces; con ellos abiertos la BBB queda deliberadamente desconectada y sus modos internos requieren la configuración futura. TP1=5V_ACT; TP2=GND_ACT; TP3=3V3; TP4=GND_LOGIC; TP5/6/7=DO; TP8=CLK_RX_RAW; TP9=servo SIG; TP10=CLK_TX.

## Fuentes técnicas consultadas

- [BeagleBone Black: conectores y restricciones de alimentación de señales](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html).
- [BeagleBone Black: alimentación de expansión](https://docs.beagleboard.org/boards/beaglebone/black/ch08.html).
- [Microchip MCP23017](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf).
- [onsemi 2N3904](https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf) y [P2N2222A](https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf). No identifican el fabricante de los lotes recibidos.
- [TI LM393](https://www.ti.com/lit/ds/symlink/lm393.pdf). La hoja del comparador no es la hoja del módulo.
- [Sharp PC817](https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf).
- [Infineon IRLML6402](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlml6402-datasheet-en.pdf).
- [Vishay 1N4148](https://www.vishay.com/docs/81857/1n4148.pdf) y [1N5819](https://www.vishay.com/docs/88525/1n5817.pdf).
- [TowerPro SG90, referencia dimensional](https://towerpro.com.tw/product/sg90-7/). La ficha de esa variante no certifica consumo ni umbral del servo comprado.

Todas las resistencias fijas se especifican 1/4 W, tolerancia 5 % o mejor; las hojas anteriores y las medidas del lote deben resolver cualquier discrepancia antes de aprobar huellas o alimentación.
