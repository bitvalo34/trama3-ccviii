# Paquete de entrega: borrador tecnico y lista de verificacion

Fecha de preparacion: 16/11/2026. Fuente directa: Proyecto_-_Capa_Fisica_ (1).pdf,
10 paginas; requisitos pp.4-9. No es acta de aceptacion ni modifica el tracker.
El lector de documentos no pudo extraer las celdas del Excel vigente, por lo
que no se marcan tareas o porcentajes sin revisar sus criterios exactos.

## Estructura prevista del ZIP final

| Contenido | Fuente o accion |
| --- | --- |
| Codigo y pruebas | Rama revisada, commit fijo, fuentes completas y SHA256SUMS |
| Protocolo | docs/protocolo/TRAMA3_Protocolo_Revision_102.md |
| Arquitectura | docs/planificacion/Informe_Runtime102_Base.md |
| Circuitos reales | hardware/documentacion/fuentes-P2 y documentos del montaje efectivamente usado |
| Instalacion/operacion | PRIMER_ENLACE.md, ARRANQUE_BBB.md, OPERACION.md y BANCO_MEDIOS.md |
| Perfiles propios | BBB-A y BBB-B calibrados; instrumentos, fecha real, polaridades, servo, I2C |
| Evidencias | T06, validacion electrica del companero, capturas, logs originales, reportes y fallos |
| Demostracion | Guion siguiente y acta con resultados observados |

El paquete de fuentes runtime actual es un apoyo para despliegue; no contiene
por si solo toda la entrega del proyecto. Mantener un manifiesto de cada archivo
del ZIP final y el commit de cada componente. Nunca mezclar P1 y P2 sin explicar
las sustituciones reales. La guia exige entrega por GES y calificacion presencial.

## Matriz de cumplimiento para completar

| Requisito (guia) | Evidencia a adjuntar | Estado verificable |
| --- | --- | --- |
| Dos equipos bidireccionales | Logs A/B con textos cruzados, captura y video | Pendiente del runtime fisico |
| 3-8 canales, incluido CLK; minimo 3 medios | Planos usados, fotos, tabla GPIO y polaridades | Diseno disponible; documento electrico reportado pendiente |
| SYN/SFD/Control/DATA/CRC; DATA/CRC 8 bits | Tabla de campos y tramas reales decodificadas | Referencia de software; contraste fisico pendiente |
| SMBUS/AUTOSAR/SAE-J1850/MAXIM-DOW seleccionables | Ensayos por CRC y evidencia de selector | Nucleo implementado; comprobar interfaz final |
| UTF-8 1/2/3/4 bytes y Extended ASCII | Mensajes exactos y bytes; declarar CP1252 como variante | Pruebas software previas; demostracion pendiente |
| ACK/NACK/retransmision y sincronizacion | Logs originales y explicacion contextual | Software disponible; demostracion fisica pendiente |
| LOG de frames, CRC, errores y reintentos | JSONL por nodo mas informe reproducible | Registro disponible; ampliar trazabilidad si el ensayo lo requiere |
| Web Server / chat funcional | Navegador en cada nodo con entrega real | Chat simulado; adaptacion al nodo fisico pendiente |
| Error intencional fisico CRC->NACK->retransmision | Video + logs del mismo ensayo | Pendiente; inyeccion de software no lo sustituye |
| Codigo ZIP y documento tecnico | Archivos, versiones, hashes, instrucciones | Borradores disponibles; empaquetado final pendiente |

## Guion de demostracion preparado

1. Identificar BBB y placa asociada, commit, firmware, calibracion e instrumentos.
   Usar fecha real del PC y registrar que el reloj de BBB puede no estar ajustado.
2. Mostrar planos de los tres medios y CLK por sentido. Distinguir I2C local de
   transporte entre equipos. Explicar P2 y alimentaciones segun montaje validado.
3. Mostrar inventario y arranque; logs independientes; ningun PASS de simulacion
   se rotula como medicion fisica.
4. Ejecutar banco por medios A->B y B->A. Para matrices, 100 bloques por pareja
   y sentido como minimo conforme al protocolo; el banco de 87 filas aporta 29
   por ejecucion. Las tramas con pilotos y ensayos de cortes se prueban aparte.
5. Abrir chat de nodo real cuando este integrado, seleccionar CRC/codificacion,
   enviar texto corto por sentido y mostrar confirmacion y unica entrega.
6. UTF-8: ejemplos A, ñ, €, 😀 cubren 1/2/3/4 bytes. CP1252: A, ñ, €;
   explicar por que 😀 no pertenece a CP1252 y demostrar rechazo explicito.
7. Ensayo de interferencia fisica preacordado: documentar canal y momento,
   observar rechazo, NACK contextual y reintento, y unica entrega.
   Dos errores corregidos por matriz pueden no provocar CRC/NACK; un fallo de
   reloj puede causar silencio/timeout. No afirmar que cualquier interrupcion
   demuestra la cadena solicitada; conservar el resultado y disenar otro ensayo.
8. Detener ambos nodos, mostrar restauracion, copiar logs y calcular hashes.
   Evaluar entregas sin ajustar expectativas a posteriori. Mostrar tambien fallos.

A 1 Hz una letra en sesion abierta requiere aproximadamente 890 s nominales,
mas apertura si corresponde; reservar tiempo real de demostracion. No usar
tiempo acelerado ni afirmar frecuencias superiores sin caracterizacion.

## Acta por ensayo (rellenar con datos observados)

- ID, fecha/hora PC, operadores, BBB-A/B, version de placa y montaje.
- Commit, hashes de firmware/host/perfiles, versiones de herramientas.
- Objetivo, criterio previo, configuracion y textos/patrones esperados.
- Logs originales A/B, capturas, fotos/video y mediciones con instrumento.
- Resultado observado, fallos, reintentos, limitaciones y restauracion.
- Conclusion limitada al alcance del ensayo; pendientes y responsable.

Sin valores rellenados significa NO ENSAYADO. La medicion electrica reportada
por el equipo se incorpora con su documento; no se recrea ni se inventa.
