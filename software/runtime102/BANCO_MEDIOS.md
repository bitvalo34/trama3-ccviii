> Integración vigente C0/C1 y ABI4: [PRIMERAS_TRAMAS_FISICAS.md](PRIMERAS_TRAMAS_FISICAS.md). El contenido inferior documenta la base anterior; sus referencias ABI3/ventana no integrada quedan históricas.

# Banco finito y evaluador de evidencias — 16/11/2026

Estado: propuesta de codigo en PR separada. No se ha ejecutado el lanzador nuevo
en Node ni compilado el modulo C en esta sesion: el entorno de ejecucion no
estaba disponible. No reemplaza el paquete v4 que esta pendiente de probar.

## Para que sirve

Separar problemas de reloj, C0 (luz), C1 (sonido) y C2 (mecanico) de problemas
de SYN/SFD, matrices, CRC o ACK. Cada TX emite exactamente 87 filas a 1 Hz,
mas la guarda existente de 2T. RX guarda observaciones independientes; no
recibe los valores esperados ni genera respuestas. El comparador offline usa
el plan y ambos logs. Un PASS del comparador no certifica todo T08/protocolo.

| Patron | Valores C0/C1/C2 |
| --- | --- |
| clock | Todos 0; sigue emitiendose reloj |
| c0, c1, c2 | Alterna 0/1 solo en ese canal |
| vectors | 000, 100, 010, 001, 111, 011, 101, 110 |
| matrix-00/01/10/11 | Repite las tres filas de la matriz del par |

Los enteros guardan C0 en bit 0, C1 en bit 1, C2 en bit 2.
87 filas son 29 bloques, no las 100 repeticiones por pareja exigidas por el
protocolo para aceptacion. Cuatro ejecuciones por pareja dan 116 bloques:
conservar todos los resultados, incluidos los fallidos. Los patrones de este
banco son diagnosticos sin pilotos ni SYN/SFD, por lo que tampoco sustituyen
los ensayos posteriores de tramas y medios interrumpidos.

## Verificacion de software antes de cualquier ensayo nuevo

Desde la raiz del checkout de esta PR, con Node 18+:

```sh
node software/runtime102/test-preparation.cjs
node software/runtime102/test-bench.cjs
node software/runtime102/test_launcher.cjs
node software/runtime102/test_supervisor.cjs
node software/runtime102/test.cjs
```

La prueba nueva test-preparation.cjs contiene 30 comprobaciones sinteticas
ejecutadas en V8 en esta sesion; falta ejecutarla en Node junto con las demas.
test-bench.cjs cubre READY, terminacion, timeout, captura y apagado con IO falso.
Tambien paso en V8 con sustitutos de assert/EventEmitter; esto no prueba Node,
subprocesos, archivos, permisos, drivers ni dispositivos.

Modulo C candidato (GCC en PC; salida en carpeta temporal):
```sh
gcc -std=c99 -Wall -Wextra -Werror software/runtime102/native/test_acoustic_window.c -o /tmp/test_acoustic_window
/tmp/test_acoustic_window
```

No se acredita esa compilacion hasta obtener su salida. En Windows usar una
ruta de salida local equivalente. No sustituir estos ensayos por py_compile.

## Futura operacion en BBB, tras revisar y validar la PR

Primero completar PRIMER_ENLACE.md: inventario, compilacion conjunta host/PRU,
perfil propio calibrado y recursos libres. Conserva todas las comprobaciones
de launcher/board_owner. No usar el checklist o las polaridades de la otra BBB.
El banco controla los tres actuadores aun si solo cambia uno; los otros reciben
su cero calibrado. No significa retirar cargas en caliente.

Ejemplo A transmite, B recibe; ejecutables y perfiles se pasan con rutas reales.
Usar directorios de log nuevos. En B iniciar RX antes que TX de A, y arrancar A
en menos de 90 segundos. El limite total por sesion es 180 segundos.

En B:
```sh
sudo node software/runtime102/bench-cli.cjs rx PERFIL_B NUEVO_LOG_B FIRMWARE HOST prueba01 none --electrical-checked --experimental-bench
```

En A:
```sh
node software/runtime102/bench-cli.cjs plan c0 prueba01 A plan-prueba01.json
sudo node software/runtime102/bench-cli.cjs tx PERFIL_A NUEVO_LOG_A FIRMWARE HOST prueba01 c0 --electrical-checked --experimental-bench
```

PERFIL_A/B, NUEVO_LOG_A/B, FIRMWARE y HOST son marcadores que se sustituyen.
No copiar literalmente estos marcadores. El modo hardware aun requiere las
validaciones previas; la bandera experimental no elimina los bloqueos.
RX se detiene tras 87 muestras, TX tras fin de guarda; ambos restauran recursos.
Ctrl+C tambien detiene. Un timeout o limpieza fallida no cuenta como exito.
Repetir invirtiendo los papeles A/B y con otro ID.

Con ambos logs en la computadora:
```sh
node software/runtime102/evaluate-evidence.cjs bench plan-prueba01.json NUEVO_LOG_A/A.jsonl NUEVO_LOG_B/B.jsonl reporte-prueba01.json
```

Se rechazan captura incompleta, saltos de secuencia/epoch, reloj fuera de bandas,
desacuerdo vectorial, planes distintos, ejecucion incompleta y errores de limpieza.
Los tiempos vienen del IEP nominal; no sustituyen un instrumento independiente.
No hay transporte de datos entre nodos por USB, TCP ni I2C interplaca.

## Evaluacion posterior del chat real

Crear una copia de manifest-enlace.example.json con los textos exactos y su orden.
Guardar esa expectativa antes del ensayo; no cambiarla para acomodar resultados.
Tras detener limpiamente ambos nodos:
```sh
node software/runtime102/evaluate-evidence.cjs pair manifest.json A.jsonl B.jsonl reporte-enlace.json
```

Valida entregas ordenadas, cantidad de confirmaciones y limpieza; distingue origen
simulation/hardware. Incluye hashes de las tres entradas. No correlaciona relojes
absolutos de BBB ni demuestra causalidad CRC->NACK->reintento. ABI3 no incluye un ID
compartido de ensayo: la asociacion de logs depende del operador y queda indicada.
Los archivos finales se crean exclusivamente; nunca sobrescribe evidencia previa.
