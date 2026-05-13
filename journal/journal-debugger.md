# Debugger de dependencias de YAML
* La idea de este debugger es que un analista funcional pueda verificar la validez de las reglas de negocio codificadas en el YAML.
* De esta manera el flujo de trabajo queda desacoplado: el analista modifica las reglas, ejecuta el validador y el debugger genera automáticamente un reporte en PDF en caso de detectar dependencias circulares.
* Esto permite ahorrar tiempo al sector técnico y además le da más autonomía al área funcional, ya que el YAML puede validarse antes de llegar al equipo de desarrollo.
* En esta primera etapa prioricé hallar las dependencias circulares usando DFS. Elegí este algoritmo de recorrido de grafos por sobre BFS dado que permite reconstruir sin problema la dependencia circular entera.
* Esto es importante para el negocio debido a que mostrar exactamente dónde ocurre el conflicto es tan importante como detectarlo.
* Decidí traducir el algoritmo entero a lenguaje de negocio para que incluso el reporte sea fácilmente comprendido por perfiles no técnicos y el desacople entre ambas áreas sea real.
* La limitación a resolver de este algoritmo es que no detecta dependencias circulares equivalentes detectadas en distinto orden. Eso queda como TODO.