# Construcción desde las bases vacías

Cada paso se realiza en A y B salvo indicación. Erwin ejecuta; Adrián coteja planos, revisión eléctrica y evidencia. Mantener etiquetas visibles durante todo el proceso. Las posiciones citadas corresponden a P0: tabla de coordenadas del capítulo de diseño y CSV de perforaciones. No pasar a taladro ni corte con una fila crítica sin medir.

## A Preparación

### A1 Separar dos kits

Objetivo: evitar mezclar variantes. Componentes: todo el inventario, dos cajas y etiquetas. Herramientas: regla, calibre si disponible, cámara, multímetro apagado hasta necesitarlo. Posición: una bandeja detrás de cada MDF. Operación: marcar BBB-A/B, PCB-A/B, LDR-A/B, MIC-A/B, SG90-A/B, SW2-A/B y SW287-A/B; contar y registrar en materiales/distribucion.csv. Medidas: contar tuercas, arandelas, separadores y longitudes reales. Orientación: foto superior con referencia de pin 1. Comprobación: un TX y RX de cada medio en cada kit. Error frecuente: tratar B sólo como receptor. Corrección: reponer elementos antes de fabricar.

### A2 Medir una sola hoja de control

Objetivo: resolver los datos que bloquean el corte. Componentes: MDF, placas, bases, conductos, resortes y espuma. Herramientas: regla/calibre, escuadra y multímetro. Posición: mesa sin energía ni virutas. Operación: completar medidas-criticas.csv incluyendo puntos de fijación y salientes inferiores; medir MDF en tres puntos; medir diámetro interior/exterior de ambos conductos; medir distancia entre agujeros de cada base de servo y switch. Medidas: no convertir 1 pulgada nominal a 25.4 mm exterior. Orientación: cotas desde mismo origen local de cada plano. Comprobación: presentar cada huella real sobre contorno impreso. Error: usar medidas de la caja o foto como verificación. Corrección: marcar pendiente y ajustar el parámetro con la pieza real.

### A3 Revisar la placa existente sin reconstruirla

Objetivo: identificar revisión efectivamente soldada. Componentes: PCB soldada, snapshot P2, checklist de desviaciones. Herramientas: lupa, multímetro, puntas finas, fotos. Posición: soporte aislante con acceso a ambas caras. Operación: seguir J1/NEG_IN/Q6/NT1/J13, confirmar ausencia de bypass J11/MOD3/J12, continuidad por red y aislamiento entre redes distintas. Medidas: registrar resistencia/continuidad sólo desenergizado; descargar condensadores por método seguro antes de medir. Orientación: no invertir coordenadas al mirar la cara inferior; usar referencia pin 1 y foto. Comprobación: Adrián firma cada diferencia resuelta. Error: deducir G/D/S por la forma TO-220. Corrección: leer marcado y ficha del lote; modificar únicamente lo imprescindible. Si Q6 incorrecto, aleta tocando metal, puente NEG_IN-GND o 5 V en RX, bloquear energización y corregir ese punto.

## B Presentación en seco

### B1 Colocar bases y electrónica

Objetivo: verificar cabida y accesibilidad. Componentes: dos MDF, BBB, PCB y separadores. Herramientas: regla, escuadra, cinta removible. Posición: A Y0..200; B global Y560..760, girada 180 grados. Operación: colocar PCB en (15,15) y BBB en (185,15); usar separadores sueltos, sin agujerear. Medidas: gap 360; huellas 150x 90 y 86.36x 53.34; margen 20 entre placas. Orientación: PCB girada rígidamente, jamás reflejada; USB hacia parte trasera. Comprobación: conectar y retirar un enchufe de prueba sin energía, acceder a P8/P9, J10, borneras y EN. Error: contar sólo el tamaño PCB sin conectores/cables. Corrección: ensayar con cables reales, mover huella y regenerar plantilla.

### B2 Presentar frontal y recorrido

Objetivo: comprobar seis carriles de medios. Componentes: tubos enteros sobrepuestos, manguera, servo, switches, escuadras, armellas. Herramientas: regla larga e hilo auxiliar. Posición: carriles globales X30/75/120/160/215/275. Operación: marcar centros en las dos bases y sostener conductos sin cortar; verificar que TX-A enfrenta RX-B y viceversa; poner el brazo r 8 sin energía en su zona libre. Medidas: ejes ópticos MDF+40, acústicos+32, nylon+36. Orientación: tabla de roles A/B, no intercambiar sólo los colores de cable. Comprobación: no atraviesa placas; alcanza ambas bocas; potenciómetros accesibles. Error: cruzar nylon al girar B. Corrección: comparar X globales y reubicar módulos, no invertir pinout.

## C Marcado

### C1 Imprimir y comprobar escala

Objetivo: transferir referencias sin error de impresora. Componentes: plantillas PDF, papel. Herramientas: impresora, regla. Posición: página A3 primera o páginas A4 segunda/tercera unidas. Operación: seleccionar tamaño real, sin márgenes adaptativos; medir línea 100 mm horizontal y vertical; para A4 alinear cruces de X150 y líneas de solape. Medidas: error máximo recomendado 0.5 mm/100 mm para presentación; fijaciones se transfieren desde pieza. Orientación: texto del origen en borde trasero, frente Y200. Comprobación: contorno 300x 200 y diagonales de 360.56 mm aproximadamente. Error: imprimir A3 reducido en A4. Corrección: usar mosaico A4 a 100%.

### C2 Transferir centros reales

Objetivo: no perforar cables ni placas. Componentes: cada pieza física y soporte. Herramientas: lápiz fino y punzón ligero. Posición: centros candidatos del CSV. Operación: colocar pieza; transferir sus agujeros reales a MDF, medir X/Y y actualizar CSV/JSON antes de regenerar. Medidas: diámetro M3 de paso propuesto 3.2 mm en soporte/MDF; no agrandar automáticamente agujeros BBB; armella según diámetro menor de rosca real. Orientación: distinguir agujeros del soporte y del PCB. Comprobación: segunda persona compara cotas diagonales y reverso. Error: aceptar cuatro esquinas nominales BBB como patrón real. Corrección: **sus cruces están pendientes y no autorizan taladro**; transferir las cuatro perforaciones reales.

## D Perforación y preparación

### D1 Taladrar sólo MDF verificado

Objetivo: fabricar base sin dañar equipos. Componentes: MDF vacío y tabla de sacrificio. Herramientas: taladro, broca adecuada, gafas, prensas y lija. Posición: fuera del área electrónica. Operación: retirar absolutamente todas las placas; sujetar MDF entre apoyo plano y prensa; perforar perpendicular con respaldo; desbarbar sin ensanchar. Medidas: diámetro de cada fila verificada; piloto de armella se prueba primero en sobrante. Orientación: entrar por cara vista, apoyar salida. Comprobación: presentar tornillo y soporte, sin forzar. Error: taladrar con módulo encima o sostener MDF en mano. Corrección: retirar componente, sujetar y repetir marca si se desvió; no usar el PCB como plantilla de broca.

### D2 Preparar conductos

Objetivo: obtener cuatro tramos útiles. Componentes: PVC1m, manguera 1m. Herramientas: cinta métrica, caja de ingletes/sierra fina, cuchilla adecuada, lija. Posición: material sujeto lejos de electrónica. Operación: confirmar fórmula de consumo; marcar primer 480, cortar escuadrado, desbarbar y medir; marcar segundo 480 con kerf reservado. Cortar manguera perpendicular sin aplastar. Medidas: dos 480 por material; anotar longitudes reales y remanentes. Orientación: identificar extremos A/B y sentido. Comprobación: probar boca y paso libre a la luz, sin rebabas internas. Error: descontar kerf dentro de la longitud útil o estirar manguera para medir. Corrección: reducir gap calculado, no forzar un tramo corto ni pegar un empalme improvisado.

## E Fijación

### E1 Montar electrónica elevada

Objetivo: proteger soldaduras y permitir servicio. Componentes: separadores plásticos, BBB y PCB. Herramientas: destornillador, regla, tuercas/arandelas. Posición: huellas verificadas. Operación: montar primero separadores; poner tornillos con arandela aislante si toca PCB y metálica ancha bajo MDF; apretar sólo hasta inmovilizar sin flexionar. Medidas: separaciones 12/8 mm provisionales; pila de tornillo calculada; mínimo libre bajo soldaduras 3 mm propuesto. Orientación: placa T51 idéntica en A/B. Comprobación: mirar con linterna por debajo, comprobar que una isla o cable no toca tornillo; retirar placa sin desmontar el medio. Error: M3x 16 que apenas alcanza una vuelta. Corrección: usar separador roscado independiente o longitud adecuada; no reducir altura para hacerla caber.

### E2 Servo y mantenimiento

Objetivo: fijar actuador y SW287 accesible. Componentes: base SG90, dos escuadras por nodo (una RX, una SW287). Herramientas: destornillador, calibre, multímetro. Posición: servo según tabla; SW287(250,96); RX según carril. Operación: atornillar base sin brazo cargado, comprobar que no bascula; presentar escuadra SW287 y bushing real; una repisa debe sostener el casquillo con tuerca, cuerpo debajo y terminales aislados. Medidas: agujero publicado 12 mm sólo si casquillo coincide; escuadra 1 pulgada nominal no garantiza repisa 26x 26. Orientación: palanca ON/OFF rotulada por continuidad, no por hacia dónde apunta. Comprobación: accionarlo sin tocar placa ni hilo. Error: montar interruptor colgando de los cables. Corrección: adaptar soporte con material rígido reciclado o fijación compatible antes de conectar.

### E3 Armellas y receptor

Objetivo: guiar sin corte y accionar switch. Componentes: tres armellas por nodo, switch y escuadra. Herramientas: pinza, regla, multímetro. Posición: guía TX, guía RX y ancla retorno del plano. Operación: montar ojo cerrado con parte lisa hacia hilo, ajustar altura mediante soporte real; no desenroscar hasta dejar agarre insuficiente para alcanzar Z43; elevar ancla con escuadra/soporte rígido si la armella es corta. Medidas: registrar longitud de vástago disponible, penetración y altura; palanca y guía deben dar componente hacia abajo. Orientación: plano del ojo alineado al recorrido. Comprobación: hilo corre sin rebaba ni roce lateral, base no se mueve. Error: usar armella roscada corta como poste largo. Corrección: soporte suplementario pequeño reutilizado y actualización de huella; marcar faltante si no existe.

### E4 Sujetar portafusible y módulos pequeños

Objetivo: impedir esfuerzos sobre terminales. Componentes: portafusible, módulos, cinchos y apoyos aislantes. Herramientas: regla y tijera. Posición: F1 en (186,88); cincho entre (182,94) y (225,94). Operación: pasar cincho por los dos agujeros de MDF y alrededor del cuerpo fijo, sin impedir abrir el portafusible; fijar los módulos a sus acoples desmontables mediante cincho separado del que retiene la manguera. Medidas: holgura de cable 20-30 mm; comprobar altura de apoyo real. Orientación: tapa del fusible y potenciómetros accesibles. Comprobación: tirar suavemente del arnés no desplaza pieza ni tapa. Error: apretar cincho sobre capacitor, micrófono, LDR o componente soldado. Corrección: apoyar sólo en zona libre de PCB o añadir pequeña cuna aislante recortada y verificar de nuevo la huella.

## F Construir medios

### F1 Luz en ambos sentidos

Objetivo: paso óptico oscuro y ajustable. Componentes: dos PVC, LED, LDR, cuatro abrazaderas, cuatro tapas opacas. Herramientas: regla, tijera/cuchilla, destornillador. Posición: tubos X30 y 75 global, ejes+40. Operación: colocar calces firmes bajo extremos; fijar una abrazadera en cada extremo (cuatro total); preparar tapas de material opaco con orificio que sólo exponga LED o LDR; montar PCB del receptor por fuera, con pot accesible; manga opaca solapada desmontable y salida de cable en laberinto. Medidas: comprobar DI frente a sensor, no introducir PCB32x 14 por fuerza; tapa de modelo 34 es provisional. Orientación: caras sensibles enfrentadas, LED hacia tubo, LDR hacia interior. Comprobación: al tapar LED no cambia por luz ambiental; tubo puede retirarse soltando abrazaderas. Error: sellar pegamento sobre LDR o doblar sus patas. Corrección: tapa nueva, fijar la placa y apoyar cables sin transmitir esfuerzo a sensor.

### F2 Sonido en ambos sentidos

Objetivo: acoplar sin bloquear ni transmitir vibración estructural. Componentes: dos mangueras, buzzer/mic, espuma, cinchos. Herramientas: tijera, regla. Posición: X120 y 160 global, bocas+32 y Y160. Operación: formar manga blanda hueca entre buzzer/mic y manguera; dejar apertura acústica libre; abrazar exterior con cincho justo, no aplastado; apoyar módulos sobre espuma y sujetarlos independientemente; separar los dos conjuntos sin compartir bloque rígido con servo. Medidas: diámetro de cámara/adaptador igual o mayor que apertura real; ningún cincho reduce sección. Orientación: agujero buzzer y cara micro hacia conducto; potenciómetro visible. Comprobación: paso libre, cable no tira del micro, manguera curva sin estrangulación. Error: tapón de espuma dentro del canal o mic tocando servo. Corrección: anillo exterior hueco y soporte aislado separado. No usar las abrazaderas grandes 1 pulgada apretando una manguera 1/2; se reservan para PVC.

### F3 Nylon y resortes

Objetivo: dos estados con retorno fiable. Componentes: nylon 0.5, dos resortes por sentido, brazo, guías. Herramientas: regla, masas conocidas, multímetro. Posición: X215 y 275 global. Operación: caracterizar resortes fuera del equipo; pasar nylon por ojo TX, resorte de serie, ojo RX bajo y lazo acolchado en palanca; añadir retorno suave hacia ancla elevada; dejar colas 75 mm en nudos. Medidas: pieza inicial 750 mm; carrera ideal 2.78 mm a r 8/20 grados, reemplazar por medida real. Orientación: trayectorias paralelas sin cruzarse y resorte de serie junto a TX. Comprobación: accionar manualmente con servo desacoplado, COM-NO cierra y abre sin atasco al soltar. Error: usar el fin de carrera como tope o tensar hasta que el servo zumbe. Corrección: aflojar, reducir ángulo, escoger resorte más suave, revisar fricción y recolocar palanca. Si carrera no alcanza tras las pérdidas, ajustar geometría medida; no aumentar fuerza a ciegas.

## G Conexiones apagadas

### G1 Preparar arneses locales

Objetivo: conexión desmontable y revisable. Componentes: cables medidos, terminales y aislantes. Herramientas: pelacables, crimpadora/cautín según terminal, multímetro. Posición: rutas del plano y materiales/arneses.csv. Operación: presentar cada ruta con holgura de servicio; cortar después de medir, marcar ambos extremos, crimpar/soldar lejos del PCB; aislar unión; verificar continuidad pin a pin y ausencia de cruces. Medidas: 22 AWG flexible candidato para potencia;26 AWG señal, sujeto a caída/corriente medidas. Orientación: identificación funcional por pin, no color solamente. Comprobación: matriz J10 completa y cada módulo mapeado individualmente. Error: copiar orden de sonido A a sonido B. Corrección: cotejar serigrafía y continuidad de cada unidad; dejar AO aislado. No soldar a headers BBB.

### G2 Relojes y alivio de esfuerzo

Objetivo: transportar sólo reloj por dos pares. Componentes: cuatro conductores y terminales diferenciados. Herramientas: multímetro, etiquetas, cinchos. Posición: borde global X5 para AB y X295 para BA. Operación: llevar J9A.1/.2 a J8B.1/.2 y J9B.1/.2 a J8A.1/.2; trenzar cada par, fijar cerca de cada bornera sin cortar aislante. Medidas: reservar 1100 mm por par, ajustar con ruta real. Orientación: + y - desde TX a LED del opto receptor. Comprobación: ninguna vía de GND directo entre nodos; los retornos del par terminan en LED remoto, no GND remoto. Error: añadir tercer hilo GND o intercambiar J8/J9. Corrección: retirar hilo extra, reidentificar extremos. No conectar ambos USB al mismo PC durante ensayo que requiera separación de tierras; usar alimentación individual documentada.

## H Inspección previa

### H1 Revisión mecánica

Objetivo: liberar sólo montaje en seco. Componentes: conjunto completo. Herramientas: checklist, regla, cámara. Posición: configuración de exposición. Operación: revisar fijaciones, accesos, roce, aislamiento inferior, tuberías, conectores y movimiento manual; fotografiar cada cara y frontal con regla. Medidas: registrar gap, alturas, corte, recorrido y resorte elegido. Orientación: etiquetas visibles al operador. Comprobación: todos los módulos se pueden retirar sin cortar cables; MDF no se desliza. Error: ocultar ajustes bajo cinchos definitivos. Corrección: conservar amarre provisional hasta calibración y no recortar colas de nylon.

### H2 Revisión eléctrica antes de GPIO

Objetivo: impedir que la preparación se interprete como aprobación. Componentes: placas, fuentes identificadas, formulario P2 actualizado. Herramientas: multímetro y osciloscopio adecuados. Posición: un nodo por vez sin enlaces. Operación: revisión seca T52; luego T08 adaptado por T55, etapas de alimentación e interruptor, sensores y entradas, servo descargado; JP4-7 abiertos hasta medir salidas. Medidas: registrar amplitud, corriente, caída y transitorios; no inventar valores de multímetro para pulsos. Orientación: NEG_IN separado de GND_ACT; aleta Q6 aislada. Comprobación: evidencia firmada de ambas placas y compatibilidad con firmware adaptado. Error: usar evaluación PASS del paquete P1 como validación P2. Corrección: repetir filas afectadas en revisión correcta.

## I Ensayos y acabado

### I1 Calibrar y registrar

Objetivo: reunir evidencia T09/T10. Componentes: conjunto, scripts adaptados y registros vacíos. Herramientas: instrumento y captura de tiempos. Posición: gap definitivo. Operación: seguir ocho procedimientos de calibración, un sentido primero, luego concurrencia; registrar fallos sin borrarlos. Medidas: secuencia 010101 a 1 Hz significa un estado por segundo; captura de revisión 102 en 0.8T y asentamiento medido. Orientación: identificar emisor/receptor en cada archivo. Comprobación: comparar señales y entradas reales; no aceptar sólo comando enviado. Error: considerar cada ciclo del tono un bit. Corrección: caracterizar presencia y su ventana de adquisición con Adrián.

### I2 Fijación final y mantenimiento

Objetivo: preservar calibración y reparar rápido. Componentes: cinchos sobrantes, etiquetas y fotos. Herramientas: tijeras de punta segura. Posición: todas las rutas fuera del mecanismo. Operación: marcar posición de pots y brazo, asegurar arneses con holgura, recortar sólo cinchos, conservar nylon de repuesto; añadir fecha/revisión a base. Medidas: repetir una secuencia después de apretar. Orientación: OFF SW287 siempre accesible. Comprobación: calibración no cambia con un ligero movimiento del cable y cada medio se puede bloquear físicamente sin tocar reloj. Error: transportar conjunto tirando de los conductos. Corrección: desconectar pares, liberar nylon, separar tubos/mangueras y transportar cada MDF por su base.
