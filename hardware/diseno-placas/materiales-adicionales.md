# Conciliación y BOM complementaria T51

Cantidades para **las dos interfaces**. Se usa la confirmación de recepción del pedido electrónico y se consideran disponibles para diseño los artículos del carrito y de la lista residual anterior, según instrucción de Erwin. No se cambia su estado de recepción en la BOM histórica. Ninguna foto aportada acredita por sí sola paso, corriente o dimensiones exactas.

## Cubierto con material existente o previsto

| Material | Necesario | Base disponible / observación |
|---|---:|---|
| BBB y cables propios | 2 | Existentes; fuera de la placa perforada |
| Perfboard nominal 90×150, una cara | 2 | Carrito considerado disponible; medir retícula/islas |
| MCP23017 y zócalo estrecho DIP28 | 2 de cada | No duplicar los zócalos ya mencionados y los del carrito |
| PC817 | 2 | Pedido recibido |
| 2N2222 | 4 | Q1/Q2 en A y B; quedan todos asignados |
| 2N3904 | 2 de los 6 requeridos | Los otros cuatro aparecen en la tabla adicional |
| LED, buzzer, LDR, módulo sonido, SG90, final de carrera | 2 de cada | Conservar; tensión, corriente y polaridad pendientes según componente |
| 1N4148 | 2 | D2 de cada optoacoplador |
| 330 Ω / 1 kΩ / 10 kΩ | 2 / 12 / 10 | Incluye resistencias confirmadas en casa; cubierto |
| 4.7 kΩ | 10 activas | Cubiertas. Las reservas I2C se dejan DNP; no se cuentan como instaladas |
| 100 nF / 1000 µF 16 V | 8 / 2 | C2–C5 y C1, respectivamente |
| Fusible 1 A y portafusible 5×20 | 2 de cada | Presencia confirmada; selección funcional todavía condicionada a T08 |
| Fuentes 5 V/2.5 A | 2 | Confirmadas; falta tipo de enchufe y polaridad/capacidad real |
| Borneras 3 vías | 6 | J4/J5/J6 por nodo; se usan todas |
| Borneras 2 vías | 12 de 14 | J1/J2/J3/J7/J8/J9/J14; faltan dos |
| Alambre sólido 22 AWG | ~5 m sumando compra prevista | Cableado inferior de potencia ~2.73 m total; reservar colores para retornos |
| Cable flexible 22 AWG | 2 m | Para arneses móviles; completar margen en lista adicional |
| Headers macho 40 pines | 2 tiras | Consumo previsto 76 pines: 70 de señal/puentes y 6 del adaptador servo; cortar sin perder contactos |
| Headers hembra 40 pines | 2 tiras | Para arneses según inserción real de módulos; no son conectores de potencia por defecto |
| Jumpers macho-hembra de 20 cm | 20 | Arnés BBB, diez por nodo; no alimentar servo con ellos |
| Kit65 jumpers, estaño, termoencogible, alambre de recorte | Existente/previsto | Herramientas/consumibles; no contar cada jumper como cable de potencia |
| Separadores aislantes y tornillos cortos | 8 + 8 | Previstos; no perforar placa sin comprobar sitio libre. Sin diseño de MDF |

390 Ω y 100 Ω compradas no son necesarias en este circuito. Se conservan como repuestos; no cambiarlas arbitrariamente por R31=270 Ω. Las armellas, nylon, resortes, tubos, espuma, escuadras y bases exteriores no forman parte de T51.

## Añadir para esta revisión

| Compra | Cantidad total | Especificación / motivo |
|---|---:|---|
| 2N3904 | 4 | TO-92 de fabricante identificado. Dos inversores por servo y un driver de reloj por nodo; seis en total contando los dos existentes |
| IRLML6402 | 2 | PMOS canal P, SOT23; no sustituir por N-MOS o un PMOS sin RDS especificado a −4.5 V |
| Adaptador SOT23 a terminales accesibles | 2 | Volumen reservado 10×10 mm, G/S/D identificados; comprobar geometría y capacidad térmica/corriente. No usar la corriente nominal del chip como rating del adaptador |
| 1N5819 | 2 | DO-41, protección de buzzer; verificar banda |
| Interruptor DPDT ON-ON | 2 | Dos polos/dos posiciones, capacidad documentada ≥3 A DC/12 V, contactos accesibles; corte de alimentación y señal del servo |
| Bornera de 2 vías | 2 | Paso **5.08 mm**, terminales aptos para retícula; rating ≥3 A y cable 22 AWG documentados |
| Capuchones de puente 2.54 mm | 14 | Seis EN y ocho enlaces GPIO. Comprar 20 si se quieren cuatro I2C y dos RESET de reserva; no montarlos todos por defecto |
| Resistencias 270 Ω | 2 | 1/4 W, ≤5 %, R31 |
| Resistencias 2.2 kΩ | 4 | 1/4 W, ≤5 %, R15 y R28 |
| Resistencias 47 kΩ | 8 | 1/4 W, ≤5 %, R11/R14/R16/R29 |
| Resistencias 100 kΩ | 8 | 1/4 W, ≤5 %, R23/R24/R25/R30 |
| Resistencias 4.7 kΩ | 0 obligatorias; 4 condicionadas | Sólo adquirir cuatro si finalmente se necesitan R2/R3; por defecto no montarlas |
| Cable aislado de montaje 26 AWG | 20 m | Varios colores. Aproximadamente 8.8 m en las dos caras inferiores, más arneses de señal y reserva. Aislamiento de diámetro exterior ≤0.8 mm para conservar las separaciones modeladas; no cable esmaltado sin aislamiento fiable |
| Cable flexible 22 AWG | 2 m adicionales | 1 m rojo + 1 m negro; total flexible disponible 4 m para entrada, SW1 y servo. Modelo inferior usa el alambre sólido ya disponible |

Los selectores de medios usan puentes removibles aislados sobre headers, una de las opciones de deshabilitación de esta revisión. No necesitan seis interruptores nuevos de panel. Los TP se realizan con diez lazos cortos de recorte por nodo; no consumen diez pines adicionales de header.

Los precios anteriores del inventario no se extienden a estos componentes nuevos. Esta tabla es una BOM de diseño, **no una cotización comercial ni una confirmación de existencias**. El pedido final debe esperar la verificación de adaptadores, borneras y corriente en T07/T08. No se necesita ESP32 ni un circuito físico para las matrices.

### Presupuesto de los controles nuevos

- Puente PINHEAD2P, paso 2.54 mm: la ficha de [La Electrónica](https://laelectronica.com.gt/products/jumper-para-2-pines) consultada el 9/11/2026 muestra Q0.50/unidad y 340 unidades; 14 cuestan Q7.00, o 20 cuestan Q10.00, sin envío. Confirmar disponibilidad al pagar. Se monta sobre JP4–JP7 y JP10–JP12; sólo conmuta señales, nunca potencia del servo. Volumen nominal reservado 5.08×2.54×3 mm, pendiente del producto real. La corriente por los selectores es del orden de decenas de microamperios en reposo; pedir la especificación del contacto al proveedor.
- SW1: reservar **Q30–Q60 por unidad**, Q60–Q120 por ambos, como estimación propia de presupuesto, no precio verificado. El modelo comercial sigue pendiente: debe ser DPDT ON-ON, ≥3 A DC/12 V, seis terminales soldables, con cuerpo exterior aproximado reservado de 20×15×20 mm y arnés a J13. Al ser externo no ocupa agujeros de la perfboard. No sustituirlo por un producto calificado únicamente en corriente alterna. El DPDT ON-OFF-ON local localizado no cumple la selección documentada y estaba agotado; no se recomienda comprarlo para este plano.

## Condicionados, no comprar sin identificar

- Adaptadores de las fuentes: dependen del conector real. No cortar ni improvisar polaridad.
- Fusible alternativo: elegir curva/corriente después de medir, no sumar uno de mayor amperaje por anticipado.
- Adaptadores de nivel para sensores: sólo si los módulos no cumplen a 3.3 V; requiere actualizar esquema y distribución, no un cable suelto a 5 V.
- Instrumentación: conseguir prestado un analizador lógico compatible con 3.3 V u osciloscopio para PWM/reloj/latencias. El multímetro basta para varias comprobaciones estáticas, no para certificar esos tiempos.
- Una tira macho extra es reserva opcional si se pierden contactos al cortar las dos previstas. Conectores de servo deben soportar el consumo medido; no se certifican por parecer iguales a un Dupont.

## Medidas críticas a enviar juntas

1. Placa: ancho/largo/espesor, número de filas/columnas, distancia entre centros de diez intervalos (dividir entre diez), diámetro de agujero, márgenes y foto de ambas caras con regla. Indicar islas separadas o pistas; agujeros de montaje existentes.
2. Zócalo y borneras: paso longitudinal, separación entre hileras del DIP28, ancho/largo/alto de borneras y diámetro de patas. Confirmar 5.00 o 5.08 mm sin forzarlas.
3. Electrolítico/portafusible/adaptador USB: diámetro y altura, paso de patas o longitud libre de cables; foto del fusible donde se lea rápido/lento y valor.
4. Fotos nítidas del marcado de 2N2222/2N3904/PC817, de los pines de cada LDR y módulo de sonido y de los conectores/etiquetas de las fuentes. No deducir el pinout del color de la PCB.
5. Si se compran Q6/adaptador/SW1: referencia exacta y dimensiones/contactos. Medir diámetro exterior de los cables aislados seleccionados; los recorridos 3D dependen de él.

Estas mediciones se piden para convertir la revisión aproximada en fabricable. No hace falta medir cada resistencia si todas corresponden al cuerpo y al paso documentados y pasan una comprobación en seco de una muestra.
