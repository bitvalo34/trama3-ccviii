# Software previsto

ARM/Linux ejecutará cuatro capas, web local, colas y planificación lógica. PRU0 será el controlador interno de PHY para reloj y captura; PWM hardware controlará el servo y MCP23017 atenderá salidas mediante drivers.

No hay implementación, firmware, RPMsg, pinmux ni instrucciones de ejecución. Incorporarlos en sus tareas correspondientes respetando el [ADR-0001](../docs/decisiones/ADR-0001-frontera-nodos-y-reloj.md).

La revisión de protocolo010 y gestión de frecuencia se definen en [ADR-0002](../docs/decisiones/ADR-0002-frecuencia-y-adaptacion.md): arranque1 Hz, período negociado, quiescencia, gestión E/F y conservación de SID/SEQ durante recuperación. Implementación pendiente de tareas T16/T18/T25/T28; no existe código ejecutable.
