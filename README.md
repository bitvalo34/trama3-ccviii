# TRAMA 3 — CC VIII

**Erwin y Adrián — Comunicación de Computadoras VIII.** Proyecto de intercambio de texto entre dos equipos mediante tres medios físicos experimentales y un protocolo propio de cuatro capas.

## Estado al 27 de octubre de 2026

T01 tiene su propuesta arquitectónica documentada. **Consultas docentes respondidas: preguntas 1–3 aprobadas según Erwin; pregunta 4 aclarada: se acepta interpretar mediante la BeagleBone los múltiples pulsos de una emisión como un único bit por ciclo. Pendiente: revisión de Adrián.** No hay implementación ni validación experimental. Los PDF y Excel originales se conservaron.

Cada nodo contiene una BeagleBone Black existente, ARM/Linux, PRU0 interno, una placa perforada soldable y un PC como terminal USB local. El servidor y las cuatro capas residen en la BBB. **No se necesita adquirir ESP32** para esta arquitectura.

Por sentido: C0 óptico (LED y LDR/comparador), C1 acústico (buzzer y micrófono mediante manguera), C2 mecánico (SG90, nylon y final de carrera), y CLK mediante PC817. Se replican en sentido contrario: ocho canales unidireccionales. Los dos hilos de excitación de cada reloj constituyen un solo canal lógico propuesto, aceptado por el auxiliar según confirmación de Erwin.

El auxiliar acepta, según confirmación de Erwin, que la BeagleBone interprete los múltiples pulsos del KY-037 para obtener un solo bit por ciclo. Se mantienen los materiales previstos; falta caracterizar el sensor y fijar ventanas, umbrales, filtrado y rearme. Esta aprobación no valida parámetros concretos ni resultados experimentales.

La transmisión propuesta es **serial-paralela sobre medios heterogéneos**: tres bits por ciclo y sucesivos grupos en el tiempo. El [ADR-0002](docs/decisiones/ADR-0002-frecuencia-y-adaptacion.md) define frecuencia configurable desde1 Hz hasta perfiles medidos, negociación y reducción coordinada ante errores; es especificación, no implementación. [Impacto exacto en el tracker](docs/planificacion/impacto-aclaraciones-frecuencia.md).

Tecnologías previstas: Linux, PRU0, GPIO de 3,3 V, I2C local/MCP23017, PWM hardware y web local. No hay instrucciones de ejecución porque todavía no existe software del protocolo.

## Documentos y estructura

```text
TRAMA3-CCVIII/
├── README.md
├── .gitignore
├── docs/
│   ├── decisiones/ADR-0001-frontera-nodos-y-reloj.md
│   ├── decisiones/ADR-0002-frecuencia-y-adaptacion.md
│   ├── planificacion/impacto-aclaraciones-frecuencia.md
│   ├── consultas/aclaraciones-auxiliar.md
│   └── referencias/README.md
├── hardware/README.md
├── software/README.md
└── tests/README.md
```

- [ADR-0001: arquitectura, diagrama y dependencias](docs/decisiones/ADR-0001-frontera-nodos-y-reloj.md).
- [Consulta y actualización manual de T01](docs/consultas/aclaraciones-auxiliar.md).
- [Fuentes y trazabilidad](docs/referencias/README.md).

Siguiente tarea disponible: **T02, inspeccionar las dos BBB**, responsable Adrián y revisor Erwin, sin dependencias. T03 necesita T01 y T02; T04 depende de T02 y T06 de T04. No se iniciaron estas tareas. Medios, pines, sincronización y alimentación deben validarse en sus tareas correspondientes.

## Git y colaboración

Repositorio remoto creado por Erwin: [bitvalo34/trama3-ccviii](https://github.com/bitvalo34/trama3-ccviii). Visibilidad verificada: **pública**. No se modificó la visibilidad elegida por el usuario.

Mantener `main` revisada. Usar una rama por tarea, por ejemplo `t02-inspeccion-bbb`, y revisión del otro integrante antes de integrar. No hacen falta ramas permanentes adicionales.

Trabajar desde Ubuntu/WSL en `/home/erwin/Capa_Fisica/TRAMA3-CCVIII`. Allí ya existen identidad Git y autenticación de GitHub del usuario; la comprobación anterior desde Windows no las detectaba. Se utiliza la configuración existente, sin inventar identidad ni cambiar ajustes globales.

El remoto `origin` corresponde a `https://github.com/bitvalo34/trama3-ccviii.git`. Para trabajo posterior, después de revisar y confirmar cambios:

```sh
git status
git push
```

No versionar contraseñas, tokens ni archivos privados. La publicación del repositorio no implica aprobación completa de T01 ni ejecución de tareas posteriores.
