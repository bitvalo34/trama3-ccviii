# Preparacion de software sin placas

Este paquete contiene fuentes, pruebas y documentos. No incluye Node, Python,
compiladores ni firmware compilado. No instala servicios ni cambia la configuracion
de las BBB. Todas las pruebas nuevas son simuladas; T06 conserva su evidencia previa.

## Chat persistente por nodo en PC

Requiere Node 18 o posterior. Desde la carpeta cc8-trama3:

```powershell
node .\repo\software\runtime102\node-web.cjs .\evidencias\chat-nodos-01 SMBUS utf-8
```

El directorio padre debe existir y chat-nodos-01 debe ser nuevo.
Abrir http://127.0.0.1:8081/?node=A y http://127.0.0.1:8081/?node=B en dos pestanas.
Cada vista envia por su propio endpoint; los mensajes llegan mediante capturas
simuladas, decodificacion, CRC y ACK. Se conserva la sesion entre mensajes.
HTTP solo controla el banco local: no demuestra transporte fisico entre BBB.
El tiempo virtual avanza rapidamente; no mide rendimiento real.

Cambiar SMBUS por AUTOSAR, SAE-J1850 o MAXIM-DOW; codificacion utf-8 o windows-1252.
La configuracion se elige al iniciar la sesion, no a mitad de un mensaje.
Estados: pendiente, enviando, confirmado por el receptor, fallido/entrega incierta.
Un recibido no implica que el emisor haya recibido el ACK final.
Cola maxima: 8 mensajes por nodo; hasta 1024 bytes por mensaje. Los registros
A.jsonl/B.jsonl se guardan en la carpeta indicada y se descargan desde cada vista.
Ctrl+C cierra la sesion y guarda la informacion de limpieza. Reiniciar requiere
directorio nuevo. El banco termina tambien al alcanzar sus limites de log/eventos.

### Demostracion de errores y recuperacion

Detener la instancia anterior con Ctrl+C antes de reutilizar el puerto 8081.
Para corromper una vez un DATA de A manteniendo su CRC original:

```powershell
node .\repo\software\runtime102\node-web.cjs .\evidencias\chat-crc-01 SMBUS utf-8 corrupt-data
```

Enviar desde A. Ver reintentos y diagnostico NACK en el chat y descargar ambos logs.
Otros escenarios: drop-data-ack, drop-end-ack, drop-all-A, bridge-exit,
capture-gap, epoch-change. Sin argumento se usa none. Solo afectan el simulador.
Los escenarios fatales detienen la sesion; crear otra para continuar.

Para ejecutar todos los casos y obtener reporte y registros:

```powershell
node .\repo\software\runtime102\fault-suite.cjs .\evidencias\runtime102-fallos-01
```

report.json contiene hashes de las fuentes, REPORTE.md el resumen y cada
subcarpeta los logs. FAIL de una sesion con fallo inyectado puede ser esperado:
el resultado del ensayo se identifica como verdict. La base del informe tecnico
esta en docs/planificacion/Informe_Runtime102_Base.md.

## Controlador P2 y perfiles

p2-adapter.cjs mantiene un proceso Python vivo y convierte prepare/shutdown en
operaciones confirmadas. p2-worker.py utiliza el mismo Outputs de p2.py.
El CLI solo permite --mock. serve() acepta un Outputs con backend Linux desde
un propietario de recursos; ese lanzador fisico sigue pendiente.
Un fallo de apagado se propaga como error: no se convierte en confirmacion de limpieza.

profiles/BBB-A.json y BBB-B.json documentan identidad, ABI3, pines, polaridad y
calibracion pendiente. COM5/COM3 y versiones Debian son referencias historicas,
no identificadores automaticos de la placa. La polaridad 0 no esta acreditada para P2.
La validacion en modo hardware rechaza los perfiles sin calibracion. No rellenar
valores ficticios para superar esa validacion. Pasarla tampoco acredita T08 ni
reemplaza la propiedad exclusiva de IEP/PRU/PWM/I2C y el checklist electrico.

La anticipacion PRU actual es 20 ms y el presupuesto de escritura 15 ms; ambos
son experimentales. READY significa escritura completada, no servo asentado.
La captura ocurre a 0.8T. Hay que caracterizar respuesta mecanica/acustica,
polaridad y filtros antes de habilitar los medios. settle_ms se registra para
validar el perfil; todavia no configura un filtro o retraso del firmware.

## Verificacion y preparacion de entrega

Desde repo, con Python disponible:

```text
node software/runtime102/test.cjs
node software/runtime102/test_supervisor.cjs
node software/runtime102/test_integration.cjs
python3 software/runtime102/test_p2.py
python3 software/runtime102/preflight-runtime.py
python3 software/runtime102/package-runtime.py runtime102-fuentes.zip
```

test_integration usa python3; en Windows se puede indicar la ruta del ejecutable
mediante TRAMA3_PYTHON. El paquete ZIP incluye SHA256SUMS y dependencias locales
de matrices/compilacion; extraerlo y ejecutar desde su raiz (sin el prefijo repo).
No se incluyen evidencias fisicas ni se modifica el tracker. El informe tecnico
puede usar docs/planificacion/entregables-runtime102.md como matriz de avances.

Antes de probar en BBB: inventario de herramientas, compilacion conjunta ABI3
host/firmware, revision de mapa/ensamblador, propietario de recursos y restauracion,
prueba sin P2, calibracion P2 y luego sesion completa. Debian 9/10 ARM y Node 18+
siguen pendientes de compatibilidad; no actualizar el sistema operativo a ciegas.
