# Reproducir y revisar

Herramientas usadas: Python 3 con biblioteca estándar y ReportLab/Pillow; KiCad CLI 10.0.8; Python y módulos FreeCAD/Part/FreeCADGui incluidos en FreeCAD 1.1.4. No se instaló un paquete de firmware ni se accedió a las BBB.

Desde la raíz del repositorio, ejecutar con el intérprete correspondiente:

```text
python hardware/diseno-placas/generar_diseno.py
python hardware/diseno-placas/generar_planos.py
python hardware/diseno-placas/generar_esquema_modular.py
python hardware/diseno-placas/completar_tablas.py
kicad-cli sch export netlist --format kicadxml -o hardware/diseno-placas/netlist/kicad-export.xml hardware/diseno-placas/esquematicos/TRAMA3_T51.kicad_sch
kicad-cli sch erc -o hardware/diseno-placas/verificaciones/kicad-erc.rpt hardware/diseno-placas/esquematicos/TRAMA3_T51.kicad_sch
kicad-cli sch export pdf -o hardware/diseno-placas/esquematicos/TRAMA3_T51_Esquematico.pdf hardware/diseno-placas/esquematicos/TRAMA3_T51.kicad_sch
python hardware/diseno-placas/verificar_diseno.py
python hardware/diseno-placas/simular_selectores.py
```

Con el Python que acompaña FreeCAD, no el Python genérico:

```text
python hardware/diseno-placas/generar_cad.py
python hardware/diseno-placas/renderizar_cad.py
```

Después, con Python y ReportLab/Pillow:

```text
python hardware/diseno-placas/generar_dossier.py
python hardware/diseno-placas/generar_visor.py
```

En esta computadora, FreeCAD está en `C:\Program Files\FreeCAD 1.1\bin` y KiCad en `C:\Program Files\KiCad\10.0\bin`. Los renderizados requieren el contexto gráfico de FreeCAD; pueden tardar. Las advertencias de estilo del motor gráfico no son resultados eléctricos. Abrir los PNG para verificar que sí contienen la placa y no una imagen vacía.

Los scripts sólo leen/escriben este paquete. `generar_diseno.py` es la fuente de componentes, posiciones y conexiones; `rutear.py` calcula recorridos de cable. Si se altera una conexión, regenerar todos los entregables dependientes. Un cambio de medida en el FCStd aislado no modifica los CSV. Guardar una copia de trabajo y registrar la revisión antes de cambiar dimensiones.

La comprobación continua de segmentos supone conductores ortogonales de diámetro exterior 1.2/0.8 mm. No verifica radios de doblado, forma de una soldadura ni la fuerza de inserción de una bornera. La simulación de selectores es DC resistiva ideal; no simula la dinámica del servo, módulos acústicos, potencia, saturación de transistores o el protocolo completo.
