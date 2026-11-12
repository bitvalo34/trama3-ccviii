# Validación de preparación T06/T08

Fecha: 12 de noviembre de 2026, Guatemala. **No se conectaron ni controlaron BBB.**
El alcance es preparación de software y revisión documental sobre la base T51
`5fcedfd5a163d26eb17d65eb7646ba5ffe9e6de7`.

## Evidencia sin hardware

- 46 pruebas Python de argumentos, análisis, CSV/JSON, estados, detección de rutas,
  propiedad, restauración, timeout y aceptación: ejecutadas correctamente en PC.
- Modelo C: incluye el firmware real con registros simulados y verifica siete
  escenarios (loopback, ausencia de flancos, instantáneas, STOP, parámetros
  inválidos, overflow y retrasos). No ejecuta instrucciones PRU ni calibra IEP.
- Auditoría estática: 63 comprobaciones de redes y hashes de ocho esquemas.
  No es ERC ni inspección de fabricación; conserva estado pendiente T51.
- Parser PowerShell: tres scripts, cero errores de sintaxis. No se ejecutó
  transporte contra una consola, puerto COM o SSH de Erwin.
- El host C se compiló con gcc en Linux x86 durante la preparación inicial,
  con `-std=c99 -O2 -Wall -Wextra -Werror`. No es compilación ARM.
- La sintaxis Python de producción se comprueba contra gramática 3.5; no equivale
  a ejecutar sobre el Python 3.5.3 instalado en BBB-B.

El script `tests/hardware/verify_pc.py --output DIRECTORIO_NUEVO` repite comprobaciones
y registra su salida en `validation.json`. Usar una instalación normal de Python;
la distribución embebida de Windows tiene rutas de importación aisladas por defecto.
El informe conserva BLOCKED cuando el entorno impide iniciar Bash; no convierte
una restricción del entorno en una comprobación de sintaxis aprobada.

## Limitaciones de ejecución

No está disponible aquí clpru/lnkpru compatible para enlazar el firmware destino.
El procedimiento `build-report.py` compila en cada BBB con su instalación TI y
gcc local, guarda la salida y comprueba el archivo generado. Compilación TI,
carga remoteproc, pinmux real, /dev/mem, PWM, señal PRU y restauración física
permanecen **NOT_TESTED** hasta ejecutar los procedimientos.

Durante la reanudación, el entorno Windows restringió el arranque de WSL y Bash
de Git. No se cambiaron permisos ni protecciones para forzarlos. También se
detectó que la carpeta temporal virtual de esa sesión no permitía renombrar
archivos; se repitieron las pruebas con TEMP/TMP dentro del espacio de trabajo,
manteniendo intacto el mecanismo atómico usado en Debian.

## Cobertura del pedido

| Requisito | Entregable | Comprobación / pendiente |
|---|---|---|
| PWM 50 Hz / 1, 1.5 y 2 ms | t06/run.py y bloque pwm/captura-pwm | Argumentos/lógica probados; señal pendiente |
| PRU generación/captura | firmware/main.c, abi.h, src/host.c | Modelo C; TI/ARM y BBB pendientes |
| Detección y restauración | resources.py, toolchain.py, cleanup.sh | Mocks de fallos y propiedad; sistema real pendiente |
| Debian 9/10 | Guía §§3–5, preflight y build-report | Interfaces detectadas en ejecución; no se fuerzan alternativas incompatibles |
| Auditoría eléctrica | T08_Auditoria_T51.md, audit_t51.py | Conectividad documental; mediciones pendientes |
| Medidas e incertidumbre | t08/mediciones.py y scripts CSV | Datos vacíos/simulados/fuera de rango probados |
| Transporte Windows / B sin red | ejecutar/*.ps1 | Parser correcto; transporte físico pendiente |
| Evidencias y cierre | seleccionar-evidencias.py, evaluar.py | Selección explícita y reanálisis; sin cierre automático |
| Paquete sin red en BBB | empaquetar.py | Fuentes y referencias incluidas; requiere herramientas ya instaladas |

## Criterio de entrega

Los ensayos de software no cierran T06/T08. Erwin debe realizar inspección inicial,
compilar en A/B, capturar loopback PRU y PWM, comprobar restauración, registrar
voltajes/inspecciones y conservar evidencia. Si la interfaz T51 todavía no existe
con revisión aprobada, su etapa se deja NOT_TESTED. No se actualiza el tracker
ni se hace merge por terminar esta preparación.
