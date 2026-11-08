# ADR 0004 Validación matricial

08/11/2026. Propuesta de implementación pendiente de contraste académico y mediciones.

La revisión 102 sustituye el reparto adaptativo y control auxiliar de reloj de 101 por una matriz binaria 9×2, tres canales y tres ticks por bloque. Conserva el cuerpo de 54 bits, con 81 ticks codificados más seis pilotos. Los detalles normativos están en ../protocolo/TRAMA3_Protocolo_Revision_102.md.

El objetivo es validar bloques durante la transmisión y recuperar bits con sistemas lineales; no presentar reparto de bits o reintentos como recuperación matricial. La fotografía de clase no permite demostrar identidad con el caso base. Se solicita al auxiliar confirmar la correspondencia y la aceptación del modo degradado.

Se mantienen componentes para ensayos a 1 Hz; no se declara frecuencia física soportada. T04 conserva su evidencia. El simulador 101 no certifica 102; la nueva referencia comprueba sólo la capa matricial. No se cierra implementación, integración ni validación física.
