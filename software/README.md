# Software previsto

ARM/Linux ejecutará cuatro capas, web local, colas y planificación lógica. PRU0 será el controlador interno de PHY para reloj y captura; PWM hardware controlará el servo y MCP23017 atenderá salidas mediante drivers.

No hay implementación, firmware, RPMsg, pinmux ni instrucciones de ejecución. Incorporarlos en sus tareas correspondientes respetando el [ADR-0001](../docs/decisiones/ADR-0001-frontera-nodos-y-reloj.md).
