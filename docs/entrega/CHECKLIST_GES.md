# Lista de preparación y entrega GES

**Estado · PREPARADO.** El chat, los evaluadores, la guía de interferencia y el empaquetador están preparados. Para el dictamen físico se requieren dos BBB, sus perfiles medidos y registros originales del mismo ensayo.

## Prueba en PC

Desde la raíz de la rama, con Node 16.20.2 o posterior, Python 3 y GCC:

~~~bash
bash software/runtime102/test-physical.sh
python3 tests/hardware/verify_pc.py --output "$(mktemp -d)/p2"
runs="$(mktemp -d)"
node software/runtime102/node-web.cjs simulation "$runs/chat" MAXIM-DOW utf-8 corrupt-data
~~~

Abrir `http://127.0.0.1:8081/?node=A` y `http://127.0.0.1:8081/?node=B`. Enviar `A` desde A para ver el primer error y la confirmación tras el reintento. Probar la vuelta desde B con `ñ€😀`. Abrir **Registro del protocolo** y filtrar NACK o retransmisiones. Descargar JSONL en cada pestaña o usar los archivos en `$runs/chat`. Ctrl+C cierra y sincroniza los registros. Para una sesión sin inyección, omitir `corrupt-data`. Para Extended ASCII, arrancar un directorio nuevo con `windows-1252` y comprobar que acepta `ñ€` y rechaza `😀`.

~~~bash
node software/runtime102/evaluate-evidence.cjs summary "$runs/chat/A.jsonl" "$runs/resumen-A.json"
node software/runtime102/evaluate-evidence.cjs summary "$runs/chat/B.jsonl" "$runs/resumen-B.json"
node software/runtime102/fault-suite.cjs "$runs/fallos"
printf '%s\n' '{"schema":1,"origin":"simulation","run_id":"crc-pc","text":"Hola"}' > "$runs/interferencia-pc.json"
node software/runtime102/evaluate-evidence.cjs interference "$runs/interferencia-pc.json" \
  "$runs/fallos/crc-nack-retry/A.jsonl" "$runs/fallos/crc-nack-retry/B.jsonl" "$runs/cadena-pc.json"
~~~

`TX_START` es despacho del runtime y `TX_DONE` es fin local informado por el puente ABI4. `ACK_ACCEPTED` acredita aceptación de la respuesta de una trama; `MESSAGE_CONFIRMED` corresponde al ACK de END. `record` es ordinal local. `t` mide segundos monotónicos locales, y la hora UTC del sistema puede estar desajustada. Los eventos detallados `CAPTURE`, `MATRIX_BLOCK` y `OUTPUT_PREPARED` están en la descarga original. El perfil, huellas de firmware/host y configuración quedan en `LAUNCH`; el estado posterior a la negociación se consulta en el chat y en los eventos HELLO/COMMIT/READY. `CLOCK_GAP` indica una pausa durante una recepción en curso; un reloj inactivo en reposo es normal.

## Llevar el chat a las BBB

1. Completar conexiones y calibraciones de [Primeras tramas físicas](../../software/runtime102/PRIMERAS_TRAMAS_FISICAS.md), incluida una DATA aislada en cada sentido y el ACK de retorno. Conservar inventario, informes de calibración, `build.log`, mapa TI y SHA-256. Usar una copia del código con el mismo commit en A/B. Instalar herramientas según esa guía; el paquete GES contiene fuentes.
2. Compilar en ambas BBB con `bash software/runtime102/native/build.sh` y revisar `file software/runtime102/native/build/runtime102-host` y `cat software/runtime102/native/build/SHA256SUMS`. La compilación del PC verifica el modelo x86. El host ARM y el firmware PRU ABI4 se construyen en el entorno de las placas.
3. Desde la raíz de la copia local, ejecutar primero en B y después en A. Para control bidireccional usar `limpio-01` en ambas. Usar directorios nuevos. Cada perfil debe pasar `phycheck frame`. Solo iniciar después de las comprobaciones eléctricas de la guía.

**BBB-B**

~~~bash
source software/runtime102/lab-env.sh BBB-B
phycheck frame
run=limpio-01
sudo "$PHY_NODE" "$PHY_ROOT/node-web.cjs" hardware "$PHY_PROFILE" \
  "$PHY_RESULTS/$run" "$PHY_ROOT/native/build/runtime102-pru0.out" \
  "$PHY_ROOT/native/build/runtime102-host" "$run" --electrical-checked
~~~

**BBB-A**

~~~bash
source software/runtime102/lab-env.sh BBB-A
phycheck frame
run=limpio-01
sudo "$PHY_NODE" "$PHY_ROOT/node-web.cjs" hardware "$PHY_PROFILE" \
  "$PHY_RESULTS/$run" "$PHY_ROOT/native/build/runtime102-pru0.out" \
  "$PHY_ROOT/native/build/runtime102-host" "$run" --electrical-checked --coordinator \
  --crc=SMBUS --encoding=utf-8
~~~

Seleccionar el CRC en A al arrancar otra sesión con `--crc=SMBUS`, `--crc=AUTOSAR`, `--crc=SAE-J1850` o `--crc=MAXIM-DOW`. Usar `--encoding=utf-8` o `--encoding=windows-1252`. B adopta la configuración de A durante HELLO/COMMIT. El runtime de banco funciona a 1 Hz; la negociación de frecuencia del diseño requiere su integración y caracterización aparte.

Cada navegador accede a su propia BBB. En el PC local de esa placa, abrir un túnel administrativo por USB con `ssh -N -L 8081:127.0.0.1:8081 debian@"$IP_BBB"` y luego abrir `http://127.0.0.1:8081/`. Usar la IP USB comprobada de esa BBB. Si ambos navegadores usan el mismo PC, reenviar B con `-L 8082:127.0.0.1:8082` y añadir `--port=8082` al servidor B. Esto requiere que ambos accesos administrativos estén disponibles. Si en B solo hay consola, usar `terminal.cjs` para diagnosticar el enlace; la demostración web de B queda pendiente hasta establecer su acceso local.

## Control, interferencia y exportación

1. Esperar `CONNECTED` en ambos. En el control limpio, enviar `A` y esperar su confirmación antes de enviar `B` de vuelta. En B debe aparecer una entrega de `A`, en A una de `B`. A 1 Hz reservar alrededor de 15 min por letra, más apertura y posibles reintentos.
2. Detener con Ctrl+C en ambas consolas. Verificar `CLEANUP` con `errors=[]`. Si se interrumpe el proceso y queda una transacción huérfana, seguir la recuperación en la guía de primeras tramas con `sudo python3 software/runtime102/recover-physical.py`.
3. Para interferencia repetir el arranque con `run=interferencia-01` en A/B. Enviar solo `A` desde A. Aplicar el [cronograma del punto 15](PUNTO_15_VERIFICACION.md) y completar el acta. Mantener C2 desconectado si se usa el perfil C0/C1 y registrar el alcance parcial; la prueba nominal de tres medios es otra evidencia.
4. Cerrar ambos procesos y copiar los JSONL originales por la conexión administrativa. Si root efectuó el ensayo, exportar una copia legible sin tocar el original, por ejemplo en cada BBB con `sudo cat "$PHY_RESULTS/$run/${BOARD#BBB-}.jsonl" > "$HOME/$run-$BOARD.jsonl"`. Guardar A/B en sendos archivos bajo el directorio de cada ensayo en el PC. Guardar acta y vídeo/captura, calcular sus huellas con `sha256sum` y completar una copia de [manifest-interferencia.example.json](manifest-interferencia.example.json). Usar los tiempos medidos respecto al CLK de DATA y rutas relativas al manifiesto. Conservar también los ensayos que solo den timeout, corrección matricial o rechazo.
5. En el PC, preparar `limpio/manifest.json` con `{"schema":1,"run_id":"limpio-01","origin":"hardware","A_to_B":["A"],"B_to_A":["B"]}`. Guardar los dos JSONL en `limpio/`. En `interferencia/` guardar los JSONL, el manifiesto, el acta y el material instrumental con las rutas declaradas.

~~~bash
node software/runtime102/evaluate-evidence.cjs pair limpio/manifest.json limpio/A.jsonl limpio/B.jsonl limpio/reporte.json
node software/runtime102/evaluate-evidence.cjs interference interferencia/manifest.json interferencia/A.jsonl interferencia/B.jsonl interferencia/reporte.json
~~~

Las salidas son de creación exclusiva. El informe contiene hashes y números de registro y mantiene tres estados para la prueba física. **PREPARADO** es el estado antes de ejecutarla. **EJECUTADO SIN CUMPLIR** corresponde a los ensayos declarados de hardware que quedan incompletos o no acreditan la cadena. **CUMPLE** requiere logs correlacionados y adjuntos verificados. Revisar personalmente que el vídeo y las mediciones muestran la intervención sobre los medios.

## Regenerar y revisar el ZIP

~~~bash
python3 scripts/entrega/package-ges.py build provisional ../TRAMA3_Entrega_Preparada.zip --ref HEAD
python3 scripts/entrega/package-ges.py verify ../TRAMA3_Entrega_Preparada.zip
mkdir ../trama3-revision-ges
unzip -q ../TRAMA3_Entrega_Preparada.zip -d ../trama3-revision-ges
(cd ../trama3-revision-ges && sha256sum -c SHA256SUMS)
~~~

El empaquetador toma archivos rastreados desde el árbol del commit indicado. El ZIP incluye el manifiesto, SHA-256 por archivo, fuentes ARM/PRU, aplicaciones, pruebas y manuales. Los pasos ejecutados y las versiones del equipo de prueba se documentan en [VALIDACION_ENTREGA_PC.md](VALIDACION_ENTREGA_PC.md). Conservar la versión exacta de TI/GCC/Node y los hashes de los binarios físicos en los registros de compilación antes de la entrega final.

Para congelar la entrega, incorporar con revisión Git los cambios acordados, incluida la evidencia separada de la PR #10. Actualizar la documentación con los dictámenes reales. Ejecutar la aceptación sobre el commit congelado, validar alcance nominal y copiar los archivos revisados a un directorio de evidencia. Completar [release.example.json](release.example.json) como `release.json`, con hashes de todos los archivos enumerados. Los reportes, sus tres entradas en orden (manifiesto, A, B) y los adjuntos de la interferencia deben estar en esa lista. `nominal_report`, `build_record` e `integration_record` apuntan a la evaluación de los tres medios, la compilación TI/ARM y la revisión de integración. Evitar identificadores personales o credenciales en los originales usando datos de ensayo neutros y revisarlos antes de publicar.

~~~bash
python3 scripts/entrega/package-ges.py build final ../TRAMA3_Entrega_Final.zip \
  --ref "$COMMIT_CONGELADO" --evidence "$DIRECTORIO_EVIDENCIAS"
python3 scripts/entrega/package-ges.py verify ../TRAMA3_Entrega_Final.zip
~~~

Antes de subir al GES, revisar la matriz de requisitos, el DOCX/PDF y los resultados reales junto con el otro integrante. Conservar el ZIP y su huella, y subirlo desde la cuenta del estudiante.

## Seguimiento

| Tracker vigente | Resultado de esta rama | Evidencia siguiente |
| --- | --- | --- |
| T29, T30 (Adrián, revisa Erwin) | Web por nodo y registro ampliado en PC. | Sesión A/B y revisión cruzada. |
| T26, T37 (Erwin, revisa Adrián) | Guion, chat bidireccional simulado y evaluadores. | Control físico, ventana 40–42, ACK y entrega única en vivo. |
| T09, T10, T23, T24, T38 | Perfil temporal y diagnóstico reutilizado de #12. | Calibración A/B, nylon, reloj y campaña nominal. |
| T43, T45, T48, T49 | Informe, instrucciones, ZIP provisional y verificación. | TI/ARM en placas, aceptación final y congelación revisada. |
| T62 | Ruta operativa a 1 Hz. | Cambio de frecuencia real a perfiles caracterizados, fuera de este avance. |
