# Validación posterior

T01 realizó revisión documental, sin pruebas físicas ni de software del protocolo.

Las tareas posteriores deben comprobar: arranque de ambas BBB; pines; tensiones y separación de tierras; reloj; respuesta de cada medio; carga Linux y plazo READY; simultaneidad; pérdida de reloj; desconexión del PC; ausencia de rutas convencionales A–B.

Cada evidencia debe incluir fecha real, nodo, versiones, configuración, procedimiento, resultados medidos y responsable. No registrar predicciones como resultados. Consultar el [ADR](../docs/decisiones/ADR-0001-frontera-nodos-y-reloj.md) y P01/P02/P08/P09/P10 de v3.0.

[ADR-0002](../docs/decisiones/ADR-0002-frecuencia-y-adaptacion.md), §9, amplía los casos:1 Hz, barrido de frecuencia, presupuesto de tiempos, reducción coordinada, pérdida de cada etapa de gestión y fallo persistente. Son pruebas especificadas, no ejecutadas. Aceptación del máximo requiere mediciones de ambos sentidos bajo carga, no sólo configuración del reloj.
