# Etapa Inicial del Pipeline: preprocesamiento de datos
* **Codificacion y saneamiento de datos:** Codifiqué y ejecuté reglas basicas para sanear los datos, alineadas con restricciones logicas del dominio.
* **Alcance del analisis:**  como el foco del proyecto está en arquitectura del sistema prioricé pipeline sencillo y determinístico.
* **Manejo de Nans:** Opté por reemplazar cada valor faltante (NaN) por la mediana de su columna correspondiente debido a su robustez frente a valores extremos. Utilizar la media estadística corría el riesgo de inflar o distorsionar las imputaciones, ya que se deja arrastrar por esos outliers.
* **Mejoras a futuro:**: separación de la lógica de imputación como componente configurable basado en segmentos basados en calificaciones crediticias (A, B, C, D, etc).
* **refactor del script**
* 1. **programación defensiva siguiendo filosofía fail fast:**: decidí chequear explícitamente la ausencia de NaNs y el orden y nombre de las columnas. De esta manera garantizo que no haya problemas en el entrenamiento.
* 2. **memoria y tipado:** aseguro que el tipo final de las variables sea float32, pensando en volúmenes grandes de datos. Usar inmutabilidad, es decir deep= true está relacionado con evitar efectos colaterales. El tradeoff que asumo es mayor uso de memoria para garantizar determinismo de la transformación.
* 3. Modifiqué el script monolítico inicial en favor de funciones puras, de manera tal que el property based testing de las distintas etapas del pipeline sea natural.
* 4. El determinismo del pipeline permite que el algoritmo SHAP sea más consistente. La explicación de SHAP no va a depender entonces de transformaciones inconsistentes del preprocesamiento.
* 5. Movi la logica de limpieza a un objeto separado, validador. Para más detalles leer journal-validador.