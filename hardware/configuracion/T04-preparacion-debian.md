# T04 — Preparación de Debian y ejecución completa

Fecha de preparación: 08/11/2026. Base: revisión 101. Responsable del tracker: Adrián; revisor en el tracker: Erwin. Ejecutor físico: Erwin; revisión técnica prevista: Adrián. No se cambiaron esas asignaciones en el Excel.

**Leer y ejecutar esta guía completa una vez por placa, primero A y después B. Enviar al final ambos registros y el inventario.** Si un bloque indica STOP, omitir las acciones que dependan de ese resultado y continuar con la otra placa o el inventario. No hace falta enviar capturas entre comandos.

## 1. Resultado de la preparación

Se inspeccionó main (72188e8), sus ramas, commits y PR abiertos: no había cambios locales ni PR pendientes. Se conservaron T01, T02, ADR y protocolo 101. El pedido está conciliado en T03. El tracker de entrada no se modificó.

Desde el PC no apareció un dispositivo BeagleBone/USB Serial en la consulta y la conexión SSH por USB agotó el tiempo. Esto sólo prueba ausencia de acceso en ese momento. **No se ejecutaron estos scripts en A o B ni se modificó Debian en esta sesión.** Las pruebas locales del código no acreditan hardware. Se comprobó sintaxis Bash/PowerShell y seis casos con sysfs simulado: selección/restauración, PRU ocupado, UART seleccionada, modo ausente, fallo a mitad del cambio y ausencia de confirmación de placa sin cargas. Los seis conservaron/restauraron los estados esperados. El transporte serial sólo se validó sintácticamente; requiere prueba real.

## 2. Decisión sobre el sistema operativo

Mantener temporalmente **A con Debian 10 y B con Debian 9**, trabajando por USB local y sin exponer servicios a Internet. Verificar primero pinmux con el software existente. No instalar VS Code Server. No ejecutar apt upgrade, cambios masivos de repositorios, flasheo, formateo o cambios de bootloader.

| Estrategia | Ventaja | Riesgo y decisión |
|---|---|---|
| A: conservar ambos temporalmente | Accesos y herramientas ya conocidos; menor riesgo de perder arranque | Diferentes kernels y sistemas antiguos; opción elegida para T04 mínima |
| B: imagen IoT común reciente | Mayor reproducibilidad y paquetes vigentes | Validar pinmux/PRU/USB y tamaño; exige recuperación y pruebas; no ejecutar hoy |
| C: probar imagen nueva en microSD de B y conservar A | Ensayar sin sobrescribir eMMC y comparar | Requiere microSD/lector; alternativa si B no permite preparación mínima |

Debian 9 y 10 ya terminaron su soporte LTS comunitario; conservarlos es una medida temporal, no recomendación de despliegue permanente. Fuentes: [ciclo de Debian](https://www.debian.org/releases/), [fin de LTS Buster](https://www.debian.org/News/2024/20240615).

El catálogo oficial ofrece imágenes IoT específicas para **BeagleBone Black AM335x**, incluyendo Debian 12.13 con kernel 5.10-ti (23/04/2026). Es una candidata para ensayo desde microSD, no una imagen validada por este proyecto. No usar imágenes de BeagleBone AI, AI-64 o PocketBeagle2. [Catálogo oficial](https://www.beagleboard.org/distros). La versión más nueva no garantiza compatibilidad con el config-pin/remoteproc de nuestros scripts.

Si se decide migrar más adelante: conseguir microSD fiable de al menos 16GB y lector; descargar imagen BBB y checksum oficial; verificar hash y tamaño descomprimido; respaldar eMMC sin montar desde un medio de recuperación a un disco del PC con espacio mayor al tamaño de la eMMC, verificar hash del respaldo, guardar uEnv y configuración; probar primero arranque normal desde microSD **no flasher**, consola USB, red, cinco pines, PRU, I2C y PWM. Sólo después solicitar aprobación explícita para escribir eMMC. Si falla el ensayo SD, apagar correctamente y retirar SD para regresar al eMMC existente. Si se llegara a autorizar flasheo, conservar SD de rescate y respaldo restaurable. No incluir ahora comandos destructivos.

## 3. Preparación física y del PC

- Sólo una BBB conectada cada vez. Identificar físicamente A/B para no atribuir resultados a la equivocada.
- P8/P9 completamente vacíos: sin sensores, puentes, servo, expansor ni reloj. Nada entre A y B. Sólo Mini USB de datos al PC, sobre superficie aislante.
- No se necesita FTDI para estos pasos. No tocar pines con puntas de multímetro mientras se prueban modos. No medir 5V en GPIO.
- Si hay calentamiento anormal, olor o reinicios repetidos, detener. No seguir reiniciando ni atribuirlo al software sin revisar cable/alimentación.
- No hace falta repetir la inspección visual de T02; contar los componentes nuevos sí pertenece a T03.
- Las mediciones activas de fuentes/servo/sensores son T08/T06 y posteriores. Sin osciloscopio podemos verificar configuración, pero no calidad ni frecuencia física del reloj.

En PowerShell de Windows, preparar una copia local de las herramientas (no cambia políticas permanentes):

```powershell
$repoT04 = '\\wsl.localhost\Ubuntu\home\erwin\Capa_Fisica\TRAMA3-CCVIII'
$kitT04 = Join-Path $env:USERPROFILE 'Documents\TRAMA3-T04'
New-Item -ItemType Directory -Force $kitT04 | Out-Null
Copy-Item -LiteralPath (Join-Path $repoT04 'hardware\configuracion\t04-bbb.sh') -Destination $kitT04
Copy-Item -LiteralPath (Join-Path $repoT04 'hardware\configuracion\T04-ConsolaUSB.ps1') -Destination $kitT04
Get-PnpDevice -PresentOnly |
  Where-Object { $_.FriendlyName -match 'Beagle|RNDIS|CDC ECM|USB Serial' } |
  Format-Table Status,Class,FriendlyName
```

Si la carpeta WSL no abre, iniciar Ubuntu una vez y repetir. Si falta la carpeta de configuración, no usar main remoto todavía: estos archivos están en la rama t04-debian-pinmux mientras se revisa el PR. No hacer merge por cuenta del script.

## 4. BBB-A por SSH (ruta preferida)

Conectar A y esperar su arranque. Ejecutar en PowerShell:

```powershell
ssh -o ConnectTimeout=5 debian@192.168.7.2
```

Introducir la contraseña localmente; no enviarla. Si hay aviso de clave cambiada, no borrar todo known_hosts ni desactivar la comprobación: comprobar que sólo A esté conectada e identificar su clave por consola USB. Ante timeout, pasar a la ruta serial de la sección 5.

Dentro de Debian, salir una vez con `exit` para transferir desde PowerShell:

```powershell
scp "$kitT04\t04-bbb.sh" debian@192.168.7.2:~/t04-bbb.sh
ssh debian@192.168.7.2
```

Si scp falla por SFTP en el servidor antiguo, probar `scp -O` con los mismos argumentos si la versión de Windows lo admite. Si no, usar la ruta serial.

Dentro de la BBB-A, pegar estos bloques, en orden. La contraseña sudo se introduce antes del bloque largo:

```bash
sudo -v
```

```bash
bash -n "$HOME/t04-bbb.sh"
bash "$HOME/t04-bbb.sh" A audit
```

Si bash -n indica error, **no ejecutar** el script: volver a transferir el archivo completo. Si audit acaba, leer los avisos según sección 6. Con la placa aún sin cargas y sólo si se identificaron ambos PRU detenidos y no hay errores de almacenamiento:

```bash
sudo -v
T04_SIN_CARGAS=SI bash "$HOME/t04-bbb.sh" A pin-test
```

La prueba comprueba sus prerrequisitos por sí misma, se detiene si falta alguno y restaura los modos previos. No seguir intentando modos alternativos si dice STOP. Copiar los resultados al PC: salir con `exit` y ejecutar en PowerShell:

```powershell
$destinoT04 = Join-Path $env:USERPROFILE 'Documents\TRAMA3-resultados\A'
New-Item -ItemType Directory -Force $destinoT04 | Out-Null
scp -r 'debian@192.168.7.2:T04-A-*' "$destinoT04"
```

No perder los registros antes de apagar. Incluyen carpetas separadas para cada ejecución. El Device Tree completo es respaldo local; enviar inicialmente sólo resultado.txt y estados-antes.tsv.

## 5. BBB-B por consola USB; también sirve de respaldo para A

Apagar A desde Debian con `sudo shutdown -h now`; esperar cese de actividad y apagado de los LEDs de usuario. La desaparición del puerto por sí sola no demuestra apagado. Si aparece solicitud de contraseña o error, resolverlo antes de desconectar. Conectar B únicamente.

En PowerShell, repetir Get-PnpDevice de sección 3. Utilizar **el COM que aparezca ahora**, no asumir COM22. Cerrar PuTTY/otras consolas que lo ocupen.

```powershell
$puertoT04 = Read-Host 'Puerto de la BBB conectada, por ejemplo COM22'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$kitT04\T04-ConsolaUSB.ps1" -Placa B -Puerto $puertoT04 -Accion audit
```

Este permiso se limita a ese proceso y ejecuta nuestro archivo local. El asistente serial entra como debian si aparece login, pide la contraseña ocultándola, transfiere el script en bloques cortos, comprueba sintaxis y guarda el registro en Documents\TRAMA3-resultados. No guarda credenciales ni requiere Internet. Si había una orden incompleta en la consola, la cancela con Ctrl+C.

Si el audit no presenta un bloqueo de sección 6, ejecutar:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$kitT04\T04-ConsolaUSB.ps1" -Placa B -Puerto $puertoT04 -Accion pin-test -SinCargas
```

Para usar esta ruta con A, sustituir -Placa B por -Placa A. La identidad A/B es la etiqueta física que asigna Erwin, no el nombre de host, que puede ser igual.

**Si sólo hay error CDC ECM y la consola funciona:** continuar por consola. No instalar un controlador RNDIS genérico sobre un dispositivo ECM sin comprobar su identificador. Que SSH escuche en la BBB no demuestra que Windows tenga enlace IP.

**Si el puerto está ocupado:** cerrar la otra terminal y repetir. **Si no hay puerto:** probar el cable de datos conocido y el mismo puerto del PC, esperar arranque, volver a enumerar. Si sigue ausente, detener la placa, registrar LEDs y no flashear. **Si contraseña falla:** no pegar comandos dentro del prompt de contraseña; corregir el acceso local o parar esa placa. **Si hay timeout de transferencia/ejecución:** el asistente cancela, intenta restaurar eco y conserva error.txt; no interpretar el registro como completo. Recuperar consola y revisar si pin-test restauró antes de conectar nada.

## 6. Preparación condicional después de audit

| Situación | Acción completa para esta sesión |
|---|---|
| Más de 500MB libres, raíz rw | Continuar pin-test. 500MB es margen operativo orientativo, no especificación de BBB. |
| 100–500MB, raíz rw | Se permite auditoría y prueba pequeña; no instalar compiladores grandes. Limpiar sólo caché conocida con clean-cache; registrar margen. |
| Menos de 100MB o errores I/O/ext4 o raíz ro | No aplicar cambios. Guardar lo que sea posible por consola. Necesita recuperación/espacio antes de preparar software. |
| DNS falla pero USB local funciona | Continuar T04 sin instalar paquetes. Falta de ruta por defecto puede ser normal sin Internet. No sustituir resolv.conf ni poner DNS públicos a ciegas. |
| config-pin, DT o PRU no identificados | Conservar salidas y detener pin-test. No descargar overlays de otro kernel. |
| GCC presente, clpru ausente | GCC no compila PRU. Anotar bloqueo de compilación para T06; no impide observar mux. |
| LightDM falla, consola/SSH funcionan | El escritorio no es necesario para el proyecto. Opción headless siguiente; no eliminar paquetes. |
| Modo UART/periférico en uno de los cinco pines | No forzar. El script cancela; revisar dueño/overlay con el registro. |
| PRU running | No detenerlo automáticamente. Identificar firmware y dueño antes de cualquier cambio. |
| pin-test restauró todo | Preparación temporal acreditable con revisión de pinctrl, no prueba eléctrica ni persistencia. |
| ERROR_RESTAURACION | No conectar cargas. Guardar estados-antes.tsv y resultado; recuperar cada modo anterior desde consola. Si no puede, parar esa placa. |

Limpieza opcional segura, sólo si el diagnóstico muestra caché descargada y falta espacio:

Dentro de Debian:
```bash
sudo -v
bash "$HOME/t04-bbb.sh" A clean-cache
```
Cambiar A por B para B si el script se transfirió por scp. Por consola automática de B:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$kitT04\T04-ConsolaUSB.ps1" -Placa B -Puerto $puertoT04 -Accion clean-cache
```

Sólo elimina paquetes descargados en caché, no programas instalados. Si no libera suficiente espacio, no borrar /usr, /opt, /boot ni repetir la limpieza de VS Code de A: B tenía /home prácticamente vacío.

Desactivar el escritorio fallido es opcional **si se usará terminal USB y no se necesita login gráfico**:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$kitT04\T04-ConsolaUSB.ps1" -Placa B -Puerto $puertoT04 -Accion headless
```
El script sólo actúa si LightDM está en failed; conserva el estado de habilitación anterior. Para revertir, si antes decía enabled, ejecutar en Debian `sudo systemctl enable lightdm`; iniciar con `sudo systemctl start lightdm` sólo si se desea volver a intentar el escritorio. Si antes era disabled, no habilitarlo. Deshabilitar LightDM no arregla AccountsService ni libera espacio; sólo evita arrancar un servicio gráfico que no usamos.

Si se dispone de sudo y debugfs no está montado, puede montarse temporalmente **sólo si /sys/kernel/debug existe y no está ya montado**:
```bash
mountpoint -q /sys/kernel/debug
```
Si devuelve no montado, ejecutar `sudo mount -t debugfs debugfs /sys/kernel/debug`, repetir audit/pin-test y luego `sudo umount /sys/kernel/debug` únicamente si lo montaste tú en esta sesión. Si el montaje falla, registrar y continuar con evidencia limitada; no modificar fstab.

No se instala persistencia de pinmux en T04. Un reinicio de comprobación, después de copiar registros, es opcional: `sudo reboot`, reconectar por el mismo método y repetir audit. Confirma arranque y modos iniciales, no permanencia de los modos de prueba. Si no vuelve el puerto/acceso, no insistir en cambios.


### Apagar B después de guardar resultados por consola USB

Puedes dejar B conectada y sin cargas hasta revisar los resultados. Si necesitas retirarla, en PowerShell utiliza este bloque inmediatamente después de una ejecución con sudo correcto. No solicita contraseña a través del bloque: si sudo ya expiró, vuelve a ejecutar audit para autenticarte y repite.

```powershell
$apagadoBBB = [System.IO.Ports.SerialPort]::new($puertoT04,115200,[System.IO.Ports.Parity]::None,8,[System.IO.Ports.StopBits]::One)
$apagadoBBB.DtrEnable = $true
try {
    $apagadoBBB.Open()
    $apagadoBBB.Write("sudo -n shutdown -h now" + [char]13)
    Start-Sleep -Seconds 2
    Write-Host $apagadoBBB.ReadExisting()
} finally {
    if ($apagadoBBB.IsOpen) { $apagadoBBB.Close() }
    $apagadoBBB.Dispose()
}
```

Si aparece error o contraseña requerida, no desconectar. Si no aparece texto, tampoco concluir que se apagó: confirmar cese de actividad y apagado de LEDs de usuario. Una pérdida de puerto puede ser desconexión o apagado; por sí sola no distingue ambos casos.

## 7. Qué entregar junto al inventario

Copiar esta ficha y completarla en una sola respuesta:

```text
Fecha real de ejecución:
BBB-A: acceso usado / audit completó sí-no / pin-test completó sí-no
BBB-A: cinco RESTAURADO sí-no / errores o STOP:
BBB-B: acceso usado / audit completó sí-no / pin-test completó sí-no
BBB-B: cinco RESTAURADO sí-no / errores o STOP:
Limpieza aplicada y espacio antes/después:
LightDM deshabilitado sí-no / estado anterior:
Reinicio opcional y regreso al sistema:
Archivos adjuntos: resultado.txt de cada ejecución + estados-antes.tsv
Pedido recibido: completo según confirmación anterior / diferencias encontradas:
M02 MCP23017: cantidad y marcado/encapsulado:
M04 LDR: cantidad/modelo:
M06 sonido: cantidad y serigrafía KY-037/KY-038:
M07 SG90: cantidad y posicional/continuo según etiqueta:
M09/M10/M11: cantidades y marcas:
M16 1k / M18 10k: conteo total incluyendo compras aparte:
M35 zócalos: cantidad / ancho entre filas:
M29 tubos: cantidad / longitud / diámetro:
M30 manguera: cantidad / longitud / diámetro interior:
M31 nylon: diámetro / longitud total / resortes disponibles:
M23/M34 fuentes: cantidades / 5V / amperios / conector / polaridad:
M25 placas: cantidad / dimensiones / paso:
M36/M37 borneras: cantidades / vías / paso:
M26/M27/M28/M32/M38–M41: cantidades o no tengo:
Compras externas: precio por lote o desconocido; sin dirección/datos de pago.
```

No subir logs crudos a GitHub. Revisar nombres, IP/MAC, números de serie, rutas privadas y mensajes de autenticación. El asistente genera registros locales; publicaremos sólo el resumen técnico necesario. No adjuntar la factura completa al PR.

## 8. Tabla de situación actual

Los datos numéricos son evidencia de T02, no mediciones del 08/11.

| Verificación | BBB-A | BBB-B |
|---|---|---|
| Debian / kernel T02 | 10 / 4.19.94-ti-r42 | 9 / 4.14.71-ti-r80 |
| Arranque actual | Pendiente de reconfirmar | Pendiente de reconfirmar |
| Acceso previo | SSH USB verificado en T02 | ttyGS0 USB verificado en T02 |
| Espacio previo | ~1.3GB después de limpieza | ~190MB |
| PRU0 | Nombre 4a334000, offline en T02; ejecución no probada | Identidad precisa pendiente; estados offline observados |
| P8_11 | Pendiente de selección y dueño | Pendiente de selección y dueño |
| P8_15 | Pendiente | Pendiente |
| P8_16 | Pendiente | Pendiente |
| P9_24 | Pendiente; revisar UART1 | Pendiente; revisar UART1 |
| P9_27 | Pendiente | Pendiente |
| P9_14 PWM | Interfaz visible T02, pin/onda no probados | Interfaz visible T02, pin/onda no probados |
| P9_19/P9_20 I2C | Bus visible T02; transacción no probada | Bus visible T02; transacción no probada |
| Persistencia | No instalada; aplazada | No instalada; aplazada |
| Bloqueos conocidos | DNS previo; resultados nuevos faltantes | Espacio, red USB Windows, DNS/LightDM; resultados nuevos faltantes |

## 9. Cierre y siguiente tarea

T04 recomendada **En curso, 25%**: estimación documental y herramientas, no porcentaje de pines aprobados. Inicio real 08/11/2026, cierre vacío. No marcar 100% hasta recibir ambas ejecuciones, interpretar dueños/registros y resolver conflictos de los cinco pines. Si falta compiler PRU o red para instalarlo, especificar el bloqueo de T06 aunque T04 termine su alcance mínimo.

T06 deberá fijar toolchain PRU compatible, probar firmware mínimo y medir P9_14, además de resolver inicialización/persistencia. No se escribió firmware, habilitó PWM, conectó expansor ni transmitió protocolo. El cuerpo de 54 bits, reloj PWM y frecuencias independientes permanecen en revisión 101.

El tracker mantiene su planificación histórica de octubre. Registrar inicio/cierre real en sus campos/observaciones sin retrofechar y sin cambiar responsables automáticamente.
