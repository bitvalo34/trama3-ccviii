# Revisión de fuentes y límites de la entrega

Fecha de trabajo: 14 noviembre 2026, America/Guatemala. Entrega de diseño MONTAJE-P0, no acta de aceptación física.

## Consultas realizadas

- Git Hub bitvalo 34/trama 3-ccviii: ramas main, protocolo-102-matrices, protocolo-revision-101, t 02-inspeccion-bbb, t 03-materiales-inventario, t 04-debian-pinmux, t 06-t 08-pruebas-hardware y t 51-diseno-circuitos-3d; PR1 a PR6. PR5 y PR6 no fueron fusionados.
- T51 público base 5fcedfd; fuente P2-LOCAL encontrada en archivos locales modificados. Se conservó el árbol original, incluidos cambios no confirmados. Copia de trabajo nueva: rama t 09-t 10-montaje-medios-3d sobre 53739569 de T06/T08.
- Tracker CCVIII_Tracker_Revision 102_15-19Nov 2026.xlsx leído sin modificar: T09 depende T08/T06; T10 depende T09/T18; T55 adapta T08 a P2. Agenda del 16 nov y referencias de revisión 102 usadas, sin reemplazarlas por hojas históricas.
- MaterialesMedios.docx: inventario declarado; no contiene medios incrustados con fotos de resortes/espuma. No se inventan dimensiones de éstos ni MDF.
- TRAMA3_Protocolo_y_Medios_Revision_102.docx y Markdown asociado: 010101,1 Hz inicial,0.8T de captura, presencia acústica y tres canales por sentido. No se reescribió protocolo.
- Enunciado oficial Proyecto_-_Capa_Fisica_.pdf: dos equipos, tres medios no convencionales, reloj y documentación. SHA256 de referencia registrado en docs/referencias/README.md. Se revisó texto local, no se publicó el original.
- BOM T03 CSV/tabla de componentes y BOM P2 local. Un inventario planificado no prueba recepción, dimensiones ni compatibilidad.
- T02 y T04: arranque y pinmux confirmados dentro de su alcance; sin atribuir PWM, niveles o PRU probado.
- T06/T08 remoto: código, CLI y guías inspeccionados; sigue pendiente adaptación P2 y ejecución. Solicitud posterior explícita de Erwin incorporada. No se modificaron esos archivos ni el firmware.
- Fotos frontal/inferior adjuntas: evidencia visual de una perfboard montada; no permiten leer todos los marcados ni reconstruir continuidad. La revisión soldada se considera candidata P2, pendiente de cotejo físico.
- BeagleBoard documentación mecánica y conectores, y ficha TowerPro SG90: referencias dimensionales y límites de uso, sin certificar lote. URLs en guía de diseño. La página BBB presenta imperial/métrico inconsistente; se utiliza huella métrica 86.36x 53.34 con cotejo obligatorio.

## Integración del modelo

774 objetos con formas válidas en el ensamble global después de ajustes de envolvente. Archivos individuales de 380 objetos por nodo. Las referencias de componentes electrónicos se obtienen del manifiesto P2; las dimensiones de varios módulos son reservas, no medidas. La perfboard se gira rígidamente, los dos diseños eléctricos no son espejos.

El modelo representa fijaciones principales, soportes/cunas, tapas, mangas huecas, placas, conectores de referencia, resortes y cableado inferior P2. Calces y acoples son geometría provisional de montaje con materiales reutilizables, no piezas comerciales existentes verificadas. No se modela cada vuelta de rosca ni todos los cinchos. Las trayectorias de arneses son reservas geométricas de mazos; para cada conductor manda arneses.csv cotejado con la placa real.

La validez BRep no demuestra ausencia de todas las colisiones. La comprobación adicional de envolventes principales y separación está en cabida.json. Contactos funcionales entre soportes y piezas, tapas y bocas, tornillos y separadores son intencionales. No se certifica resistencia de MDF, rigidez, fricción ni retorno del mecanismo sin medir.

## Pendientes que cambian la fabricación

1. Espesor MDF, patrón real de fijaciones BBB/perfboard, tipo de separador y salientes inferiores.
2. Diámetros reales PVC/manguera, compatibilidad de abrazaderas y sellos; huellas individuales de módulos y acceso a sus pots.
3. Geometría del final de carrera y amarre seguro; armellas suficientemente sujetas a alturas propuestas; resorte de retorno/serie caracterizado; fricción y carrera útil.
4. Soporte real SW287: escuadra 1 pulgada puede necesitar pequeña repisa/adaptación rígida, sin atribuirla como ya disponible.
5. Fuentes flotantes identificadas, pinouts/continuidad y revisión P2 real en ambas placas.
6. Longitud de nylon y cable de reloj; tornillería pasante larga/aislantes,4 tuercas y 3 arandelas adicionales en el caso pasante. Recalcular si separadores roscados disponibles eliminan estas necesidades.
7. Instrumentación y firmware compatible T06/T08/T18/T57. No se fabricó evidencia de desempeño a 1 Hz.

## Conservación y publicación

Sólo se añaden archivos bajo hardware/montaje-medios en la rama nueva. No se modifica tracker, diseño eléctrico T51 original ni programas T06/T08. La referencia P2 dentro de fuentes es una instantánea trazable; sus hashes están en fuentes-sha 256.json. Las extracciones privadas de documentos de entrada y las páginas raster de revisión se excluyen de Git. No se publican las fotos del usuario ni el tracker completo.
