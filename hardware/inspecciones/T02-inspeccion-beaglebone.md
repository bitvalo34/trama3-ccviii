# T02 — Inspección de las dos BeagleBone Black

**Inicio real:** 2026-10-28, Guatemala. **Estado: completada con observaciones; cierre 07/11/2026.**

Responsable del tracker: Adrián; revisor del tracker: Erwin. Ejecutor físico: Erwin, quien tiene las dos placas. Revisor técnico cruzado previsto: Adrián. Roles y fechas planificadas del Excel no modificados. Una hora-persona es estimación histórica, no duración real acreditada.

## Cierre de inspección básica — 07/11/2026

Erwin confirma condición física general correcta en ambas placas, ninguna con microSD, cables propios y prueba en el mismo puerto del computador. Tiene segundo cable Mini USB, multímetro, cautín y estaño; no dispone de osciloscopio. No se confirmó analizador lógico ni se transcribió la revisión impresa exacta.

Ambas arrancan desde eMMC y permiten acceso autenticado Debian. A por SSH USB (Debian 10), con 1.3 GB libres tras limpieza; B por consola USB (Debian 9), con 190 MB libres y fallo de LightDM. Las herramientas básicas están presentes. Esto completa el diagnóstico básico; no certifica alimentación definitiva, estabilidad prolongada ni ejecución PRU.

T02 se cierra con observaciones a petición de Erwin. T04 recibe configuración compatible entre placas, espacio de B, red/DNS, pinmux y prueba PRU. Las especificaciones de fuentes externas y sus mediciones quedan pendientes para alimentación/montaje. La revisión cruzada de Adrián y la serigrafía exacta no se atribuyen como realizadas. Tampoco hay evidencia explícita del apagado final.

Una microSD no es necesaria para acreditar este arranque; puede servir después para recuperación o preparación del sistema. La caracterización de señales requiere acceso a instrumentación apropiada; tener multímetro no sustituye observar los pulsos.

Para el tracker: T02 completada con observaciones, 100 % del alcance de inspección básica, cierre 07/11/2026. Mantener responsables previstos y no inventar horas reales. Observaciones: ambas BBB inspeccionadas y accesibles; pendientes de configuración transferidos a T04, fuentes finales y caracterización pendientes. Sin osciloscopio disponible.

## Registro histórico

Los estados parciales y pendientes inferiores describen cada etapa anterior y quedan actualizados por el cierre de arriba.
## Objetivo y condiciones

Comprobar identidad, condición física, alimentación, arranque, Debian, acceso Mini USB y herramientas. Diagnóstico sin cambios de configuración. El28/10 Erwin autoriza liberar espacio si hace falta; se propone únicamente limpieza de paquetes descargados de APT tras registrar tamaño, aún no ejecutada ni acreditada. Sin instalar paquetes, cambiar GPIO/pinmux/PWM, cargar firmware PRU ni conectar sensores. ADR-0002 se mantiene; no se mide frecuencia máxima en T02.

Erwin confirma una placa conectada únicamente por Mini USB, sin accesorios ni FTDI. La llamamos provisionalmente **BBB-A**; BBB-B es la segunda, todavía no inspeccionada. Falta identificación física consistente. La revisión visual sin alimentación debe hacerse después de un apagado seguro: la placa ya estaba conectada al comenzar. No atribuir una revisión previa que no ocurrió.

## Evidencia real obtenida

- Repositorio local limpio y sincronizado con `bitvalo34/trama3-ccviii`; se creó rama `t02-inspeccion-bbb`.
- Windows detecta `Remote NDIS Compatible Device`, estado Up. Dirección local USB verificada; omitida del registro público.
- Enumera almacenamiento Linux USB, volumen BEAGLEBONE y puerto serial USB en estado OK. La consola serial no se abrió: su presencia no prueba acceso autenticado.
- Función secundaria `CDC ECM` con código28 (controlador faltante). No se modificaron controladores. RNDIS sí permite la conectividad observada.
- La dirección candidata respondió a ping y el servicio SSH anunció disponibilidad; dirección y banner exacto omitidos del registro público.
- El intento automático por clave no permitió acceso. Erwin inició sesión legítimamente en su terminal local y compartió una captura de comandos: `/etc/os-release` confirma Debian GNU/Linux10 (buster), `uname -r` devuelve4.19.94-ti-r42 y `uname -m`, armv7l. `uptime` mostraba14min y carga0.57/0.61/0.52. No se recoge ninguna contraseña. La hora de la placa no se usa como fecha de inspección.

Se demuestra enumeración USB, transporte de datos y un servicio activo; no se demuestra arranque completo, estabilidad, calidad de alimentación ni salud del almacenamiento. No hay mediciones eléctricas.

## Comparación actual

| Aspecto | BBB-A | BBB-B |
|---|---|---|
| Modelo y revisión | Device Tree: TI AM335x BeagleBone Black; revisión física pendiente | BBB Black declarada; no verificada |
| Condición física/conectores | No verificado | No verificado |
| Arranque | Sesión autenticada; Erwin observa alimentación fija, D2 parpadea y D4 parpadea tenue; secuencia inicial no observada | No verificado |
| Debian | Debian GNU/Linux10 (buster), confirmado por /etc/os-release | No verificado |
| Kernel y CPU | 4.19.94-ti-r42; armv7l | No verificado |
| RAM | 483Mi total, 57Mi usada, 416Mi disponible; swap0B (instantánea) | No verificado |
| Almacenamiento/eMMC/microSD | eMMC: mmcblk1 type MMC,3,6G, raíz mmcblk1p1 ext4 y particiones boot0/boot1 | No verificado |
| Fuente usada | Sólo Mini USB desde PC, sin accesorios; confirmado por Erwin | No verificado |
| Fuente definitiva | No verificado | No verificado |
| Mini USB/datos | Gadget y red responden | No verificado |
| Acceso Debian autenticado | SSH por USB comprobado en sesión de Erwin, usuario debian | No verificado |
| PRU/I2C/PWM reconocibles | Dos PRU en remoteproc offline; I2C0/1/2 y pwmchip0/1/3/4/6/7 presentes; funcionalidad no probada | No inspeccionados ni probados |
| Problemas | Raíz95% ocupada,185Mi disponibles; CDC ECM código28;0servicios fallidos reportados | Diagnóstico pendiente |
| Recomendación | Continuar recursos, logs, herramientas y revisión física | Mantener desconectada hasta terminar A |

## Segunda evidencia de BBB-A — 28/10/2026

Erwin aporta salida de Device Tree, free, lsblk, df, findmnt y systemctl:

- Modelo: `TI AM335x BeagleBone Black`; no identifica revisión impresa.
- RAM: total483Mi, usada57Mi, libre340Mi, compartida1,0Mi, caché85Mi y disponible416Mi. Sin swap configurada. Son valores de esa lectura.
- Disco mmcblk1:3,6G, partición mmcblk1p1 ext4 montada en `/`; aparecen mmcblk1boot0 y boot1 de2M. La estructura sugiere eMMC; confirmar `type` de sysfs antes de concluir origen. No aparece otra tarjeta en esta salida; falta inspección física de microSD.
- `df -h /`:3,5G total,3,1G usados,185M disponibles y95% de uso. **Espacio reducido para desarrollo/instalaciones**: documentar ocupación y planificar recuperación de espacio o respaldo en T04, sin instalar ni borrar archivos del sistema. Autorización posterior del usuario permite limpiar caché de paquetes si aporta espacio; resultado todavía pendiente.
- Raíz montada `rw,noatime,errors=remount-ro`. `errors=remount-ro` es política ante error, no evidencia de que el disco esté actualmente en sólo lectura. Revisar logs antes de descartar problemas de almacenamiento.
- `systemctl --failed`:0unidades fallidas cargadas. No equivale a ausencia de errores en logs ni certificación de salud de todos los subsistemas.
- Observación física de Erwin: LED de alimentación fijo, D2 parpadeando y D4 con parpadeo tenue. Consulta posterior de triggers: usr0 heartbeat, usr1 mmc0, usr2 cpu0, usr3 mmc1. No se atribuye una correspondencia exacta con D2/D4 sin revisar serigrafía; no diagnosticar daño por brillo aparente.

## Tercera evidencia de BBB-A — 28/10/2026

Captura aportada por Erwin confirma:

- mmcblk1/device/type = MMC. Con las particiones de arranque y la raíz observadas, se identifica almacenamiento eMMC en uso.
- remoteproc0: wkup_m3, running. Es distinto de las PRU.
- remoteproc1:4a334000.pru, offline; remoteproc2:4a338000.pru, offline. Ambos dispositivos PRU son reconocibles y no están ejecutando firmware; no se activaron.
- /dev/i2c-0,1,2 y pwmchip0,1,3,4,6,7 presentes. No se accedió a dispositivos del bus ni se exportaron canales PWM.
- Python3, Git, SSH, gcc, g++ y make disponibles en /usr/bin; config-pin en /usr/bin. Versiones pendientes de recoger.
- Triggers usr0 heartbeat, usr1 mmc0, usr2 cpu0 y usr3 mmc1. La actividad reportada de LEDs es compatible con funciones de sistema; no se certifica alimentación mediante esta observación.

El usuario pide agrupar los pasos para agilizar y autoriza borrar contenido si es necesario. Se prioriza medir ocupación y limpiar sólo caché APT descargada; no se propone autoremove, formateo, reinstalación ni borrado de carpetas desconocidas. No se ha ejecutado todavía ninguna limpieza.

## Alimentación y revisión física pendientes

A está alimentada sólo por Mini USB y sin accesorios según Erwin. No se ha medido tensión ni corriente. Por fuente: marca/modelo, salida5V, corriente indicada, jack y polaridad, cable, disponibilidad permanente y medición si hay multímetro. M34 prevé5V regulados/2A con centro positivo y jack5,5x2,1mm; que encaje no acredita compatibilidad. No conectar12V ni alimentar por P8/P9.

La alimentación Mini USB puede permitir diagnóstico básico sin accesorios según documentación oficial; no acredita alimentación final. FTDI sólo si se necesita consola, verificando UART TTL3,3V antes de conectar; no RS232 ni VCC improvisado.

Tras apagado seguro, revisar por placa: modelo/revisión legible, ambos lados, P8/P9, Mini USB, jack, Ethernet, USB-A, micro HDMI, microSD, botones, LEDs, corrosión, daños térmicos, pines y modificaciones. Pedir fotos sólo cuando aclaren una duda y no publicar identificadores.

## Diagnóstico Debian pendiente

Usar credenciales legítimas existentes. No solicitar contraseñas en el chat. Tras acceso, ejecutar en Debian de cada BBB:

```sh
cat /etc/os-release
uname -r
uname -m
tr -d '\000' < /proc/device-tree/model
uptime
free -h
df -h /
findmnt -no SOURCE,FSTYPE,OPTIONS /
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
systemctl --failed --no-pager
```

Leer logs acotados de arranque, nombres/estado de remoteproc, dispositivos I2C y pwmchip, y versiones de Python/Git/SSH/gcc/g++/make. No exportar PWM, escanear buses, cambiar servicios ni cargar firmware. Archivos presentes sólo indican soporte aparente. Verificar tipo de almacenamiento; no suponer que mmcblk0 siempre es eMMC. Registrar apagado seguro antes de cambiar a B.

## Herramientas e inventario

| Elemento | Evidencia actual | Impacto |
|---|---|---|
| Cable USB de datos en uso | Conectividad comprobada; estado físico pendiente | Permite diagnóstico inicial A |
| Segundo Mini USB | No verificado | Se puede reutilizar uno para inspección secuencial |
| Fuentes BBB M34 | No verificadas | Pendiente disponibilidad y aptitud final |
| Fuentes actuadores M23/M28 | No verificadas; no conectar | T08 y montaje posteriores |
| FTDI | No conectado según usuario; modelo/nivel no verificados | No requerido si acceso SSH funciona |
| Multímetro | No verificado | Necesario para afirmar tensión medida |
| Cautín, estaño/flux, soporte, desoldado, ventilación | No verificados | Montaje posterior |
| Pinzas/pelacables/conectores | No verificados | Montaje posterior |
| microSD de recuperación | No verificada | Opcional; no grabar ni formatear |
| Osciloscopio/analizador | No verificado | Pruebas posteriores; evaluar préstamo |

No se recomienda una compra nueva con estos datos. La BOM es planificación, no inventario de posesión.

## Hallazgos y discrepancia documental

CDC ECM sin controlador no impide la respuesta RNDIS; dejarlo para T04 si se necesita esa función. La alimentación USB está declarada y SSH autenticado está comprobado. Faltan medición eléctrica, fuente definitiva, revisión física y segunda placa. No hay evidencia para declarar una placa dañada.

El tracker actual marca **T01 Completada/100%**, mientras README/ADR dicen revisión pendiente y la observación antigua del Excel aún menciona confirmaciones. Registrar discrepancia sin reabrir T01 ni alterar sus documentos en esta tarea.

## Aceptación y actualización manual

- [ ] Identidad y revisión física de ambas placas.
- [ ] Alimentación y arranque observados en ambas.
- [ ] Debian/kernel/recursos obtenidos por acceso real.
- [ ] Acceso Mini USB autenticado o bloqueo concreto por placa.
- [ ] Herramientas y limitaciones identificadas.
- [x] Evidencia inicial real de USB y respuesta de red de A.
- [ ] Revisión cruzada de resultados finales.

**T02 no puede cerrarse.** Estado parcial sugerido: En progreso,35% orientativo. Inicio real28/10/2026; sin fecha de fin. Conservar13/10 histórico. Hoja Tracker maestro, fila7: K7 En progreso, M7 35%, responsables originales y criterio P7 sin cambios. O7: “Informe parcial T02 en hardware/inspecciones”.

Q7 propuesto: “28/10: Erwin inicia inspección; Adrián mantiene rol del tracker y revisará evidencias. Primera placa detectada por Windows: RNDIS, ping y TCP22 responden. CDC ECM código28. Erwin confirma sólo Mini USB, sin accesorios. SSH autenticado confirma Debian10, kernel4.19.94-ti-r42 y armv7l. Modelo BBB confirmado; RAM416Mi disponible, raíz95% ocupada/185Mi libres y0servicios fallidos. PRU/I2C/PWM visibles y herramientas básicas presentes. Pendientes logs/versiones, revisión física, fuente definitiva, inventario físico y segunda placa. Sin cambios de sistema; T02 no cerrada”. **No se modifica el Excel.**

## Continuación

T03 recibirá inventario real de fuentes/cables/herramientas; no comprar por supuestos. T04 recibirá Debian/kernel, problemas USB y soporte aparente PRU/I2C/PWM; no se configuran aquí. T06 prueba funcionamiento posteriormente.

Fuentes: tracker filas6–13; BOM M01/M23/M24/M28/M34; v3.0 caps.5–7A; ADR-0001/0002. Documentación oficial de [conectores](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html) y [alimentación](https://docs.beagleboard.org/boards/beaglebone/black/ch06.html).

## Ampliación de evidencia — 28/10/2026

Esta sección actualiza las observaciones anteriores de espacio, versiones y logs. La atribución de las nuevas capturas a A queda provisional: se solicitó confirmar si hubo cambio de placa o reinicio, porque el uptime pasó de 14 a 9 minutos entre capturas; aún no hay respuesta. No usar estas capturas como evidencia independiente de B.

- Versiones observadas: Python 3.7.3, Git 2.20.1, GCC/G++ 8 y GNU Make 4.2.1; cliente SSH disponible.
- El usuario ejecutó `sudo apt-get clean` con autorización previa para limpieza: espacio libre de 185M a 198M, ocupación aún 95%. La caché APT restante ocupa 8.0K. Esta es una modificación realizada; reemplaza cualquier indicación previa de diagnóstico completamente sin cambios.
- `/home/debian/.vscode-server` ocupa 1.1G y contiene varias versiones del servidor remoto y extensiones. `/home/debian/.cache` ocupa 54M. La eliminación del servidor remoto aún no se ha ejecutado ni confirmado.
- Logs mostrados: conflicto de reserva de PIN108 entre pinmux y HDMI, fallo del controlador tda998x, avisos de administración de energía y reglas de permisos para EEPROM. No se ha corregido la configuración. En el fragmento de almacenamiento no se observan errores de E/S ni corrupción EXT4; esto no equivale a una prueba integral del almacenamiento.
- `/boot/uEnv.txt` declara overlays habilitados, overlay PRU remoteproc AM335X-PRU-RPROC-4-19-TI-00A0 y cape-universal habilitado. Es configuración leída, no prueba de funcionamiento PRU ni causa definitiva del conflicto.
- `/etc/resolv.conf` es un enlace a `/run/connman/resolv.conf`; leerlo devuelve archivo inexistente. Resolución DNS pendiente de diagnóstico en T04; SSH local continúa funcionando. No se ha probado acceso a Internet.
- Última captura: raíz ext4 montada `rw`, 198M disponibles, 0 unidades fallidas, uptime 14 minutos. El valor `errors=remount-ro` es una política del montaje, no evidencia de montaje actual en sólo lectura.

Evidencia: capturas aportadas en el chat, transcritas sin publicar imágenes ni identificadores. T02 sigue En progreso; pendientes atribución de capturas, revisión física, inventario y evidencia inequívoca de ambas placas. La propuesta antigua Q7 debe actualizarse con estos hallazgos antes de copiarse al tracker; el Excel no se ha modificado.

### Confirmación de placa A y limpieza completada — 28/10/2026

Erwin confirma que todas las capturas recientes corresponden a BeagleBone A y que la reconectó. Queda resuelta la atribución provisional de la sección anterior: el cambio de uptime está explicado por esa reconexión, sin evidencia aportada de reinicio espontáneo.

La captura codex-clipboard-1ffc7334-d384-4e7f-9f83-9636d03199db.png muestra la ejecución de la eliminación autorizada y acotada de `/home/debian/.vscode-server` (1.1G). Después: raíz 3.5G, usados 2.1G, disponibles 1.3G, ocupación 62%; uptime 16 minutos. El problema inmediato de espacio insuficiente queda aliviado. Los componentes remotos de VS Code deberán reinstalarse si se vuelven a usar; no se eliminaron mediante estos comandos carpetas de proyectos ni programas del sistema.

ConnMan responde `active` y `enabled`. Esto no resuelve ni invalida el enlace DNS roto observado: la generación del archivo de resolución y la conectividad externa siguen pendientes para T04. No se modificaron servicios ni configuración de red.

Pendientes para continuar T02: inspección física y revisión impresa de A/B, inventario de fuentes y herramientas, apagado seguro observado y diagnóstico real de B. A dispone de acceso SSH y herramientas básicas para continuar; no declarar aún validados GPIO, PRU en ejecución, alimentación definitiva ni la segunda placa.

### Primer diagnóstico de conexión de B — 28/10/2026

El usuario confirma que conectó B. SSH por la dirección USB esperada agota el tiempo de espera. La captura codex-clipboard-ba078ee0-2353-4377-ab5e-48fc92cd64ba.png muestra Windows detectando USB Serial Device (COM22), Linux File-Stor Gadget USB Device y BEAGLEBONE con estado OK, y CDC ECM con Error. La consulta filtrada de adaptadores de red no devuelve RNDIS/USB/ECM/Linux y no aparece una dirección de host en las subredes USB esperadas. No se publican las otras direcciones de red del equipo.

B enumera funciones USB, pero no se ha establecido acceso autenticado ni verificado su sistema operativo. El error ECM requiere obtener su código antes de atribuirlo a un controlador faltante. Se propone comprobar si COM22 ofrece consola USB; puerto presente no garantiza servicio de login. FTDI aún no conectado. Estado físico, LEDs y uso del mismo cable/puerto aún pendientes de confirmación. T02 permanece en progreso.

### B ofrece consola USB — 28/10/2026

La captura codex-clipboard-d505b319-0ef7-42ca-b754-3df8aa3a4e31.png confirma respuesta en COM22: consola ttyGS0 con solicitud de login. El banner anuncia Debian GNU/Linux 9 e imagen BeagleBoard.org de 2018-10-07; pendiente confirmación autenticada con os-release/kernel. La placa llegó al servicio de consola USB; no está acreditado aún su estado integral. No se ha iniciado sesión ni usado credenciales mediante el diagnóstico. No se reproduce el banner completo ni sus credenciales anunciadas. FTDI no necesario para continuar por esta vía.

### Acceso autenticado y recursos de B — 28/10/2026

Capturas 08fdaa30-2803-4597-9295-ae7553af45c5 y 11f6f675-d395-46a1-88aa-731ece9f7af7: sesión autenticada por consola USB ttyGS0/COM22. Confirmado Debian GNU/Linux 9 (stretch), kernel 4.14.71-ti-r80, armv7l, uptime 20 minutos. RAM total 483M, disponible 406M, swap 0B. Disco mmcblk1 3.6G, raíz mmcblk1p1 ext4; particiones boot0/boot1 16M y rpmb 512K. df: 3.5G total, 3.1G usados, 190M disponibles, 95% ocupado. Tipo MMC aún pendiente de lectura explícita.

Una unidad fallida: lightdm.service (gestor de acceso gráfico); causa pendiente de logs. No impidió la consola autenticada. SSH responde active; usb0 UP con dirección y ruta de enlace USB configuradas, usb1 DOWN/linkdown. No se copian direcciones ni identificadores de red a este informe público. La conexión SSH desde Windows sigue sin establecerse; que ssh esté activo no acredita por sí solo escucha o conectividad de extremo a extremo. Diagnosticar el lado Windows/función USB sin cambiar a ciegas la dirección de B.

No se ha limpiado B ni cambiado sus servicios. Pendientes versiones de herramientas, PRU/interfaces, logs y revisión física/inventario. Diferencia A/B de Debian y kernel a resolver en planificación de T04, sin actualizar ni reinstalar en T02.

### Diagnóstico ampliado de B — 28/10/2026

Capturas 61f5be7d, f9767b20, 889c512b y 6d957cd1 aportadas por Erwin: modelo TI AM335x BeagleBone Black, tipo de almacenamiento MMC, raíz ext4 rw con data=ordered. Herramientas disponibles: python3, git, ssh, gcc, g++, make y config-pin. Versiones Python 3.5.3, Git 2.11.0, GCC/G++ 6.3.0, GNU Make 4.1.

remoteproc0 aparece running y remoteproc1/2 offline. La consulta de archivos name no encontró dichos archivos: no atribuir nombres exactos ni validar funcionalmente los PRU con esta salida. La configuración leída declara overlay AM335X-PRU-RPROC-4-14-TI-00A0 y cape-universal habilitado. I2C 0/1/2 y pwmchip 0/1/3/4/6/7 visibles, sin pruebas eléctricas ni activaciones.

LightDM registra servicio org.freedesktop.Accounts no disponible y salida del proceso con código 1 tras reintentos. Es evidencia de fallo del entorno gráfico; causa completa no establecida. Logs incluyen avisos de energía, HDMI/audio, resolución DNS, robotcontrol por ejecutable ausente y montaje fusectl. Hay intentos fallidos de autenticación/sudo previos; no atribuirlos a una causa concreta ni repetir intentos automatizados. No se solicitó ni almacenó contraseña.

ss confirma escucha TCP22 en IPv4/IPv6, sin acreditar acceso SSH desde Windows. La captura del listado de ocupación de /home/debian está incompleta y no permite seleccionar archivos grandes para limpieza. No hay evidencia nueva de limpieza de B ni de cambio de su espacio libre respecto a 190M. Pendientes revisión física, LEDs, microSD, fuentes/herramientas y resumen completo de ocupación. No modificar servicios ni reinstalar Debian dentro de esta inspección.

### Espacio y observaciones de B confirmados — 28/10/2026

Erwin declara que B no tiene microSD y que los LEDs se comportan igual que en A (referencia previa: alimentación fija, D2 parpadea y D4 parpadea tenuemente). Es observación del usuario, sin medición eléctrica. Captura b6a0ed74-62de-4336-92ec-f1e17bb978d1: /home/debian ocupa sólo 220K; no es la causa del almacenamiento ocupado. Raíz sigue con 190M libres y 95% de ocupación. No procede repetir la eliminación de VS Code usada en A ni borrar directorios del sistema sin diagnóstico. La preparación de espacio/sistema de B queda como pendiente para T04. Configuración de arranque confirma uname_r=4.14.71-ti-r80 y enable_uboot_overlays=1.

Diagnóstico básico por acceso real realizado en ambas placas; inspección física, revisión impresa, fuentes e inventario aún incompletos. T02 no se declara completada ni se modifica el tracker.
