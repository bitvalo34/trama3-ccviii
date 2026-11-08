# T03 — Conciliación de materiales

Revisión documental: 08/11/2026. Responsable del tracker: Erwin. Revisor: Adrián.
Estado: en curso. Compra documentada; recepción y compras externas pendientes.
Base: BOM maestra, IDs M01–M41, y protocolo revisión 101. Se utilizaron los archivos adjuntos sin sufijo (2), que son los efectivamente disponibles.

## Pedido consultado

Se accedió a la sesión autorizada de Electrónica DIY. La página mostró confirmación del 14 de octubre (no expuso el año), estado de preparación «Confirmado», 22 renglones y 73 unidades después de expandir todos los artículos. Total y subtotal: **Q309.50**, envío gratis. La sección de pago registra Q309.50, pero no se publica el medio de pago ni ningún identificador privado. No aparece prueba de entrega ni fecha de retiro. No inferimos recepción a partir de confirmación/pago.

Cantidades reconstruidas desde cada subtotal y precio unitario, coincidentes con las cantidades de la lista de recompra visible; no se accionó recompra. SKU no expuesto por renglón en la página del pedido. Los modelos de la tabla son las correspondencias propuestas con la BOM, no inspecciones del lote.

| ID | Variante o referencia | Plan | Pedido | Unitario Q | Subtotal Q |
|---|---|---:|---:|---:|---:|
| M02 | MCP23017 DIP28 | 2 | 2 | 52.00 | 104.00 |
| M03 | LED 5 mm rojo | 2 | 2 | 0.75 | 1.50 |
| M04 | D6 LDR LM393 | 2 | 2 | 16.00 | 32.00 |
| M05 | Buzzer activo 2 terminales | 2 | 2 | 3.50 | 7.00 |
| M06 | KY037 SKU D14 | 2 | 2 | 19.00 | 38.00 |
| M07 | SG90 180 grados | 2 | 2 | 27.00 | 54.00 |
| M08 | SPDT con rueda | 2 | 2 | 7.00 | 14.00 |
| M09 | 2N2222 | 4 | 4 | 0.75 | 3.00 |
| M10 | 2N3904 | 2 | 2 | 0.75 | 1.50 |
| M11 | PC817 DIP4 | 2 | 2 | 4.00 | 8.00 |
| M12 | 1N4148 | 2 | 2 | 0.75 | 1.50 |
| M13 | 330 ohm | 2 | 2 | 0.50 | 1.00 |
| M14 | 390 ohm | 2 | 2 | 0.50 | 1.00 |
| M15 | 100 ohm | 2 | 2 | 0.50 | 1.00 |
| M16 | 1K ohm | 12 | 9 | 0.50 | 4.50 |
| M17 | 4.7K ohm | 10 | 10 | 0.50 | 5.00 |
| M18 | 10K ohm | 10 | 8 | 0.50 | 4.00 |
| M19 | 100 nF | 8 | 8 | 0.75 | 6.00 |
| M20 | 1000uF 16V | 2 | 2 | 3.50 | 7.00 |
| M21 | 5x20mm 1A | 2 | 2 | 0.75 | 1.50 |
| M22 | 5x20mm con cable | 2 | 2 | 4.00 | 8.00 |
| M28 | Micro USB hembra a DIP2.54 | 2 | 2 | 3.00 | 6.00 |

La suma independiente de los 22 renglones es Q309.50. No hay sobrecompra frente a la BOM en este pedido.
M16: 9 de 12 resistencias de 1 kΩ; diferencia 3. M18: 8 de 10 resistencias de 10 kΩ; diferencia 2.
M01: dos BBB reutilizadas; M24: dos cables Mini USB declarados y utilizados en T02. Multímetro, cautín y estaño disponibles por declaración. El peso y composición del estaño no están confirmados: no equivale aún al tubo M38.
Sin microSD ni osciloscopio; analizador lógico no confirmado. No hace falta ESP32.

## Inventario completo y cantidades sin evidencia

[T03-inventario.csv](T03-inventario.csv) contiene los 41 ID, cantidades previstas, compras de este pedido, reutilización conocida y campos de recepción/verificación en blanco. **Blanco significa desconocido, no cero.** «Brecha» descuenta este pedido y la reutilización acreditada; no es una orden de compra ni descuenta supuestas compras externas.

Los materiales M02–M22 y M28 figuran comprados, con recepción no acreditada. Los otros ID, salvo M01/M24, necesitan confirmación. No hay sensores declarados funcionales.

## Conciliación física en una sola sesión

Trabajar sin alimentación y separar dos conjuntos A/B. Completar el CSV y enviar fotos agrupadas sólo cuando sea necesario identificar variantes:

1. **Integrados y drivers:** M02 dos MCP23017 de 28 pines, DIP estrecho de 7.62 mm entre hileras; M09 cuatro 2N2222, M10 dos 2N3904, M11 dos PC817 DIP4, M12 dos 1N4148. Registrar marca/sufijo. No asumir orden E-B-C por la forma del transistor; consultar hoja del fabricante del lote antes de cablear.
2. **Medios:** M03 dos LED rojos de 5 mm, M04 dos módulos LDR/comparador LM393, M05 dos buzzer activos (marcado de tensión), M06 dos sensores anunciados KY-037. El enlace comercial de M06 dice KY-038: enviar foto conjunta del frente/reverso y serigrafía. M07 dos SG90 posicionales 180°, no rotación continua; no forzar el eje ni alimentarlo para esta inspección. M08 dos finales SPDT con rueda; contar COM/NO/NC.
3. **Pasivos:** contar por bolsa 330Ω×2, 390Ω×2, 100Ω×2, 1kΩ×9, 4.7kΩ×10, 10kΩ×8, 100nF×8, 1000µF/16V×2. Son cantidades del pedido. Medir resistencias sueltas sin alimentación, en Ω y con puntas en COM/VΩ; comparar con tolerancia impresa. Nunca medir Ω sobre un circuito energizado. Para condensadores basta valor, tensión y polaridad visual en T03.
4. **Protecciones:** dos fusibles 5×20mm/1A y dos portafusibles correspondientes. Con multímetro en continuidad y sin energía, comprobar continuidad del fusible; no puentear un fusible abierto. Registrar si rápido/lento está indicado. Su calibre final depende de las corrientes futuras de T08.
5. **Montaje:** dos placas perforadas 9×15cm, dos zócalos DIP28 estrechos, 12 borneras de 2 vías y 6 de 3 vías, dos tiras de 40 pines y paso 2.54mm, cable y consumibles. Medir el paso entre centros: 5.08mm corresponde a dos pasos de placa 2.54mm; 5.00mm no es exactamente igual. No forzar terminales ni soldar todavía.
6. **Alimentación:** identificar dos fuentes de actuadores 5V/2.5A y dos fuentes BBB 5V/2A centro positivo; fotografiar sólo etiquetas técnicas. «Cable de poder» no acredita una fuente regulada. M28 son adaptadores Micro USB de actuadores, distintos del Mini USB de datos BBB. No probar tensión de red ni abrir fuentes. Mediciones energizadas y corrientes se reservan para T08.
7. **Elementos del medio:** dos tubos opacos de 30cm; dos mangueras de 30cm DI10–12mm; dos líneas de nylon de 50cm útiles con margen para nudos y dos resortes ligeros; dos bases rígidas y fijaciones. Espuma alrededor de la unión acústica, no tapando su interior.
8. **Herramientas:** confirmar multímetro operativo, cautín y cantidad de estaño; si no hay pinza/regla, anotar. No comprar otro juego si el existente sirve.

En el switch sin alimentación puede verificarse COM–NC cerrado y COM–NO abierto en reposo, y el intercambio al presionar la rueda. No demuestra tiempo de rebote. Si hay una diferencia, marcar «incompatible o dudoso», aislar la pieza y continuar con las demás. Las pruebas activas de luz, sonido, servo y reloj pertenecen a tareas posteriores.

## Compra residual provisional

No comprar esta lista hasta descontar compras externas y material recibido. No se hicieron reservas, pedidos ni pagos.
Prioridad crítica para montaje: M16/M18 (si no hay resistencias adicionales), M23/M34 alimentación, M25 placa, M35 zócalos, M36/M37 borneras, M27/M39/M41 conexiones.
Necesario después: M29–M32 medios y bases, M38/M40 consumibles.
M26 kit de jumpers es condicional: revisar tipo de extremos y arnés existente. M33 es una provisión, no un componente, no duplicar envíos ya pagados.
MicroSD con lector: opcional para T04 mínima; necesaria antes de una migración con recuperación. Osciloscopio/analizador: acceso recomendado para T06 y caracterización, no requisito para inventariar.

| ID | Cantidad sin cobertura en este pedido/reuso | Precio histórico Q | Provisión Q |
|---|---:|---:|---:|
| M16 | 3 | 0.50 | 1.50 |
| M18 | 2 | 0.50 | 1.00 |
| M23 | 2 | 55.00 | 110.00 |
| M25 | 2 | 15.00 | 30.00 |
| M26 | 1 | 32.00 | 32.00 |
| M27 | 4 | 2.25 | 9.00 |
| M29 | 2 | 10.00 | 20.00 |
| M30 | 2 | 18.00 | 36.00 |
| M31 | 2 | 15.00 | 30.00 |
| M32 | 2 | 20.00 | 40.00 |
| M33 | 1 | 40.00 | 40.00 |
| M34 | 2 | 60.00 | 120.00 |
| M35 | 2 | 2.50 | 5.00 |
| M36 | 12 | 2.00 | 24.00 |
| M37 | 6 | 3.00 | 18.00 |
| M38 | 1 | 22.00 | 22.00 |
| M39 | 2 | 3.00 | 6.00 |
| M40 | 2 | 15.00 | 30.00 |
| M41 | 2 | 4.00 | 8.00 |

Provisión total antes de otras compras: **Q582.50**, basada en precios históricos, no cotización vigente. El presupuesto residual definitivo sigue desconocido. El pedido no implica que todos sus componentes sean equivalentes ni estén entregados.

La [ficha pública de resistencias](https://www.electronicadiy.com/products/copia-de-resistencias-por-unidad-kilo-ohms-1-4w) muestra Q0.50 y opción de compra al revisarla el 08/11/2026. Las cinco unidades adicionales supondrían Q2.50 antes de envío; el stock por variante/cantidad no está publicado y no se ha reservado. Enlaces de las demás partidas en el CSV conservan la referencia histórica, no una declaración de existencias actuales. Cotizar únicamente las brechas confirmadas después del conteo.

## Criterio de cierre y tracker

Avance recomendado provisional: 50% (estimación de trabajo documental, no porcentaje recibido). Inicio real de esta ejecución: 08/11/2026. Sin fecha de cierre. Se consultó el pedido, se mapeó a los 41 ID y se reconciliaron importes. Falta recepción, variantes críticas, compras externas y cotización residual final. T03 no se cierra; la recepción posterior corresponde a T05/T07, pero aquí debemos saber qué está comprado y qué falta.

El tracker original no se modificó. Conserva responsables y fechas históricas. El tracker marca T01/T02 completas aunque el README aún menciona revisión de T01 pendiente: no se altera ese historial sin aclarar su evidencia.

## Actualización de materiales

La copia de materiales distingue pedido, recepción, verificación, reutilización y brecha provisional. El histórico se conserva. No escribir cantidades compradas en «Disponible propio» como si ya fueran material recibido. No cargar el gasto real en una fórmula que sólo resta dinero de una necesidad física: podría ocultar faltantes. Los importes y cantidades nuevos quedan en una hoja de conciliación separada.
