# Simulador TRAMA 3

Abre **Simulador_TRAMA3.html** en el navegador. Incluye el motor y funciona sin Internet. Esta edición acompaña al documento **TRAMA3_Protocolo_y_Medios.docx**. Las instrucciones del ensayo están en las secciones 13 a 17.

## Para mostrarlo en clase

1. Escribe **Hola** de A hacia B. Deja 1 Hz y una duración de corte de 0, que mantiene el bloqueo hasta el final.
2. En «Qué vas a tapar», elige **Luz** en la ida y **Ninguno** en el retorno. Pulsa **Preparar simulación** y **Ir a DATA**. Sonido y nylon reparten los 54 bits en 27 ciclos.
3. Cambia la ida a **Luz y sonido** y prepara otra simulación. El nylon lleva el cuerpo completo en 54 ciclos. Pulsa **Ver resultado**.
4. Mantén luz y sonido, cambia el inicio a **Durante el primer DATA** y la duración a **120**. Pulsa **Próximo cambio de líneas** dos veces. El registro muestra la salida de las líneas y su posterior reincorporación. La H sigue teniendo SEQ 3 en todos sus intentos.
5. Con **Exportar JSON** puedes conservar el registro exacto. Para distinguir la entrega del texto de su confirmación, usa **Perder el ACK final**.

## Reloj modulado y aclaración del auxiliar

Cada subida lógica inicia un ciclo. El ancho distingue inicio S (60 % de T), cero (20 %) y uno (40 %). La tolerancia es ±5 % de T; las zonas intermedias son inválidas. El primer ciclo ya lleva datos. Los siguientes 17 llevan control y su CRC. Se normaliza la inversión del PC817. Tras el ciclo 17, los pulsos adicionales son cortos.

La trama lógica sigue en 54 bits; el total de información sobre las cuatro líneas incluye el control adicional. Las líneas excluidas llevan una prueba 101010 en sus primeros seis ciclos, sin agregar tiempo.

El auxiliar aclaró el uso de pulsos variables y lectura por reloj recibido. Adoptamos PWM bajo ese criterio; falta validación física. No hace falta ESP32 para esta propuesta. El documento detalla PC817, materiales y revisión del enunciado.

## Qué cambió

La revisión 101 elimina los 40 ciclos previos. El reloj anuncia versión, mapa y reporte en 17 bits auxiliares enviados por ancho de pulso durante los primeros 18 ciclos del cuerpo. No se envía texto por CLK. El receptor guarda las muestras, valida el control y reconstruye los 54 bits. El emisor usa el reporte de una respuesta válida en tramas posteriores. Gestión y confirmaciones viajan replicadas. Se necesitan un medio y un reloj por sentido para completar una comunicación confirmada. Los subconjuntos de ida y vuelta pueden ser distintos.

El motor conserva el formato lógico de 54 bits, los cuatro CRC, la codificación de texto, la longitud máxima, el tráfico bidireccional y los reintentos. Durante un mensaje también puede bajar el reloj después de dos intentos fallidos. Un reinicio abre otra sesión y deja al usuario la decisión sobre el mensaje anterior.

## Ensayos del reloj y tiempos

Sin cortes a 1 Hz, A tarda 604 s y Hola 832 s virtuales. Con luz cortada desde el arranque, Hola tarda 904 s; con luz y sonido, 1120 s. El corte temporal de dos medios durante 120 s produce dos reintentos y un total de 1020 s. Se incluyen apertura, longitud, guardas, ACK y END.

Deja los medios disponibles y selecciona control PWM alterado, ancho intermedio, marcador perdido, relleno incorrecto, período irregular o truncamiento. El registro muestra el descarte y la recuperación. La gráfica dibuja el código enviado y debajo indica el ancho recibido.

En las hipótesis de tiempo puedes editar clockRiseMs, clockFallMs y clockJitterMs. A 4 Hz, 20 ms de demora de bajada supera la banda propuesta. Esto es un límite del ensayo, no una medida del PC817.

## Código y pruebas

Se requiere Node.js 18 o superior para modificar o ejecutar el código fuera del navegador. No hay paquetes que instalar.

- `node build.cjs` vuelve a generar el HTML con el motor actual.
- `npm test` ejecuta 42 pruebas automatizadas de protocolo e interfaz.
- `node verify.cjs` ejecuta las pruebas y actualiza los registros de ejemplo en `evidencias/`.
- `node cli.cjs --a Hola --hz 4 --scenario fallback` muestra la bajada de reloj durante el mensaje.
- En `lineas.test.cjs` están la matriz de 64 combinaciones iniciales y los ensayos de interrupciones durante el tráfico.

En pwm.test.cjs están los ensayos de mapas, anchos, control, guardas y recuperación del reloj. También se verificó el HTML en Microsoft Edge.

Para programar varios cortes desde código, llama a `simulate` con el arreglo `outages`. Por ejemplo:

```js
const { simulate } = require('./engine.js');
const r = simulate({
  a: 'Hola',
  hz: 1,
  outages: [{ dir: 0, mask: 3, on: 'mid', duration: 120 }]
});
console.log(r.deliveries, r.events.filter(e => e.kind === 'LINE_CHANGE'));
```

`dir` vale 0 para A→B, 1 para B→A y 2 para los dos sentidos. `mask` indica los medios que se cortan en el laboratorio: luz=1, sonido=2 y nylon=4. Suma los valores para combinarlos. En cambio, el campo `map` de una trama indica los **medios habilitados**. Por ejemplo, cortar luz y sonido (3) deja habilitado nylon (4). `on` admite `start`, `data` y `mid`. Con `start` se puede fijar un instante absoluto con `at`. `duration` se expresa en segundos virtuales, `level` admite 0 o 1 para una entrada trabada y `clock: true` corta el reloj indicado.

Los resultados son virtuales. El ensayo de perfiles mide el comportamiento del modelo con los retardos elegidos. La misma prueba sobre las dos BeagleBone permitirá establecer los límites físicos.

## Frecuencias por sentido

La revisión 101 permite configurar A → B y B → A independientemente, empezando en 1 Hz. El HTML tiene dos selectores. En código se usan hzA y hzB; en CLI --hz-a y --hz-b. El ACK utiliza la frecuencia de retorno y su timeout depende de ella. Bajar una dirección no cambia el período configurado de la otra; la negociación pausa nuevos datos para cambiar de forma coordinada.

Las 42 pruebas incluyen los 16 pares entre 1 y 4 Hz, los cuatro CRC, retorno lento, pérdidas de gestión y cortes de medios con velocidades distintas. El ejemplo de 200 Hz del auxiliar no se anuncia como perfil alcanzable. La versión binaria es 101; el cuerpo sigue en 54 bits.
