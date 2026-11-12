# Transporte y bloques para Erwin

La [guía completa](../../documentacion/Guia_Completa_T06_T08.md) separa comandos
PowerShell, Debian A/B y conexiones con alimentación apagada.

- `Preparar-Pruebas.ps1`: inventario USB por defecto; transferencia explícita SSH
  o consola serial autenticada. No instala drivers ni ejecuta pruebas activas.
- `Transferir-Consola.ps1`: base64 por bloques, SHA-256, restauración del eco de
  terminal. Cerrar PuTTY antes de usarlo. Máximo de transferencia 8 MiB; no se
  mandan contraseñas por el script. Para archivos grandes usar SSH o almacenamiento
  ya preparado, no formatear medios.
- `Recopilar-Resultados.ps1`: recupera `~/trama3-resultados/BBB-A|BBB-B` en tar.gz
  nuevo por fecha. Revisar información privada antes de publicar el archivo.
- `ejecutar-bloque.sh`: `preparacion`, `compilar`, `pwm`, `pru`, `loopback`,
  `captura-pwm`, `alimentacion`. Pasa opciones al ejecutor; no añade `--active`.

```bash
bash hardware/pruebas/ejecutar/ejecutar-bloque.sh BBB-A preparacion
```

No encadenar bloques que requieren cambiar cables sin apagado intermedio.
La inspección eléctrica inicial precede a las pruebas activas.
