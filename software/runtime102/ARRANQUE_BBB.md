# Lanzador por BBB: preparacion y limites

Implementado el 16 de noviembre de 2026. Probado en PC con procesos reales Node y
Python y un sistema de archivos que simula recursos. No ejecutado en las BBB.

## Prueba disponible ahora, sin placas

Desde cc8-trama3, indicar Python si no existe el comando python3:

```powershell
$env:TRAMA3_PYTHON = (Resolve-Path .\work\python\python.exe).Path
node .\repo\software\runtime102\launcher.cjs plan .\repo\software\runtime102\profiles\BBB-A.json
node .\repo\software\runtime102\launcher.cjs mock .\repo\software\runtime102\profiles\BBB-A.json .\evidencias\arranque-A-01 .\work\bbb-A-simulada-01
```

La ruta Python anterior corresponde al entorno de este proyecto; si se ejecuta
en otra maquina, sustituirla por su ejecutable Python. Ambos directorios de la
prueba deben ser nuevos y sus padres deben existir. Ctrl+C detiene y restaura.

plan solo lee el perfil y muestra el orden previsto y los bloqueos conocidos;
no inventaria la BBB, no modifica sysfs ni crea una autorizacion para energizar.
mock crea archivos bajo la raiz indicada, usa un firmware ficticio y un host de
prueba. No representa intercambio con otro nodo: queda esperando hasta parar.
El chat de dos nodos y fault-suite.cjs siguen disponibles como bancos separados.

## Orden de arranque implementado

1. Validar modo/perfil y crear log exclusivo.
2. Iniciar el proceso Python propietario de recursos. Crear su directorio de
   propiedad de forma exclusiva; nunca reemplazar uno existente.
3. En Linux, obtener tambien flock sobre /run/trama3-t06/lock para excluir T06
   mientras el runtime esta activo. Rechazar diarios pendientes de T06.
4. Revisar PRU0/PRU1 offline, PTP independiente del IEP, PWM libre, propietarios
   de GPIO/pinmux e I2C. Reutiliza Hardware/Transaction de T06 sin modificarlos.
5. Exportar solo el canal PWM propio, inicializar salidas inactivas y configurar
   entradas. Mantener P8_11 en gpio_pd; copiar firmware por hash y arrancar PRU0.
6. Iniciar host ARM y esperar ready con ABI3 y epoch correcto. Solo entonces
   conectar P8_11 a pruout e iniciar el supervisor de un unico nodo.
7. Ante parada: STOP al puente, apagado P2, terminar host propio, restaurar los
   recursos de la transaccion, terminar propietario y cerrar log.

El bloqueo I2C es cooperativo entre nuestras instancias. Se rechaza un driver
kernel en 2-0020, pero eso no prueba que otro programa no use /dev/i2c-2.
No ejecutar otras aplicaciones sobre estos recursos durante una sesion.

## Recuperacion y errores

Un fallo de arranque intenta deshacer las operaciones propias. La restauracion
se niega a usar estados de otro boot_id y no detiene firmware que haya cambiado
de propietario. Errores de limpieza conservan owner.json/resources.json cuando
corresponde y cleanup-errors.json; no se presentan como restauracion exitosa.

No hay borrado automatico de bloqueos viejos ni recuperacion ciega tras SIGKILL
o corte de alimentacion. Si el directorio /run/trama3-runtime102 permanece,
inspeccionar el diario y los recursos antes de otra sesion. No ejecutar T06
cleanup sobre ese diario: ademas hay estado P2 que T06 no administra.
Una interrupcion entre exportar y registrar PWM exige inspeccion manual; el
diario no es una transaccion atomica del kernel. Tras un reinicio no reutilizar
un diario anterior. Los mocks comprueban rutas de error, no fallos electricos.

## Ruta experimental Linux para cuando haya placas

La API launch({mode:'hardware', ...}) y el comando hardware estan implementados.
Los perfiles distribuidos conservan calibration.status=PENDING y
mcp_reset_confirmed=false, por lo que el arranque fisico esta bloqueado.
No cambiar estos datos sin las comprobaciones reales correspondientes.

Precondiciones pendientes: compilacion TI/ARM; mapa y ABI3; perfil de la placa;
calibracion P2; confirmacion de alimentacion/montaje; MCP recien reiniciado BANK0;
P9_19/P9_20 ya en I2C; Node compatible y acceso root. El host requiere rebuild
para emitir el mensaje ready; los hosts de versiones anteriores no sirven.

Referencia del comando, para la futura sesion validada, desde repo en la BBB:

```sh
sudo node software/runtime102/launcher.cjs hardware PERFIL.json DIRECTORIO_LOG_NUEVO RUNTIME_PRU.out RUNTIME_HOST --electrical-checked --coordinator
```

Usar --coordinator solo en A; B espera el HELLO. No instala servicios de arranque
automatico ni actualiza Debian. El comando es experimental, no se ha probado en
Linux ARM y no equivale a una autorizacion de prueba P2. El supervisor expone
send() para integracion; este CLI aun no presenta el chat web de un nodo fisico.

Si aparecen PWM exportados por udev (como en la BBB-A), se bloquea sin liberarlos.
Los parametros de I2C y del pinmux se corroboraran con inventario real. El MCP
se devuelve con salidas apagadas y puerto A de entrada, partiendo de reset
confirmado. Desactivar PWM no garantiza un nivel electrico bajo en el pin.

## Verificacion reproducible

```text
python3 software/runtime102/test_board_owner.py
node software/runtime102/test_launcher.cjs
```

Once casos Python cubren ciclo, doble instancia, PRU/PWM ajenos, error parcial,
fallo de pin, cambio de propietario, reboot, limpieza fallida y bloqueo previo.
Los casos Node arrancan procesos reales contra archivos simulados, verifican
timeout/salida/ABI del puente, caida durante ejecucion y rechazo de perfil sin
calibrar. Windows simula pwm0; el reconocimiento de pwm-4:0 TI procede del
helper T06 reutilizado, sin afirmar una nueva comprobacion sobre ese kernel.

## Referencia fisica contrastada

El PR #5 contiene P1. La fuente P2 usada es el PR #7, commit
9ba0bcaa271740effe206ec1ef79b72c070168e6, conservada en
hardware/documentacion/fuentes-P2. No confundirla con hardware/diseno-placas,
que conserva el circuito P1 en aquella rama. P2 cambia Q6 por IRLZ44N en el
retorno, retira J11/J12 y utiliza SW-287 ON-OFF-ON. Estas condiciones electricas
no se verifican con software; tampoco se modifica el tracker ni se cierra T08.

El PC817 invierte CLK RX: en la mascara normalizada bit 3 debe estar activo.
Los perfiles pendientes conservan rx_invert=0 como valor sin calibrar y NO son
aptos para hardware. Para la ruta fisica se exige hardware_revision=T51-P2-LOCAL,
bit 3 activo y calibration.rx_invert coincidente con rx_invert, con evidencia
real de las polaridades. C0/C1 requieren medicion; C2 cerrado es bajo en P2.
No copiar la mascara del loopback directo al circuito con optoacoplador.

Tambien se exige calibration.i2c_device coincidente con /dev/i2c-2: el arnes
confirma P9_19/P9_20, pero no acredita la numeracion del adaptador del kernel.
La evidencia de calibracion debe registrar esa comprobacion en cada BBB.
El validador comprueba coherencia declarada, no autentica la medicion.
