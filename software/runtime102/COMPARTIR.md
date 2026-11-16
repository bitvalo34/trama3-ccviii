# Obtener los avances para otro PC o BBB

La rama `implementacion-protocolo102-runtime` incluye la adaptacion T06/T08 P2
y el runtime. No requiere fusionar las PR para descargarla. No reemplazar una
copia con cambios locales: usar una carpeta nueva o conservar esos cambios.

```sh
git clone --branch implementacion-protocolo102-runtime https://github.com/bitvalo34/trama3-ccviii.git trama3-runtime
cd trama3-runtime
git rev-parse HEAD
node software/runtime102/test.cjs
node software/runtime102/cli.cjs simulate Hola Respuesta
```

Requiere Git y Node 18 o posterior. Python 3 se necesita para el propietario
de recursos y las pruebas P2. Descargar fuentes en una BBB no inicia hardware.
No instalar una version de Node sin comprobar compatibilidad con su Debian.

Chat simulado en PC, con un directorio de log nuevo cuyo padre exista:

```sh
node software/runtime102/node-web.cjs logs-chat-01
```

Consultar OPERACION.md para argumentos y vistas A/B. El chat actual simula
ambos nodos; no es todavia el chat conectado a cada BBB fisica.

Para un traslado sin Git/Internet en BBB, generar ZIP de fuentes desde la raiz:

```sh
python software/runtime102/package-runtime.py runtime102-fuentes.zip
```

El nombre debe ser nuevo. Incluye SHA256SUMS y referencias P2; no incluye Node,
Python, compiladores TI ni binarios ARM/PRU. Registrar el commit del checkout
junto al ZIP. Leer ARRANQUE_BBB.md antes de cualquier prueba del lanzador.

T06 BBB-BARE tiene evidencias previas; el ZIP original de evidencias se distribuye
por separado. El resumen y hash estan en hardware/documentacion/Cierre_T06_2026-11-15.md.
T08, calibracion P2, compilacion TI/ARM del runtime y comunicacion entre placas
siguen pendientes. Los perfiles distribuidos bloquean la activacion fisica.

Orden de revision: PR base T06/T08 existente, adaptacion T55/P2 y cierre T06,
y runtime. La referencia electrica P2 proviene del PR #7; P1 del PR #5 no debe
sustituirla. No se fusionan PR automaticamente ni se cambia la calendarizacion.
