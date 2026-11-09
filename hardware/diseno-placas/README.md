# T51 — Interfaces de las BeagleBone A y B

**T51-P1 · 9 de noviembre de 2026 · Diseño provisional para revisión, no autorizado para soldar.**

Este paquete define las dos placas perforadas de interfaz para el protocolo 102. Los modelos A y B tienen la misma distribución; los arneses de los módulos acústicos se identifican individualmente porque las variantes recibidas no tienen necesariamente el mismo orden de pines.

Erwin autorizó usar tamaños aproximados cuando no existen medidas reales y considerar disponibles las compras previstas. Eso permite preparar el diseño, pero no convierte las dimensiones nominales en medidas ni cierra T07, T08 o T52. El tracker se consultó y no se modificó. Los archivos con sufijo `(3)` mencionados en el prompt no estaban disponibles; se usó el tracker sin sufijo, las declaraciones del usuario y los registros T03/Pendientes del repositorio.

## Abrir los entregables

| Entregable | Archivo |
|---|---|
| Dossier de revisión y montaje, con planos y tablas | [T51_Dossier_Diseno_y_Montaje.pdf](planos/T51_Dossier_Diseno_y_Montaje.pdf) |
| CAD editable A | [TRAMA3_Interfaz_A.FCStd](cad/placa-A/TRAMA3_Interfaz_A.FCStd) |
| CAD editable B | [TRAMA3_Interfaz_B.FCStd](cad/placa-B/TRAMA3_Interfaz_B.FCStd) |
| STEP A / B | [A](cad/placa-A/TRAMA3_Interfaz_A.step) · [B](cad/placa-B/TRAMA3_Interfaz_B.step) |
| Proyecto KiCad 10 | [Proyecto](esquematicos/TRAMA3_T51.kicad_pro) · [Esquema](esquematicos/TRAMA3_T51.kicad_sch) · [PDF](esquematicos/TRAMA3_T51_Esquematico.pdf) |
| Explicación eléctrica y cálculos | [diseno-electrico.md](diseno-electrico.md) |
| Plano superior e inferior reflejado | [Superior](planos/superior.svg) · [Inferior](planos/inferior.svg) |
| Perforaciones y cables | [coordenadas.csv](soldadura/coordenadas.csv) · [cableado.csv](soldadura/cableado.csv) |
| Visor local para seguir cada cable/red | [visor-conexiones.html](planos/visor-conexiones.html) |
| Conexiones exteriores y configuración | [arneses-externos.csv](soldadura/arneses-externos.csv) · [puentes.csv](soldadura/puentes.csv) |
| Compra adicional y conciliación | [materiales-adicionales.md](materiales-adicionales.md) |
| Secuencia de montaje futuro | [guia-montaje.md](soldadura/guia-montaje.md) |
| Revisión independiente de Adrián | [T51-T52-checklist.md](verificaciones/T51-T52-checklist.md) |
| Evidencia de las comprobaciones | [resultado-integrado.json](verificaciones/resultado-integrado.json) · [ERC](verificaciones/kicad-erc.rpt) |

## Qué representa el modelo

FreeCAD 1.1: placa nominal **90 × 150 × 1.6 mm**, 32 columnas y 56 filas, paso 2.54 mm, origen de la primera perforación a 5 mm de ambos bordes. Son **1,792 agujeros estimados**, no el patrón medido de las placas compradas. Hay 79 referencias de montaje, 200 terminales ocupados y 134 cables inferiores por nodo, además del puente NT1, los puentes removibles y los arneses externos. La altura máxima nominal sobre la placa es 20 mm, correspondiente a C1. El paso de las borneras se presupone 5.08 mm.

Los cuerpos son volúmenes simplificados; no son modelos oficiales de los lotes recibidos. R2/R3 aparecen como reserva de espacio DNP: no instalarlas en el montaje base. Los FCStd conservan objetos individuales, propiedades de terminales y sólidos editables. Los generadores reconstruyen el conjunto al cambiar medidas; editar una propiedad visual no recalcula por sí sola la netlist ni todas las perforaciones. Los STEP son intercambio de sólidos, sin historial paramétrico. No se requiere GLB para abrir o revisar estos archivos.

La cara superior define filas y columnas. La vista inferior SVG está reflejada horizontalmente: no volver a reflejarla al imprimir. Las coordenadas XYZ del cableado conservan la referencia superior; z negativo indica distancia bajo la placa. Las capturas FreeCAD inferiores se orientaron del mismo modo. Un cruce dibujado no es una conexión: sólo se unen los extremos de un cable o el puente expresamente indicado.

## Distribución

Alimentación arriba a la izquierda; servo arriba a la derecha; MCP23017 y zócalo en el centro izquierdo; drivers de LED/buzzer en el centro; recepción a la derecha; selectores EN en la franja inferior; optoacoplador y reloj en el borde inferior. El lado remoto de PC817 queda en una zona separada del retorno local. Fusible en portafusible de cable, interruptor de mantenimiento y sensores son externos a la placa; no se ha diseñado MDF, tubos, fijaciones exteriores ni carcasa.

Los selectores JP10/11/12, rotulados EN_C0/1/2, deshabilitan la **recepción de un medio en ese nodo**. No apagan el emisor del otro nodo ni cortan el servo. SW1 realiza el corte de mantenimiento del servo. Esta diferencia está documentada en el esquema y la guía.

## Estado y reproducibilidad

Base consultada: rama `protocolo-102-matrices`, commit `2c42f34`; trabajo propio en `t51-diseno-circuitos-3d`. Se revisaron las ramas de materiales T03 y configuración T04 y los PR existentes; no se fusionaron. Se conserva intacta la revisión 102 y el simulador. T04 acredita los cinco pines PRU, pero no acredita una prueba PWM en P9_14 ni una transacción I2C con estos circuitos.

Orden para regenerar, con las herramientas instaladas: `generar_diseno.py`, `generar_planos.py`, `generar_esquema_modular.py`, `completar_tablas.py`; exportar netlist/ERC/PDF con KiCad CLI; `verificar_diseno.py` y `simular_selectores.py`; `generar_cad.py` con Python de FreeCAD, `renderizar_cad.py` con FreeCAD GUI, `generar_dossier.py` y `generar_visor.py`. Ninguno controla las BBB. Las dependencias y comandos concretos están en [reproducir.md](verificaciones/reproducir.md).

**Siguiente paso:** revisar en seco las medidas críticas y el checklist con Adrián. El paquete está preparado para T52; la firma de revisión y la resolución de T07/T08 siguen pendientes.
