# Debugger de dependencias de YAML
* La idea de este debugger es que un analista funcional pueda verificar la validez de las reglas de negocio codificadas en el YAML.
* De esta manera el flujo de trabajo queda desacoplado: el analista modifica las reglas, ejecuta el validador y el debugger genera automáticamente un reporte en PDF en caso de detectar dependencias circulares.
* Esto permite ahorrar tiempo al sector técnico y además le da más autonomía al área funcional, ya que el YAML puede validarse antes de llegar al equipo de desarrollo.
* En esta primera etapa prioricé hallar las dependencias circulares usando DFS. Elegí este algoritmo de recorrido de grafos por sobre BFS dado que permite reconstruir sin problema la dependencia circular entera.
* Esto es importante para el negocio debido a que mostrar exactamente dónde ocurre el conflicto es tan importante como detectarlo.
* Decidí traducir el algoritmo entero a lenguaje de negocio para que incluso el reporte sea fácilmente comprendido por perfiles no técnicos y el desacople entre ambas áreas sea real.
* La limitación a resolver de este algoritmo es que no detecta dependencias circulares equivalentes detectadas en distinto orden. Eso queda como TODO.
* Revisando el código nuevamente detecto un problema a corregir en el algoritmo. El dependencias_cadena.index es O(n) en complejidad, en consecuencia no escala bien. el refactor propuesto es cambiar la lista por un diccionario. Así la consulta tendrá complejidad O(1)
* Ahora implementé un filtro para eliminar ciclos repetidos.
* Notemos que el YAML actual no tiene dependencias circulares, dado que lo implementé yo de esa manera, pero eso no garantiza que en el futuro no vaya a existir ese problema. El analista funcional es quien modela las reglas del negocio y no se puede confiar en su conocimiento técnico.
* La premisa fundamental en la que se basa el filtro es que los ciclos no tienen comienzo ni fin.
Por ejemplo: si A depende de B y B depende de A, entonces el conflicto puede detectarse como A-B-A o como B-A-B dependiendo de qué nodo haya sido el punto de partida del DFS.
* El analista precisa conocer solamente un conflicto y no sus “versiones rotadas”, que no representan conflictos distintos sino distintas perspectivas del mismo ciclo de dependencias.
* Ahora, el algoritmo del filtro, para cada conflicto detectado, es simple:
* 1. "Normalizo" el ciclo, es decir, elimino el último elemento. A-B-A pasa a ser A-B
* 2. Después "roto" el ciclo, de manera tal que el primer elemento del mismo (en orden lexicográfico) esté en el comienzo.
* 3. Al final transformo al ciclo ya normalizado en una tupla y la almaceno en un set. Detengámosnos un poco más en este último paso:
* * 1. La decisión de usar tuplas y sets no es casual. Tomé esta decisión en base al análisis de distintas alternativas, de acuerdo a la cantidad de operaciones que realiza cada una y a las propiedades de cada estructura de datos.
* * 2. En primer lugar notemos que las tuplas son inmutables, y que además son estructuras que el intérprete de python puede representar internamente como valores numéricos (proceso que se conoce como hashing). Al ser inmutable esa representación jamás va a variar.
* * 3. En segundo lugar, los sets almacenan internamente esos hashes y permiten realizar exactamente una sola comparación para verificar si el hash de la tupla está contenido en el set.
* * 4. En consecuencia para el intérprete de python el costo computacional de revisar pertenencia es muy bajo. Esta decisión escala muy bien y permite validar YAML con miles de dependencias en muy poco tiempo, minimizando el tiempo dedicado por el analista a esta tarea.
## Refactor
* Agregué un formateador sencillo que arma un gran string con todas las dependencias circulares encontradas.
* A su vez también agregué un script sencillo que arma el pdf que el analista va a descargar. Usé formato sencillo para facilitar la lectura y debugging en caso de haber problemas.
* Queda pendiente el endpoint de FastApi y el correspondiente schema.
## Refactor 2
* Decidi que el debugging sea offline. Por eso implementé un script wrapper sencillo que toma de línea de comando un nombre de archivo yaml y luego lo carga y ejecuta el debugger.
* En caso de no haber dependencias circulares se muestra un mensaje "ok" en pantalla.
* Si se encuentra algún problema se exporta pdf con los conflictos.
* Corregido return de diagnostico_reglas_conflicto, ahora devuelve los conflictos sin repetir, tal como tenía previsto.
## Complejidad
* La complejidad del algoritmo está dominada por el DFS, que realiza una cantidad teórica de operaciones proporcional a la cantidad de vértices (campos en este caso) y aristas (las dependencias en este caso). Es decir O(cantidad de vértices+cantidad de aristas).
* Notemos que como cada campo tiene exactamente una dependencia como máximo entonces la cantidad de aristas del grafo puede ser, a lo sumo, V vértices. Entonces la complejidad es O(V) directamente, es decir, en peor caso este código realiza una cantidad de operaciones directamente proporcional a la cantidad de campos del YAML.
## A observar
* El stack en python tiene límite de elementos, vale la pena pensar una implementación iterativa para optimizar la complejidad espacial del stack de llamadas. La implementación iterativa evita sobrecargar el stack 
* El debugger en este momento presume la existencia de una sola dependencia.
* El YAML se emplea para la generación automática de clientes para testing con hypothesis. Notemos que esto es completamente diferente de la inferencia. Ahora, es vital entender que debe implementarse un sanity check para asegurar que el yaml contiene exactamente los mismos campos que el dataset usado para entrenar el modelo.