# Validacion del borrador — 16/11/2026

Base remota inspeccionada: afabfab39accf28e26edc1bf25a0095062029863 (PR #9).
Esta PR es un avance separado; no se ha fusionado.

| Comprobacion | Resultado y limite |
| --- | --- |
| Parseo de todos los archivos CJS nuevos/modificados | PASS en V8, sin ejecutar CLI |
| test-preparation.cjs | 30 comprobaciones PASS en V8 con cargador CommonJS en memoria |
| test-bench.cjs | PASS en V8 con IO falso y sustitutos de assert/EventEmitter |
| Node real, procesos Python, launcher y regresiones | PENDIENTE: entorno local no disponible |
| Header C candidato y test C | PENDIENTE de compilacion GCC/TI |
| Firmware ABI3 en ambas BBB | PENDIENTE, sin cambios de service.c en esta entrega |
| Captura, reloj, medios fisicos y logs reales | NOT_TESTED en esta entrega |

Las pruebas de V8 utilizaron las fuentes publicadas de core/engine/Endpoint,
StreamDecoder y Supervisor; no inventaron un receptor que conociera los vectores
del transmisor. Los datos de las pruebas son sinteticos y no se guardan como
evidencia de una placa.

El banco usa la restauracion del supervisor existente, y el lanzador recibe una
fabrica opcional para crear una sesion de banco. La ruta por defecto sigue creando
Supervisor. Antes de merge, ejecutar test_launcher.cjs, test_supervisor.cjs,
test_integration.cjs, test_terminal.cjs, test_profiles_hardware.cjs y test.cjs,
ademas de las pruebas nuevas. No descargar esta rama como reemplazo validado de v4.

La ventana acustica es un modulo candidato aislado; la ABI y el firmware activos
siguen leyendo C1 instantaneamente. VENTANA_ACUSTICA.md enumera la integracion
necesaria. No cerrar este pendiente por la mera existencia del acumulador.
