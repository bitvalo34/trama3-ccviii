# Correccion PWM Debian 9 / kernel TI 4.14

El ensayo en BBB-B confirmo el canal `pwmchip4/pwm-4:0`, en lugar
de `pwmchip4/pwm0`. Se admiten ambos formatos, con rechazo de identidad
ambigua y de canales exportados por otro consumidor.

La transaccion devuelve la ruta realmente detectada para configurar PWM.
La limpieza utiliza esa misma deteccion; si no encuentra el canal adquirido,
comprueba que el controlador esta libre tambien en debugfs antes de borrar el
diario. Si no puede corroborarlo, conserva el fallo y el diario.
Se mantiene la correccion de `re.split` incompatible con Python 3.5.

El periodo se configura antes de intentar aplicar duty/enable: con periodo cero
el kernel TI puede devolver EINVAL incluso al escribir cero. Se verifica primero
que el canal nuevo este inactivo. La limpieza evita escrituras redundantes con
periodo cero y permite recuperar un diario tras un unexport ya completado.

Validacion: suite test_hardware.py, 52 pruebas, 50 satisfactorias y 2 omitidas
en Windows porque requieren directorios con dos puntos (formato sysfs TI).
La deteccion moderna/antigua y ambiguedad se prueba ademas con rutas simuladas.
Pruebas fisicas finales: loopback y capturas PWM 1/1.5/2 ms PASS en BBB-B
(Debian 9.5/TI 4.14) y BBB-A (Debian 10.3/TI 4.19). Ver Cierre_T06_2026-11-15.md.
La instrumentacion adicional de errores de escritura del codigo local no forma
parte de los parches manuales acreditados por los ensayos historicos.

En BBB-A, 81-pwm-noroot.rules exporta ambos canales al arrancar. No se desactivo
la regla: antes del ensayo se identifico 48302200 y se comprobo enable, period
y duty_cycle iguales a cero en ambos canales; despues se liberaron solo esos
dos canales. Repetir la inspeccion tras reiniciar; no liberar consumidores activos
ni desactivar globalmente PWM. El programa mantiene su bloqueo ante canales ajenos.

Los reportes originales no se modifican. En el intento
20251031T143304Z-05c44fda, restored=true era incorrecto: export tuvo exito,
pero no se ejecuto unexport. La lectura posterior de debugfs confirmo
requested/sysfs, sin enabled, y P9_14 en default/input.

Este paquete contiene fuentes; conservar los resultados y el checklist
externos. Los binarios ya compilados pueden copiarse del paquete anterior:
no se modificaron firmware, ABI, host ni opciones de compilacion.
El ensayo PWM sin captura devuelve NOT_TESTED con pwm.config_status=PASS
cuando la configuracion se verifica: esto no acredita una senal medida.
