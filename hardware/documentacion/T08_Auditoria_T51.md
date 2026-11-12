# T08: auditoría del diseño T51 y límites de aceptación

Revisión documental: 12 de noviembre de 2026, Guatemala. Base examinada:
`5fcedfd5a163d26eb17d65eb7646ba5ffe9e6de7`, rama `t51-diseno-circuitos-3d`.
Esta auditoría no modifica esquemas, netlist, compras ni tracker. **T51 sigue sin
autorización para soldadura.** Una comprobación de conexiones no demuestra
comportamiento analógico, capacidad térmica ni seguridad de una placa construida.

## Procedencia y dependencias

- T02 aporta inspección e inventario de los dos sistemas; no contiene prueba PRU/PWM física.
- T04 documenta selección/restauración de pinmux en ambos nodos. No acredita pulsos.
- La rama elegida incluye revisión 102 y dependencias T03/T04/T51. No se reconstruye
  el diseño desde los tiempos históricos del protocolo anterior.
- Tracker consultado: `CCVIII_Tracker_y_Cronograma.xlsx`, versión recibida en este chat.
  T04 figura completada; T06 y T08 pendientes. T08 depende de T04 y T07. T51/T52
  conservan sus dependencias y revisión pendiente. No se cambió ninguna celda.
- Los nombres originales con sufijo `(3)` no se encontraron como adjuntos disponibles;
  se utilizaron el tracker recibido y los materiales versionados del repositorio.

## Hallazgos por circuito

| Circuito | Conectividad y cálculo revisados | Condición que falta comprobar físicamente |
|---|---|---|
| Entrada 5 V | J1/J11 alimentan +5V_RAW. Fusible por J14 conduce a +5V_FUSED; Q6 por J12 conduce a +5V_ACT | Elegir una sola entrada, polaridad real, corriente de conectores/cables y caída bajo carga |
| IRLML6402 | G=1, S=2, D=3; adaptador J12 debe respetarlos. D recibe alimentación fusionada y S entrega salida protegida; R30=100 kΩ lleva gate a GND | No invertir S/D por analogía con un interruptor de lado alto. Verificar adaptación SOT-23 y montaje real |
| Potencia Q6 | Con RDS(on) máx. 0.065 Ω a VGS=-4.5 V: I²R≈0.065 W a 1 A y 0.406 W a 2.5 A. Son estimaciones a condiciones de ficha, no temperaturas medidas | El encapsulado, cobre y adaptador limitan disipación; 2.5 A nominal de fuente no autoriza esa corriente en la placa |
| Fusible F1 | Provisional 1 A, fuente externa propuesta 5 V/2.5 A | Curva, I²t, arranque y capacidad de conductores deben coordinarse. No subir fusible para evitar disparos |
| Retornos NT1 | Una unión local GND_ACT/GND_LOGIC. Retorno del servo por potencia, no por BBB | Dos USB al mismo PC pueden unir tierras entre nodos; revisar instrumentos y fuentes antes de afirmar aislamiento |
| MCP23017 U1 | VDD9, VSS10, SCL12, SDA13; A0/A1/A2 a GND (0x20), RESET18 con pull-up, desacoplo 100 nF | Contrastar encapsulado, orientación, tensión y presupuesto total del riel 3.3 V. Puertos arrancan como entrada; pulldowns externos necesarios |
| I2C | Pull-ups R2/R3 de 4.7 kΩ previstos DNP y JP2/JP3 abiertos inicialmente | No duplicarlos sin conocer resistencia equivalente y tiempo de subida; no habilitar sólo porque I2C aparece en Linux |
| LED Q1 | R6=330 Ω: a 5 V, VF≈2 V y VCE≈0.1 V, I≈8.8 mA. Variando caídas puede acercarse a 10.7 mA; disipación de R6 inferior a unos 0.04 W en ese ejemplo | Medir LED/lote y polaridad; el cálculo no determina potencia óptica ni alcance |
| Buzzer Q2 | Driver separado; criterio de diseño 20 mA máximo. Diodo 1N5819 debe tener cátodo al positivo para carga inductiva | Tipo activo/pasivo, corriente real, polaridad del diodo y pinout del transistor. No asumir E-B-C universal para piezas vendidas como 2N2222 |
| Servo Q3/Q4 | Dos inversiones adaptan señal a 5 V; resistores 4.7 kΩ/2.2 kΩ y pulldowns 47 kΩ. Pull-ups ligados a +5V_SERVO | Verificar bordes y transitorios. No alimentar un servo desde GPIO ni usarlo como carga de prueba de fuente |
| Mantenimiento SW1 | DPDT corta alimentación servo y pone señal a tierra en OFF | Confirmar continuidad de ambos polos y medir J4.2/TP9 sin servo. El dibujo no prueba el interruptor comprado |
| PC817 U2 | Pines 1 ánodo, 2 cátodo, 3 emisor, 4 colector. Isla J8/U2-LED/D2 separada de retorno receptor. Pull-up 4.7 kΩ demanda alrededor de 0.66 mA | Excitación por Q5 y R31=270 Ω: estimación IF≈5.4–9.2 mA según caídas. CTR de ficha se especifica a IF=5 mA y VCE=5 V; no garantiza retardo ni comportamiento exacto a 3.3 V |
| Sensores | J5/J6 se alimentan de 3.3 V local; TP5/TP6 antes del GPIO | LDR y módulo acústico reales pueden funcionar mal a 3.3 V. Un resistor serie de 1 kΩ no convierte una salida de 5 V |
| Contacto mecánico | R19=4.7 kΩ y C5=100 nF: constante RC nominal 0.47 ms | No equivale a eliminación completa del rebote; comprobar umbral y forma de onda |
| Aislamiento GPIO | JP4..JP7 abiertos permiten medir lado fuente antes de conectar BBB; TP5..TP8 accesibles | Medir LOW/HIGH y picos con instrumento apropiado antes de cerrar un enlace |
| EN_C0/1/2 | JP10/11/12: 1 RAW, 2 SEL, 3 GND; habilitar 1–2, deshabilitar 2–3; pulldown 100 kΩ | Cambiar sin alimentación. Deshabilitar una señal no corta la potencia del medio ni prueba su parada mecánica inmediata |

La prueba `tests/hardware/audit_t51.py` contrasta redes exportadas con CSV, conexiones
críticas y separación de la isla PC817. Registra hashes de esquemas. No ejecuta ERC,
simulación SPICE ni revisión de huellas/fabricación; esas comprobaciones conservan
el estado de T51/T52. El PMOS de inversión **no es un bloqueo universal de retorno**.

## Encendido, apagado y retroalimentación

1. Inspección sin fuentes ni USB; revisar polaridad, NT1, jumpers, capacitores y piezas.
2. Sólo placa construida y revisada: servo desconectado, SW1 OFF, JP4..7 abiertos,
   EN deshabilitados y una única fuente de actuadores. No energizar una propuesta CAD.
3. Medir rieles y salidas con respecto al retorno local correspondiente.
4. Desconectar energía antes de cerrar GPIO; no aplicar señal a una BBB apagada.
5. Medir encendido/apagado con osciloscopio cuando haya fuentes externas. El promedio
   del multímetro y ausencia de mensajes del kernel no descartan retroalimentación.
6. USB e instrumentos pueden puentear nodos: no retirar tierras de protección para
   intentar aislarlos. T06 usa una única BBB sin enlace entre nodos.

J11 se limita al montaje de banco de baja carga previsto por T51; no respalda servo
ni suma de dos fuentes. El límite de ensayo de lógica de 75 mA reserva margen respecto
al máximo condicional de expansión de BBB; no es una medición ni autorización para
extraer la corriente nominal máxima publicada en cualquier condición.

## Rangos del formulario y su significado

| Punto | Criterio | Fundamento / límite de interpretación |
|---|---|---|
| Fuentes y riel 5 V | 4.75–5.25 V | Ventana conservadora del ensayo; no especificación universal de todos los servos/clones |
| P9_3, TP3, U1 y sensores 3.3 V | 3.135–3.465 V | Rango recomendado VDDSHV para dominio nominal 3.3 V en AM335x |
| GPIO LOW / HIGH | 0–0.8 V / 2.0–3.3 V | Umbrales LVCMOS 3.3 V y techo conservador del proyecto |
| GPIO PEAK / MIN | 0–3.3 V / 0–0.8 V | Osciloscopio; además PEAK no supera límite inferior del riel medido |
| Servo OFF y señal OFF | 0–0.1 V | Criterio conservador de comprobación sin servo conectado |
| Lógica / buzzer | ≤75 mA / ≤20 mA | Presupuestos de ensayo/diseño, no máximos absolutos del procesador |

Se exige que **todo el intervalo valor ± incertidumbre** quede dentro del rango.
Un intervalo que cruza cero o un límite no obtiene PASS: repetir con instrumento
apropiado o dejar pendiente; no recortar la incertidumbre para aprobarlo.
El máximo absoluto de entrada (riel I/O + 0.3 V) no es tensión de trabajo recomendada.
Ninguna entrada debe recibir 5 V. Un analizador lógico digital/PRU mide tiempos,
no amplitud ni sobreimpulso analógico. Valores ausentes siguen NOT_TESTED.

## Fuentes primarias consultadas

- [TI AM335x SPRS717L](https://www.ti.com/lit/ds/symlink/am3358.pdf): condiciones recomendadas, máximos absolutos y características LVCMOS, §§5.1, 5.3, 5.7.
- [BeagleBone Black, conectores](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html): pines, dominios y restricciones de alimentación/señales.
- [BeagleBone Black, expansión](https://docs.beagleboard.org/boards/beaglebone/black/ch08.html): presupuesto de alimentación de expansión condicionado.
- [Infineon IRLML6402](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlml6402-datasheet-en.pdf): pinout, RDS(on) y condiciones térmicas.
- [Microchip MCP23017](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf): alimentación, reset, pines y GPIO.
- [Sharp PC817](https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf): pines y condiciones de CTR.
- [Linux PWM](https://docs.kernel.org/driver-api/pwm.html): estado solicitado frente a señal real y ausencia de garantía de nivel al deshabilitar.

Los cálculos de esta auditoría son estimaciones del diseño, expresamente distintas
de las mediciones que registrará Erwin. El procedimiento completo y las puntas del
multímetro están en [Guia_Completa_T06_T08.md](Guia_Completa_T06_T08.md).
