# Diseño y medidas antes de fabricar

## Estado real y procedencia

Se revisaron las ocho ramas públicas y PR 1 a 6. PR5/T51 público tiene base `5fcedfd5a163d26eb17d65eb7646ba5ffe9e6de7`; PR6/T06-T08 tiene `53739569ffdee224909381b2564bbeeb2988e43b`. P2 no estaba publicado como rama independiente: existe en el árbol local con modificaciones sin confirmar. Se creó una copia de trabajo separada para no alterar esos archivos. La instantánea del montaje permite auditar qué P2 se usó; no convierte la revisión local en aprobada.

El tracker actualizado identifica P2, T55 y las dependencias T09<-T08,T06 y T10<-T09,T18. Sus hojas históricas conservan relaciones antiguas: se usaron las tareas y agenda de 15-19 noviembre, no las filas históricas que harían depender T53/T54 de T09/T10.

Las fotos muestran una perfboard rotulada 9 x 15 cm, un TO-220, DIP de 28 pines, borneras y cableado inferior abundante. Son compatibles visualmente con partes de P2; el marcado de Q6, el pinout, todos los puentes y las conexiones ocultas no son legibles con certeza. No se determina la revisión construida sólo por semejanza. Antes del arnés, Erwin identifica A/B y Adrián coteja conexiones contra la instantánea y documenta cada diferencia. No se propone desoldar toda la placa.

MaterialesMedios.docx contiene texto, pero **no imágenes incrustadas de los resortes o la espuma**. No hay constante k, altura, densidad ni espesor confirmados. La BOM T03 tampoco establece espesor MDF. El 6 mm del CAD es exclusivamente un parámetro inicial, no una medida encontrada.

## Alternativas estudiadas

| Alternativa | Cabida y acceso | Decisión |
|---|---|---|
| Perfboard 90 x 150 con BBB lateral | Deja sólo 50 mm de fondo frontal; resta recorrido y espacio a receptores | Descartada por frontal estrecho |
| Perfboard sobre BBB en segundo nivel | Cabe, pero bloquea headers, instrumentación y desmontaje | Descartada; complicación innecesaria |
| Perfboard girada 150 x 90 junto a BBB | Ambas caben atrás; franja frontal amplia y soldaduras elevadas | Elegida |

En P0 la altura de cara inferior de perfboard es MDF+12 mm; BBB es MDF+8 mm. El punto más bajo de soldadura debe quedar al menos **3 mm libre** del MDF y cualquier fijación, criterio de separación mecánica propuesto, no distancia de aislamiento certificada. Medir salientes, sumar 3 mm y elevar separadores si hace falta. No comprimir cables inferiores. La aleta de Q6 es NEG_IN y no puede tocar ninguna fijación conductora.

## Coordenadas y orientaciones

Origen local (0,0) en esquina trasera izquierda mirando hacia el otro equipo. X a la derecha, Y hacia los medios, Z arriba. El borde frontal es Y=200. Todas las coordenadas de perforaciones son locales y en mm. La etiqueta Nodo B siempre se lee desde detrás de B; al enfrentarlo, el sistema global lo rota 180 grados. PCB A/B conservan distribución idéntica.

| Elemento | Nodo A local | Nodo B local | Altura respecto a MDF |
|---|---|---|---|
| Perfboard esquina | (15,15), 150 x 90 | Igual | 12 mm bajo PCB |
| BBB esquina | (185,15), 86.36 x 53.34 | Igual | 8 mm bajo PCB |
| C0 TX | x 30, boca y 140 | x 225, boca y 140 | Eje 40 mm |
| C0 RX | x 75, boca y 140 | x 270, boca y 140 | Eje 40 mm |
| C1 TX | x 120, boca y 160 | x 140, boca y 160 | Eje 32 mm |
| C1 RX | x 160, boca y 160 | x 180, boca y 160 | Eje 32 mm |
| Servo TX | eje x 215, y 155 | eje x 25, y 155 | Brazo 36 mm |
| Switch RX | centro x 275, cuerpo y 145 | centro x 85, cuerpo y 145 | Palanca aprox 25-32 mm |
| Guía nylon TX | (223,185) | (33,185) | Centro 36 mm |
| Guía nylon RX | (275,185) | (85,185) | Centro 22 mm |
| Ancla retorno | (275,130) | (85,130) | Centro 43 mm |
| SW287 | (250,96) | Igual | Envolvente aprox 55 mm |
| F1 | esquina (186,88) | Igual | Portafusible accesible |

Las posiciones son de diseño, no medidas del hardware. Los objetos de FreeCAD aproximan conectores y sensores; los bloques opacos alrededor de bocas representan mangas/tapas y calces que deben fabricarse con sobrantes disponibles. No presuponen impresora 3D. La longitud de BBB 86.36 x 53.34 mm procede de la especificación métrica oficial; la misma página tiene una conversión imperial incoherente. Usar la cifra métrica para reserva y cotejar placa real. No usar la altura 4.76 mm del texto como altura total de sus conectores: el modelo reserva hasta 15 mm y requiere comprobarlos.

Reservas: 20 mm entre PCB y BBB; 15 mm o más delante de PCB antes de receptores; zona sobre P8/P9 despejada al menos 25 mm para retirar Dupont; Mini USB sale a Y<0; paso lateral para multímetro. Los arneses no deben ocupar el círculo de radio 12 mm alrededor del eje servo ni tocar la palanca del switch. Si un módulo real invade una reserva, moverlo dentro del frontal, actualizar parámetros/plantilla y repetir presentación, sin recortar el módulo.

## Conductos y distancia calculada

PVC: L=480 mm, penetración sobre cada MDF=200-140=60 mm. La distancia entre bordes es L-2x 60=360 mm. Las dos piezas requieren 960 mm; con dos cortes de ancho 3 mm se consumen 966 mm y quedan 34 mm. Medir longitud real y ancho de sierra; una barra nominal de un metro no debe asumirse exactamente 1000 mm. Antes de cortar la segunda, medir el remanente. Condición general: 2L+2kerf<=Ldisponible.

Manguera: bocas en Y160 y Y600 global, cuerda geométrica 440 mm. Se cortan dos tramos de 480 mm, dejando 40 mm de reserva total. El exceso de 40 mm por tramo sobre la cuerda forma una curva amplia; el CAD usa una parábola de longitud de eje 480 mm, no un tubo estirado. Debe haber al menos 10 mm de solape de manga exterior en cada punta, sin robar longitud al conducto: la manga abraza por fuera. No imponer la curva del CAD si dobla o estrangula la manguera real; bajar su arco o acercar las bases. No exigir que quede suspendida con esa forma sin soporte: apoyar el tramo medio en un calce de espuma suelto sobre la mesa si cae. Ese apoyo no une eléctricamente los nodos.

Dos PVC y dos mangueras sí salen del material declarado bajo estas condiciones. La longitud de nylon disponible y de los pares de reloj no se conoce. Preparar 750 mm de nylon por sentido, incluidos 2x 75 mm para nudos y ajuste; conservar colas hasta validar. Para reloj, medir recorrido completo bornera a bornera, no sólo el espacio entre bases. La propuesta reserva 1100 mm por par (2200 mm de par, 4400 mm de conductor). Si el cable disponible es menor, reducir gap y recalcular PVC/acoples antes de cortar; no unir tierras para ahorrar cable.

## Mecanismo C2 sencillo

SG90 vertical en su soporte comprado. El brazo queda aproximadamente perpendicular al tiro de nylon, con agujero a r=8 mm. Sólo usar un agujero existente compatible; no perforar cerca de la estría. Giro inicial propuesto ±10 grados alrededor del centro mecánico, total 20 grados. No se supone correspondencia exacta ángulo/PWM: medirla en vacío. Carrera tangencial entre extremos: s=2r sin(delta/2)=2.78 mm. Ésta es la cuerda geométrica ideal, no toda la carrera disponible en la palanca.

La guía TX se alinea con el agujero del brazo en reposo, x=eje+8. El nylon sale hacia el frente y, tras una pequeña desviación hacia el carril nominal, lleva un resorte de extensión en serie cerca del TX, en el espacio entre bases. En RX pasa por la armella baja de Y185 y vuelve a la punta de la palanca del switch, Y167 y Z32. El tiro tiene componente hacia abajo: con diferencia de altura 10 mm y distancia horizontal 18 mm, sin(alpha)=10/sqrt(18²+10²)=0.486. El resorte de retorno va de la punta hacia la armella trasera elevada de Y130,Z43. La rueda/palanca y resorte del switch suelen proporcionar retorno, pero se mantiene el resorte externo sólo con mínima precarga y si mejora retorno sin sobrecarga.

Atar con lazo acolchado detrás de la rueda o en una zona resistente de la palanca; no doblar ni taladrar la lámina del switch. Si el switch real no ofrece punto de amarre seguro, usar una pequeña lengüeta rígida reciclada independiente accionada por el nylon y apoyada sobre la rueda; añadir su dimensión al registro y mover el soporte. Esta alternativa no está dimensionada para fabricación automática: no perforar hasta presentar la variante real. La geometría directa sobre palanca es el diseño P0.

Fuerza vertical necesaria Fv = fuerza de actuación del switch + componente contraria del resorte + rozamiento. La tensión mínima aproximada es Fv/0.486; el giro del brazo exige tau=Tension x r x sin(beta), con máximo conservador Tension x 0.008 m. Medir fuerza del switch en el mismo punto de amarre, no en el pulsador interno. No usar el par de bloqueo de catálogo como carga continua admisible. Se desconoce el par real del SG90 comprado; iniciar con la menor tensión que conmute, pulsos cortos y parada ante zumbido, calentamiento o no retorno.

Seleccionar dos resortes de serie iguales y dos de retorno compatibles. Colgar masas conocidas con el resorte fuera de la electrónica; medir longitud inicial L0 y longitudes a dos fuerzas F1=m 1g, F2=m 2g. k=(F2-F1)/(L2-L1). Empezar con masas pequeñas; no superar límite elástico y comprobar retorno a L0. Anotar incertidumbres. Si hay tensión inicial de espiras cerradas, registrar F0 e intercepto; no imponer F=kx desde cero. Elongación de serie en servicio: (T-F0)/k si T>F0. El balance de carrera es s_util=s_servo-holgura-elongación_resorte-elongación_nylon-de formación_soportes. Debe superar carrera de actuación medida más margen y ser menor que recorrido seguro del switch. No se asigna k numérica a los resortes disponibles.

Medir elongación de nylon bajo la carga elegida en su longitud real; no usar un módulo elástico genérico. Ajustar nudo dejando holgura suficiente para liberar, pero sin lazo que se salga de la guía. Limitar el giro por software tras la prueba en vacío; no usar el switch como tope del servo. No tensar el hilo moviendo las MDF con servo encendido. Sujetar cada base a la mesa con apoyo antideslizante o sujeción disponible si el tiro las desplaza. Medir asentamiento, histéresis y rebote: **1 Hz no está validado**.

## Tornillos y fijaciones

Para tornillo pasante: Lmin=t_MDF+h_separador+t_pieza+t_arandelas+t_tuerca+salida. Ejemplo provisional: tuerca 2.4 mm, dos arandelas sumando 1 mm, salida 1 mm. Perfboard: 6+12+1.6+1+2.4+1=24 mm -> M3x 25 candidato. BBB: 6+8+1.6+1+2.4+1=20 mm -> M3x 20 mínimo nominal, verificar rosca y saliente; M3x 22 o 25 si tolerancias lo exigen. Soporte bajo de 2 mm: 6+2+1+2.4+1=12.4 mm -> M3x 16 candidato. En todos los casos medir pila real.

Alternativa prioritaria: separadores plásticos con rosca interior y tornillos independientes por abajo y arriba, si el lote los incluye; se calculan ambos tramos y profundidad de rosca por separado. Los separadores de clip pueden no requerir tuerca, pero deben fijarse al MDF según su diseño. No recortar la separación inferior para aprovechar M3x 16. No poner arandelas metálicas encima de islas/cables. Para placas usar arandelas aislantes o apoyo plástico; para MDF, metal ancho por debajo. El montaje pasante propuesto requiere 28 tuercas y 28 arandelas inferiores: faltan 4 tuercas y 3 arandelas respecto a lo declarado, más los aislantes superiores. Si los 16 separadores de placas son roscados y fijan sin tuerca independiente, este faltante puede desaparecer; comprobar su tipo antes de comprar. La tabla de distribución conserva ambos casos.

Fuentes dimensionales: https://docs.beagleboard.org/boards/beaglebone/black/ch 09.html y https://towerpro.com.tw/product/sg 90-7/ (consultadas 14 nov 2026, fecha de trabajo Guatemala). La ficha TowerPro 23x 12.2x 29 mm identifica referencia dimensional, no el lote ni su par real. Fuentes eléctricas y redes: instantánea T51-P2-LOCAL y documentación oficial BBB de conectores. Enunciado oficial local revisado: tres medios, dos equipos transceptores, reloj y documentación de conexiones; no se altera su protocolo para facilitar el montaje.
