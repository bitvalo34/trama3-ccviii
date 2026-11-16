# T08 — Auditoría eléctrica P2-LOCAL
Fecha: 15/11/2026. Fuentes del circuito: [instantánea P2](fuentes-P2/ORIGEN.md).
No certifica que el montaje soldado corresponda: exige fotos frente/reverso y revisión
independiente T52/T53/T54 por cada nodo. Las posiciones son referencias P2;
si una referencia no se identifica físicamente, registrar BLOCKED, no adivinar.

## Cambios frente al histórico
IRLZ44N canal N protege el retorno; no equivale al PMOS anterior.
J11/MOD3 y J12/adaptador se retiraron. No aparecen como puntos activos nuevos.
La documentación P1 se conserva en Git para auditoría, no para cablear P2.

## Q6: identidad, función y límites
Confirmar fabricante, marcado completo y hoja del lote. Para la referencia Infineon
IRLZ44NPbF TO-220AB, pin1 G, pin2 D, pin3 S; aleta D.
P2 especifica G=+5V_ACT, D/aleta=NEG_IN, S=GND_ACT y R30=100 kohm G-S.
Pads C10/C11/C12 según instantánea; verificar vista superior real, no inferir
orientación desde una fotografía. Aleta aislada de chasis, tornillos y otros retornos.

Con polaridad correcta el diodo S→D inicia conducción; VGS enciende el canal.
En inversión en frío el esquema busca bloquear. No probar inversión energizada,
ni con BBB/servo, ni inferir protección de sobrecorriente o corriente inversa.
Fuente aislada/flotante por nodo, salida y polaridad acreditadas por documentación.
NEG_IN no es GND_ACT. Un puente, una masa de osciloscopio o fuente común puede anular Q6.
NT1 es la unión local prevista GND_ACT-GND_LOGIC; no une NEG_IN ni los nodos.

La hoja Infineon citada por P2 especifica RDS(on) máximo 35 mohm a VGS=4 V, 25 C:
a 1 A, caída calculada 35 mV y potencia 35 mW; no son mediciones.
I²R depende de temperatura, VGS y lote. No usar 47 A de catálogo como capacidad
de perfboard. F1 1 A provisional, calibre, contactos y disipación limitan el montaje.
Medir caída bajo carga limitada conocida y temperatura; criterio de ensayo Q6_CAIDA
<=0.15 V a <=1 A es diagnóstico conservador, no especificación universal del transistor.
Si falla, cortar alimentación; revisar terminales, VGS, soldadura y carga.
No elevar fusible ni voltaje para compensar. Sin fuente limitada/carga segura, pendiente.

## SW287
Identificar seis terminales con multímetro, interruptor aislado y sin alimentación.
Los números son funcionales del arnés J13, no numeración garantizada del fabricante.
Medir todos los pares (15 combinaciones) en cada posición y adjuntar tabla/foto.

| Posición | Pares cerrados | Resto | Potencia servo | Señal |
|---|---|---|---|---|
| OFF extremo | 2-3, 5-6 | Abiertos | Cortada; 3 sin cable | Tierra directa |
| CENTRO | Ninguno | Abiertos | Cortada | Descarga R16 47 kohm |
| ON | 1-2, 4-5 | Abiertos | Conectada | PWM doble inversor |

Comunes 2 y 5. Terminal1 +5V_ACT, 2 +5V_SERVO, 3 aislado, 4 PWM_5V,
5 SERVO_SIG, 6 GND_ACT. No asumir que centro equivale a OFF.
Cambiar selector sin alimentación durante comprobaciones; con carga sólo tras
caracterización y especificación real de contactos. El dato comercial no autoriza
corriente del sistema. Para mantenimiento OFF más retirar toda alimentación.

## Procedimiento por etapas y riesgos
1. Sin energía: desconectar fuentes, BBB, sensores y enlaces entre nodos. Verificar
   tensión cercana a cero antes de continuidad. No descargar C1 por cortocircuito.
   Inspeccionar puentes, polaridad, Q6/R30/NT1, fusible y arneses.
   NEG_IN-GND_ACT puede mostrar diodo interno y carga capacitiva: un pitido no
   demuestra bypass. Contrastar recorrido y, si hay ambigüedad, aislar una pata Q6
   sólo mediante reparación documentada por persona competente; no puentear para probar.
2. Fuentes aisladas: negra negativo identificado y roja positivo accesible, V DC
   rango 20 V/autorango; sin abrir adaptador de red ni cortocircuitar jack.
   Medir tres veces en 30 s. Bajo carga usar carga electrónica/fuente apropiada,
   no servo bloqueado. Sin equipo, registrar NOT_TESTED.
3. BBB sola: P9_1 negra, P9_3 roja; sin P2. Registrar arranque y 60 s.
4. Interfaz aislada: BBB/J10 y servo desconectados, JP4..7 abiertos, SW287 OFF.
   Confirmación de montaje antes de energizar. Usar fuente limitada de ensayo y
   carga dimensionada; riel lógico 3.3 V de equipo adecuado sólo con J10 desconectado.
   Nunca inyectar esa fuente en P9_3. Establecer límite de corriente según carga real,
   no un valor arbitrario copiado; excederlo detiene la etapa.
5. Entradas: medir en TP5/6/7/8 y extremo interfaz del arnés correspondiente, BBB
   desconectada, enlaces abiertos. Caracterizar LOW/HIGH, mínimo y pico en arranque,
   apagado y conmutación. No cerrar GPIO si faltan esas evidencias. C0/C1 dependen
   de módulo exacto; comprobar funcionamiento a 3.3 V, no sólo datasheet LM393.
6. Integración: únicamente T08 PASS y revisión humana; conexiones progresivas con
   energía retirada entre cambios. No conectar tierra entre nodos. Dos USB al mismo
   PC ya pueden unir referencias; documentarlo, no afirmar aislamiento total.

Para cada fallo: retirar alimentación, conservar registro, corregir causa y repetir
como intento nuevo. Para BLOCKED/NOT_TESTED: no pasar la etapa dependiente.
No declarar seguridad por ausencia de humo ni porque Debian arranque.

## Límites y fuentes
- AM3358 SPRS717, alimentación I/O 3.3 V: 3.135–3.465 V; umbrales 0.8/2.0 V.
  [TI](https://www.ti.com/lit/ds/symlink/am3358.pdf).
- GPIO: ensayo conservador 0..3.3 V y pico/alto no superior al mínimo del riel local;
  no usar máximos absolutos como rango normal. El osciloscopio comprueba extremos.
- 5 V 4.75–5.25 V: criterio de ensayo de P2, no aprobación de cualquier fuente/servo.
- MCP23017 admite 1.8–5.5 V según [Microchip](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf);
  aquí se exige riel P2 de 3.3 V para compatibilidad local.
- J5/J6: se exige alimentación 3.3 V de P2 y identificación/funcionamiento del lote.
  No hay hoja completa de los módulos reales; limites_lotes y checks de módulo
  siguen pendientes hasta corroborar. No elevar alimentación a 5 V.
- SG90: J4_ON >=4.8 V como referencia P2, techo de ensayo 5.25 V.
  Confirmar variante comprada. OFF/CENTRO <=0.1 V es criterio conservador tras
  estabilización, no certificación de arranque; pico central se mide tras descarga.
- 75 mA lógica es presupuesto P2, 20 mA buzzer es condición del driver, 1 A es
  fusible provisional: los formularios exigen corriente real, no cálculo.
- [Infineon IRLZ44N](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf),
  [BeagleBoard conectores](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html),
  [expansión](https://docs.beagleboard.org/boards/beaglebone/black/ch08.html),
  [Sharp PC817](https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf).
Las fuentes genéricas no identifican lotes reales. Pinout U2: 1 ánodo,2 cátodo,
3 emisor local,4 colector local; verificar variante y aislamiento de isla.

## Campos estructurados especiales
q6_verificado.detail, tras comprobar la pieza, requiere:
```json
{"part":"IRLZ44N","manufacturer":"FABRICANTE_REAL","package":"TO-220","datasheet":"REFERENCIA_REAL","pins":{"1":"G","2":"D","3":"S","tab":"D"},"nets":{"G":"+5V_ACT","D":"NEG_IN","S":"GND_ACT"}}
```
No copiar placeholders como evidencia.
sw287_ON.detail: {"closed":["1-2","4-5"],"all_other_pairs_open":true,"terminal_map_evidence":"TABLA_REAL"}.
OFF usa ["2-3","5-6"]; CENTRO []. Se exige comprobar todos los pares.
p2_conforme.detail: netlist_sha256, front_photo, back_photo, reviewer, board_serial.
El hash identifica documento cotejado; fotos/revisor acreditan declaración de conformidad,
no son autenticados por el software.

## Tabla operativa por punto
Todos los registros exigen board, hardware_revision=P2-LOCAL, schema=2, origin=physical,
operator, fecha real ISO, instrumento (modelo/rango), evidencia, método y valor.
Numéricos: incertidumbre en mismas unidades, no porcentaje ni valor nominal.
Negra COM y roja V/ohm para tensión/continuidad. Corrientes sólo sonda o lectura de fuente
con resolución adecuada; **nunca** puntas entre positivo y negativo en modo amperímetro.
La columna referencia indica posición eléctrica; contrastar ubicación física con foto P2.
Para inspecciones/continuidad la evidencia debe incluir valores/tabla observada, no sólo yes.

| Campo CSV | Referencia / accion | Negra | Roja | Metodo / escala | Alimentacion / SW287 | Esperado y fuente |
|---|---|---|---|---|---|---|
| fuente_bbb_5v | Salida fuente BBB aislada | Negativo salida | Positivo salida | multimeter V DC 20 V/auto | Fuente sola; interfaz ausente | 4.75..5.25 V; P2 / limites y lotes arriba |
| fuente_act_5v_vacio | Salida adaptador actuadores | Negativo salida | Positivo salida | multimeter V DC 20 V/auto | Fuente sola, sin carga | 4.75..5.25 V; P2 / limites y lotes arriba |
| fuente_act_5v_carga | Salida con carga segura conocida | Negativo salida | Positivo salida | multimeter V DC 20 V/auto | Fuente + carga de ensayo, sin BBB/servo | 4.75..5.25 V; P2 / limites y lotes arriba |
| P9_3 | Header BBB P9 | P9_1 | P9_3 | multimeter V DC 20 V/auto | BBB sola | 3.135..3.465 V; AM3358 + criterio conservador GPIO |
| J1_ENTRADA | Bornera J1 | J1.2 NEG_IN | J1.1 positivo | multimeter V DC 20 V/auto | Interfaz aislada; OFF | 4.75..5.25 V; P2 / limites y lotes arriba |
| TP1_5V_ACT | Riel protegido efectivo | TP2 GND_ACT | TP1 +5V_ACT | multimeter V DC 20 V/auto | Interfaz aislada; OFF | 4.75..5.25 V; P2 / limites y lotes arriba |
| Q6_VGS | Q6 G-S | Q6.3 S | Q6.1 G | multimeter V DC 20 V/auto | Carga limitada documentada; OFF | 4.0..5.25 V; P2 / limites y lotes arriba |
| Q6_CAIDA | Q6 S-D | Q6.2 D NEG_IN | Q6.3 S GND_ACT | multimeter V DC 20 V/auto | Carga <=1 A documentada; OFF; multimetro flotante | 0..0.15 V; P2 / limites y lotes arriba |
| TP3_3V3 | Riel logico | TP4 | TP3 | multimeter V DC 20 V/auto | 3.3 V ensayo, J10 desconectado; OFF | 3.135..3.465 V; P2 / limites y lotes arriba |
| U1_VDD | MCP23017 DIP28 | U1.10 VSS | U1.9 VDD | multimeter V DC 20 V/auto | 3.3 V ensayo, J10 desconectado; OFF | 3.135..3.465 V; P2 / limites y lotes arriba |
| J5_VDD | Bornera optico, no orden del modulo | J5.2 | J5.1 | multimeter V DC 20 V/auto | Modulo identificado a 3.3 V, JP4 abierto; OFF | 3.135..3.465 V; P2 / limites y lotes arriba |
| J6_VDD | Bornera acustico, no orden del modulo | J6.2 | J6.1 | multimeter V DC 20 V/auto | Modulo identificado a 3.3 V, JP5 abierto; OFF | 3.135..3.465 V; P2 / limites y lotes arriba |
| J4_servo_OFF | Bornera servo J4 | J4.1 GND_ACT | J4.2 | multimeter V DC 20 V/auto | Interfaz aislada sin servo; OFF | 0..0.1 V; P2 / limites y lotes arriba |
| TP9_servo_OFF | Senal servo TP9/J4.3 | GND_ACT | TP9 | multimeter V DC 20 V/auto | Sin servo; OFF | 0..0.1 V; P2 / limites y lotes arriba |
| J4_servo_CENTRO | Bornera servo J4 | J4.1 GND_ACT | J4.2 | multimeter V DC 20 V/auto | Interfaz aislada sin servo; CENTRO | 0..0.1 V; P2 / limites y lotes arriba |
| TP9_servo_CENTRO | Senal servo TP9/J4.3 | GND_ACT | TP9 | multimeter V DC 20 V/auto | Sin servo; CENTRO tras descarga | 0..0.1 V; P2 / limites y lotes arriba |
| J4_servo_ON | Bornera servo J4 | J4.1 GND_ACT | J4.2 | multimeter V DC 20 V/auto | Interfaz aislada sin servo; ON | 4.8..5.25 V; P2 / limites y lotes arriba |
| TP9_servo_CENTRO_PICO | Senal servo TP9/J4.3 | GND_ACT | TP9 | oscilloscope | Sin servo; CENTRO tras descarga | 0..0.1 V; P2 / limites y lotes arriba |
| riel_logico_mA | Corriente total 3.3 V interfaz | No puntas en paralelo | Sonda/fuente en conductor positivo | current_probe | Interfaz aislada; OFF; anotar carga | 0..75 mA; P2 / limites y lotes arriba |
| buzzer_mA | Rama J3 driver Q2 | No puntas en paralelo | Sonda/fuente en rama J3 | current_probe | Ensayo aislado limitado, sin BBB; OFF | 0..20 mA; P2 / limites y lotes arriba |
| carga_act_A | Carga total actuadores de ensayo | No puntas en paralelo | Sonda/fuente positivo | current_probe | Carga segura sin servo, limitada; OFF | 0..1 A; P2 / limites y lotes arriba |
| J7_ABIERTO | Final carrera NO libre | J7.1 | J7.2 | multimeter V DC 20 V/auto | 3.3 V ensayo; JP6 abierto; OFF | 2.0..3.3 V; P2 / limites y lotes arriba |
| J7_CERRADO | Final carrera COM-NO accionado manualmente | J7.1 | J7.2 | multimeter V DC 20 V/auto | 3.3 V ensayo; JP6 abierto; OFF | 0..0.8 V; P2 / limites y lotes arriba |
| P8_15_LOW | TP8 / JP7 hacia P8_15 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP8 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P8_15_HIGH | TP8 / JP7 hacia P8_15 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP8 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 2.0..3.3 V; AM3358 + criterio conservador GPIO |
| P8_15_PEAK | TP8 / JP7 hacia P8_15 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP8 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..3.3 V; AM3358 + criterio conservador GPIO |
| P8_15_MIN | TP8 / JP7 hacia P8_15 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP8 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P8_16_LOW | TP6 / JP5 hacia P8_16 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP6 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P8_16_HIGH | TP6 / JP5 hacia P8_16 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP6 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 2.0..3.3 V; AM3358 + criterio conservador GPIO |
| P8_16_PEAK | TP6 / JP5 hacia P8_16 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP6 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..3.3 V; AM3358 + criterio conservador GPIO |
| P8_16_MIN | TP6 / JP5 hacia P8_16 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP6 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P9_24_LOW | TP7 / JP6 hacia P9_24 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP7 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P9_24_HIGH | TP7 / JP6 hacia P9_24 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP7 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 2.0..3.3 V; AM3358 + criterio conservador GPIO |
| P9_24_PEAK | TP7 / JP6 hacia P9_24 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP7 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..3.3 V; AM3358 + criterio conservador GPIO |
| P9_24_MIN | TP7 / JP6 hacia P9_24 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP7 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P9_27_LOW | TP5 / JP4 hacia P9_27 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP5 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |
| P9_27_HIGH | TP5 / JP4 hacia P9_27 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP5 | multimeter V DC 20 V/auto | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 2.0..3.3 V; AM3358 + criterio conservador GPIO |
| P9_27_PEAK | TP5 / JP4 hacia P9_27 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP5 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..3.3 V; AM3358 + criterio conservador GPIO |
| P9_27_MIN | TP5 / JP4 hacia P9_27 (lado interfaz, BBB ausente) | TP4 GND_LOGIC | TP5 | oscilloscope | 3.3 V ensayo; enlace GPIO abierto; OFF; estimular ambos estados | 0..0.8 V; AM3358 + criterio conservador GPIO |

Por cada fila numerica: JP4..7 abiertos y BBB/servo desconectados salvo P9_3 (BBB sola). Riesgo: corto con punta, referencia equivocada o nivel peligroso. Ante fuera de rango retirar energia y no cerrar GPIO; guardar FAIL y revisar componente/riel. Osciloscopio: registrar escala, ancho de banda, sonda y captura de minimo/maximo; no usar promedio DC.

| Campo | Modalidad / accion concreta | Estado y referencia de puntas |
|---|---|---|
| p2_conforme | inspection: Montaje cotejado con netlist P2, fotos de ambas caras y revision T52/T53/T54 | Sin energia; inspeccion visual/documental, sin puntas |
| fuentes_identificadas | inspection: Modelo, polaridad, capacidad y salida aislada/flotante de adaptadores identificados | Sin energia; inspeccion visual/documental, sin puntas |
| fuentes_separadas | inspection: Sin fuente comun entre actuadores y BBB | Sin energia; inspeccion visual/documental, sin puntas |
| sin_corto | continuity: Sin corto persistente entre rieles, descargados | Todo desconectado/descargado; ohm/continuidad; negras y rojas en ambos extremos de cada red/par identificado |
| polaridad_correcta | inspection: Polaridad de entrada y condensadores comprobada | Sin energia; inspeccion visual/documental, sin puntas |
| retornos_correctos | continuity: NT1 unica union GND_ACT-GND_LOGIC local | Sin energia; TP2 a NT1 lado ACT y TP4 a NT1 lado LOGIC; comprobar unica union prevista |
| neg_in_sin_bypass | continuity: Sin bypass NEG_IN-GND_ACT por cable, aleta, instrumento o fuente | Sin energia; J1.2/NEG_IN frente TP2/GND_ACT en ambas polaridades; distinguir diodo Q6 de puente; ver procedimiento |
| sin_puente_nodos | inspection: Sin cable GND entre nodos; rutas USB/instrumentos documentadas | Sin energia; inspeccion visual/documental, sin puntas |
| fusible_revisado | inspection: F1 y cableado coordinados con carga; 1 A provisional no aumentado | Sin energia; inspeccion visual/documental, sin puntas |
| q6_verificado | inspection: IRLZ44N, lote/fabricante, encapsulado, G/D/S y aleta verificados | Sin energia; inspeccion visual/documental, sin puntas |
| aleta_aislada | inspection: Aleta Q6 NEG_IN sin contacto con GND ni chasis | Sin energia; inspeccion visual/documental, sin puntas |
| r30_verificada | continuity: R30 100 kohm entre +5V_ACT y GND_ACT | Sin energia; Q6 G a S; aislar resistencia si caminos paralelos impiden lectura; nominal 100 kohm +/-5% |
| sw287_OFF | continuity: Tabla de contactos OFF medida y rotulada | Interruptor aislado; medir los 15 pares en posicion OFF; usar mapa fisico rotulado |
| sw287_CENTRO | continuity: Tabla de contactos CENTRO medida | Interruptor aislado; medir los 15 pares en posicion CENTRO; usar mapa fisico rotulado |
| sw287_ON | continuity: Tabla de contactos ON medida y rotulada | Interruptor aislado; medir los 15 pares en posicion ON; usar mapa fisico rotulado |
| pinouts_revisados | inspection: Pinouts reales U1, U2, transistores y modulos contrastados | Sin energia; inspeccion visual/documental, sin puntas |
| sin_anomalias | inspection: Sin calentamiento, reinicios, olor, dano o fuente inestable | Sin energia; inspeccion visual/documental, sin puntas |
| servo_desconectado | inspection: Servo desconectado durante diagnostico T06 | Sin energia; inspeccion visual/documental, sin puntas |
| selectores_comprobados | continuity: EN_C0/1/2 y JP4..7 diferenciados y verificados | Todo desconectado/descargado; ohm/continuidad; negras y rojas en ambos extremos de cada red/par identificado |
| aislamiento_pc817 | continuity: U2.1/2 y J8 sin union al retorno receptor | Sin energia; U2.1/U2.2/J8 frente U2.3/U2.4/TP4; no continuidad galvanica; no ensayo de alta tension |
| arranque_apagado | oscilloscope: Capturas de encendido/apagado sin tension indebida a GPIO | Osciloscopio referenciado a TP4 en TP5..8; JP4..7 abiertos, BBB ausente; encendido/apagado con fixture aislado |
| conectores_revisados | inspection: J1/J4/J10/J13 y borneras P2 contrastados | Sin energia; inspeccion visual/documental, sin puntas |
| carga_fuente_revisada | inspection: Carga segura caracterizada; no usar servo bloqueado | Sin energia; inspeccion visual/documental, sin puntas |
| modulo_optico_3v3 | inspection: Modulo optico real identificado y funcional a 3.3 V | Sin energia; inspeccion visual/documental, sin puntas |
| modulo_acustico_3v3 | inspection: Modulo acustico real identificado y funcional a 3.3 V | Sin energia; inspeccion visual/documental, sin puntas |
| limites_lotes | inspection: Hojas de lote, carga maxima y limites de componentes revisados | Sin energia; inspeccion visual/documental, sin puntas |
