# Primeras tramas físicas de TRAMA 3 revisión 102

Esta es la entrada única para el ensayo provisional **C0 luz + C1 sonido, CLK físico, C2 desconectado**, a 1 Hz. El software está integrado y probado en PC. **Esta entrega no contiene una transmisión física nueva ni un firmware PRU compilado por TI en este entorno.** Hay que compilar en las BBB con las herramientas de T06, completar las verificaciones mínimas indicadas y ejecutar los comandos de las dos terminales. No se actualiza el Excel ni se declara cumplido el requisito de tres medios.

## A. Base utilizada

Rama de trabajo: `primera-trama-fisica-c0-c1`, separada de `main` y de las ramas de Adrián.

| Fuente | Commit inspeccionado | Uso |
|---|---|---|
| [PR #11](https://github.com/bitvalo34/trama3-ccviii/pull/11) | `f83ecb510edc38880ed9aa0b40aa8c4d178f1116` | Base directa. Banco, evaluación de capturas y acumulador acústico |
| [PR #9](https://github.com/bitvalo34/trama3-ccviii/pull/9) | `afabfab39accf28e26edc1bf25a0095062029863` | Ya incluida por #11. Runtime continuo, host, propietarios, consola, matrices y sesiones |
| [PR #8](https://github.com/bitvalo34/trama3-ccviii/pull/8) | `db1e7b2ed01f0be46cda84fd43e87c8ab0c8ec41` | Ya incluida por #9. T06/T08 y referencia P2 |
| [PR #10](https://github.com/bitvalo34/trama3-ccviii/pull/10) | `8702cfa410404c5331f371a5e49405ce3ea7556f` | Inspeccionada como evidencia: LED/U1 A, incidencia I²C abierta. No se copian resultados a B |

No se fusionó ninguna PR. P2 procede de `hardware/documentacion/fuentes-P2`, origen #7 `9ba0bcaa271740effe206ec1ef79b72c070168e6`; no usar los antiguos planos P1 que también existen en el repositorio. T02/T04 proporcionan contexto de Debian, kernel, acceso y pinmux; T09/T10 aportan el montaje de medios. Las referencias anteriores no acreditan nuevos resultados físicos.

## B. Qué se reutiliza y qué cambia

Se reutilizan `matrices102/core.js`, `engine.js`, `protocol.cjs`, `Endpoint`, `Supervisor`, `ProcessBridge`, el propietario de recursos y los helpers T06. No hay otro parser, CRC ni transporte por red.

Cambios principales:

- Perfil `optical-acoustic`: máscara 3, C2 borrado explícito, sin exportar PWM ni tocar P9_14/P9_24. Servo físicamente desconectado y SW-287 OFF. Los perfiles definitivos no reciben calibraciones inventadas.
- `p2.py`: IODIRA/IOCON/OLATA leídos y comprobados al inicializar y durante cada fila; error o reinicio de MCP impide READY, detiene el ensayo y conserva evidencia.
- ABI **4**, derivada de ABI3: mismo runtime continuo, longitud TX 1–87 para diagnósticos cortos; tramas siempre 87. Ventana acústica integrada en `service.c`, estadísticas por muestra y captura R31 original. Host y firmware deben recompilarse juntos. Slot 36 bytes; memoria compartida 9660 bytes dentro de los 12 KiB disponibles.
- `phy-cli.cjs`: pruebas cortas, parejas, trama aislada y respuesta ACK real por retorno. `phy-evaluate.cjs`: comparación offline de archivos independientes y reconstrucción desde las capturas.
- Node 16.20.2 como alternativa offline para los sistemas antiguos; no hace falta npm ni actualizar Debian. Node 18+ ejecutable en la placa también sirve. Node 16 está fuera de mantenimiento: se limita a este banco local, sin servicios web.

El presupuesto sigue siendo exigente: preparación ARM/Python/I²C en 15 ms y anticipación PRU de 20 ms. Si la placa no lo cumple, se aborta; no se etiqueta como enviado. No se afirma que PC haya caracterizado esa latencia en ARM.

## C. Matriz, C2 y recepción acústica

Se conserva exactamente:

| Tick | C0 | C1 | C2 |
|---|---|---|---|
| 0 | a | b | a XOR b |
| 1 | b | a XOR b | a |
| 2 | a XOR b | a | b |

Las seis filas observadas de G son `[10,01,01,11,11,10]`. Las primeras dos ya son independientes: rango 2. Las cuatro palabras restringidas tienen distancia mínima 4. Se recuperan dos bits y se corrige una inversión bajo el criterio original `2e < distancia`; más errores pueden rechazarse o producir una palabra equivocada, que todavía debe superar CRC. No se promete detección universal.

C2 se representa como `null` en cada bloque, aunque R31 tenga ruido o parezca seguir pilotos. La razón es la configuración explícita del laboratorio, no un diagnóstico de avería. C0/C1 todavía deben superar `010101`; una lectura constante posterior no se convierte automáticamente en borrado. Se guardan máscara, muestras, síndrome restringido, distancia, posiciones corregidas y rechazos.

La PRU lee R31 una sola vez por iteración. C0 usa la muestra a 0.8T. C1 integra el tiempo activo del comparador, con polaridad normalizada, dentro de la ventana declarada. La plantilla propone **una ventana de observación** 0.2T–0.8T, no una calibración de sensor. `min_active=0` significa observar y registrar, sin sustituir la muestra puntual por una decisión calibrada. Solo se permiten diagnósticos en ese estado. Las tramas requieren umbral obtenido de capturas reales. `acoustic_active` y `acoustic_gap` usan ticks IEP de 5 ns; no son precisión metrológica certificada. Huecos de polling o captura tardía provocan fallo.

## D. Conexiones mínimas P2

Hacer cambios de conexiones sin energía. Cada placa conserva su fuente local y el arnés P2. No añadir GPIO, I²C ni GND entre nodos.

| Función | Conector y destino |
|---|---|
| LED TX | J2.1 ánodo, J2.2 cátodo; driver GPA0/U1.21 |
| Buzzer activo TX | J3.1 positivo +5V_ACT, J3.2 BUZZ_NEG; driver GPA1/U1.22 |
| LDR/LM393 RX | J5.1 3.3 V, J5.2 GND_LOGIC, J5.3 DO; EN_C0 JP10 1–2, JP4 hacia P9_27 |
| Acústico RX | J6.1 3.3 V, J6.2 GND_LOGIC, J6.3 DO; EN_C1 JP11 1–2, JP5 hacia P8_16 |
| Reloj A → B | J9.A.1 → J8.B.1; J9.A.2 → J8.B.2 |
| Reloj B → A | J9.B.1 → J8.A.1; J9.B.2 → J8.A.2 |
| CLK local | TX P8_11, RX PC817/JP7 hacia P8_15; RX invierte la señal |
| C2 | Servo ausente/desconectado, SW-287 OFF; JP12 2–3 fija la selección a GND local; no usar la lectura para reconstruir |

J10: 1=P9_3, 2=P9_1, 3=P9_19 SCL, 4=P9_20 SDA, 5=P9_14 PWM, 6=P8_11, 7=P9_27, 8=P8_16, 9=P9_24, 10=P8_15. Mantener las conexiones instaladas conforme a la tabla P2; este ensayo no utiliza PWM ni C2.

Orientar LED A hacia LDR B mediante tubo opaco y buzzer A hacia micrófono B mediante manguera; invertir para B→A. Cada módulo acústico tiene su propia serigrafía: no copiar el orden VCC/GND/DO del otro. AO queda libre. Para el ACK se necesitan ambos enlaces de datos y ambos pares de reloj.

J1.1 es positivo de actuadores y J1.2 es NEG_IN. Q6 IRLZ44N está en el retorno; **no puentear NEG_IN con GND_ACT**. NT1 mantiene la unión local prevista GND_ACT–GND_LOGIC. El PC817 aísla el camino de señal; dos USB al mismo PC pueden compartir masa por fuera, por lo que no se afirma aislamiento galvánico total.

Fuente detallada: [diseño P2](../../hardware/documentacion/fuentes-P2/diseno-electrico.md), [arneses](../../hardware/documentacion/fuentes-P2/arneses-externos.csv).

## E. Preparación y verificaciones indispensables

No se repite toda T08. Antes de cerrar JP4/JP5/JP7, confirmar en **cada** placa: arranque estable; 3.3 V lógico; alimentación de actuadores y retorno P2 correctos; ausencia de corto conocido; niveles y transiciones de DO/CLK seguros para 3.3 V; correspondencia del arnés; servo desconectado; reloj por PC817. Registrar instrumento, valores, placa y fecha en un archivo local. Si una conexión puede aplicar 5 V al GPIO, bloquear esa rama hasta corregirla. La resistencia de 1 kΩ no adapta niveles.

### Descargar o transferir

Con Internet en el PC, el código de la rama se obtiene con:

```bash
git clone --branch primera-trama-fisica-c0-c1 --single-branch https://github.com/bitvalo34/trama3-ccviii.git trama3-phy
```

El paquete entregado `TRAMA3_Primera_Trama_Fuentes.tar.gz` contiene fuentes, guía, pruebas, helpers de transferencia y SHA256SUMS. El archivo `node-v16.20.2-linux-armv7l.tar.xz` y `NODE_SHASUMS256.txt` se entregan aparte dentro del paquete offline completo. No contiene dependencias descargadas durante el ensayo ni un host x86 presentado como ARM.

Para copiar por SCP, abrir cada terminal de placa y obtener su dirección con `ip -br addr`. En PowerShell definir `$IP_A` y `$IP_B` con las direcciones realmente mostradas y distintas. No asumir las mismas direcciones USB ni conectar dos interfaces con IP idéntica. Ejecutar, sustituyendo solo esas variables y la carpeta local donde se descomprimió la entrega:

```powershell
$IP_A = Read-Host 'Dirección de BBB-A mostrada por ip -br addr'
$IP_B = Read-Host 'Dirección de BBB-B mostrada por ip -br addr'
scp .\TRAMA3_Primera_Trama_Offline.tar.gz "debian@${IP_A}:~/"
scp .\TRAMA3_Primera_Trama_Offline.tar.gz "debian@${IP_B}:~/"
```

Si B sigue disponible solo por consola, usar el helper T06 incluido: iniciar sesión en PuTTY, cerrar PuTTY dejando la shell autenticada y ejecutar `Transferir-Consola.ps1 -Puerto COM22 -Accion Enviar -Archivo .\TRAMA3_Primera_Trama_Fuentes.tar.gz -Placa BBB-B`. **COM22 es el antecedente documentado, no una detección actual:** obtener el COM presente con `Get-PnpDevice -PresentOnly` y sustituirlo por el que corresponda. El helper acepta hasta 8 MiB: usarlo solo para el paquete de fuentes, en la carpeta que indique al terminar. El archivo de Node ARM necesita SCP, memoria USB o microSD; no intentar transmitir el paquete offline grande por ese helper. USB/SSH solo llevan fuentes y logs fuera del enlace de datos del protocolo.

En cada BBB, con Bash y usuario `debian`:

```bash
mkdir -p "$HOME/trama3-phy"
tar -xzf "$HOME/TRAMA3_Primera_Trama_Offline.tar.gz" -C "$HOME/trama3-phy"
cd "$HOME/trama3-phy"
sha256sum -c SHA256SUMS
cat /etc/os-release
uname -m
uname -r
getconf GNU_LIBC_VERSION
df -h .
node --version
```

Antecedentes T02: A Debian 10, ARMv7, kernel 4.19.94-ti-r42; B Debian 9, ARMv7, kernel 4.14.71-ti-r80. Verificarlos de nuevo en la terminal; no son lecturas de esta entrega. El binario Node16 ARMv7 requiere glibc≥2.24 y kernel≥4.14 según [su documentación oficial](https://github.com/nodejs/node/blob/v16.20.2/BUILDING.md). Si el Node instalado no inicia o es anterior a 16:

```bash
bash software/runtime102/use-offline-node.sh
export PATH="$PWD/tools/node16/bin:$PATH"
node --version
```

Se extrae únicamente `bin/node`, sin instalación global. Comprobar espacio antes de extraer: el inventario antiguo tenía poco espacio libre. No borrar archivos del sistema automáticamente. El Node ARM descargado está verificado por SHA256 oficial; su ejecución en BBB todavía debe comprobarse.

### Dos terminales y preflight de solo lectura

En A:

```bash
source software/runtime102/lab-env.sh BBB-A
```

En B:

```bash
source software/runtime102/lab-env.sh BBB-B
```

En **ambas**, estos comandos no energizan salidas:

```bash
python3 software/runtime102/preflight-runtime.py --board "$BOARD" --output "$HOME/trama3-lab/preflight-$BOARD-01.json"
ls -l /dev/i2c-*
for d in /sys/class/i2c-dev/i2c-*; do echo "$d"; readlink -f "$d/device"; done
for d in /sys/class/remoteproc/remoteproc*; do echo "$d"; cat "$d/name" "$d/state" "$d/firmware"; done
ps -eo pid,args | grep -E 'runtime102|trama3-t06|i2cset|i2cget' | grep -v grep
```

Identificar el adaptador de P9_19/P9_20 por `4819c000`, no solo por su número. El propietario acepta `/dev/i2c-N` corroborado con esa dirección. No ejecutar barridos I²C generales ni `i2cset` mientras el runtime posee el bus. No detener procesos ajenos: cerrar con `stop` o Ctrl+C la terminal que inició T06/runtime y usar su limpieza. No lanzar T06 y runtime102 simultáneamente.

Si debugfs no está montado y se tiene acceso administrativo, montarlo con `sudo mount -t debugfs debugfs /sys/kernel/debug`; no montar una segunda instancia si ya existe. La comprobación de propietarios depende de esa información.

### Compilar sin activar hardware

```bash
command -v gcc
command -v clpru
find /usr/share/ti /usr/lib/ti /opt -maxdepth 6 -type f -name clpru 2>/dev/null
bash software/runtime102/native/build.sh
file software/runtime102/native/build/runtime102-host
cat software/runtime102/native/build/SHA256SUMS
```

El script detecta un único compilador TI o usa `CLPRU`. Si hay varios, definir `export CLPRU=` seguido de la ruta absoluta **mostrada por find** del compilador usado en T06. Necesita sus headers, `lnkpru`, `libc.a` y `rtspruv3_le.lib`; no basta copiar el ejecutable. Conservar `build.log`, `.map` y el ensamblador. Revisar que el mapa respete IRAM de 8 KiB y que las publicaciones en memoria compartida mantengan orden. No cargar un firmware de diagnóstico T06 ni un runtime ABI3 con el host ABI4.

Compilar en A y B con su gcc local produce el host para cada sistema. `file` debe identificar **ARM**, no x86-64. Aquí solo se compiló el host en x86 y se ejecutó el modelo C; TI/ARM se registran pendientes. Si falta TI en una BBB, usar la instalación que ya permitió T06 o trasladar el árbol completo del toolchain autorizado; no actualizar Debian ni fingir una compilación.

### Perfil local por placa

```bash
mkdir -p "$HOME/trama3-lab"
cp "software/runtime102/profiles/$BOARD-optical-acoustic.json" "$HOME/trama3-lab/$BOARD.json"
nano "$HOME/trama3-lab/$BOARD.json"
```

Completar únicamente con evidencia real:

| Campo | Cómo completarlo |
|---|---|
| `mcp_reset_confirmed` | `true` tras reset conocido de U1/BANK0, sin consumidores simultáneos. El software comprobará IODIRA=FF e IOCON=00 antes de configurar |
| `i2c_device` y `calibration.i2c_device` | Mismo `/dev/i2c-N` identificado por 4819c000 |
| `calibration.i2c_adapter_evidence` | Archivo de preflight y lectura que identifican el adaptador |
| `rx_invert` y `calibration.rx_invert` | Bit0=1 si luz activa baja; bit1=1 si sonido activo bajo; bit3=1 por PC817. Sumarlos: 8, 9, 10 u 11. Medir cada receptor; no copiar A a B |
| `calibration.status` | `COMMISSIONING` para diagnósticos; no escribir MEASURED para saltar calibración |
| `calibration.evidence`, `checked_at` | Ruta/identificador de las mediciones mínimas y fecha real con zona |
| `calibration.checks` | Cambiar cada booleano por separado solo cuando se haya verificado: 3.3 V, fuente P2, ausencia de corto, arnés, niveles, opto aislado, servo desconectado |
| `acoustic.min_active` | Mantener 0 en diagnóstico. Se calculará desde capturas; no inventar umbral |

`phycheck clock` verifica el perfil, no sustituye las mediciones. `phycheck frame` debe bloquear mientras falten calibración acústica y evidencia de reloj. No se exige calibrar servo ni nylon. Un perfil incompleto bloquea solo las acciones activas; fuentes, pruebas PC, compilación y preflight siguen disponibles.

## F. Primeros ensayos A → B

En cada fila iniciar primero la orden de **B**, esperar el mensaje `PHY rx`, y luego la de **A**. `phy` es la función definida por `lab-env.sh`; llama al mismo CLI usando root solo para los recursos locales. Ninguna orden envía el contenido esperado al receptor.

| Prueba | Terminal B (RX primero) | Terminal A (TX después) | Emisión + guarda |
|---|---|---|---|
| MCP repetido local A | No requiere RX | `phy send i2c mcp-a-01` | 20+2 s |
| Reloj | `phy receive clock reloj-ab-01` | `phy send clock reloj-ab-01` | 6+2 s |
| Luz 010101 | `phy receive c0 luz-ab-01` | `phy send c0 luz-ab-01` | 6+2 s |
| Sonido 010101 | `phy receive c1 sonido-ab-01` | `phy send c1 sonido-ab-01` | 6+2 s |

El ensayo MCP alterna GPA0 y registra IODIRA/OLATA después de cada preparación. Es una comprobación breve con carga; no garantiza estabilidad durante toda una trama. Verificar también que físicamente el LED responde. Un fallo de escritura o lectura aborta y no se reintenta de forma oculta. El resto usa los flancos reales del PC817 para registrar datos; sin reloj no se inventan muestras.

El firmware mantiene además 2T de reposo inicial antes de permitir el primer CLK TX de una sesión. Las duraciones de la tabla cuentan desde el primer flanco; añadir ese reposo al primer envío.

Las bandas son inicio 0.55–0.65T, ticks 0.15–0.25T, período T±5 %. Captura nominal 0.8T, tolerancia de software ±10 µs. El primer pulso se genera alto 0.6T y los siguientes 0.2T. El informe muestra anchos, períodos, offsets, R31 y actividad acústica. Para un diagnóstico sin captura se obtiene timeout, no PASS.

## G. Repetir B → A y calibrar

| Prueba | Terminal A (RX primero) | Terminal B (TX después) |
|---|---|---|
| MCP local B | No requiere RX | `phy send i2c mcp-b-01` |
| Reloj | `phy receive clock reloj-ba-01` | `phy send clock reloj-ba-01` |
| Luz | `phy receive c0 luz-ba-01` | `phy send c0 luz-ba-01` |
| Sonido | `phy receive c1 sonido-ba-01` | `phy send c1 sonido-ba-01` |

Al terminar cada ensayo, copiar los logs al PC o a una de las placas para evaluación. Esto ocurre **después** de la captura. Por ejemplo, si el PC organiza `resultados/A/<ensayo>/A.jsonl` y `resultados/B/<ensayo>/B.jsonl`:

```bash
node software/runtime102/phy-evaluate.cjs resultados/A/reloj-ab-01/A.jsonl resultados/B/reloj-ab-01/B.jsonl reloj-ab.json
node software/runtime102/phy-evaluate.cjs resultados/A/luz-ab-01/A.jsonl resultados/B/luz-ab-01/B.jsonl luz-ab.json
node software/runtime102/phy-evaluate.cjs resultados/A/sonido-ab-01/A.jsonl resultados/B/sonido-ab-01/B.jsonl sonido-ab.json
node software/runtime102/phy-evaluate.cjs resultados/B/reloj-ba-01/B.jsonl resultados/A/reloj-ba-01/A.jsonl reloj-ba.json
node software/runtime102/phy-evaluate.cjs resultados/B/luz-ba-01/B.jsonl resultados/A/luz-ba-01/A.jsonl luz-ba.json
node software/runtime102/phy-evaluate.cjs resultados/B/sonido-ba-01/B.jsonl resultados/A/sonido-ba-01/A.jsonl sonido-ba.json
```

El primer archivo es siempre TX. El evaluador no modifica los originales ni sobrescribe informes existentes. Sonido compara las duraciones activas de los ticks OFF/ON y propone un umbral solo si hay separación. Los seis ticks son una calibración inicial limitada, no una campaña de ruido. Si `ACOUSTIC_NO_SEPARATION`, ajustar el módulo/manguera/ruido, confirmar polaridad y repetir con otro ID. No escribir un número conveniente para pasar.

Copiar los tres informes del sentido correspondiente al receptor. En B, desde la carpeta que contiene `luz-ab.json`, `reloj-ab.json`, `sonido-ab.json`:

```bash
python3 "$PHY_ROOT/calibrate-physical.py" --profile "$PHY_PROFILE" --optical luz-ab.json --clock reloj-ab.json --acoustic sonido-ab.json --output "$HOME/trama3-lab/BBB-B-medido.json"
cp "$PHY_PROFILE" "$HOME/trama3-lab/BBB-B-commissioning.json"
cp "$HOME/trama3-lab/BBB-B-medido.json" "$PHY_PROFILE"
phycheck frame
```

En A usar los informes `luz-ba.json`, `reloj-ba.json`, `sonido-ba.json` y nombres `BBB-A-medido.json` / `BBB-A-commissioning.json`. La utilidad verifica que los tres PASS corresponden a ese **receptor**, calcula el umbral y conserva referencias con hashes. No cambia las verificaciones eléctricas ni el perfil original. Repetir las pruebas de sonido con el perfil medido antes de la trama y observar posible diafonía al usar ambos medios.

## H. Parejas, trama completa y ACK

Con ambos perfiles medidos, ejecutar en orden:

| Prueba | RX primero | TX después |
|---|---|---|
| Pareja 00 A→B | B: `phy receive pair pareja-ab-01` | A: `phy send pair pareja-ab-01 --pair 00` |
| Cuatro parejas A→B | B: `phy receive pair parejas-ab-01 --ticks 12` | A: `phy send pair parejas-ab-01 --pair all` |
| Cuatro parejas B→A | A: `phy receive pair parejas-ba-01 --ticks 12` | B: `phy send pair parejas-ba-01 --pair all` |
| Trama DATA A→B | B: `phy receive frame trama-ab-01` | A: `phy send frame trama-ab-01 --data-hex 41` |
| Trama DATA B→A | A: `phy receive frame trama-ba-01` | B: `phy send frame trama-ba-01 --data-hex 42` |
| DATA + ACK físico | B: `phy receive frame ack-ab-01 --ack` | A: `phy send frame ack-ab-01 --data-hex 41 --ack` |

Una pareja ocupa 3 ticks y 2T de guarda; las cuatro, 12 ticks. Son diagnósticos, **no tramas**. `--pair 01`, `10` y `11` permiten repetir cada caso aislado.

La trama DATA conserva SYN12=`111000111000`, SFD6=`101010`, CONTROL4=DATA, DATA8, CRC8, SEQ8 y SID8. Defaults: SEQ0, SID1, CRC SMBUS; también se admiten `--crc AUTOSAR`, `SAE-J1850` y `MAXIM-DOW`, siempre iguales en ambos comandos. No hace falta probar las cuatro variantes antes del primer enlace.

Son 6 pilotos + 27 parejas×3 ticks=87 ticks, más guarda de 2T. La RX termina tras la muestra final, cerca de 86.8 s desde el primer flanco; TX declara fin después de la guarda, cerca de 89 s. `ticks=N state=RUNNING` debe avanzar aproximadamente cada segundo. El timeout incluye 60 s para iniciar la otra terminal; `--timeout` permite un entero hasta 600 si la operación lo necesita. No interpretar una trama de 87 s como bloqueo.

Evaluar después de terminar:

```bash
node software/runtime102/phy-evaluate.cjs resultados/A/parejas-ab-01/A.jsonl resultados/B/parejas-ab-01/B.jsonl parejas-ab.json
node software/runtime102/phy-evaluate.cjs resultados/B/parejas-ba-01/B.jsonl resultados/A/parejas-ba-01/A.jsonl parejas-ba.json
node software/runtime102/phy-evaluate.cjs resultados/A/trama-ab-01/A.jsonl resultados/B/trama-ab-01/B.jsonl trama-ab.json
node software/runtime102/phy-evaluate.cjs resultados/B/trama-ba-01/B.jsonl resultados/A/trama-ba-01/A.jsonl trama-ba.json
node software/runtime102/phy-evaluate.cjs resultados/A/ack-ab-01/A.jsonl resultados/B/ack-ab-01/B.jsonl ack-ab.json
```

PASS de trama exige captura completa, reloj válido, ambos pilotos C0/C1, 27 bloques, 54 bits iguales al TX **en comparación posterior**, CRC correcto y limpieza sin errores. Los campos `levels` distinguen TX completada, captura, reconstrucción, CRC y ACK. Un perfil válido o un proceso iniciado no produce esos niveles.

En `--ack`, B construye ACK solo a partir de la DATA recibida y validada, espera 2.2 s desde su captura final y la emite por sus propios LED/buzzer/CLK. A valida SID/SEQ/CONTROL y CRC de la captura de retorno. No hay ACK artificial local. Un intercambio tarda aproximadamente 178 s más el tiempo de iniciar RX. **Es una respuesta de laboratorio a una trama aislada; no acredita handshake, entrega de mensaje ni toda T25.** Si DATA está dañada, esta prueba permanece en silencio: carece de contexto fiable para inventar SID/SEQ de un NACK.

### Sesión completa y NACK contextual, después del primer enlace

El runtime anterior conserva Stop-and-Wait, handshake y deduplicación. Para usarlos con el mismo backend C0/C1, primero detener los ensayos y ejecutar:

En B:

```bash
sudo "$PHY_NODE" "$PHY_ROOT/terminal.cjs" hardware "$PHY_PROFILE" "$PHY_RESULTS/sesion-01" "$PHY_ROOT/native/build/runtime102-pru0.out" "$PHY_ROOT/native/build/runtime102-host" --electrical-checked
```

En A, la misma orden añadiendo `--coordinator`. Esperar `CONNECTED` en ambas; entonces en la consola A escribir `send A`. `status` consulta y `stop` cierra. No se fuerza CONNECTED. La apertura requiere cuatro tramas de gestión; una letra requiere START/LEN_LO/LEN_HI/DATA/END y sus respuestas. A 1 Hz esto tarda muchos minutos. No bloquear la primera trama aislada por esa duración. NACK solo se genera en una sesión establecida con contexto de secuencia fiable; pérdida de reloj produce silencio/timeout. No se presenta el ACK aislado como validación de reintentos/deduplicación.

## I. Fallos, evidencia y limpieza

| Síntoma/código | Interpretación y siguiente acción |
|---|---|
| `LAB_ELECTRICAL_CHECKS`, `LAB_EVIDENCE_REQUIRED` | Faltan mediciones mínimas o identificación por placa. Completar lo real, sin reemplazarlo por valores ficticios |
| `LAB_FRAME_CALIBRATION` | Diagnósticos permitidos, trama bloqueada hasta informes de luz/reloj/sonido de ese receptor |
| `I2C_ADAPTER_NOT_P9_19_P9_20` | El adaptador no corresponde a 4819c000; revisar inventario y perfil |
| `MCP_RESET_STATE` | U1 no está en el reset/BANK0 esperado. Apagar cargas y revisar consumidores/reset; no seguir escribiendo |
| `MCP_IODIRA_CHANGED`, `MCP_READBACK`, error read/write | Posible reinicio/intermitencia o escritura no confirmada. Se abortó. Conservar diagnóstico, revisar 3.3 V/reset/desacoplo/I²C. Si OFF no pudo confirmarse, quitar alimentación de actuadores |
| `OUTPUT_PREPARE_TIMEOUT/LATE`, PRU fault 10 | READY no llegó dentro del presupuesto. Revisar carga Linux, I²C y logs; no prolongar plazos para encubrir bits no emitidos |
| `BRIDGE_ABI_OR_EPOCH`, host sin ready | Host/firmware antiguos o incompatibles. Recompilar ambos ABI4; revisar hash/mapa y `HOST_DIAGNOSTIC` |
| PRU fault 1 | Ring lleno: captura invalidada. Revisar bloqueo del host/disco/carga |
| PRU fault 3/5/7/12 | Polling PRU tardío / heartbeat ARM perdido / muestra tardía / ventana acústica incompleta |
| `PHY_TIMEOUT`, `INCOMPLETE_CAPTURE` | Falta inicio, flancos o muestras. Comprobar J9→J8, JP7 y polaridad. No completar con ceros |
| `PHY_CLOCK_INVALID`, `PWM_WIDTH`, `CLOCK_PERIOD` | Anchos/período incorrectos; revisar PC817 y flancos antes de afirmar sincronización |
| Luz totalmente invertida | Medir DO, corregir solo bit0 de `rx_invert` y su evidencia en esa placa; repetir con ID nuevo |
| `ACOUSTIC_NO_SEPARATION` | Ruido, polaridad, umbral del módulo o arrastre entre ticks. Ajustar montaje y repetir; no adoptar umbral sin separación |
| `MATRIX_SYNDROME`, `CRC`, `PHY_RX_INVALID` | Guardar las muestras y bloques; revisar asentamiento, diafonía y pilotos. Capturar no equivale a reconstruir |
| `PHY_ACK_CONTEXT`, `NO_PHYSICAL_ACK` | Retorno inexistente o identidad incorrecta. Mantener como logro separado la trama de ida |
| `T06_OR_RUNTIME_BUSY`, PRU ocupado, pin no seguro | Cerrar al propietario legítimo. No matar procesos desconocidos, borrar locks o cambiar pinmux a la fuerza |
| `CLEANUP_FAILED` | Conservar `/run/trama3-runtime102` y los logs; comprobar salidas antes de otra ejecución |

Ctrl+C o `stop` envía STOP, apaga LED/buzzer, detiene solo el host propio, desacopla CLK, restaura pines/firmware y libera recursos. C2 no se energiza. Los registros conservan `CLEANUP` y errores; si falla I²C, el software no puede garantizar el apagado físico.

Si un proceso murió sin limpieza, inspeccionar `/run/trama3-runtime102/owner.json`, `profile.json` y `resources.json`. Con el PID propietario ya inexistente y el mismo boot, `sudo python3 software/runtime102/recover-physical.py` intenta apagar MCP y restaurar solo la transacción registrada. Se niega a recuperar un PID vivo, otro boot, firmware de otro propietario o estado MCP desconocido. No ejecutar `rm -rf` sobre los locks.

Recolectar en cada placa:

```bash
tar -czf "$HOME/phy-$BOARD-01.tar.gz" -C "$HOME/trama3-lab" .
sha256sum "$HOME/phy-$BOARD-01.tar.gz"
```

Copiar al PC por SCP o por el helper serial con `-Accion Recibir -ArchivoRemoto phy-BBB-B-01.tar.gz`. Descomprimir cada archivo en una carpeta distinta y reunir los subdirectorios `results/BBB-A` y `results/BBB-B` como `resultados/A` y `resultados/B` usados arriba. Incluir preflight, perfiles usados, informes de calibración, `native/build/build.log`, `.map`, SHA256SUMS y observaciones/instrumentos. No editar los JSONL originales. Cambiar `01` por `02` al repetir para no sobreescribir evidencias.

Los logs registran placa, fecha de sistema no certificada, commit, perfil y hashes de host/firmware, epoch, secuencia, R31, vector normalizado, actividad acústica, bloques, CRC, respuesta y limpieza. `origin=hardware` describe la ruta ejecutada; no autentica por sí solo el instrumento ni convierte un log sintético en prueba física. El evaluador conserva hashes de sus dos entradas. PASS es la evaluación del ensayo; BLOCKED identifica prerrequisitos ausentes; FAIL identifica una ejecución/evaluación fallida; NOT_TESTED se mantiene para niveles aún sin evidencia. El campo conservador `physical_status:NOT_TESTED` de cada registro básico del Journal no se sobrescribe: consultar los niveles explícitos del informe posterior.

## J. Tracker y resultados de esta entrega

Ver [AVANCE_PRIMERA_TRAMA.md](AVANCE_PRIMERA_TRAMA.md) y [VALIDACION_FISICA_SOFTWARE.md](VALIDACION_FISICA_SOFTWARE.md). El Excel original no se modificó. T23 sigue sin cierre físico, aunque la ruta de software esté implementada. Un futuro PASS C0/C1 será cumplimiento parcial, con C2 y campaña nominal pendientes.

## K. Archivos y reproducción de pruebas PC

Entradas operativas: `phy-cli.cjs`, `lab-env.sh`, `phy-evaluate.cjs`, `calibrate-physical.py`, perfiles `*-optical-acoustic.json`, `recover-physical.py`, `prepare-offline.py`, `use-offline-node.sh`. Implementación: `phy.cjs`, `p2.py`, `board_owner.py`, `profiles.cjs`, `lab_profile.py`, `launcher.cjs`, `stream.cjs`, `supervisor.cjs`, backend `native/` y extensiones mínimas del codec compartido. Pruebas nuevas: `test-phy.cjs`, `test_physical.py` y ampliación `native/test_service.c`.

```bash
bash software/runtime102/test-physical.sh
python3 tests/hardware/verify_pc.py --output /tmp/trama3-validacion-p2-nueva
```

La primera orden ejecuta matrices, runtime, banco, nuevos casos, procesos Python/Node, fallos y modelo C x86. En Node16 activa `--experimental-fetch` únicamente para las regresiones web antiguas; la CLI física no usa fetch, HTTP ni ese indicador. La segunda verifica los componentes P2/T06/T08 reutilizados. Ninguna constituye una prueba BBB.

## ¿Se retransmite antes de terminar la trama?

**No hay aborto ni retransmisión anticipada de una trama TX en curso.** La revisión 102 sí valida cada bloque después de tres ticks, antes de completar los 54 bits. Esa detección temprana permite rechazar el intento y, con contexto fiable, encolar NACK. Pero `Endpoint.take()` no inicia otra transmisión si ya existe `sending`; el firmware termina la emisión/guarda y `txDone()` habilita el plazo de respuesta. Un NACK también ocupa 87 ticks. El runtime actual es Stop-and-Wait por trama y los reintentos se hacen con la misma SID/SEQ, hasta cuatro intentos totales.

Por tanto, **validación temprana por bloque no equivale a retransmisión temprana**. Para esta última haría falta definir cancelación TX segura, señalización de aborto, rearme del receptor y guardas en ambos sentidos. No se añadió ese cambio de protocolo a la integración urgente.
