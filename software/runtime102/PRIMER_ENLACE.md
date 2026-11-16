# Primera sesion fisica: preparar, diagnosticar y enviar

El operador reporta validacion de caminos y niveles electricos de las placas;
su especificacion y evidencia detallada estan pendientes de incorporacion.
Esto permite planificar ensayos funcionales, pero no demuestra tiempos,
polaridades normalizadas ni asentamiento del servo. T08 no se cierra aqui.

## 1. Diagnostico que se puede ejecutar ahora en cada BBB

Desde la raiz del checkout, sustituir BBB-A por BBB-B en la segunda placa:

```sh
python3 software/runtime102/preflight-runtime.py --board BBB-A --output diagnostico-BBB-A-01.json
bash software/runtime102/native/build.sh > compilacion-BBB-A-01.log 2>&1
echo $?
cat compilacion-BBB-A-01.log
```

Usar nombres nuevos para conservar intentos. El inventario nunca escribe sysfs
ni abre buses I2C; el archivo de salida se crea exclusivamente. La compilacion
solo genera archivos locales. No carga firmware. Revisar errores, versiones,
mapa PRU/IRAM y ABI3 antes de continuar. Node 18+ sigue siendo requisito del
runtime: comprobar su ejecucion real en el Debian de cada placa, no solo copiarlo.

## 2. Antes de usar la ruta hardware

Completar el perfil de cada placa con evidencia real, segun ARRANQUE_BBB.md:
revision P2, rx_invert y calibration.rx_invert iguales (CLK PC817 invertido,
bit3), adaptador I2C corroborado, extremos del servo y tiempo de asentamiento,
MCP recien reiniciado. No editar MEASURED para eludir una comprobacion.
Las plantillas siguen PENDING. No basta comprobar tension estatica para fijar
estos parametros. El receptor acustico actual usa muestra puntual a 0.8T;
si DO pulsa, hace falta caracterizar e implementar la ventana antes de aceptar
ese medio. Este entregable no implementa aun el banco de patrones aislados.

Primero verificar reloj por PC817 A->B y B->A, despues patrones por medio y
matrices antes de intentar un mensaje completo. Mantener el montaje P2 y los
arneses del PR #7; no convertirlo en un loopback GPIO entre placas.

## 3. Consola de un nodo conectada al lanzador

terminal.cjs usa el mismo Supervisor, propietario P2, host y firmware del
lanzador. No crea el nodo remoto ni usa red IP para transportar el mensaje.
Se elige esta consola para el primer enlace; el chat web simulado sigue aparte.

Ensayo local sin hardware (PowerShell desde cc8-trama3):

```powershell
$env:TRAMA3_PYTHON = (Resolve-Path .\work\python\python.exe).Path
node .\repo\software\runtime102\terminal.cjs mock .\repo\software\runtime102\profiles\BBB-B.json .\evidencias\terminal-B-01 .\work\terminal-B-mock-01
```

Los padres de los directorios deben existir; los directorios finales deben ser
nuevos. Introducir `status`, `send Hola`, `stop`. En mock no hay par remoto y
send se rechaza por falta de CONNECTED: es el resultado esperado, no un fallo
de sensores. Ctrl+C o cerrar la entrada inicia parada y restauracion.

Solo tras compilar y revisar perfiles/ensayos previos, comandos de referencia
desde la raiz en las BBB (PERFIL y LOG son rutas elegidas por operador):

```sh
# B primero: espera apertura del enlace
sudo node software/runtime102/terminal.cjs hardware PERFIL-B.json LOG-B-01 software/runtime102/native/build/runtime102-pru0.out software/runtime102/native/build/runtime102-host --electrical-checked
# A en su propia BBB: inicia HELLO
sudo node software/runtime102/terminal.cjs hardware PERFIL-A.json LOG-A-01 software/runtime102/native/build/runtime102-pru0.out software/runtime102/native/build/runtime102-host --electrical-checked --coordinator
```

No son comandos para ejecutar con perfiles pendientes. Durante el enlace:

- `status`: estado local y de protocolo, reintentos y mensajes recibidos.
- Esperar CONNECTED en ambas consolas; iniciar con `send A` en A.
- SUBMITTED solo significa solicitud aceptada. Revisar MESSAGE_CONFIRMED en el
  JSONL del emisor y DELIVERY en receptor; no presentar pendiente como entregado.
- Probar despues B->A, y luego envio bidireccional.
- `stop`: devolver recursos; conservar STOPPED y CLEANUP sin errores. Ante
  CLEANUP_FAILED conservar el diario y diagnosticar, no forzar otra instancia.

Los registros estan en LOG/A.jsonl o LOG/B.jsonl. Capturas y respuestas del
protocolo quedan ahi. Guardar commit, perfiles, logs completos y build/SHA256SUMS
de ambas BBB. physical_status permanece NOT_TESTED hasta evaluar evidencia;
un proceso activo o texto SUBMITTED no certifican comunicacion.

A 1 Hz cada trama ocupa 87 ticks mas guarda. Un caracter requiere varios
intercambios y unos 890 s nominales con sesion abierta. No confundir esa espera
con un bloqueo ni subir frecuencia sin caracterizacion.
