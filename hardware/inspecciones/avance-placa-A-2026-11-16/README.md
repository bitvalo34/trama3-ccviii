# Avance físico de la placa de interfaz — corte 16/11/2026

**Resultado: U1 y el encendido/apagado del LED funcionaron en las pruebas finales; validación integral pendiente. La incidencia de comunicación intermitente permanece abierta.**

## Alcance y procedencia

Pruebas realizadas por Erwin y compartidas en la conversación de inspección. Codex revisó las capturas y consolidó los resultados; no operó la BeagleBone ni los instrumentos. Se denomina **placa A** para mantener la referencia del expediente T53; no se registró aquí un identificador físico único. No extrapolar resultados a la segunda placa ni a BBB-B.

Consolidación: **16/11/2026, America/Guatemala**. Conversación de las sesiones del 15–16/11; sin sello horario individual verificable por medición. Los valores aproximados o «esperados confirmados» no son registros metrológicos de precisión. Modelo/rango exacto/calibración del multímetro, consumo y formas de onda no quedaron documentados.

Referencia: [diseño P2](../../documentacion/fuentes-P2/diseno-electrico.md), [origen P2](../../documentacion/fuentes-P2/ORIGEN.md) y [auditoría T08/P2](../../documentacion/T08_Auditoria_P2.md). Base: PR #8, commit `db1e7b2ed01f0be46cda84fd43e87c8ab0c8ec41`. El PR #5 conserva P1; no sustituir P2 por esos planos anteriores.

Este registro no cierra T08/T53, no cambia tracker, formularios de aceptación, firmware ni planos y no acredita el protocolo 102. El cierre BBB-BARE de T06 publicado por separado no equivale a validar esta interfaz con cargas.

## Resultados alcanzados

| Bloque | Resultado y evidencia | Límite |
|---|---|---|
| Adaptadores | Operador reportó 5.03 V y 5.12 V por separado | Sin rizado, aislamiento, regulación bajo carga ni corriente caracterizados |
| Fusible | Continuidad J1.1–C1+ con fusible y ausencia al retirarlo, reportadas | No valida curva, calibre ni coordinación |
| 5 V | C1 aproximadamente 5 V; primer encendido sin calentamiento perceptible ni humo reportados | Observación breve, sin consumo ni registro térmico |
| 3.3 V / RESET | Operador confirmó valores esperados en U1.9, U1.18 y conectores de sensores | Hubo confusión inicial de pines; esas lecturas contradictorias no diagnostican JP1/R1 |
| Tierra y R1 | Continuidad C1−–J10.2 y resistencia compatible con 10 kΩ entre U1.18–U1.9 confirmadas | Sin cifra exacta ni foto de instrumento |
| C4 | Marcado 104 confirmado: 100 nF nominales | No se confirmó explícitamente continuidad de ambas patas hacia U1.9/U1.10 |
| Alimentación cruzada, DC | Con solo 5 V y BBB físicamente desconectada: aproximadamente 0.03 V en J10.1, U1.18, J10.3 y J10.4 respecto a J10.2 | No descarta transitorios ni certifica aislamiento |
| Final de carrera | Operador confirmó cambio aproximadamente 3.3 V abierto / 0 V presionado | Faltan GPIO, rebote y mecanismo de nylon |
| Receptor óptico | Cambio con luz/oscuridad a 3.3 V confirmado por operador | Polaridad no registrada; faltan GPIO y enlace completo |
| MCP23017-E/SP | Bus 2 identificado por 4819c000; respuesta 0x20 y registros iniciales 0xff, 0xff, 0x00 | Comunicación intermitente observada en otros intentos |
| Salidas lógicas | U1.21 alto confirmado usando J10.2 como referencia; U1.22 reportado en 3.3 V al activar 0x02 | No acredita buzzer ni todas las características de salida |
| Retención breve | Diez pares IODIRA=0xfc / OLATA=0x01; intervalo programado de 1 s; operador confirmó 5 V conectados | Sin cargas externas en ese ensayo; no cierra estabilidad |
| LED | Captura de preparación, encendido y apagado; confirmación textual de ambas acciones; foto del LED iluminado | No mide corriente, alcance, temperatura ni recepción remota |

Detalle por comprobación: [resultados.csv](resultados.csv). Transcripciones: [evidencias.md](evidencias.md). Identificación y hashes de originales: [fuentes.json](fuentes.json). No se publican capturas completas de terminal ni se presentan las transcripciones como logs originales de la BBB.

## Incidencia abierta: comunicación I²C intermitente

Se observaron `Error: Write failed`, `Error: Read failed` y retorno de IODIRA a 0xff después de configurarlo a 0xfc. En E04, tras un reintento, IODIRA=0xff coexistió con OLATA=0x01: escribir el latch no restaura por sí solo la dirección de salida.

Parte de los fallos coincidió con 5 V externos conectados. Se probaron dos adaptadores y se reportaron fallos con ambos. Después se obtuvieron diez lecturas correctas con 5 V y el LED respondió a encendido/apagado. **No se aisló la causa.** Un reinicio es una hipótesis compatible; tampoco quedaron descartados cambios por software, contactos intermitentes o perturbaciones de alimentación/señales.

Corregir la identificación de pines y medir desde J10.2 mejoró algunas pruebas. No atribuir todos los errores a esa confusión ni considerar reparado el problema por cambiar el adaptador. Tensiones DC correctas no descartan eventos breves. Si reaparece un error, retirar los 5 V de las cargas; una escritura fallida no garantiza apagado.

## Correcciones del procedimiento

- DIP28 visto desde las letras, muesca arriba: izquierda 1–14 de arriba abajo; derecha 15–28 de abajo arriba. **U1.18 es la cuarta patilla desde abajo por la derecha**, U1.21 la octava desde arriba y U1.22 la séptima desde arriba. Se corrige una indicación verbal anterior que situó U1.18 en la quinta.
- U1.10=GND, U1.9=VDD, U1.12=SCL, U1.13=SDA, U1.18=RESET. La cara de soldaduras refleja la vista superior.
- En P2, JP1 cerrado lleva RESET a tierra; abierto permite elevarlo mediante R1. Las lecturas iniciales opuestas y de contactos A/B no se usan como evidencia de falla concreta tras la confusión de identificación; no justifican modificar el cableado.
- Tras quitar alimentación, volver a configurar I²C y U1. IODIRA=0xff significa entradas; OLATA=0x01 por sí solo no prueba una salida alta.
- Los números de las fotos anotadas identifican componentes, no terminales ni coordenadas físicas verificadas.

## Pendientes para aceptación

| Pendiente | Evidencia necesaria |
|---|---|
| Estabilidad | Repeticiones con carga y arranques, sin errores I²C ni pérdida de configuración; diagnóstico si reaparece la incidencia |
| Receptores en BBB | Lecturas reales P9_27/P8_16/P9_24; EN, JP4–JP6, polaridades y niveles |
| Acústico | Captura de flancos y umbral; la escasa variación del multímetro ante ruido no acredita pulsos válidos |
| Servo | SW1 real, conmutación de alimentación/señal, PWM en J4, tensión durante movimiento y ensayo sin carga mecánica; después nylon |
| Reloj | TX/Q5, RX/PC817, inversión, ancho/retardo y pares entre nodos |
| Buzzer | Componente no disponible: verificar modelo/consumo/polaridad y probar Q2 con carga |
| Conjunto | Cargas previstas con registro de errores/reinicios; repetir en segunda placa |
| Revisión final | Identificación física, registros completos y revisión independiente |

Al corte se entregaron instrucciones para GPIO y consultas de gpiomon/PWM, pero **no se recibió resultado de ejecución**. No se cuentan como pruebas superadas ni se marcan perfiles del runtime como calibrados.

Continuar con receptores, servo y reloj usando la [guía P2](../../documentacion/GUIA_DEFINITIVA_T06_T08_P2_BBB-A_BBB-B.md). Este informe documenta lo observado; no reemplaza el procedimiento de cableado ni constituye autorización general de energización.
