# Sustituciones locales — T51-P2-LOCAL

9 de noviembre de 2026. Sustituye las decisiones de compra de Q6, su adaptador y SW1 de T51-P1. El protocolo 102 no cambia. No se ha comprado ni energizado ningún componente durante esta revisión.

## Decisión

| Elemento anterior | Solución P2 para las dos placas | Efecto |
|---|---|---|
| IRLML6402 SOT23, canal P | 2 IRLZ44N TO-220, canal N | Protección trasladada al retorno; conexión nueva obligatoria |
| Adaptador SOT23 | Se elimina | Q6 se inserta directamente en tres perforaciones de 2.54 mm |
| DPDT ON-ON E-Switch importado | 2 Tettsa SW-287 ON-OFF-ON | Conserva ON y extremo OFF; centro abre ambos polos y R16 descarga señal |

Comprar sólo las piezas del diseño P2. No colocar IRLZ44N en el arnés anterior ni reutilizar el plano P1. Las referencias J11 y J12 se retiran; Q6 ocupa directamente el lugar de J12. No renumerar el resto de componentes al montar.

## Alimentación que se usará

El usuario puede disponer de adaptadores de pared o USB, pero no de fuente de laboratorio. Para P2 se eligen **dos adaptadores de pared de 5 V/2.5 A con salida aislada y flotante**, uno por interfaz. Todavía falta identificar marca, modelo, conector y polaridad. Las BBB conservan su alimentación Mini USB propia.

No usar USB del mismo PC para alimentar actuadores. No unir NEG_IN con GND_ACT/GND_LOGIC por cables, aleta metálica, chasis, salidas comunes de una fuente o periféricos. El cambio es válido sólo si el retorno de actuadores pasa por Q6. El hecho de tener dos adaptadores independientes no demuestra por sí solo aislamiento: comprobar documentación del producto. No medir resistencia sobre una fuente conectada a la red ni abrirla.

No se necesita comprar otra fuente si las dos disponibles cumplen esta condición. Si no cumplen, detener el montaje de esta etapa y revisar una protección en el positivo; no puentear Q6 para continuar. El adaptador USB auxiliar recibido se guarda sin montar. Esto evita una ruta que podría anular la protección nueva.

## Conexiones que cambian

| Referencia | P2 |
|---|---|
| J1.1 | Positivo 5 V de fuente aislada → F1 por J14 |
| J1.2 | NEG_IN, negativo de entrada; NO es GND_ACT |
| J14.2 / F1 salida | +5V_ACT directamente |
| Q6.1 G | +5V_ACT |
| Q6.2 D y aleta | NEG_IN |
| Q6.3 S | GND_ACT |
| R30 100 kΩ | +5V_ACT a GND_ACT, descarga G-S |
| NT1 | Sigue uniendo GND_ACT con GND_LOGIC dentro del nodo |
| J11 / MOD3 | Eliminados del montaje |
| J12 / adaptador | Eliminados; Q6 directo en placa |

Los pads de Q6 son C10, C11 y C12 para G, D y S. Consultar coordenadas.csv antes de montar; vista superior. El frente marcado se orienta hacia el borde superior y la aleta hacia el interior; comprobar el encapsulado real. Aislar la aleta de cualquier elemento conductor cercano. Volumen reservado de Q6: 10.7×4.8 mm, 21 mm de altura incluida la separación estimada de patas.

## Interruptor local

SW-287 tiene seis terminales y tres posiciones estables. Se reserva 30×25×55 mm para cuerpo/palanca/terminales, como aproximación, no plano del fabricante; agujero de panel publicado de 12 mm. Está fuera de la perfboard. Sus dos comunes se identifican con multímetro antes de soldar. Los números siguientes son del arnés J13; no se deducen mirando una fotografía del interruptor.

| Posición rotulada | Contactos funcionales | VCC servo | Señal |
|---|---|---|---|
| ON | 1–2 y 4–5 | Alimentada | PWM de doble inversor |
| CENTRO | Todos abiertos | Desconectada | Descarga por R16 de 47 kΩ |
| OFF, extremo opuesto | 2–3 y 5–6; 3 sin cable | Desconectada | Tierra directa |

Ambos polos deben cambiar juntos. Comprobar que no se puenteen ambos tiros durante el cambio. Usar el extremo OFF para mantenimiento y desconectar alimentación antes de intervenir. El centro no equivale a una conexión directa de la señal a tierra. Para 1 nF hipotético de cable/entrada, la descarga central tiene τ=47 µs; el lote y arnés reales requieren medición. La señal sigue de 5 V y sus pull-ups se alimentan después del interruptor.

## Fundamento y alcance de simulación

La topología N-FET en retorno está documentada en la nota de [Diotec sobre protección de polaridad](https://diotec.com/en/application/application-notes/application-note-reverse-polarity-protection.html?file=files/diotec/files/pdf/service/applications/Reverse+Polarity+Protection.pdf). El [datasheet Infineon IRLZ44N](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf) especifica 35 mΩ máximos a VGS=4 V y 25 °C. No confundir IRLZ44N con IRFZ44N ni elegir por el voltaje umbral solamente. Verificar fabricante del lote recibido.

El análisis usa ngspice incluido en KiCad y extrae del manifiesto los terminales y resistencias que cambian. Q6 se representa por un interruptor controlado, diodo interno genérico y resistencia de conducción de 25, 35 y 70 mΩ. La fuga se aproxima con 200 kΩ (25 µA a 5 V); no acredita todo el rango térmico. Las dos etapas 2N3904 usan un modelo BJT genérico y 1 nF hipotético de entrada/cable. No se ha simulado el motor interno, la carga mecánica ni un modelo oficial del SG90.

Se barren fuentes de 4.75/5/5.25 V, cargas nominales de 0.05/0.5/1/2.5 A y polaridad invertida en frío. También se ensayan PWM de 1.5 ms/20 ms con ON/centro/OFF, pérdida de 5 V con PWM todavía activo y descarga al centro. Dos fallos deliberados deben ser detectados: puente NEG_IN-GND y compuerta mal conectada. Los casos a 2.5 A son sensibilidad y no autorizan reemplazar el fusible provisional de 1 A.

La simulación no demuestra protección frente a inversión de cables mientras hay energía, retorno desde una segunda fuente, sobrecorriente o cortocircuito. Nunca realizar esas pruebas con BBB/servo conectados. T08 debe comprobar consumo, tensiones bajo carga, caída de contactos y fusible. La referencia de 4.8 V para el SG90 exige margen: si en J4 se mide menos durante arranque, no queda validado aunque el MOSFET esté funcionando. No compensar subiendo arbitrariamente la tensión de sensores o GPIO.

## Compra y recepción

La cotización local está en cotizacion-materiales-2026-11-09.md. Los nuevos repuestos suman Q90 para ambos nodos, sin transporte local. No requieren dirección de courier. Confirmar existencias al pagar: la última página abierta de Tettsa mostraba sólo dos SW-287.

Al recibir: anotar marcado Q6, verificar G/D/S y aislamiento de aleta; mapear SW1 en sus tres posiciones; medir dimensiones y comparar la plantilla. Sigue pendiente la revisión independiente T52 y las mediciones T07/T08. No se cierran tareas ni se declara montado el circuito por regenerar los archivos.
