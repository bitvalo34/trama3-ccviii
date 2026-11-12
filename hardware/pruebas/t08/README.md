# T08: inspección y mediciones

Leer [auditoría T51](../../documentacion/T08_Auditoria_T51.md) y
[procedimiento de multímetro](../../documentacion/Guia_Completa_T06_T08.md#6-t08-procedimiento-de-medición).

```bash
python3 hardware/pruebas/t08/inspeccion.py --board BBB-A
python3 hardware/pruebas/t08/registrar-mediciones.py --board BBB-A --file medidas-BBB-A.csv
python3 hardware/pruebas/t08/evaluar-mediciones.py --board BBB-A --file medidas-BBB-A.csv --output t08-BBB-A.json
```

Repetir con BBB-B y rutas separadas. Inspección sólo lee: identidad, memoria/disco,
CPU, arranque, sensores disponibles, errores clasificados, servicios, pinmux, PRU
y PWM. No mide P9_3 ni convierte logs en voltaje. Los sensores se etiquetan como
información del sistema; ausencia es no disponible.

El CSV tiene 45 puntos: 16 comprobaciones y 29 medidas. Guardar valores reales,
incertidumbre absoluta, unidad, método, instrumento, fecha y referencia de evidencia.
No rellenar campos con estimaciones del diseño. Cada actualización conserva copia
del archivo anterior cuando hay datos; el generador no sobrescribe un formulario.

`evaluar-mediciones.py` retorna 0 PASS, 3 NOT_TESTED, 4 BLOCKED, 5 FAIL.
Un formulario vacío queda NOT_TESTED. Una medida fuera de rango obliga a detener
la prueba física. Datos sintéticos nunca acreditan mediciones. PASS comprueba el
registro aportado; no autentica una fotografía ni certifica el diseño.

La etapa de placa de interfaz sólo se realiza cuando exista un montaje revisado;
sus filas permanecen vacías mientras no exista. Eso impide cierre integral de T08,
sin impedir diagnóstico de BBB sola. Se conserva el tracker sin cambios.
