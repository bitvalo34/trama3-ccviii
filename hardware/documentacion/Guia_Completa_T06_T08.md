# TRAMA 3 — Guía completa T06/T08 para Erwin

Preparación: 12 de noviembre de 2026, Guatemala. Referencia funcional: **revisión 102**.
Adrián prepara software; Erwin ejecuta posteriormente en BBB-A y BBB-B.
**No se han realizado pruebas físicas durante esta preparación.**

## 0. Alcance, orden y lectura de resultados

T06 comprueba PWM hardware P9_14 y generación/captura PRU0. T08 inspecciona fuentes, rieles, entradas y arquitectura de alimentación. No se transmite TRAMA 3, no se mueve el servo, no se modifica CAD, bootloader, eMMC, kernel, servicios ni tracker. Los ADR antiguos son históricos donde los sustituye revisión102.

El orden es: inspección eléctrica básica → preparación/compilación → PRU sin cables → PWM sin cargas → apagar y montar loopback PRU → apagar y montar loopback PWM → mediciones restantes → recopilar → evaluar. Cada bloque termina y restaura antes de cambiar cables. **No ejecutar bloques distintos en paralelo.**

| Estado | Significado |
|---|---|
| PASS | Se cumplió el criterio específico registrado; revisar su alcance |
| FAIL | Prueba realizada con incumplimiento; corregir antes de repetir |
| BLOCKED | Falta prerrequisito, permiso, interfaz compatible o evidencia válida |
| NOT_TESTED | No se midió ese criterio; incluye auditoría sin activación |

Un PASS de compilación, inicio del firmware o configuración no es PASS eléctrico.
El evaluador final exige loopback y PWM capturado/restaurado en **ambas** BBB.
Los CSV vacíos y datos simulados no dan aprobación.

Cada prueba imprime una carpeta única `trama3-resultados/BBB-A|BBB-B/fecha-UUID`.
Guarda identidad, argumentos, órdenes/readbacks, errores, resultados y restauración.
Las fechas de las BBB pueden estar desajustadas: registrar también fecha real del PC.
El firmware queda únicamente temporal; tras reinicio repetir preflight. No se instala autostart.

## 1. Lista previa y conexiones

Leer [Checklist_T06_T08.md](Checklist_T06_T08.md) y [T08_Auditoria_T51.md](T08_Auditoria_T51.md).
Para T06, dejar desconectadas placa T51, servo, buzzer, sensores y segunda BBB.
Revisar polaridad de alimentación y medir P9_3 con el procedimiento de §6 antes de los loopbacks.

**Cablear siempre con BBB apagada, USB y alimentación retirados.**
Primero apagar Debian con `sudo poweroff`, esperar LEDs de actividad detenidos y retirar toda fuente.
Nunca desconectar sólo tierra dejando una señal energizada. No usar 5 V, P9_5/P9_6 ni P9_7/P9_8 en los loopbacks.

| Ensayo | Cableado en la MISMA BBB, apagada |
|---|---|
| Inicio PRU | Ningún cable en P8/P9 |
| TX con instrumento | P8_11 a sonda compatible con 3.3 V; referencia P9_1 |
| Loopback PRU | P8_11 → resistencia **1 kΩ, 1/4 W** → P8_15 |
| Captura PWM | P9_14 → resistencia **1 kΩ, 1/4 W** → P8_15 |
| Entradas opcionales | P8_16, P9_24 y P9_27, cada uno por **10 kΩ** a P9_1; cambiar un solo resistor a P9_3 con la BBB apagada |
| PWM con instrumento | P9_14 a sonda 3.3 V y P9_1 a referencia; servo ausente |

La resistencia 1 kΩ limita una corriente accidental; **no convierte niveles** ni hace segura una conexión entre salidas. Ambos extremos comparten alimentación y tierra de la misma BBB. Identificar P8/P9 y numeración con la serigrafía y tabla oficial, nunca por la orientación de una fotografía.

P8_11 es salida PRU0 R30.15; P8_15 entrada R31.15.
P8_16=R31.14, P9_24=R31.16, P9_27=R31.5.
Los bits opcionales se obtienen de una lectura común de R31. No hay decodificador matricial.

## 2. Windows PowerShell: obtener y transferir

Los siguientes comandos son **PowerShell**, ejecutados en una carpeta de trabajo.
Si ya se recibió el ZIP, extraerlo en una carpeta nueva. El ZIP es para Windows;
el archivo **tar.gz incluido dentro del ZIP** es para transferir a Debian.

### Desde Git

```powershell
git clone --branch t06-t08-pruebas-hardware https://github.com/bitvalo34/trama3-ccviii.git TRAMA3-T06-T08
Set-Location TRAMA3-T06-T08
```

La rama contiene dependencias T51/T04/102. No hacer merge ni cambiar el tracker.
Si Git no está disponible, usar el ZIP entregado: contiene las fuentes necesarias.

### Inventario USB sin cambiar controladores

```powershell
.\hardware\pruebas\ejecutar\Preparar-Pruebas.ps1 -Placa BBB-A
Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'Ports' } | Select-Object Status,FriendlyName
```

Conectar **una sola BBB**. COM22 fue observado anteriormente en B, pero usar el puerto que muestre Windows ahora. No reinstalar drivers por un número diferente.

### BBB-A mediante SSH USB

En esta imagen, 192.168.7.2 es dirección candidata, no garantía. Si la conexión conocida usa otra, sustituir `-Destino`. No aceptar una clave SSH cambiada sin revisar la identidad; no deshabilitar comprobación de host.

```powershell
.\hardware\pruebas\ejecutar\Preparar-Pruebas.ps1 -Placa BBB-A -Modo SSH -Destino debian@192.168.7.2 -Paquete .\TRAMA3_T06_T08.tar.gz
ssh debian@192.168.7.2
```

El script imprime una carpeta nueva `~/trama3-t06-t08-XXXXXXXX`; usar exactamente ese nombre.
No requiere Internet en BBB. La transferencia no ejecuta pruebas activas.

### BBB-B mediante consola USB

1. Abrir PuTTY: Serial, puerto COM observado, 115200, 8 bits, sin paridad, un stop, Flow control **None**.
2. Iniciar sesión Debian con las credenciales existentes, localmente.
3. Dejar la terminal en el prompt Linux y cerrar PuTTY para liberar COM.
4. Ejecutar (sustituir COM22 por el observado):

```powershell
.\hardware\pruebas\ejecutar\Preparar-Pruebas.ps1 -Placa BBB-B -Modo Serial -Puerto COM22 -Paquete .\TRAMA3_T06_T08.tar.gz
```

La transferencia usa bloques base64 con confirmación, SHA-256 del archivo y de sus contenidos.
No captura contraseñas, no programa firmware y no activa pines.
Volver a abrir PuTTY y entrar en la carpeta impresa. Si no reconoce una shell autenticada, se detiene: iniciar sesión manualmente y repetir. No abrir dos programas sobre el mismo COM.

Alternativa si B ya tiene SSH funcional: utilizar el mismo comando SSH de A, con `-Placa BBB-B` y su dirección comprobada. No se presupone que CDC ECM funcione.

## 3. BBB-A — Debian 10 / kernel 4.19.94-ti-r42

Todos los comandos de esta sección se ejecutan **dentro de Debian**.
Entrar en la carpeta impresa por la transferencia; el ejemplo usa un nombre ilustrativo:

```bash
cd ~/trama3-t06-t08-XXXXXXXX
sha256sum -c SHA256SUMS
export T06_RESULTS="$HOME/trama3-resultados"
python3 --version
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A preparacion --results "$T06_RESULTS"
```

No copiar literalmente XXXXXXXX: la transferencia entrega el nombre real.
En una copia clonada con Git, entrar en la raíz del repositorio; no existe SHA256SUMS hasta empaquetar.

### Interpretar preflight

Debe reconocer AM335x BeagleBone Black, Debian9/10, PRU0/1 por direcciones
4a334000/4a338000 y eHRPWM1 por 48302200 (o jerarquía 48302000/ehrpwm).
Los números remoteproc/pwmchip **no son constantes**. No escribir a una ruta encontrada por aproximación.

Preflight registra versiones gcc/clpru, lnkpru, stdint.h, runtime TI libc.a, módulos y espacio.
Una versión separada de remoteproc puede no existir: el kernel y srcversion disponible son la referencia.
La auditoría puede ser parcial sin root. Para comprobar debugfs con permisos, repetir sólo lectura:

```bash
sudo python3 hardware/pruebas/t06/run.py preflight --board BBB-A --results "$T06_RESULTS"
```

### Compilar — no modifica hardware

```bash
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A compilar --results "$T06_RESULTS"
```

Si clpru no está en PATH, listar candidatos y elegir **el archivo real** de la instalación ya presente:

```bash
find /usr/share/ti /usr/lib/ti /opt -maxdepth 6 -type f -name clpru 2>/dev/null
```

Ejemplo de uso con la ruta obtenida (no supone que ésa exista):

```bash
CLPRU=/ruta/observada/bin/clpru bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A compilar --results "$T06_RESULTS"
```

`build.sh` incluye comandos exactos de gcc, clpru, enlazado y hashes.
Usa headers/runtime del **mismo** compilador; no requiere librerías RPMsg ni libprussdrv.
Debe generar:
- `hardware/pruebas/t06/build/trama3-t06-host`: ejecutable ARM compilado en BBB.
- `hardware/pruebas/t06/build/trama3-t06-pru0.out`: ELF PRU.
- Mapa, log y SHA256SUMS en esa carpeta; reporte con placa/fecha en resultados.

No copiar el ejecutable x86 de validación a la BBB. No se entrega un binario PRU sin verificar.
Si no existe toolchain completo, conservar BLOCKED y registrar rutas; no ejecutar apt upgrade,
no cambiar imagen ni kernel. La alternativa es provisionar offline un toolchain TI compatible
en una carpeta de usuario y apuntar CLPRU a ella; el paquete no distribuye software propietario.

### PRU sin conexiones — cambio temporal explícito

Con P8/P9 libres y checklist realizado:

```bash
sudo python3 hardware/pruebas/t06/run.py pru-smoke --board BBB-A --active --electrical-checked --results "$T06_RESULTS"
```

Requiere ambos PRU offline; no detiene firmware ajeno ni wkup_m3.
Carga un nombre exclusivo `trama3-t06-HASH.out`, comprueba ABI y heartbeat, para PRU0
y restaura el selector original. No selecciona pines de salida en smoke.
PASS significa inicialización y comunicación, **no señal física**.

### PWM sin servo — tres ensayos finitos

```bash
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A pwm --active --electrical-checked --results "$T06_RESULTS"
```

Aplica 20 ms de período y altos 1.0, 1.5 y 2.0 ms, durante 2 s cada uno.
Readback confirma solicitud/habilitación; sin captura, resultado eléctrico NOT_TESTED.
No existe modo de movimiento del servo.

Para inspección con instrumento, configurar primero disparo ascendente y captura única;
usar escala inicial 5 ms/div y 1 V/div, sonda apropiada. Ajustar al instrumento real.
Para más tiempo, ejecutar individualmente (máximo 10 s):

```bash
sudo python3 hardware/pruebas/t06/run.py pwm --board BBB-A --high-us 1500 --seconds 10 --active --electrical-checked --results "$T06_RESULTS"
```

Guardar captura con período, ancho, amplitud, referencia y modelo/resolución del instrumento.
Un multímetro DC mostrará un promedio; no permite afirmar ancho ni frecuencia.

### Loopback PRU — apagar, cablear y arrancar

```bash
sudo poweroff
```

Retirar USB/fuente. Montar **P8_11 → 1 kΩ → P8_15**. No tocar los otros pines.
Encender, entrar nuevamente en la carpeta, repetir preflight y ejecutar:

```bash
export T06_RESULTS="$HOME/trama3-resultados"
sudo python3 hardware/pruebas/t06/run.py loopback --board BBB-A --fixture loopback --active --electrical-checked --results "$T06_RESULTS"
```

Esperado: 25 pulsos generados y 25 pares subida/bajada, altos ~1500 µs,
períodos ~20000 µs, sin overflow, sin retrasos ni gaps de sondeo >10 µs.
La tolerancia de ensayo es 2% o 20 µs, lo mayor; no es especificación del servo.
La captura se hace por R31, **no por leer R30**. Sin el cable debe fallar por ausencia de pulsos.

Otro patrón conservador, si se desea:

```bash
sudo python3 hardware/pruebas/t06/run.py loopback --board BBB-A --fixture loopback --period-us 100000 --high-us 10000 --cycles 20 --seconds 3 --active --electrical-checked --results "$T06_RESULTS"
```

### Captura del PWM sin osciloscopio

Apagar con `sudo poweroff`, retirar toda alimentación y **quitar completamente** el
loopback anterior. Montar **P9_14 → 1 kΩ → P8_15**. Nunca dejar P8_11 conectado a P9_14.
Encender y ejecutar:

```bash
export T06_RESULTS="$HOME/trama3-resultados"
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A captura-pwm --fixture pwm-loopback --active --electrical-checked --results "$T06_RESULTS"
```

Ejecuta 1.0/1.5/2.0 ms con capture PRU independiente de la interfaz PWM.
Exige al menos diez períodos completos por ensayo. Puede empezar a mitad de un pulso:
se descarta el alto parcial inicial. Distingue configurado, habilitado, observado,
frecuencia comprobada y ancho comprobado.

**Límite:** PWM e IEP derivan sus relojes de la misma placa. Esto comprueba el recorrido
eléctrico/relación temporal, pero no calibra su frecuencia absoluta ni mide voltaje,
sobreimpulsos, tiempos de subida o calidad analógica. No sustituye medición de amplitud T08.

### Lectura de entradas opcional

Apagar y quitar loopback. Cablear los tres resistores de 10 kΩ de §1.
No activar sensores ni placa T51.

```bash
sudo python3 hardware/pruebas/t06/run.py inputs --board BBB-A --fixture inputs --active --electrical-checked --results "$T06_RESULTS"
```

Las muestras deben mostrar C0/C1/C2 bajos. Apagar, mover sólo el resistor de una entrada
a P9_3, encender y repetir: sólo ese bit cambia a alto. Repetir para cada entrada.
No atribuir niveles de una entrada flotante a una prueba válida.

### Finalizar o recuperar

La salida PRU termina baja; cleanup desacopla P8_11 a entrada con pull-down, detiene
PRU0 y restaura modo anterior. PWM solicita duty=0, deshabilita, restaura pin y libera
sólo el canal adquirido. El estado eléctrico de un PWM deshabilitado no está garantizado
por la API: mantener cargas desconectadas y apagar antes de retirar cableado.

Ctrl+C, SIGTERM y pérdida de terminal con SIGHUP intentan restaurar.
SIGKILL, kernel colgado o corte de energía no pueden prometer restauración por software.
Después de una sesión interrumpida, **sin conectar cargas**, ejecutar:

```bash
sudo python3 hardware/pruebas/t06/run.py cleanup --board BBB-A --active --results "$T06_RESULTS"
```

Sólo usa el diario root de `/run/trama3-t06/state.json`, con exclusión mutua.
No hay diario: no toca recursos. Diario de otro arranque: se bloquea.
Si restauración falla, conservar diario/resultado y no ejecutar otra prueba activa.

## 4. BBB-B — Debian 9 / kernel 4.14.71-ti-r80

Acceso mediante la consola USB de §2. Python 3.5.3 y GCC6.3 fueron documentados en T02.
El código operativo evita f-strings, dataclasses y paquetes pip. No se exige Internet.

Entrar en la carpeta impresa; reservar resultados en el home del operador:

```bash
cd ~/trama3-t06-t08-XXXXXXXX
sha256sum -c SHA256SUMS
export T06_RESULTS="$HOME/trama3-resultados"
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-B preparacion --results "$T06_RESULTS"
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-B compilar --results "$T06_RESULTS"
sudo python3 hardware/pruebas/t06/run.py pru-smoke --board BBB-B --active --electrical-checked --results "$T06_RESULTS"
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-B pwm --active --electrical-checked --results "$T06_RESULTS"
```

Apagar antes de cada cambio de montaje, siguiendo exactamente §3:

```bash
sudo poweroff
```

Después del loopback P8_11–1k–P8_15 y nuevo arranque:

```bash
cd ~/trama3-t06-t08-XXXXXXXX
export T06_RESULTS="$HOME/trama3-resultados"
sudo python3 hardware/pruebas/t06/run.py loopback --board BBB-B --fixture loopback --active --electrical-checked --results "$T06_RESULTS"
sudo poweroff
```

Después de retirar ese loopback y montar P9_14–1k–P8_15:

```bash
cd ~/trama3-t06-t08-XXXXXXXX
export T06_RESULTS="$HOME/trama3-resultados"
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-B captura-pwm --fixture pwm-loopback --active --electrical-checked --results "$T06_RESULTS"
sudo python3 hardware/pruebas/t06/run.py cleanup --board BBB-B --active --results "$T06_RESULTS"
```

B tenía ~190 MB libres. Paquete/compilación son pequeños; comprobar df en preflight.
No borrar archivos del sistema ni reinstalar para ganar espacio. Si no cabe, conservar
BLOCKED y usar una unidad de almacenamiento ya preparada; no formatear medios.
No reparar LightDM o CDC ECM para estas pruebas: consola USB basta.

## 5. Funcionamiento y compatibilidad técnica

- `build.sh`: TI clpru/lnkpru y runtime del mismo directorio; gcc nativo para host.
- `resources.py`: sysfs PWM, remoteproc, config-pin y debugfs ya presentes en T04.
- Firmware: PRU0 directo, tabla de recursos vacía, SRAM compartida PRUSS en 0x10000
  (ARM física 0x4a310000), ABI versionada, memoria acotada a 12 KiB.
- Host: /dev/mem con O_SYNC y barreras de memoria; no altera permisos. Si kernel
  restringe ese mapa, BLOCKED: no desactivar protecciones ni cambiar kernel.
- IEP: contador 200 MHz nominal, incremento1, sin comparadores/compensación.
  Ambos PRU deben estar offline al adquirir; PTP presente bloquea uso del IEP.
- Máximo 1024 eventos; overflow y parada son explícitos. Pruebas limitadas a10s,
  aritmética de tiempo relativa y ventana menor a media vuelta de32bits.
- Config-pin consulta modos y propietario. Sólo entradas/default seguros son
  reemplazables; se permite el helper universal en entrada identificado por el pin.
  UART, GPIO ajeno, PWM solicitado o PRU activo bloquean sin forzarlos.
- No se asume equivalencia entre los dos kernels: toda interfaz se detecta en cada
  ejecución. Si falta state/firmware/debugfs, usar la recuperación documentada y
  conservar BLOCKED, sin aplicar rutas legacy adivinadas ni uio_pruss.
- `trama3-t06-host probe|status|stop` implementa control ARM/PRU; el orquestador
  realiza la secuencia autorizada. No llamar directamente al binario con firmware
  ajeno o PRUSS detenido: /dev/mem requiere la adquisición previa.
- Después de toda prueba se detiene el firmware; no deja un servicio residente.
  Persistencia/autostart no forma parte del entregable mínimo T06.

## 6. T08: procedimiento de medición

### Preparar el instrumento

Multímetro en buen estado, puntas con aislamiento. Negra a COM; roja a V/Ω
para voltaje/continuidad. Rango DC adecuado (20V o autorango).
**Nunca colocar el multímetro en corriente directamente entre + y − de una fuente.**
No abrir fuentes de red ni retirar tierras de protección. Para corrientes se usa
sonda DC o lectura de fuente de banco con resolución adecuada; si no existe,
dejar NOT_TESTED. No improvisar una medición de corriente de arranque del servo
ni bloquear su eje para medir corriente de bloqueo.

Anotar marca/modelo, resolución y precisión del rango. Incertidumbre conservadora:
porcentaje de lectura + dígitos × resolución; registrar en la misma unidad del CSV.
Si no se conoce, no inventarla: BLOCKED. Un display 3.30 no acredita exactamente3.300V.

### A. Todo apagado y desconectado

Retirar USB, fuentes, sensores externos y conexiones entre nodos.
Esperar descarga de capacitores; comprobar primero voltaje DC cercano a0 antes de Ω.
No cortocircuitar C1 para descargarlo.

| Comprobación | Puntas / acción | Interpretación |
|---|---|---|
| F1 | Una punta en cada extremo del fusible aislado | Continuidad; anotar tipo, valor y curva, no aprobar sólo por pitido |
| Retorno local | TP2 ↔ NT1.1; TP4 ↔ NT1.2; NT1.1 ↔ NT1.2 | Continuidad según unión local única |
| Corto en5V | TP1 ↔ TP2, luego invertir puntas | Carga de C1 puede cambiar lectura; baja persistente exige investigar |
| Corto3.3V | TP3 ↔ TP4 | No aceptar baja persistente; no convertir un pitido en umbral universal |
| Separación nodos | GND_A ↔ GND_B con fuentes/USB desconectados | Sin unión intencional; comprobar también equipos conectados antes de afirmar aislamiento |
| Isla PC817 | J8.1/J8.2 respecto TP4 | Sin continuidad galvánica al receptor; modo diodo entre U2.1/U2.2 identifica LED |
| Conectores | Contrastar J1/J11/J4/J10/J13 con tabla T51 | Pinout por pieza real, no sólo color |
| SW1 y EN | Continuidad sin energía | SW1 OFF deja servo sin5V y señal a tierra; EN no corta potencia |

Los puntos T51 sólo existen si hay placa construida. Si no existe, registrar etapa D pendiente.
Para BBB sola, revisar físicamente P8/P9, ausencia de puentes y fuente antes del arranque.

### B. Fuentes desconectadas de la carga

Negra al retorno de salida identificado, roja al positivo. Medir voltaje y polaridad
en conector accesible usando adaptador correcto; no introducir puntas que puedan puentear
el jack/USB. Nunca explorar la entrada de red.

Registrar tres lecturas en30s en vacío; variación visible/inestabilidad bloquea.
Para carga: únicamente carga electrónica o resistencia de potencia dimensionada y
montada por persona competente. No utilizar la BBB o servo como carga experimental.
Anotar corriente aplicada, voltaje y duración. Sin montaje apropiado, dejar vacío.

Criterio conservador del ensayo5V:4.75–5.25V incluyendo incertidumbre. Es rango de prueba,
no especificación universal del SG90 ni aprobación de corriente2.5A. La corriente
nominal de la fuente es capacidad; no significa que fuerce esa corriente en la carga.

### C. BBB sola energizada

Con alimentación propia comprobada y sin cargas externas:
fijar primero la punta negra en **P9_1 GND local**, evitando que resbale;
roja en **P9_3**, sin puentear pines adyacentes. Medir al arrancar y después de60s.
No sondear patas del procesador. Detener si hay calor, olor, reinicios o alimentación intermitente.

Rango de dominio3.3V AM335x: **3.135–3.465V** (SPRS717L §5.3).
Se usa como criterio del riel P9_3; no como permiso para elevar una entrada GPIO.
Registrar alimentación USB/jack y puerto utilizado en notas.

```bash
python3 hardware/pruebas/t08/inspeccion.py --board BBB-A --results "$HOME/trama3-resultados"
```

Para B cambiar únicamente a `--board BBB-B`. El script no tiene un voltímetro:
sensor térmico o `voltage_now` disponible se etiqueta como reporte del sistema,
no lectura de multímetro. Ausencia de mensajes undervoltage no prueba buena alimentación.

### D. Interfaz — sólo construida, revisada y autorizada

No energizar la propuesta CAD. Requiere verificación del lote, revisión de cableado/huellas,
fusible y fuente adecuada. No se concede autorización de soldadura mediante este paquete.

Antes de conectar GPIO: **JP4/JP5/JP6/JP7 abiertos**, SW1 OFF,
EN_C0/1/2 deshabilitados2–3, JP2/JP3 abiertos, servo físicamente desconectado.
Usar una sola entrada J1 **o** J11. J11 sólo banco de baja carga, sin servo.
No puentear positivos de BBB/actuadores. NT1 une retornos sólo dentro del nodo.

| Medición | Punta negra | Punta roja | Condición |
|---|---|---|---|
| Entrada5V | J1.2 | J1.1 | Fuente correcta y protección verificada |
| Salida protegida | TP2 | TP1 | Medir caída respecto J1.1 bajo carga segura |
| Riel local | TP4 | TP3/J10.1 |3.135–3.465V |
| MCP | U1.10 | U1.9 |3.3V local; evitar puentear patas |
| LDR/acústico | J5.2/J6.2 | J5.1/J6.1 | Sólo3.3V, validar módulo completo |
| Servo OFF | J4.1 | J4.2 | Cercano0V; criterio ensayo≤0.1V |
| Señal servo OFF | TP2 | TP9 | Cercano0V; servo desconectado |
| Luz RAW | TP4 | TP5 y JP4.1 | Luz/oscuridad, antes de cerrar JP4 |
| Sonido RAW | TP4 | TP6 y JP5.1 | Reposo/estímulo, requiere captura para pulsos |
| Mecánico RAW | TP4 | TP7 y JP6.1 | Contacto abierto/cerrado |
| Reloj RAW | TP4 | TP8 y JP7.1 | Opto inactivo/activo con excitación local revisada |
| Reloj TX | TP4 | TP10 | Sólo instrumento, sin interconectar nodos en T06 |

La guía no ordena alimentar/mover el servo. La revisión de SW1/potencia/etapa5V puede
hacerse sin servo; una futura prueba dinámica requiere su propio montaje seguro.
Q6 correcto no impide todas las retroalimentaciones. No conectar simultáneamente J1/J11
ni aplicar5V por señal a BBB apagada.

### E. Entradas GPIO

Medir primero en el **lado fuente** de JP4..7 abierto. El lado BBB desconectado puede
flotar: no confundir su lectura con el voltaje del módulo. Comprobar LOW y HIGH estables,
pico máximo y mínimo durante transición/encendido/apagado. Después de apagar y confirmar
niveles, cerrar un enlace por vez y repetir en el pin BBB correspondiente.

| Entrada | Lado de prueba | LOW | HIGH | Pico conservador |
|---|---|---|---|---|
| P9_27 | JP4.1, TP5 |0–0.8V |2.0–3.3V |≤menor de3.3V y riel local |
| P8_16 | JP5.1, TP6 |0–0.8V |2.0–3.3V |Ídem |
| P9_24 | JP6.1, TP7 |0–0.8V |2.0–3.3V |Ídem |
| P8_15 | JP7.1, TP8 |0–0.8V |2.0–3.3V |Ídem |

SPRS717L §5.7 especifica umbrales2.0/0.8V para estas clases LVCMOS3.3V.
El máximo absoluto de §5.1 llega a riel I/O+0.3V; **no es un objetivo de funcionamiento**.
El proyecto conserva techo3.3V y no acepta señales negativas como condición normal.
La evaluación exige intervalo completo valor±incertidumbre dentro del rango.

Multímetro sirve para estados DC. Para picos/transitorios usar osciloscopio con referencia
local y sonda apropiada. Un analizador lógico común o entrada PRU no mide amplitud.
Sin instrumento adecuado, esos puntos permanecen NOT_TESTED: no inventar un pico a partir
de un promedio. No conectar nunca tierra de osciloscopio a un nodo de potencia o red;
la masa puede estar unida a protección eléctrica y crear un puente entre nodos.

### Registrar y evaluar sin improvisar fórmulas

Crear formulario (no sobrescribe uno existente):

```bash
mkdir -p "$HOME/trama3-resultados/BBB-A/mediciones"
python3 hardware/pruebas/t08/registrar-mediciones.py --board BBB-A --file "$HOME/trama3-resultados/BBB-A/mediciones/t08-mediciones.csv"
```

El CSV es editable con editor de texto o Excel conservando nombres/unidades y punto decimal.
No rellenar cifras hasta medirlas. Cada fila exige instrumento, método, fecha y evidencia.
`value=yes/no` sólo aplica a inspecciones; valores numéricos necesitan incertidumbre.

Ejemplo de **estructura de comando**, reemplazando variables con medidas reales; no contiene
un voltaje de ejemplo que pueda confundirse con evidencia:

```bash
read -r -p "Voltaje real P9_3: " MEDIDA
read -r -p "Incertidumbre absoluta V: " INCERTIDUMBRE
read -r -p "Marca/modelo multimetro: " INSTRUMENTO
read -r -p "Nombre de foto/registro: " EVIDENCIA
read -r -p "Fecha real ISO del PC: " FECHA_REAL
python3 hardware/pruebas/t08/registrar-mediciones.py --board BBB-A --file "$HOME/trama3-resultados/BBB-A/mediciones/t08-mediciones.csv" --point P9_3 --value "$MEDIDA" --uncertainty "$INCERTIDUMBRE" --method multimeter --instrument "$INSTRUMENTO" --evidence "$EVIDENCIA" --date "$FECHA_REAL"
python3 hardware/pruebas/t08/evaluar-mediciones.py --board BBB-A --file "$HOME/trama3-resultados/BBB-A/mediciones/t08-mediciones.csv" --output "$HOME/trama3-resultados/BBB-A/mediciones/t08.json"
```

Estos prompts pertenecen a la futura toma de medidas por Erwin; no requieren otra sesión
de desarrollo con Adrián. También puede editar todas las filas de una vez.
Para B, mismos comandos cambiando **BBB-A por BBB-B en argumento y rutas**.
El evaluador usa códigos0 PASS,3 NOT_TESTED,4 BLOCKED,5 FAIL. No continuar energizando
si una inspección es no o un valor es FAIL. Vacío permanece sin medir; NaN/inf son inválidos.

## 7. Recuperar evidencias y aceptación conjunta

### PowerShell

Desde la raíz de los archivos recibidos, con una BBB conectada por vez:

```powershell
.\hardware\pruebas\ejecutar\Recopilar-Resultados.ps1 -Placa BBB-A -Modo SSH -Destino debian@192.168.7.2
.\hardware\pruebas\ejecutar\Recopilar-Resultados.ps1 -Placa BBB-B -Modo Serial -Puerto COM22
```

Cerrar PuTTY antes de la recuperación serial. Los tar.gz se guardan en una carpeta nueva
por fecha. Extraer cada uno a una carpeta de evidencia nueva con `tar -xzf` o7-Zip.
Conservar originales de todos los intentos; no mezclar placas ni elegir únicamente el mejor
resultado. No publicar contraseñas, logs crudos, MAC, números de serie ni fotos sin revisar.

El recolector SSH conserva la comprobación de clave. La ruta de resultados por defecto
es el home de Debian; si se usó otra, copiar esa carpeta explícitamente con scp o devolver
los registros a `~/trama3-resultados` sin borrar originales.

### Seleccionar ensayos expresamente y generar informe

El manifiesto evita escoger automáticamente un PASS antiguo sobre un FAIL nuevo.
Desde Linux o Windows con Python3, seleccionar los JSON que correspondan a la campaña
revisada, dentro de una misma carpeta de evidencias. Ejemplo Linux con rutas reales a sustituir:

```bash
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-A --test loopback --file evidencias/BBB-A/FECHA-ID/loopback.json
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-A --test pwm-capture --file evidencias/BBB-A/FECHA-ID/pwm-capture.json
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-A --test t08 --file evidencias/BBB-A/mediciones/t08.json
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-B --test loopback --file evidencias/BBB-B/FECHA-ID/loopback.json
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-B --test pwm-capture --file evidencias/BBB-B/FECHA-ID/pwm-capture.json
python3 hardware/pruebas/seleccionar-evidencias.py --manifest evidencias/aceptacion.json --board BBB-B --test t08 --file evidencias/BBB-B/mediciones/t08.json
python3 hardware/pruebas/evaluar.py --manifest evidencias/aceptacion.json --output evidencias/informe-aceptacion.json
```

Seleccionar el PWM1.5ms de la campaña y conservar los tres anchos como evidencia complementaria.
Las carpetas FECHA-ID son las impresas por cada ejecución, no un nombre fijo.
El informe vuelve a comprobar muestras/mediciones; no acepta sólo el campo PASS.
Para demostrar estado inicial sin hardware:

```bash
python3 hardware/pruebas/evaluar.py --manifest hardware/pruebas/aceptacion-vacia.json --output informe-sin-hardware.json
```

Esperado: T06 NOT_TESTED, T08 NOT_TESTED. Si hay pruebas parciales, el detalle por placa
muestra cuáles pasaron; los faltantes impiden cierre conjunto. T08 incluye la etapa de
interfaz como seguimiento condicionado: mientras no exista placa revisada, no dar cierre
eléctrico integral. Esto no impide preparar código o validar BBB sola.

## 8. Fallos y recuperación

| Problema | Actuación concreta |
|---|---|
| PWM no identificado | Ejecutar preflight como sudo y revisar device/npwm/debugfs. No escoger pwmchip por número. Sin identidad inequívoca, conservar BLOCKED |
| PWM ocupado | No unexportar ni parar consumidor ajeno. Identificarlo en /sys/kernel/debug/pwm; planificar liberación con su propietario antes de repetir |
| PRU ocupado | Revisar name/state/firmware de los remoteproc detectados. No detener wkup_m3 ni firmware de otro proyecto |
| config-pin falla | Consultar `config-pin -q P9_14`, `config-pin -l P9_14` (o el pin reportado). Conservar error y comprobar restauración; no forzar devmem de pinmux |
| Falta debugfs | `sudo test -r /sys/kernel/debug/pwm` y `sudo test -r /sys/kernel/debug/gpio`. T04 ya lo tenía; no montar ni cambiar boot automáticamente. Sin lectura confiable, BLOCKED |
| Permiso denegado | Auditoría puede ir sin sudo. Pruebas activas con sudo en terminal. No chmod666 /dev/mem ni sysfs |
| clpru/lnkpru/libc ausente | Usar find de §3 y CLPRU real; no mezclar instalaciones ni firmware de otra arquitectura |
| Firmware no inicia | Revisar build.json, build.log, map y reporte de comando. Ejecutar cleanup; sólo diagnóstico local: `sudo dmesg | tail -n 40`. No publicar ese log sin revisión |
| ABI/mmap no compatible | No forzar /dev/mem ni pasar a UIO cambiando drivers. Guardar BLOCKED; comprobar instalación/driver/ELF y recurso cargado |
| Captura sin flancos | Apagar, revisar resistor/cable y pin correcto. Confirmar que el loopback anterior fue retirado. No intentar resolver aplicando5V |
| Captura fuera de tolerancia | Revisar raw, max_gap, late, overflow y montaje. Repetir con período más largo; contrastar con instrumento. No ampliar tolerancia para esconder el fallo |
| UART o GPIO propietario | No cambiar pin asignado a periférico activo. Mantener BLOCKED y resolver conflicto de configuración revisado |
| Pérdida de USB | Firmware TX es finito; PWM puede persistir si proceso muere sin cleanup. No conectar cargas; recuperar consola y ejecutar cleanup antes de otra prueba |
| PRU no se detiene | Mantener salida desconectada/cargas retiradas, conservar diario y apagar correctamente. No repetir arranques sobre recurso ocupado |
| Voltaje, polaridad o corto incorrecto | Apagar/desconectar fuentes; corregir montaje y repetir inspección sin energía. Nunca aumentar fusible para ocultar disparos |
| Fuente/placa caliente o reinicios | Detener; registrar fallo. Revisar corriente, polaridad, conectores y fuente antes de repetir |
| Reinicio y diario viejo | No restaurar estado de otro arranque. El diario /run normalmente desaparece; repetir auditoría y revisar físicamente antes de activar |

## 9. Cierre de tareas y límites de la entrega

Desarrollo incluye fuentes, control, restauración, firmware, pruebas, formularios,
auditoría T51, guías y transporte. Validación PC incluye modelos de software;
no demuestra que clpru enlace con la versión instalada en cada BBB.
La compilación TI y pruebas reales quedan para Erwin, con comandos listos.

T06 se puede recomendar para cierre sólo después de evidencia de ambas placas.
T08 requiere fuentes/medidas completas y resolver pendientes T07/T51/T52 aplicables.
La revisión T51 no queda autorizada para soldar; software no reemplaza inspección física.
**No actualizar tracker ni hacer merge automático** por terminar este paquete.

Fuentes y discrepancias: [T08_Auditoria_T51.md](T08_Auditoria_T51.md).
Contrato técnico: [../pruebas/t06/README.md](../pruebas/t06/README.md).
Verificación sin hardware: [Validacion_T06_T08.md](Validacion_T06_T08.md).
