# Montaje físico TRAMA 3 para T09 y T10

Propuesta MONTAJE-P0, preparada el 14 de noviembre de 2026 para Erwin y Adrián. Base eléctrica: **T51-P2-LOCAL**, capturada de los archivos locales del 9 de noviembre. Protocolo 102. CAD y documentos no acreditan funcionamiento ni autorizan perforar sin cotejo dimensional.

## Abrir y construir

1. Abrir `cad/TRAMA3_Global.FCStd` en FreeCAD 1.1. Vista axonométrica y ajustar todo. Cada objeto tiene función, estado y revisión; los colores distinguen medios. Los documentos `TRAMA3_A.FCStd` y `TRAMA3_B.FCStd` son individuales y usan sus coordenadas locales.
2. Leer `construccion/Guia_completa.pdf` y `construccion/01-diseno-y-medidas.md`. Confirmar la hoja `materiales/medidas-criticas.csv` antes de cortar o perforar.
3. Imprimir `planos/MDF-A-perforaciones.pdf` y `MDF-B-perforaciones.pdf` en A3, tamaño real 100%, sin ajustar. Cada una tiene regla de 100 mm. Incluyen también dos páginas A4 1:1 con solape para impresoras comunes. Las cruces de placas y soportes son candidatas: transferir los centros reales de las piezas.
4. Montar en seco siguiendo `construccion/02-construccion.md`; cablear apagado con `03-cableado-P2.md` y `materiales/arneses.csv`.
5. Ejecutar los procedimientos de `calibracion/04-pruebas.md` únicamente tras sus condiciones de entrada. Los registros permanecen vacíos. T09/T10 no se cierran con esta entrega.

## Decisión de distribución

Cada base mide 300 x 200 mm. La perfboard se gira rígidamente 90 grados y ocupa x 15..165, y 15..105. La BBB ocupa x 185..271.36, y 15..68.34: hay 20 mm entre huellas, acceso superior a P8/P9 y salida trasera de Mini USB. La franja y 125..200 aloja acoples, servo y receptor mecánico. SW287 queda accesible en x 250,y 96. No se necesitan MDF más grandes para la geometría nominal.

Las bases se enfrentan con 360 mm entre bordes; el conjunto ocupa 300 x 760 mm, más conectores y alimentación trasera. B gira 180 grados sobre la mesa, sin reflejar la electrónica. Se reordenan únicamente los módulos frontales para alinear TX con RX. Dos tubos de 480 mm usan 960 mm más el material perdido por corte; dos mangueras de 480 mm usan 960 mm. El nylon requiere unos 1.5 m de preparación y los relojes **dos pares de 1.1 m** como reserva de corte. Sus existencias no están medidas: el metro disponible de conductos no garantiza disponer del cable eléctrico necesario.

## Entregables

| Carpeta | Contenido |
|---|---|
| cad | FreeCAD A/B/global; STEP A/B/global; OBJ+MTL; parámetros JSON; generador y renderizador |
| planos | Vistas del CAD, plano global y por nodo PDF/SVG/DXF, perforaciones CSV y plantillas 1:1 |
| materiales | Distribución de inventario, faltantes condicionales, fijaciones, medidas, arneses, J10 y rutas |
| construccion | Diseño, montaje por etapas, cableado P2 y guía PDF |
| calibracion | Ocho procedimientos, registros CSV, comprobador offline sin acceso a GPIO |
| evidencias | Validación geométrica nominal, verificación de entregables y revisión de fuentes |
| fuentes/T51-P2-LOCAL | Instantánea de manifiesto, BOM y arneses locales con huellas SHA256; referencia, no sustitución de T51 |

## Dependencias de software

La solicitud posterior de Erwin fija que **T06/T08 se adaptarán posteriormente a T51**. No se modifican sus scripts, firmware ni formularios en esta rama. El paquete remoto `53739569` todavía tiene supuestos P1, límite de diagnóstico de 10 s y su CLI no admite período de reloj de 1 s. No utilizarlo tal cual para aceptar P2 ni para el enlace a 1 Hz. Los preflight de sólo lectura siguen siendo útiles. Adrián debe entregar la revisión compatible, T18 y la captura pertinente antes de las pruebas activas dependientes.

## Cambiar medidas

Editar `cad/parametros.json` y ejecutar con el Python que incluye FreeCAD:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\hardware\montaje-medios\cad\generar_cad.py
```

En FreeCAD, crear una macro que ejecute `cad/renderizar.py` para regenerar imágenes. El script `generar_documentacion.py` usa Python con reportlab, pypdfium 2 y numpy para planos y PDF. `cad/Parametros` dentro del FCStd muestra una copia de los valores; **no es una hoja con expresiones vinculadas**. Cambiarla no mueve piezas: editar el JSON y regenerar. Cambios de posiciones principales se propagan al CAD; verificar rutas, agujeros y documento generado después de cada cambio. Las instrucciones escritas de esta entrega describen los valores P0 y deben actualizarse si se cambian.

La transformación de B global es X=300-x, Y=760-y, Z=z. Si cambia gap, Y=400+gap-y. La matriz es una rotación, no una reflexión. Las longitudes de tubos deben respetar la cabida y la disponibilidad; el generador no certifica una combinación arbitraria de parámetros.

## Avance en cinco días

15 nov: Erwin mide y presenta en seco; termina segunda placa y registra desviaciones. Adrián concilia T51/T55/T52, sin dar por aprobado el paquete P1. Sólo después se mide T08 por etapas.

16 nov: T06 adaptado, T09 10:00-12:00 y T10 13:00-15:00 según tracker, condicionados a T18. La preparación mecánica de este paquete debe hacerse antes; cuatro horas no incluyen corregir un mecanismo fallido. Reservar T11 para tiempos y documentar cualquier retraso real.

17 nov: integrar captura, relojes y trazabilidad; repetir pruebas afectadas por cableado o cambios de firmware. 18 nov: estabilizar ajustes, ensayar diafonía y fallos físicos; evitar cambios estéticos. 19 nov: fijación final, fotos reales, dossier y entrega. No se modifica el tracker ni se inventa disponibilidad adicional de Adrián.

El faltante de instrumentación se resuelve preferentemente con préstamo: multímetro para continua y continuidad; osciloscopio para amplitud/picos; captura lógica compatible para tiempos. Un analizador lógico no acredita amplitudes. No se necesita instalar otra aplicación CAD.
