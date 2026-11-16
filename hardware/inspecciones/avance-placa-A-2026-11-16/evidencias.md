# Evidencias seleccionadas

Consolidación: 16/11/2026, America/Guatemala. Placa denominada A en el expediente, sin identificación física única registrada. Originales aportados por Erwin. Transcripción manual de fragmentos pertinentes revisada contra las imágenes del chat; **no son logs originales ni una ejecución nueva de Codex**. Hora individual no acreditada.

Los originales permanecen fuera del repositorio; [fuentes.json](fuentes.json) conserva nombres y hashes, sin rutas personales ni datos de acceso/red.

## E01 — LED: registros y confirmación

Origen: `codex-clipboard-1601b554-3395-4bfb-96e8-0c70c72314d9.png`.

```text
Preparación: OLATA (0x14) <- 0x00; IODIRA (0x00) <- 0xfc.
Lectura IODIRA: 0xfc
Lectura OLATA: 0x00

Encendido: OLATA <- 0x01.
Lectura IODIRA: 0xfc
Lectura OLATA: 0x01

Apagado: OLATA <- 0x00.
Lectura OLATA: 0x00
```

Confirmación asociada: «Funcionó el encendido y apagado». Acredita operación funcional en esa prueba, no corriente ni estabilidad prolongada.

## E02 — Fotografía del LED iluminado

Origen: `codex-clipboard-5cadddc6-f3fe-4644-b678-7db663bee670.png`.

Se observa un LED rojo iluminado en un soporte tubular, con cables conectados. La imagen fija no demuestra apagado, cambio temporal, corriente ni circuito completo. El apagado se sustenta en E01 y la confirmación del operador.

## E03 — Diez lecturas correctas con 5 V

Origen: `codex-clipboard-d71a7164-2806-4684-acb8-39585b289203.png`.

El operador confirmó 5 V conectados en el turno anterior; el procedimiento mantenía LED y cargas externas desconectados. El bucle programa sleep 1; sin marcas temporales no se acredita período exacto.

```text
1: direccion=0xfc salida=0x01
2: direccion=0xfc salida=0x01
3: direccion=0xfc salida=0x01
4: direccion=0xfc salida=0x01
5: direccion=0xfc salida=0x01
6: direccion=0xfc salida=0x01
7: direccion=0xfc salida=0x01
8: direccion=0xfc salida=0x01
9: direccion=0xfc salida=0x01
10: direccion=0xfc salida=0x01
```

Prueba breve; no cierre de estabilidad bajo carga.

## E04 — Fallo previo y pérdida de configuración

Origen: `codex-clipboard-47a13bc3-cff2-424c-827f-754b53adb300.png`.

```text
Preparación: IODIRA=0xfc; OLATA=0x00.
Primer intento OLATA <- 0x01: Error: Write failed
Segundo intento OLATA <- 0x01: sin error visible.
Lectura IODIRA: 0xff
Lectura OLATA: 0x01
```

Contexto reportado: tensiones DC correctas; ensayo previsto con 5 V y sin LED. Esta captura no establece la causa ni prueba un pulso de RESET. Los éxitos posteriores no eliminan la incidencia.

## Confirmaciones sin fotografía del instrumento

Adaptadores, fusible, rieles, tierra, R1, final de carrera, óptico y U1.22 proceden de confirmaciones textuales. Se distinguen en [resultados.csv](resultados.csv). No se inventan decimales, tiempos, corrientes o mínimos/máximos.
