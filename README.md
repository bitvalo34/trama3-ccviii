# TRAMA 3

Proyecto de Comunicación de Computadoras VIII, desarrollado por Erwin y Adrián.

Queremos comunicar dos BeagleBone Black usando luz, sonido y tensión en un hilo de nylon. La idea es enviar mensajes de texto desde un chat y ver cómo llegan al otro equipo a través de los tres medios, incluyendo qué pasa cuando hay interferencias.

## Cómo lo vamos a hacer

Ya contamos con las dos BeagleBone Black. Cada una ejecutará el protocolo y su servidor web. Conectaremos una computadora por USB a cada placa para escribir y leer los mensajes; la comunicación entre las BeagleBone pasará por los medios del proyecto.

En cada dirección tendremos estos canales:

| Canal | Componentes | Qué transmite |
|---|---|---|
| C0 — Luz | LED y receptor con LDR, dentro de un tubo opaco | Luz encendida o apagada |
| C1 — Sonido | Buzzer y sensor KY-037, unidos por una manguera | Presencia o ausencia de sonido |
| C2 — Mecánico | Servo SG90, nylon y final de carrera | Tensión o liberación del hilo |
| Reloj | PRU0 y optoacoplador PC817 | Los tiempos de lectura de los bits |

Vamos a repetir los transmisores y receptores para tener comunicación en ambos sentidos. Son cuatro canales por dirección: tres para datos y uno para reloj. El reloj usará un par de conductores por sentido, sin unir las tierras de los dos equipos.

Con tres medios activos, cada ciclo llevará tres bits, uno por medio; con dos se envían pares y con uno, un bit por ciclo. Los siguientes grupos se enviarán en los ciclos siguientes hasta completar la trama. Por eso describimos la transmisión como serial-paralela: combina varios bits al mismo tiempo con una secuencia de grupos.

La PRU0, que ya viene dentro de la BeagleBone, se encargará del reloj y de las lecturas que necesitan tiempos precisos. Linux manejará el chat y la lógica del protocolo. No tenemos previsto agregar un ESP32. Las interfaces se montarán en placas perforadas soldables.

## Frecuencia e interferencias

El reloj deberá poder bajar hasta 1 Hz para observar la transmisión paso a paso. Después aumentaremos la frecuencia hasta encontrar el máximo que soporten los tres medios de forma confiable. Ese máximo todavía lo tenemos que medir.

También queremos detectar errores, retransmitir cuando haga falta y reducir la velocidad de forma coordinada si los errores se repiten. Si un medio queda bloqueado o desconectado, el sistema deberá indicar el fallo; bajar la frecuencia no resolverá cualquier interferencia.

Para sonido, la BeagleBone interpretará los pulsos del KY-037 para obtener un solo bit por ciclo. El auxiliar ya nos confirmó que podemos hacerlo así. Nos falta probar el sensor y ajustar la detección.

## En qué vamos

Por ahora tenemos documentada la arquitectura y las aclaraciones del auxiliar sobre el reloj, los medios y el uso del USB como conexión local. También definimos los cambios para ajustar la frecuencia y responder a interferencias.

El protocolo no está implementado ni validado físicamente en las placas; sí realizamos la inspección básica. Falta la revisión de Adrián para cerrar T01. T02 quedó cerrada el 07/11/2026 como inspección básica con observaciones. Los pendientes de configuración de B y prueba PRU pasan a T04.

## Documentación

- [Inventario y conciliación T03](hardware/inventario/T03-conciliacion-materiales.md).
- [Excel de materiales con conciliación](hardware/inventario/CCVIII_Materiales_y_Compras_T03.xlsx).

- [Simulador y pruebas de la revisión 101](software/simulador/README.md).
- [Decisión sobre reloj y frecuencias por sentido](docs/decisiones/ADR-0003-reloj-modulado-y-direcciones.md).

- [Protocolo revisión 101](docs/protocolo/TRAMA3_Protocolo_y_Medios_Revision_101.docx): base de implementación con reparto dinámico, reloj modulado y frecuencias independientes por sentido. Incorpora la aclaración del auxiliar del 07/11/2026; la validación física sigue pendiente.
- [Cierre de T02](hardware/inspecciones/T02-inspeccion-beaglebone.md).


- [Arquitectura y frontera de los equipos](docs/decisiones/ADR-0001-frontera-nodos-y-reloj.md).
- [Frecuencia configurable y adaptación](docs/decisiones/ADR-0002-frecuencia-y-adaptacion.md).
- [Aclaraciones del auxiliar](docs/consultas/aclaraciones-auxiliar.md).
- [Cambios que corresponden a cada tarea del tracker](docs/planificacion/impacto-aclaraciones-frecuencia.md).
- [Referencias del proyecto](docs/referencias/README.md).

## Organización del repositorio

```text
docs/       Decisiones, consultas y planificación
hardware/   Circuitos, conexiones y montaje
software/   Protocolo, firmware PRU y servidor web
tests/      Pruebas y evidencias
```

Por ahora estas carpetas contienen la documentación inicial. Iremos agregando el código, los esquemas y los resultados conforme avancemos.

Para trabajar entre los dos usaremos una rama por tarea, por ejemplo `t02-inspeccion-bbb`, y revisaremos los cambios antes de pasarlos a `main`.
