# Paquete T06/T08

Empezar por [Guia_Completa_T06_T08.md](../documentacion/Guia_Completa_T06_T08.md).
Preparación de software no equivale a validación física. No cerrar tareas ni
actualizar tracker con resultados simulados.

Desde raíz del repositorio:

```bash
python3 tests/hardware/test_hardware.py
python3 tests/hardware/audit_t51.py
python3 hardware/pruebas/empaquetar.py --output entrega-t06-t08
```

El ZIP contiene fuentes, pruebas, documentos y un tar.gz listo para transferir.
El tar.gz tiene SHA256SUMS verificable en Debian y permisos de scripts preservados.
No contiene binarios compilados, credenciales ni resultados físicos inventados.
Compilar en cada BBB con las herramientas instaladas. El script comprueba los
bytes internos de ambos archivos después de generarlos.

Los resultados físicos van fuera del repositorio, en `~/trama3-resultados`.
`seleccionar-evidencias.py` crea un manifiesto explícito y `evaluar.py` revisa
ambas placas. `aceptacion-vacia.json` documenta el estado NOT_TESTED inicial.
