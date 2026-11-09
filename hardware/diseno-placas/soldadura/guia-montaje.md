# Guía de montaje futuro — T51-P1

**No iniciar soldadura con esta revisión provisional.** Este procedimiento se prepara para después de verificar T07/T08 y de la revisión independiente T52. Esta sesión no realizó montaje ni pruebas energizadas.

## Referencia única de posición

Trabajar primero en A, inspeccionar cada etapa y repetir en B. Ambas usan las mismas coordenadas; no reflejar B por ser el otro extremo. Etiquetar físicamente A y B y cada arnés. La vista superior tiene columnas 1–32 de izquierda a derecha y filas A–BD de arriba abajo. El pin1 se marca rojo en SVG. Fórmulas: x=5+2.54·(columna−1), y=5+2.54·índice_de_fila; z=0 es la cara inferior de la placa. Espesor nominal 1.6 mm. La cara inferior dibujada es espejo horizontal y conserva los nombres de las perforaciones.

`coordenadas.csv` contiene **todos** los terminales y redes. `cableado.csv` contiene los 134 cables por nodo, longitudes iniciales, extremos, calibre, color y todos los cambios XYZ de recorrido. Las rutas no son pistas impresas ni conexiones internas de una protoboard. `puentes.csv` define los enlaces adicionales que no son cables W. `arneses-externos.csv` incluye el cableado fuera de la placa y los dos pares de reloj; sus longitudes son reservas ajustables, no dimensiones medidas de la mesa.

## Preparación, sin soldar ni alimentar

Comparar la placa real con la plantilla impresa al 100 % y su barra de 25.4 mm. Contar filas y columnas. Comprobar islas aisladas con multímetro. Si la retícula, el paso de borneras, el zócalo o el diámetro de patas no coinciden, detener y regenerar coordenadas: no desplazar piezas a ojo ni forzar terminales. Confirmar pinout de cada transistor y polaridad de cada componente. Ensayar inserción y acceso a tornillos de borneras, extracción de U1 y colocación de puentes.

Herramientas: multímetro en continuidad/diodos con placa sin energía, regla/calibrador, lupa, pinzas, cortador y pelacables adecuados; para el montaje posterior, cautín regulado, estaño con flux y soporte. Mantener BBB, sensores y fuentes desconectados; U1 fuera del zócalo. SW1 en OFF. JP4–JP7 abiertos. JP1–JP3 abiertos. R2/R3 sin colocar. EN_C0/1/2 en OFF (2–3).

## Etapas después de la autorización

| Etapa | Colocación y soldadura | Control para continuar |
|---|---|---|
| 1. Marcas | Identificar A/B, filas/columnas y pin1; colocar sólo la placa vacía | Plantilla y retícula coinciden; no hay pistas compartidas inesperadas |
| 2. Resistencias | R1, R4–R8, R10–R31 según tabla; R9 no existe y R2/R3 son DNP | Leer valor antes de cortar; ningún cuerpo o terminal invade otra isla; comprobar R31=270 Ω |
| 3. Zócalo y opto | Zócalo U1 con muesca hacia fila A; U2 PC817 pin1 superior izquierdo | IC MCP todavía fuera; continuidad individual de contactos, sin puentes entre patas |
| 4. Diodos/transistores | D1 banda hacia +5V_ACT; D2 banda hacia U2.1. Q1–Q5 con E/B/C según lote y pads | No copiar orientación plana; aislar patas cruzadas. Si no se puede adaptar limpiamente, corregir huella |
| 5. Capacitores | C2–C5 cerámicos, luego C1 electrolítico al final de piezas altas | C1 negativo a GND_ACT; reserva nominal Ø10×20 mm confirmada. Cerámicos sin polaridad |
| 6. Conectores | Headers de señal/EN/JP, borneras J1–J9/J14, J10, J11 y puntos TP | El paso real encaja; tornillos accesibles; TP sin puntas expuestas que toquen otro terminal |
| 7. Potencia/adaptador | Puntos soldados J12/J13, adaptador Q6, portafusible F1 y SW1 externos | Q6 G/S/D y contactos SW1 comprobados con continuidad; cables 22 AWG con alivio de tensión |
| 8. Cableado inferior | W001–W134; comenzar por recorridos más próximos a placa y después sus cruces inferiores | Cada cable coincide con extremos, red y ruta XYZ; aislamiento intacto; no se unen cruces |
| 9. Retornos/puentes | NT1 permanente 1–2, EN en OFF; enlaces GPIO abiertos | GND_ACT y GND_LOGIC unidos sólo por NT1; lado remoto del PC817 separado |
| 10. Arneses | BBB, sensores, LED/buzzer, servo y reloj, todavía sin enchufar a BBB | Etiqueta en ambos extremos; mapa de cada módulo comprobado; no hay 5 V en arnés de BBB |
| 11. Revisión de A | Recorrer redes y tabla cable por cable con Adrián | Registrar errores y corregir en archivos antes de copiar a B |
| 12. Replicación B | Repetir usando las mismas tablas, con su módulo acústico particular | Comparar lista de continuidad A/B; firmar por separado |

En cada isla se inserta una sola pata de componente. Los cables se sueldan lateralmente a la pata/isla con sólo el extremo necesario descubierto; no intentar introducir dos o tres conductores en un agujero de 1 mm. La distribución usa como máximo dos terminaciones W por pad; si el lote no permite una unión limpia con ese volumen, cambiar la distribución antes de construir. En potencia hacer contacto mecánico cable-terminal y soldadura correcta; no depender de un puente largo de estaño entre islas.

Las rutas se distribuyen nominalmente a z=−2.4, −3.9 y −5.4 mm. Son niveles de cruce de cable aislado, no capas de PCB. Doblar con radio suave y añadir margen para curvas; los codos del CAD son idealizados. La longitud `cut_mm` incluye 12 mm de margen, no obliga a cortar antes de ensayar. Pelar aproximadamente 2 mm junto a la unión y evitar cobre expuesto en los cruces. Si se requiere más longitud o diámetro de aislamiento, registrar el cambio y comprobar separación antes de soldar. No sujetar cables contra cantos cortantes ni cubrir soldaduras con pegamento antes de revisarlas.

## Puentes y modo de comprobación

- NT1: puente permanente de 22 AWG entre GND_ACT y GND_LOGIC, aislado excepto extremos.
- JP10/11/12: 1–2 habilita recepción; 2–3 la fija a cero. Nunca puentear 1–3. Retirar el puente también fija la entrada seleccionada baja mediante 100 kΩ.
- JP4/5/6/7: abiertos hasta comprobar nivel y polaridad de cada entrada; cerrar sólo tras aprobación de integración.
- JP1: reset manual momentáneo, normalmente abierto. JP2/JP3: sólo cerrar si se instalan y justifican los pull-ups R2/R3.
- SW1: OFF para toda revisión mecánica; EN_C2 no es el corte del servo.

## Continuidad final sin energía

Retirar fuentes, BBB y conexiones entre nodos. U1 fuera. Descargar C1 de forma controlada; no cortocircuitarlo con una herramienta. Revisar las redes CSV terminal por terminal. Medir resistencia entre +5V_ACT/GND_ACT y +3V3/GND_LOGIC: el capacitor puede producir una lectura transitoria, pero un corto persistente requiere detenerse. No imponer “infinito” a circuitos que tienen resistencias o semiconductores. Usar modo diodo para polaridad, no concluir ausencia de falla sólo por el pitido.

Comprobar por separado los dos contactos de SW1 en ambas posiciones. Verificar EN y JP contra su tabla. Con NT1 retirado temporalmente, comprobar que no hay otro puente conductor intencional de retornos; restaurarlo y registrar. Entre los pines remotos U2.1/U2.2 y tierra local no debe existir una conexión metálica de cableado. D2 y el LED de U2 sí unen entre sí los dos terminales remotos por semiconductor; no confundirlo con puente al lado local. Esta prueba no certifica aislamiento de alta tensión.

## Primera energización: plan posterior, no ejecución de T51

1. Con BBB, MCP, sensores y servo desconectados y enlaces GPIO abiertos, usar fuente regulada con limitación de corriente para revisar por separado la etapa 5 V, caída en Q6 y polaridades. Si sólo se tiene la fuente fija 2.5 A y multímetro, conseguir apoyo de laboratorio para esta primera prueba; el fusible no sustituye limitación de corriente.
2. Probar el dominio de lógica con una fuente de banco 3.3 V limitada **únicamente con arnés BBB desconectado**. No conectarla nunca a la vez que P9_3. Medir TP3/TP4 y ausencia de 5 V en todos los futuros pines BBB. Apagar antes de cambiar cualquier cable.
3. Probar individualmente receptores a 3.3 V, sin GPIO conectado. Registrar corriente, nivel alto/bajo y polaridad. Si un DO excede 3.3 V o no funciona, no cerrar su enlace: corregir circuito/variante.
4. Después de verificar continuidad y tensiones, apagar y descargar; insertar MCP orientado correctamente. Retirar la fuente de banco 3.3 V antes de conectar BBB. Revisar presupuesto de corriente y estados de reset.
5. Comprobar I2C y PWM en una tarea de integración separada; medir PWM/reloj con instrumento adecuado. No se escribió ese firmware aquí. SW1 sigue OFF hasta comprobar señal estable y mecanismo descargado.
6. Medir consumo de actuadores y arranque de servo; resolver F1, Q6 y capacidad de conexiones. Si hay caída, calentamiento, reinicios o fusible abierto, apagar y analizar. No aumentar fusible ni aplicar movimiento repetitivo para “probar”.
7. Comprobar cada dirección del reloj por separado y después ambos sentidos. Finalmente ensayar medios a 1 Hz y sus ocho combinaciones EN bajo el protocolo102. La inspección CAD no es evidencia de transmisión física correcta.

Guardar tabla de medidas A/B, fotos de las dos caras y las observaciones de Adrián. Una modificación física debe reflejarse en netlist, coordenadas, cableado y CAD antes de declarar el montaje conforme.
