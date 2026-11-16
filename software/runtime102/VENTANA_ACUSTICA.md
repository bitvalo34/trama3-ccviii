> Integración vigente C0/C1 y ABI4: [PRIMERAS_TRAMAS_FISICAS.md](PRIMERAS_TRAMAS_FISICAS.md). El contenido inferior documenta la base anterior; sus referencias ABI3/ventana no integrada quedan históricas.

# Recepcion acustica: modulo candidato y contrato de integracion

El protocolo 102 exige presencia durante una ventana para C1. El service.c de
ABI3 sigue haciendo una unica lectura a 0.8T. Esta entrega NO cambia ese firmware:
agrega acoustic-window.cjs y native/acoustic_window.h para revisar y probar el
acumulador antes de cambiar el contrato ARM/PRU.

## Algoritmo propuesto

- Recibe C1 ya normalizado por la polaridad medida del nodo.
- Cada tick inicia acumulador nuevo; integra tiempo activo dentro de [start,end).
- Decision 1 si tiempo activo >= minActive; de lo contrario 0.
- Una rafaga que acaba antes de 0.8T puede detectarse; ruido mas corto que el
  umbral no alcanza para aceptar presencia. Ruido repetitivo suficiente SI puede
  causar falso 1: este filtro no identifica la frecuencia del buzzer.
- Un hueco de muestreo superior a maxGap, tiempo invertido o ventana incompleta
  da error, nunca un cero inventado.
- No hay valores por defecto. start/end/minActive/maxGap son enteros en ticks
  relativos IEP, con end <= 0.8T y T=200000000. Los numeros pequenos de los tests
  son datos sinteticos, no calibracion.

## Integracion pendiente, antes de habilitar hardware

1. Medir salida DO del sensor propio en silencio, tono, ruido y con servo activo.
   Determinar polaridad, latencia, duracion de pulsos y falsas detecciones.
2. Versionar ABI, host, firmware, perfiles, mocks y contrato de log juntos.
   No introducir campos nuevos en ABI3 ni reutilizar binarios anteriores.
3. Pasar configuracion medida e identificada por nodo al iniciar; congelarla en
   la sesion. Registrar hashes, tiempos de ventana, umbral, muestras y decision.
4. Alimentar el acumulador desde cada poll de PRU y reiniciarlo por flanco CLK.
   Mantener C0/C2 y la entrega vectorial comun a 0.8T; registrar por separado
   R31 instantaneo y vector con C1 agregado. Normalized deja de significar
   exclusivamente una lectura instantanea: documentar explicitamente ese cambio.
5. Ante fallo del acumulador abortar captura con razon; no convertir a borrado
   automatico ni sustituir por valores esperados.
6. Compilar modelo C, firmware TI y host ARM; verificar watchdog, ring, STOP,
   envoltura del contador y maximo hueco de poll con el trabajo adicional.
7. Comparar en ambas BBB patrones C1 y matrices con todos los medios activos;
   conservar resultados fallidos. Solo entonces habilitar la ruta real.

Este modulo prepara implementacion y tests, pero la integracion del firmware
y su caracterizacion quedan pendientes. No se modifica el documento de protocolo
ni se declara una nueva frecuencia admitida.
