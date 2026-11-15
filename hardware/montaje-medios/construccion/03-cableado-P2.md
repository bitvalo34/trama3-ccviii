# Cableado conforme a P2 y conciliación de placa real

## Condición para usar estas tablas

Esta guía es un arnés propuesto para **P2-LOCAL comprobada**. Si la placa real difiere, registrar origen/destino reales antes de fabricar el cable. La referencia pública P1 no sustituye la instantánea en fuentes/T51-P2-LOCAL. No se modifica el circuito ni la placa soldada por comodidad mecánica.

| P1 anterior | P2 usada aquí | Comprobación necesaria |
|---|---|---|
| IRLML6402 P-MOS en positivo | IRLZ44N N-MOS en retorno | Marcado, G/D/S y continuidad; no sustitución pin a pin |
| Retorno de entrada común interpretado como GND | NEG_IN separado de GND_ACT por Q6 | No puente por cable, aleta, fuente o instrumento |
| J11/MOD3 MicroUSB auxiliar | Eliminados | Sin conexión eléctrica auxiliar a actuadores |
| J12/adaptador SOT23 | Eliminado; Q6 directo | No conectar el antiguo arnés |
| Interruptor anterior | SW287 DPDT ON-OFF-ON | Identificar comunes y tiros de la unidad real |

Conservar módulo MicroUSB como repuesto. No retirar componentes que ya estén correctos. Correcciones imprescindibles se limitan a fallos confirmados: inversión de Q6, bypass de protección, corto de soldadura, nivel de 5 V hacia BBB, contacto de aleta con conductor, inversión de fuente o señales del servo mal conmutadas. Registrar reparación y repetir prueba afectada.

## Alimentación y retornos

BBB mantiene su alimentación individual. No sacar 5 V de BBB hacia actuadores. J10.1 recibe 3.3 V de P9_3 y J10.2 referencia P9_1. Cada interfaz requiere su propio adaptador 5 V/2.5A aislado y flotante identificado; confirmar conector y polaridad de la unidad. J1.1 es positivo; J1.2 es **NEG_IN**, no tierra lógica.

J1.1 -> J14.1 -> F1 -> J14.2 -> +5V_ACT. Q6: G(pin 1)=+5V_ACT; D(pin 2 y aleta)=NEG_IN; S(pin 3)=GND_ACT, conforme al encapsulado del lote confirmado. R30=100 kohm G-S. NT1 es la única unión prevista entre GND_ACT y GND_LOGIC dentro de cada nodo. No añadir retornos duplicados en arneses. El fusible 1A sigue provisional: no elevar su valor para evitar que se funda sin caracterizar carga y cable.

Dos USB al mismo PC pueden unir las tierras locales. Un osciloscopio con masa común también puede unir nodos o puentear Q6 si se conecta a NEG_IN y GND_ACT simultáneamente. Medir un nodo por vez y referenciar cada sonda correctamente; para medir diferencia de retorno usar método diferencial adecuado. No desconectar tierra protectora del instrumento. No abrir adaptadores de red ni medir resistencia con ellos energizados.

## J10 desmontable de diez conductores

| J10 | BBB | Función | Color sugerido |
|---|---|---|---|
| 1 | P9_3 | 3V3 lógica | naranja |
| 2 | P9_1 | GND_LOGIC local | negro |
| 3 | P9_19 | I2C SCL | amarillo |
| 4 | P9_20 | I2C SDA | verde |
| 5 | P9_14 | PWM_BBB3.3 V | blanco |
| 6 | P8_11 | CLK_TX | violeta |
| 7 | P9_27 | C0 óptico RX | azul |
| 8 | P8_16 | C1 acústico RX | gris |
| 9 | P9_24 | C2 mecánico RX | café |
| 10 | P8_15 | CLK_RX | rosa |

Usar hembra 2.54 compatible con header real, etiqueta pin 1 y retención de cable. Identificar P8/P9 por serigrafía; una rotación del MDF no cambia numeración. Las dimensiones/orden J10 derivan del manifiesto P2; confirmar continuidad extremo a extremo antes de conectarlo. Ruta de referencia: J10 cerca de(111.44,50..73) hacia corredor Y112,X177 y headers BBB. Preparar 300 mm por hilo como reserva, medir antes del corte. No soldar directamente sobre BBB. No poner 3.3 V externo en P9_3.

## Conectores de medios

J2.1=ánodo LED; J2.2=cátodo, driver de C0. La resistencia 330 ohm está en placa: no puentearla. J3.1=positivo buzzer; J3.2=retorno conmutado por Q2. Sólo buzzer activo 5 V compatible con driver provisional<=20mA; consumo real en T08.

J5.1=3V3, J5.2=GND_LOGIC, J5.3=DO óptico. J6.1=3V3, J6.2=GND_LOGIC, J6.3=DO acústico. Estos números identifican las borneras T51, **no el orden físico de pines del módulo**. Completar una foto y tabla por LDR-A, LDR-B, MIC-A y MIC-B con VCC/GND/DO/AO. No usar AO como DO. Alimentación sólo 3.3 V; si no conmuta, detener, caracterizar y resolver adaptación formal, nunca subirlo a 5 V con GPIO conectado.

J7.1=COM del final de carrera; J7.2=NO. NC se aísla. Reposo abierto produce alto; tensión que cierra NO produce bajo. RC4.7 kohm/100n F da 0.47 ms nominal y no elimina cualquier rebote. SW2 no es SW287.

J4.1=GND_ACT; J4.2=+5V_SERVO; J4.3=SERVO_SIG. Adaptador a conector servo hembra JR de tres contactos; verificar el orden real, incluso si los colores habituales son marrón/rojo/naranja. No pasar potencia por un Dupont de señal sin verificar su capacidad. Ajustar calibre/terminal a corriente medida, longitud y bornera.

## SW287 y señal del servo

Numeración funcional, a marcar tras ensayo de continuidad:

| Terminal SW1 | Desde | Función |
|---|---|---|
| 1 | J13.1 | +5V_ACT |
| 2 común polo 1 | J13.2 | +5V_SERVO |
| 3 | Sin cable | Aislar |
| 4 | J13.4 | PWM_5 V |
| 5 común polo 2 | J13.5 | SERVO_SIG |
| 6 | J13.6 | GND_ACT |

ON une 1-2 y 4-5. Centro abre todo; R16 descarga señal. OFF extremo une 2-3 y 5-6, con 3 aislado, por lo que corta positivo y fija señal a tierra local. Etiquetar ON/CENTRO/OFF después de medir; no asumir vista de terminales desde foto del vendedor. Aislar cada terminal con funda. Mantener pole 1 potencia y pole 2 señal distinguibles. PWM_5 V proviene del doble inversor P2, cuyas pull-ups se alimentan del riel conmutado. No llevar PWM5 V a BBB. Encender con SW1 OFF, establecer PWM válido comprobado, después habilitar servo sin nylon; para mantenimiento OFF más retirar alimentación.

## Relojes por pares aislados

AB: J9A.1 -> J8B.1 (ánodo U2B.1); J9A.2 -> J8B.2 (cátodo U2B.2). BA igual intercambiando nodos. Cada par es un circuito de LED remoto impulsado desde TX. No une GND de los equipos. U2.3 y U2.4 pertenecen al receptor local; comprobar isla separada de J8. D2 antiparalelo respeta su orientación P2.

P8_11 excita Q5 local; corriente al LED remoto produce bajo en P8_15 receptor. Registrar inversión. El par sólo transporta reloj y sus anchos de protocolo; ningún texto, USB, UART, SPI ni I2C cruza entre nodos. Rutas por bordes, lejos del brazo y de las mangueras. Usar etiquetas AB/+/- y BA/+/-; conectores de colores distintos o llaves que impidan cruce. Longitud de corte propuesta 1.1m por par, pendiente de disponibilidad.

## Selectores y puntos de medida

EN_C0=JP10, EN_C1=JP11, EN_C2=JP12:1-2 habilita,2-3 deshabilita recepción local. No cortar reloj. En A afectan B->A; en B afectan A->B. No detienen servo ni alimentación. JP4/JP5/JP6/JP7 son enlaces de prueba hacia BBB y permanecen abiertos hasta comprobar niveles. No confundirlos con EN.

TP1=5V_ACT;TP2=GND_ACT;TP3=3V3;TP4=GND_LOGIC;TP5=C0_RAW;TP6=C1_RAW;TP7=C2_RAW;TP8=CLK_RX_RAW;TP9=servo SIG;TP10=CLK_TX. Usar pinzas aisladas y apoyo de punta que no puenteen terminales. Guardar foto de ubicación real: el dibujo P2 es referencia, no identifica automáticamente cada cable de la foto.

## Rutas y longitudes

materiales/arneses.csv contiene una fila por conductor, origen, destino, calibre propuesto, longitud de reserva, color y terminal. No son longitudes medidas ni garantía eléctrica. Potencia por corredor trasero Y8 y derecho X285; señales por Y112-119; reloj por bordes X5/X295; derivaciones a sensores por detrás de sus acoples. La capa inferior de PCB queda para sus cables existentes, no para esconder nuevos arneses. Dejar curva de servicio 20-30 mm y alivio de tensión antes de cada terminal. Si se cruzan potencia/señal, hacerlo brevemente a 90 grados, sin lazos sobre mecanismos. I2C permanece corto y local; no aumentar sus pull-ups ni longitud sin medir flancos.

Antes de cerrar: comprobar continuidad de cada conductor, ausencia de continuidad entre adyacentes, pin 1 y polaridad, terminales sin cobre expuesto, ninguna rosca contra Q6 y ningún cable sujeto al nylon. Archivar tabla firmada de A y B. Las modificaciones eléctricas futuras se registran como revisión nueva y requieren regenerar arneses, no editar silenciosamente una etiqueta.
