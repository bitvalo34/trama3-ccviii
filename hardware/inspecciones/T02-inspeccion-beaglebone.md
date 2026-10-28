# T02 — Inspección de las dos BeagleBone Black

**Inicio real:** 2026-10-28, Guatemala. **Estado: parcial, en progreso.**

Responsable del tracker: Adrián; revisor del tracker: Erwin. Ejecutor físico: Erwin, quien tiene las dos placas. Revisor técnico cruzado previsto: Adrián. Roles y fechas planificadas del Excel no modificados. Una hora-persona es estimación histórica, no duración real acreditada.

## Objetivo y condiciones

Comprobar identidad, condición física, alimentación, arranque, Debian, acceso Mini USB y herramientas. Lectura y diagnóstico únicamente; sin instalar paquetes, cambiar GPIO/pinmux/PWM, cargar firmware PRU ni conectar sensores. ADR-0002 se mantiene; no se mide frecuencia máxima en T02.

Erwin informa una placa conectada al PC, sin FTDI. La llamamos provisionalmente **BBB-A**; BBB-B es la segunda, todavía no inspeccionada. Falta identificación física consistente. La revisión visual sin alimentación debe hacerse después de un apagado seguro: la placa ya estaba conectada al comenzar. No atribuir una revisión previa que no ocurrió.

## Evidencia real obtenida

- Repositorio local limpio y sincronizado con `bitvalo34/trama3-ccviii`; se creó rama `t02-inspeccion-bbb`.
- Windows detecta `Remote NDIS Compatible Device`, estado Up. Dirección local USB verificada; omitida del registro público.
- Enumera almacenamiento Linux USB, volumen BEAGLEBONE y puerto serial USB en estado OK. La consola serial no se abrió: su presencia no prueba acceso autenticado.
- Función secundaria `CDC ECM` con código28 (controlador faltante). No se modificaron controladores. RNDIS sí permite la conectividad observada.
- La dirección candidata respondió a ping y el servicio SSH anunció disponibilidad; dirección y banner exacto omitidos del registro público.
- No se inició sesión ni se probaron contraseñas. **El banner SSH no prueba la versión real del sistema operativo o kernel.**

Se demuestra enumeración USB, transporte de datos y un servicio activo; no se demuestra arranque completo, estabilidad, calidad de alimentación ni salud del almacenamiento. No hay mediciones eléctricas.

## Comparación actual

| Aspecto | BBB-A | BBB-B |
|---|---|---|
| Modelo y revisión | BBB Black declarada; falta confirmar modelo y revisión | BBB Black declarada; no verificada |
| Condición física/conectores | No verificado | No verificado |
| Arranque | USB y SSH activos; secuencia de encendido no observada | No verificado |
| Debian | No verificado; sólo anuncio SSH, insuficiente para identificar Debian | No verificado |
| Kernel y CPU | No verificado | No verificado |
| RAM | No verificado | No verificado |
| Almacenamiento/eMMC/microSD | No verificado | No verificado |
| Fuente usada | Falta confirmar USB solo o fuente externa | No verificado |
| Fuente definitiva | No verificado | No verificado |
| Mini USB/datos | Gadget y red responden | No verificado |
| Acceso Debian autenticado | Pendiente; SSH disponible | No verificado |
| PRU/I2C/PWM reconocibles | No inspeccionados ni probados | No inspeccionados ni probados |
| Problemas | CDC ECM código28; no bloquea RNDIS observado | Diagnóstico pendiente |
| Recomendación | Confirmar alimentación y acceso; continuar lectura | Mantener desconectada hasta terminar A |

## Alimentación y revisión física pendientes

Confirmar si A está alimentada sólo por Mini USB, si tiene fuente externa y accesorios. Por fuente: marca/modelo, salida5V, corriente indicada, jack y polaridad, cable, disponibilidad permanente y medición si hay multímetro. M34 prevé5V regulados/2A con centro positivo y jack5,5x2,1mm; que encaje no acredita compatibilidad. No conectar12V ni alimentar por P8/P9.

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

CDC ECM sin controlador no impide la respuesta RNDIS; dejarlo para T04 si se necesita esa función. Alimentación, identidad física y autenticación siguen sin verificar. No hay evidencia para declarar una placa dañada.

El tracker actual marca **T01 Completada/100%**, mientras README/ADR dicen revisión pendiente y la observación antigua del Excel aún menciona confirmaciones. Registrar discrepancia sin reabrir T01 ni alterar sus documentos en esta tarea.

## Aceptación y actualización manual

- [ ] Identidad y revisión física de ambas placas.
- [ ] Alimentación y arranque observados en ambas.
- [ ] Debian/kernel/recursos obtenidos por acceso real.
- [ ] Acceso Mini USB autenticado o bloqueo concreto por placa.
- [ ] Herramientas y limitaciones identificadas.
- [x] Evidencia inicial real de USB y respuesta de red de A.
- [ ] Revisión cruzada de resultados finales.

**T02 no puede cerrarse.** Estado parcial sugerido: En progreso,10% orientativo. Inicio real28/10/2026; sin fecha de fin. Conservar13/10 histórico. Hoja Tracker maestro, fila7: K7 En progreso, M7 10%, responsables originales y criterio P7 sin cambios. O7: “Informe parcial T02 en hardware/inspecciones”.

Q7 propuesto: “28/10: Erwin inicia inspección; Adrián mantiene rol del tracker y revisará evidencias. Primera placa detectada por Windows: RNDIS, ping y TCP22 responden. CDC ECM código28. Pendientes alimentación, revisión física, acceso Debian autenticado, herramientas y segunda placa. Sin cambios de sistema; T02 no cerrada”. **No se modifica el Excel.**

## Continuación

T03 recibirá inventario real de fuentes/cables/herramientas; no comprar por supuestos. T04 recibirá Debian/kernel, problemas USB y soporte aparente PRU/I2C/PWM; no se configuran aquí. T06 prueba funcionamiento posteriormente.

Fuentes: tracker filas6–13; BOM M01/M23/M24/M28/M34; v3.0 caps.5–7A; ADR-0001/0002. Documentación oficial de [conectores](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html) y [alimentación](https://docs.beagleboard.org/boards/beaglebone/black/ch06.html).
