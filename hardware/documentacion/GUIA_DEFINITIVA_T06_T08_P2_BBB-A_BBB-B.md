# GUIA DEFINITIVA T06/T08 P2 — BBB-A y BBB-B

Preparación 15/11/2026. Revisión de protocolo 102. Hardware de interfaz P2-LOCAL.
Operador previsto: Erwin. Código preparado sin acceso físico a BBB en esta ejecución.
Esta guía sustituye las instrucciones activas de P1. No modifica el tracker.

## 1. Qué prueba cada nivel
- Nivel 1: BBB sola; diagnóstico PRU/PWM, loopbacks locales y alimentación propia.
- Nivel 2: interfaz P2 aislada de BBB; continuidad, fuentes, niveles y transitorios.
- Nivel 3: integración manual únicamente tras T08 PASS por nodo y revisión humana.
El software T06 de este paquete sólo activa nivel 1. No hay opción que conecte o
habilite automáticamente P2. No mueve servo ni implementa la transmisión 102.
Compilación PASS no es señal física PASS. Loopback no es reloj entre nodos.

Calendario del prompt: 15/11 T55, T52/T53/T54 y T08; 16/11 T06, T09, T10, T11;
17–19/11 integración T18/T24/T56/T57 y demostración. Recomendación: adelantar
inventario/compilación/nivel 1 mientras P2 se revisa, pero no adelantar integración.
El Excel original permanece intacto. La extracción del XLSX no estuvo disponible;
no se afirma haber revisado filas adicionales a las transcritas en el prompt.

## 2. Materiales y reglas de conexión
Una BBB por vez, Mini USB de datos, fuente propia identificada, multímetro con puntas
aisladas, resistencia 1 kohm 1/4 W para loopback, resistencias 10 kohm para entradas.
P2 requiere las herramientas de [auditoría eléctrica](T08_Auditoria_P2.md).
Para picos/rebotes: osciloscopio compatible, preferiblemente prestado; el multímetro
no sustituye capturas. Sin fuente de ensayo apropiada limitada en corriente, las
mediciones de interfaz aislada quedan pendientes, no se improvisan con la BBB.

Para cada cambio de cableado:
1. Ejecutar cleanup de recursos propios si procede.
2. Ejecutar `sudo poweroff`; esperar apagado; retirar USB y TODAS las fuentes.
3. Identificar pines con serigrafía/tabla oficial y realizar el cableado indicado.
4. Encender, entrar, repetir preflight y revisar la nueva declaración física.
5. Ejecutar sólo ese ensayo y conservar carpeta de evidencia.
6. Verificar `resources.restored=true`; apagar y retirar alimentación antes de mover cables.

No conectar 5 V a GPIO. La resistencia de 1 kohm no convierte niveles.
No unir dos salidas. No alimentar servo desde P9_3. No unir GND entre nodos.
No medir continuidad con alimentación ni corriente colocando el multímetro entre + y -.
No conectar dos masas de osciloscopio a NEG_IN y GND_ACT: puentearían Q6.

## 3. Windows: preparar y transferir
Extraer el ZIP P2 en una carpeta nueva; abrir PowerShell allí. Debe contener
`hardware` y `TRAMA3_T06_T08_P2.tar.gz`. No reutilizar la carpeta antigua de BBB.
Identificar una placa, etiquetarla A/B y guardar foto/identificador en el formulario.

```powershell
Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'Ports' } | Select-Object Status,FriendlyName
Get-FileHash .\TRAMA3_T06_T08_P2.tar.gz -Algorithm SHA256
```

Comparar hash con paquete-verificado.json de la entrega. La transferencia verifica
también el SHA del archivo y cada entrada de SHA256SUMS.

### BBB-A, Debian 10: USB SSH
Verificar primero en consola de la placa `ip -br addr`. En Windows comprobar
`ipconfig`. Sustituir la dirección de ejemplo por la real; no garantiza 192.168.7.2.

```powershell
Test-NetConnection 192.168.7.2 -Port 22
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\hardware\pruebas\ejecutar\Preparar-Pruebas.ps1 -Placa BBB-A -Modo SSH -Destino debian@192.168.7.2 -Paquete .\TRAMA3_T06_T08_P2.tar.gz
ssh debian@192.168.7.2
```

Usar credenciales existentes; confirmar identidad del host, no desactivar verificación.
Si SSH no responde, usar el procedimiento serial de B con `-Placa BBB-A`.

### BBB-B, Debian 9: consola USB
Abrir terminal serial a COM observado, 115200, 8N1, sin control de flujo.
Iniciar sesión Debian; dejar prompt autenticado. Pulsar Disconnect y cerrar la
aplicación para liberar COM; conservar USB y alimentación. COM3 es un ejemplo
acreditado en esta sesión, comprobarlo de nuevo.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\hardware\pruebas\ejecutar\Preparar-Pruebas.ps1 -Placa BBB-B -Modo Serial -Puerto COM3 -Paquete .\TRAMA3_T06_T08_P2.tar.gz
```

Esperar `Paquete verificado. En Debian: cd ~/trama3-t06-t08-XXXXXXXX`.
Copiar el comando **nuevo**, no el identificador de una entrega anterior.
Abrir otra vez terminal COM3. Acceso denegado: cerrar otras terminales; no se
necesita reinstalar controladores. Timeout: recuperar shell y verificar salida;
no ejecutar archivos parciales. No abrir dos programas sobre el mismo COM.

## 4. Debian: inventario y compilación en cada placa
Desde la carpeta recién transferida. Estos comandos son Linux, no PowerShell.
Para A elegir `BOARD=BBB-A`; para B `BOARD=BBB-B`. Repetir después de reiniciar.

```bash
BOARD=BBB-A
export T06_RESULTS="$HOME/trama3-resultados"
cat /etc/debian_version
uname -r
cat /proc/device-tree/model
echo
python3 --version
df -h .
sha256sum -c SHA256SUMS
sudo python3 hardware/pruebas/t06/run.py preflight --board "$BOARD" --results "$T06_RESULTS"
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh "$BOARD" build --results "$T06_RESULTS"
```

En BBB-B cambiar sólo primera línea a `BOARD=BBB-B`.
Python 3.5 y biblioteca estándar bastan; no pip, Internet ni actualización de Debian.
Se reservan 16 MiB libres para compilación/logs (margen de ingeniería para el paquete,
no medición máxima del compilador). Los 189 MiB observados anteriormente en B deben
revalidarse. No borrar archivos del sistema para continuar.

Preflight NOT_TESTED significa inventario sin medición física. BLOCKED imprime la
carpeta; leer `preflight.json` allí. La compilación debe terminar PASS. Genera host ARM,
ELF PRU, mapa, log y SHA en hardware/pruebas/t06/build. El mapa debe caber en IRAM/DRAM
de 8 KiB; el linker limita regiones. Evidencia build.json incluye hashes de fuente/binarios.

Si clpru no aparece:
```bash
command -v clpru
find /usr/share/ti /usr/lib/ti /opt -maxdepth 6 -name clpru 2>/dev/null
```
Se admite instalación TI completa y disposición Debian /usr/bin con datos
/usr/share/ti/cgt-pru. Requiere stdint.h TI, libc.a y rtspruv3_le.lib; no usar libc ARM
ni bibliotecas C6x. CLPRU puede indicar una instalación completa alternativa ya existente.
Falta herramienta: BLOCKED; preparar herramienta offline compatible, no cambiar kernel.

## 5. Declaración física antes de cada montaje de nivel 1
Copiar una plantilla para cada fixture; rellenar con datos **reales**.
```bash
cp hardware/pruebas/checklist-nivel1.json "$HOME/checklist-none.json"
nano "$HOME/checklist-none.json"
```
En B poner board BBB-B. operator debe coincidir con --operator. checked_at es fecha
real ISO del PC. evidence identifica foto/registro. Medir P9_3: multímetro V DC,
negra P9_1, roja P9_3, sin puentear vecinos; registrar valor e incertidumbre en V e
instrumento. El intervalo completo debe estar en 3.135–3.465 V.
Las confirmaciones empiezan en false; sólo cambiarlas tras revisar cada condición.
fixture: none, loopback, pwm-loopback o inputs. Nivel siempre 1, hardware BBB-BARE.
Guardar una copia por configuración (checklist-loopback.json etc.). No atribuir
a esta declaración una medición automática. El JSON del ensayo incluye su contenido y hash.

## 6. PRU smoke y PWM sin cargas
P8/P9 libres. Elegir operador real (ejemplo Erwin).
```bash
sudo python3 hardware/pruebas/t06/run.py pru-smoke --board "$BOARD" --active --electrical-checked --operator Erwin --checklist "$HOME/checklist-none.json" --results "$T06_RESULTS"
```
PASS exige respuesta READY/heartbeat y cleanup sin errores; no demuestra salida física.
Si falla, leer pru-smoke.json de la carpeta impresa. No encadenar prueba siguiente.

```bash
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh "$BOARD" pwm --active --electrical-checked --operator Erwin --checklist "$HOME/checklist-none.json" --results "$T06_RESULTS"
```
Aplica 1/1.5/2 ms durante dos segundos cada uno, período 20 ms. Configuración PASS
puede coexistir con NOT_TESTED eléctrico hasta capturar. No conectar servo.

PTP: el inventario registra nombre, ruta y driver. Sólo CPTS/CTPS del CPSW AM335x
identificado en 4a100000 y driver cpsw/ti-cpsw se reconoce independiente.
PTP desconocido o PRUSS/IEP mantiene BLOCKED. No descargar módulos ni detener
servicios para pasar. Conservar:
```bash
cat /sys/class/ptp/ptp*/clock_name
ls -l /sys/class/ptp/
readlink -f /sys/class/ptp/ptp*/device
readlink -f /sys/class/ptp/ptp*/device/driver
```
No se afirma que el reloj observado previamente en BBB-B sea CPTS: su dueño no
fue aportado. La nueva detección decide usando evidencia real.

## 7. Loopback PRU
Apagar y retirar toda alimentación. P8_11 → resistencia 1 kohm → P8_15 en la misma BBB.
Sin P2 ni segunda BBB. Los modos anteriores admisibles son default/gpio_input/gpio_pd/gpio_pu,
y se verifica propietario; una salida ajena bloquea. La entrada se selecciona antes de TX.
Completar checklist-loopback.json con fixture loopback. Encender, entrar en carpeta,
redefinir BOARD y T06_RESULTS, repetir preflight.

```bash
sudo python3 hardware/pruebas/t06/run.py loopback --board "$BOARD" --fixture loopback --active --electrical-checked --operator Erwin --checklist "$HOME/checklist-loopback.json" --results "$T06_RESULTS"
```
Esperado: 25 pulsos, período 20 ms, alto 1.5 ms; sin overflow/retrasos, sondeo <=10 us,
tolerancia 2% o 20 us (lo mayor). Revisar raw, analysis y resources.restored.
Sin cable falla; nunca inventar eventos. Detener y apagar antes de quitar este puente.

## 8. Captura PWM
Con placa apagada y sin alimentación, **quitar** el puente P8_11.
P9_14 → resistencia 1 kohm → P8_15. No unir P8_11 con P9_14.
Completar checklist-pwm.json con fixture pwm-loopback. Encender, preflight.

```bash
sudo bash hardware/pruebas/ejecutar/ejecutar-bloque.sh "$BOARD" pwm-capture --fixture pwm-loopback --active --electrical-checked --operator Erwin --checklist "$HOME/checklist-pwm.json" --results "$T06_RESULTS"
```
Tres carpetas, una por ancho 1000/1500/2000 us. Exige >=10 períodos completos.
La captura PRU comprueba señal recibida, no amplitud ni calibración absoluta:
PWM e IEP comparten origen de reloj. T08 requiere instrumentación para niveles/picos.

## 9. Entradas y polaridad
Apagar, retirar puente. Conectar cada entrada P9_27/P8_16/P9_24 mediante 10 kohm a P9_1.
Completar checklist-inputs.json fixture inputs. Encender, preflight:
```bash
sudo python3 hardware/pruebas/t06/run.py inputs --board "$BOARD" --fixture inputs --active --electrical-checked --operator Erwin --checklist "$HOME/checklist-inputs.json" --invert-mask 0 --results "$T06_RESULTS"
```
C0=P9_27 bit5, C1=P8_16 bit14, C2=P9_24 bit16. Una lectura R31 por muestra.
raw_vector debe ser 0. Apagar y mover UN resistor a P9_3; repetir:
C0 produce 1, C1 produce 2, C2 produce 4. No cambiar energizado.
invert-mask sólo normaliza bits (XOR 0..7); conserva originales y no adivina polaridad.
Elegirla tras caracterizar módulos en T09; mecánico P2 cerrado es bajo. Reloj PC817
también invierte, pero T06 loopback directo no valida ese camino ni aplica su inversión.

pru-tx y pru-rx existen para instrumentación. TX requiere checklist none e instrumento
3.3 V en P8_11/P9_1. RX requiere fixture pwm-loopback y fuente compatible previamente
verificada; preferir pwm-capture para controlar ambos recursos en una transacción.
No ejecutar dos procesos T06 simultáneos ni iniciar PWM en uno para capturarlo en otro.

## 10. Limpieza y recuperación
Cada ensayo intenta cleanup. Si restored=false, conserva diario y detén la secuencia.
Sin cambiar cables ni conectar cargas:
```bash
sudo python3 hardware/pruebas/t06/run.py cleanup --board "$BOARD" --active --results "$T06_RESULTS"
```
No requiere checklist para recuperar recursos propios. Sólo utiliza diario de este arranque.
Sin diario: NOT_TESTED, no toca recursos. Dueño PRU cambiado: BLOCKED, no detener ajeno.
No borrar /run/trama3-t06/state.json para forzar otra prueba. Guardar diagnóstico.
Ctrl+C/SIGTERM/SIGHUP intentan restaurar; SIGKILL, corte o kernel colgado no garantizan
limpieza. Si falla recuperación, apagar controladamente, retirar alimentación y revisar
antes de reiniciar. Un firmware propio no se instala al arranque.

## 11. T08: formularios y registro
Seguir [auditoría P2](T08_Auditoria_P2.md) en orden, un nodo por vez.
```bash
python3 hardware/pruebas/t08/registrar-mediciones.py --board "$BOARD" --file "$HOME/T08-$BOARD-P2.csv"
```
La plantilla es esquema 2 / P2-LOCAL; no copiar medidas de P1. Guardar fecha real del PC.
Ejemplo de sintaxis, sustituir VALOR, INCERTIDUMBRE, FECHA y referencias por datos reales:
```bash
python3 hardware/pruebas/t08/registrar-mediciones.py --board "$BOARD" --file "$HOME/T08-$BOARD-P2.csv" --point P9_3 --value VALOR --uncertainty INCERTIDUMBRE --method multimeter --instrument MODELO_RANGO --operator Erwin --date FECHA --evidence FOTO_O_REGISTRO
```
No copiar valores de ejemplo como medidas. Para bool usar yes/no, incertidumbre vacía,
method de plantilla, evidence y operator siempre. Para q6_verificado, p2_conforme y
sw287_* el campo detail contiene JSON según auditoría. El editor CSV permite incluirlo;
el script acepta --detail con JSON entre comillas simples. Conserva backups de cambios.

```bash
python3 hardware/pruebas/t08/evaluar-mediciones.py --board "$BOARD" --file "$HOME/T08-$BOARD-P2.csv" --output "$T06_RESULTS/$BOARD/t08-intento01.json"
```
No sobrescribe informes; usar intento02 para repetir. Genera JSON y Markdown.
Vacío NOT_TESTED, metadatos/revisión incompatibles BLOCKED, fuera de rango FAIL.
Un presupuesto de corriente no es medida. Simulaciones no acreditan hardware.
Sólo integration_allowed=true más revisión humana permite integrar ese nodo.
No se promueve automáticamente a nivel 3.

## 12. Integración posterior
Antes de cerrar JP4..7: nivel 2 PASS, T52 y continuidad firmadas, fuentes/lotes
confirmados y ausencia de tensión indebida, incluidas transiciones.
Apagar todo. Revisar arnés J10 contra tabla P2: 1 P9_3, 2 P9_1, 3 P9_19,
4 P9_20, 5 P9_14, 6 P8_11, 7 P9_27, 8 P8_16, 9 P9_24, 10 P8_15.
Conectar primero alimentación lógica y referencia local verificadas, GPIO desconectados;
confirmar rieles. Apagar antes de añadir cada receptor. No usar run.py bare con P2 conectada.
La verificación I2C y actuación integrada pertenece a T18/T09/T10; no hacer barridos
indiscriminados ni escribir registros desde este paquete. SW287 OFF y servo ausente al inicio.
T24 verifica reloj por PC817 entre nodos; T57 recepción continua. T06 no los acredita.

## 13. Seleccionar evidencia y evaluar ambas BBB
Todas las referencias deben quedar dentro de la carpeta del manifiesto.
Copiar el CSV y evidencias asociadas junto a resultados. Elegir explícitamente intentos;
no elegir automáticamente el mejor PASS. Usar rutas reales de carpetas impresas.

```bash
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test build --file "$T06_RESULTS/$BOARD/CARPETA_BUILD/build.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test pru-smoke --file "$T06_RESULTS/$BOARD/CARPETA_SMOKE/pru-smoke.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test loopback --file "$T06_RESULTS/$BOARD/CARPETA_LOOP/loopback.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test pwm-capture-1000 --file "$T06_RESULTS/$BOARD/CARPETA_1000/pwm-capture.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test pwm-capture-1500 --file "$T06_RESULTS/$BOARD/CARPETA_1500/pwm-capture.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test pwm-capture-2000 --file "$T06_RESULTS/$BOARD/CARPETA_2000/pwm-capture.json"
python3 hardware/pruebas/seleccionar-evidencias.py --manifest "$T06_RESULTS/aceptacion.json" --board "$BOARD" --test t08 --file "$T06_RESULTS/$BOARD/t08-intento01.json"
python3 hardware/pruebas/evaluar.py --manifest "$T06_RESULTS/aceptacion.json" --output "$T06_RESULTS/aceptacion-intento01.json"
```
En una placa, la otra permanece NOT_TESTED. Unir posteriormente ambas carpetas
y seleccionar las referencias de A/B en un mismo manifiesto. El evaluador recalcula
capturas/mediciones y comprueba hashes build-ensayo. No cierra tareas por un PASS aislado.

## 14. Exportar a Windows
En SSH, desde PowerShell:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\hardware\pruebas\ejecutar\Recopilar-Resultados.ps1 -Placa BBB-A -Modo SSH -Destino debian@192.168.7.2 -Carpeta .\evidencias-A
```
En B dejar shell autenticado, Disconnect/cerrar terminal:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\hardware\pruebas\ejecutar\Recopilar-Resultados.ps1 -Placa BBB-B -Modo Serial -Puerto COM3 -Carpeta .\evidencias-B
```
No sobrescribir exportaciones. Conservar fotografías/oscilogramas junto al paquete y
manifestar sus rutas. Los scripts sólo recogen ~/trama3-resultados/BBB-X:
copiar allí CSV/checklists/fotos antes de exportar, sin borrar originales.
Un reloj BBB atrasado se identifica; registrar fecha PC en observaciones, no ocultar
intentos antiguos ni modificar timestamps para que parezcan nuevos.

## 15. Criterio de salida
T06: build, smoke, loopback, tres capturas PWM y limpieza en ambas BBB.
T08: todos los puntos P2, evidencia física e identificación por nodo, sin FAIL/BLOCKED.
T55: software/formularios adaptados; conformidad de montaje pendiente.
T57: contrato/modelo separado; no se declara receptor continuo implementado.
