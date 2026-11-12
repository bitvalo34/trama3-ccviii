# Checklist previo y de cierre T06/T08

Registrar placa BBB-A/BBB-B, fecha real, operador, instrumento y nombre de evidencia.
Una casilla vacía significa pendiente, no aprobación.

## Antes de cablear
- [ ] Identificados P8/P9, pin1 y fuente de cada BBB.
- [ ] Debian apagado; USB, fuentes y cargas desconectadas.
- [ ] No se conectan las dos BBB entre sí durante diagnóstico.
- [ ] No hay energía residual en capacitores antes de continuidad.
- [ ] Fuentes con conector/polaridad correctos; sin daños.
- [ ] No se abre fuente de red ni se anula tierra de protección.
- [ ] Puntas en COM y V/Ω; nunca amperímetro entre + y − de fuente.
- [ ] Placa T51 y actuadores desconectados para T06.
- [ ] Resistencia1k verificada, un único loopback, ninguna unión de dos salidas.
- [ ] Servo no se alimenta desde GPIO ni riel3.3V.

## Antes de activar
- [ ] P9_3 medido; incertidumbre y rango documentados.
- [ ] Señales sólo desde la misma BBB en loopback; no5V.
- [ ] Preflight sin conflicto en recursos de la prueba.
- [ ] Compilación TI y host completadas en esta BBB.
- [ ] Ambos PRU offline antes de adquirir; ningún consumidor PWM.
- [ ] Fixture coincide con comando; se usará --active --electrical-checked.
- [ ] Se conoce el comando cleanup y dónde guardar evidencia.
- [ ] Sin cortos, polaridad invertida, calentamiento ni fallos de alimentación.

## Interfaz, sólo cuando exista y haya revisión
- [ ] T07/pinouts reales contrastados, incluidos PMOS/adaptador y transistores.
- [ ] F1 tipo/curva seleccionados con carga, cables, Q6 y fuente.
- [ ] Un solo ingreso J1 o J11; positivos BBB/actuadores separados.
- [ ] Capacitores y diodos con polaridad correcta.
- [ ] NT1 única unión local GND_ACT/GND_LOGIC; sin puente indebido A–B.
- [ ] USB/instrumentos no invalidan la afirmación de aislamiento global.
- [ ] PC817 y sus pines1/2 remotos separados del retorno receptor.
- [ ] SW1 OFF y servo retirado; EN no se usa como interruptor de seguridad.
- [ ] JP4..7 abiertos antes de medir fuentes de señal.
- [ ] Sensores funcionan a3.3V; resistencia serie no se usa como conversor.
- [ ] LOW/HIGH y transitorios medidos antes de cerrar enlaces GPIO.
- [ ] Alimentación y GPIO no permanecen activos con BBB apagada.

## Cierre
- [ ] Capturas y resultados de todos los intentos conservados.
- [ ] PWM deshabilitado/liberado, PRU detenido, selector firmware/pines restaurados.
- [ ] Sin errores de cleanup; si hay error, detener y conservar diario.
- [ ] Apagar antes de desmontar; no dejar puntas sueltas.
- [ ] Resultados A/B separados y fecha real PC anotada.
- [ ] Evaluador final distingue PASS/FAIL/BLOCKED/NOT_TESTED.
- [ ] No se atribuyen medidas a auditoría/simulación.
- [ ] No se modificó tracker ni se fusionó a main.

**Detener inmediatamente** ante sobrevoltaje, negativo inesperado, polaridad inversa,
corto, humo/olor/calor, daño, fuente inestable, reinicios o entrada fuera de rango.
No continuar porque un comando Linux haya terminado con código0.
