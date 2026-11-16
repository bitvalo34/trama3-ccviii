# Auditoria de adaptacion T55/T06/T08
Base Git: t06-t08-pruebas-hardware 53739569ffdee224909381b2564bbeeb2988e43b.
P2 localizada en origin/t09-t10-montaje-medios-3d 9ba0bcaa271740effe206ec1ef79b72c070168e6.
Rama de trabajo: t55-p2-t06-t08-revision102. No modifica T51, matrices, main ni tracker.

## Fuentes e integridad
Auditoria de ZIP exterior, ZIP interior y TAR en auditoria-paquete-original.json.
El TAR original tiene SHA valido; la correccion toolchain local es mas reciente
que el paquete original y se conserva. No se restaura el codigo viejo sobre ella.
La rama remota de T06 coincide con base, y P2 se consulta desde rama de montaje,
sin fusionar sus archivos CAD ni sobrescribir su diseño.
Fuentes P2 copiadas sin cambios en fuentes-P2 con origen de commit.

El XLSX adjunto no devolvio texto y la materializacion fallo por acceso al transporte.
No se modifico ni se afirma haber cotejado todas sus filas. Calendario aplicado:
texto completo del prompt 15–19/11. Esta limitacion documental no se oculta como bloqueo fisico.
Fotos actuales, fuente/modelos y firma de revision soldada no disponibles en las
fuentes P2 consultadas: su conformidad sigue pendiente.

## Revision archivo por archivo
| Archivo o conjunto | Hallazgo / decision |
|---|---|
| firmware/main.c | Conservar motor finito, lectura unica R31, TX bajo, limites y overflow; no extender a 87 s |
| firmware/abi.h | ABI1 8264 bytes dentro SRAM 12 KiB; layout comprobado en host; ABI2 separada |
| AM335x_PRU0.cmd | Conservar regiones IRAM/DRAM 8 KiB y tabla resource vacia |
| src/host.c | Agregar espera acotada de READY al probe; no leer buffer mutable tras timeout sin estado terminal; assert layout |
| toolchain.py/build.sh | Conservar arreglo Debian /usr/bin + /usr/share/ti/cgt-pru; exigir biblioteca PRU, no ARM/C6x |
| build-report.py | Exigir identidad BBB y espacio, hashes fuente/binarios; build PC no acredita ARM |
| resources.py | Inventario PTP por propietario; excepcion solo CPSW/CPTS corroborado, desconocidos siguen bloqueados |
| run.py | Confirmacion humana con operador/checklist, hashes, metadata de revision, conservar respuesta host fallida |
| analyze.py | Conservar tiempos/tolerancias; agregar raw_vector/normalized_vector con XOR explicito |
| t08/inspeccion.py | Solo lectura de sistema; no convierte CPU/logs en voltajes; versiona alcance BBB sola |
| t08/mediciones.py | Catalogo P2, retiro P1, SW287/Q6 detallados, origen/operador/unidades/fecha/incertidumbre |
| registrar-mediciones.py | Fecha real/operador y detalle estructurado; conserva backups |
| evaluar-mediciones.py | Rechazo P1, sin simulacion aceptada, informe MD/JSON sin sobrescritura |
| evaluar.py | Build+smoke+loopback+tres PWM en cada BBB; recalculo y hashes consistentes; T08 P2 |
| seleccionar-evidencias.py | Seleccion explicita por ancho; no elegir mejor PASS automaticamente |
| Preparar/Transferir/Recopilar .ps1 | Mantener transporte SSH/serial verificado; comprobar COM exclusivo; no toca GPIO |
| ejecutar-bloque.sh | Añadir alias claros y formularios por etapa; ninguna transicion automatica a integracion |
| Guia/Checklist/T08_Auditoria_T51 | Sustituir instrucciones activas P1 por guia unica P2; historia en Git |
| tests/hardware/test_hardware.py | Conservar regresiones; actualizar fixture P2 explícitamente sintetico |
| test_firmware.c | Motor C real con registros simulados; no PRU ISA ni electricidad |
| verify_pc.py | Descubrimiento de nuevas pruebas, validaciones disponibles y bloqueos honestos |
| interfaces/stream102.* | Modelo/contrato futuro acotado, no declaracion de T57 terminada |

## Riesgos y estado recomendado para tracker
- T55: implementacion preparada; pendiente conformidad de lotes/montaje y cotejo directo del XLSX.
- T08: formularios/procedimientos listos; mediciones fisicas pendientes en ambas interfaces.
  No usar PASS de auditoria estatica P1 como aprobacion de P2.
- T06: compilacion previa BBB-B reportada PASS por usuario (version anterior a esta entrega);
  preflight paso; smoke anterior BLOCKED por PTP, sin prueba de pulso.
  Recompilar nueva entrega en A/B; repetir smoke/loopback/PWM y limpieza.
- T57: interfaz/modelo preparados, receptor continuo real pendiente.
- T09/T10/T11: pueden usar resultados T06 aislados, integracion condicionada a T08.

## Fuentes PTP
TI Linux cpts.c publica clock_name CTPS timer:
https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel-next/tree/drivers/net/ethernet/ti/cpts.c?id=416af7b49038192f1c27d76e38595ffd9ac41429
AM335x DTS sitúa CPSW en 4a100000:
https://git.ti.com/cgit/ti-linux-kernel/ti-linux-kernel-next/tree/arch/arm/boot/dts/am33xx.dtsi?h=ti-linux-5.10.y-next-20220818&id=1b7240a951ed8201ee10c38cc24c02732569bc97
El nombre por si solo no autoriza IEP: se corroboran ruta y driver. No se desconectan
servicios de sincronizacion. Propiedad desconocida conserva BLOCKED.
