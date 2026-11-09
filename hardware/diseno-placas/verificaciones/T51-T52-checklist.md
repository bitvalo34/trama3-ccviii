# Revisión T51 / T52

Revisión T51-P1, 2026-11-09. Autor del trabajo: Erwin con apoyo de herramientas de diseño. Revisor independiente previsto: Adrián. **Revisión independiente aún no realizada. T52 no aprobada.** El análisis automático y una segunda lectura por la misma herramienta no sustituyen esa revisión.

## Evidencia disponible

| Comprobación | Evidencia | Alcance |
|---|---|---|
| Protocolo102 y asignación de pines | Documento102 y T04-resultados.md | No se modificaron; PWM P9_14 e I2C aún no tienen prueba de esta interfaz |
| Dos modelos nativos | FCStd/STEP A y B; cad-A.json y cad-B.json | Sólidos válidos, volúmenes aproximados, misma distribución |
| Perforaciones | resultado-geometria.json | 200 terminales únicos dentro de 1792 agujeros nominales; no se midió placa comprada |
| Cabida | Cajas de componentes y límites | Sin solapamiento de cuerpos nominales; no certifica acceso con destornillador o tolerancias reales |
| Cableado | CSV, modelo y resultado-integrado.json | Todas las redes de placa conectadas por cables explícitos, excepto enlaces de configuración documentados |
| Esquema/netlist | Exportación XML KiCad comparada con manifiesto | Coincidencia exacta de redes y terminales; no sólo nombres de archivos |
| ERC | kicad-erc.rpt | Cero mensajes en esquema documental; símbolos mayormente pasivos. No comprueba voltajes, corriente ni fusibles |
| Cruces de cable | Verificación de segmentos 3D | Sin intersecciones entre aislamientos de redes diferentes con diámetros modelados; márgenes y radios de doblado requieren revisión real |
| EN y servo | Tablas de estados y cálculos | Ocho combinaciones EN y doble inversión estática; no simula transitorios, rebote ni dinámica SG90 |
| Revisión real de Adrián | Pendiente | No hay firma ni autorización para soldar |

## Dependencias del tracker

T07 y T08 figuraban pendientes en el tracker consultado. T51 y T52 también estaban pendientes. No se alteró ningún estado ni porcentaje. Las compras que el usuario pidió considerar disponibles se usan como hipótesis de diseño, no como certificación dimensional o eléctrica.

## Lista para revisar en seco y firmar

- [ ] T07: patrón real de la placa, márgenes, islas separadas, paso y diámetro de perforaciones iguales al modelo o archivos regenerados.
- [ ] Paso de borneras, zócalo DIP28 y PC817 confirmado; no forzar 5.00 mm sobre 5.08 mm si la pieza no lo admite.
- [ ] Pin1, muesca de U1, polaridad C1, D1/D2 y orden E/B/C de cada lote confirmados.
- [ ] Q6 y adaptador seleccionados: G1/S2/D3, D entrada, S salida; capacidad térmica/corriente y volumen aprobados.
- [ ] Conector de las fuentes, polaridad, estabilidad y retorno local identificados. J1 y J11 nunca alimentados simultáneamente.
- [ ] T08: consumo real de buzzer/servo, arranque, caída de tensión, calibre, conectores y selección/curva de F1 resueltos.
- [ ] Módulos LDR y acústicos funcionan a 3.3 V; DO seguro y polaridad registrados por módulo; ningún GPIO recibe 5 V.
- [ ] Riel 3.3 V dentro del presupuesto incluyendo otros accesorios BBB. No se inyecta alimentación externa en P9_3.
- [ ] R2/R3 DNP y JP2/JP3 abiertos salvo cálculo y evidencia de necesidad de pull-up I2C.
- [ ] NT1 es la única unión local intencional de retornos; no hay cable GND A–B. Documentar si USB común elimina aislamiento global.
- [ ] Los arneses de relojes conectan J9 al J8 opuesto por pares y no unen la isla remota a tierra local.
- [ ] Revisados todos los cables W y puentes: origen/destino, longitud, color, capa, espacio para dos extremos como máximo por pad.
- [ ] Diámetro exterior del cable ≤1.2 mm en 22 AWG y ≤0.8 mm en 26 AWG o ruteo regenerado. Revisar holguras en resultado-integrado.json.
- [ ] Curvas y cruces fabricables sin tensión sobre soldaduras, separación suficiente y acceso de cautín; respetar zona del opto.
- [ ] Acceso a borneras y puentes, extracción del MCP y altura de C1 comprobados en seco. No hay fijaciones en islas con señales.
- [ ] JP10/11/12 actúan sólo sobre RX del nodo; las etiquetas EN_C0/1/2 y ON/OFF se entienden. No confundir con parada del servo.
- [ ] SW1 OFF corta alimentación del servo y fija señal a tierra; contactos físicos coinciden con tabla. Procedimiento de habilitación aprobado.
- [ ] JP4–JP7 abiertos en revisión inicial; punto de prueba accesible antes de conectar cada GPIO.
- [ ] Comparación A/B terminada, incluidas diferencias de los arneses acústicos.
- [ ] BOM complementaria revisada y compras seleccionadas; no hay sustituciones sin actualizar netlist/huellas.
- [ ] Observaciones resueltas y documentos regenerados; revisión independiente firmada.

## Registro de cierre

| Dato | Completar |
|---|---|
| Revisión exacta y commit revisados | Pendiente |
| Fecha / revisor Adrián | Pendiente |
| Observaciones y resolución | Pendiente |
| T07 acreditada | Pendiente |
| T08 acreditada | Pendiente |
| Decisión sobre soldadura | NO AUTORIZADA en T51-P1 |

Un resultado “sin errores” del generador no cambia esta decisión por sí solo. Si el patrón de la placa o un componente crítico cambia, invalidar la plantilla anterior y repetir las comprobaciones pertinentes.
