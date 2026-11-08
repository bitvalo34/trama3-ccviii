# T04 — Resultados y cierre técnico

Revisión: 08/11/2026. T04 cumple su alcance mínimo: **Completada, 100%, con observaciones**. Inicio real y cierre: 08/11/2026. Responsable: Adrián; revisor: Erwin; ejecución física: Erwin. El tracker no se modifica y el PR sigue sujeto a revisión, sin merge automático.

## Evidencia revisada

Originales locales en Documents/TRAMA3-resultados; no se publican logs crudos.

| Registro | Resultado |
|---|---|
| A/T04-A-audit-Kxkr2z/resultado.txt | Debian 10, 4.19.94-ti-r42; raíz escribible, 1.3G libres |
| A/T04-A-pin-test-i1oqaY/resultado.txt | Cinco selecciones corroboradas por pinctrl y cinco restauraciones |
| B-20261108-013407/resultado.txt | Debian 9, 4.14.71-ti-r80; consola USB operativa, raíz escribible, 190M libres |
| B-20261108-015122/resultado.txt | Cinco selecciones corroboradas por pinctrl y cinco restauraciones; salida 0 |
| B-20261108-015344/resultado.txt | headless: salida 5; acción opcional parcialmente aplicada |

Las fechas internas de las placas están desajustadas; se usa la fecha de revisión del PC.

## Pines

| Pin | Modo probado en ambas | Registro en ambas | Restauración en ambas |
|---|---|---|---|
| P8_11 | pruout | 0x26, mux 6 | default |
| P8_15 | pruin | 0x2e, mux 6, RXACTIVE | default |
| P8_16 | pruin | 0x2e, mux 6, RXACTIVE | default |
| P9_24 | pruin | 0x2e, mux 6, RXACTIVE | default |
| P9_27 | pruin | 0x2e, mux 6, RXACTIVE | default |

Propietarios y grupos pinctrl corresponden a cada función seleccionada. No se observó conflicto impeditivo. Los cinco mensajes RESTAURADO acreditan retorno lógico a default. El registro inicial P9_24 era 0x37 en A y 0x27 en B; se restauró el estado propio de cada imagen, no una palabra genérica.

PRU0/PRU1 identificados como 4a334000/4a338000, offline. clpru y lnkpru presentes en ambas; falta probar compilación y ejecución en T06. P9_14 siguió en 0x27 y los pads I2C en 0x33: no se activó PWM ni probaron transacciones.

## Observaciones

- headless de B retiró display-manager.service y luego falló al detener ese alias. No se verificó el estado final disabled; no se declara éxito. Su reparación es opcional para trabajar por consola. No repetir a ciegas: si se retoma, consultar primero is-enabled/is-active de lightdm.service y display-manager.service.
- B mantiene 190M libres y problema CDC ECM en Windows; la consola USB funciona. Caché apt de 8K: clean-cache no resolvería el espacio.
- DNS no disponible en las auditorías de ambas placas. Se mantienen sistemas actuales, sin migración ni flasheo.
- debugfs ya permitió corroborar pinctrl; no hace falta montarlo ni repetir las pruebas. Reinicio opcional; apagado sólo si se retirará la placa.
- Persistencia aplazada a T06 para coordinar mux e inicialización segura de R30.

El cierre acredita configuración temporal y restauración, no niveles eléctricos, firmware, reloj o transmisión. T06 debe validar toolchain, firmware, PWM y persistencia. T03 sigue pendiente del inventario detallado.

Para el tracker: Completada, 100%, inicio/cierre real 08/11/2026; entregable: este registro y las guías; criterio: cinco pines seleccionados/restaurados en ambas BBB con corroboración pinctrl. Conservar responsables y planificación histórica.
