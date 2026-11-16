# Checklist T06/T08 P2

Registrar placa, operador, fecha PC, instrumento, revision y evidencia.
- [ ] Nivel 1: interfaz y actuadores desconectados; P9_3 medido.
- [ ] Cableado hecho sin energia; pinout identificado; fixture coincide.
- [ ] Checklist JSON de nivel 1 rellenado con datos reales y hash registrado.
- [ ] Build por placa; PRU/PWM disponibles; ninguna propiedad ajena forzada.
- [ ] Nivel 2: T52/T53/T54; fotos frente/reverso y netlist P2 cotejada.
- [ ] IRLZ44N N canal G/D/S/aleta y R30 correctos, fabricante identificado.
- [ ] NEG_IN sin bypass a GND_ACT; NT1 unica union local con GND_LOGIC.
- [ ] Fuentes aisladas/flotantes, polaridad, fusible y carga real comprobados.
- [ ] SW287 OFF/CENTRO/ON mapeado por continuidad; centro no es OFF.
- [ ] JP4..7 abiertos; modulos identificados, niveles y picos medidos.
- [ ] No tierras entre nodos; rutas por USB/instrumentacion documentadas.
- [ ] Nivel 3 manual solo tras T08 PASS y revision humana; no usar diagnostico bare conectado a P2.
- [ ] Todos los intentos guardados; recursos restaurados antes de recablear apagado.
- [ ] T06 exige ambas BBB y PWM 1/1.5/2 ms; T08 exige esquema P2.
- [ ] Sin medidas inventadas ni cierre automatico de tracker.

Procedimiento: [guia completa](GUIA_DEFINITIVA_T06_T08_P2_BBB-A_BBB-B.md).
Mediciones por punto: [auditoria](T08_Auditoria_P2.md).
