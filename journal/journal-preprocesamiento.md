# Etapa Inicial del Pipeline: preprocesamiento de datos
* **Codificacion y saneamiento de datos:** Codifiqué y ejecuté reglas basicas para sanear los datos, alineadas con la realidad biologica.
* **Alcance del analisis:**  Como se trata de un MVP no ejecuté previamente un EDA, pero es recomendable hacerlo para hallar todas las inconsistencias y que el entrenamiento sea mas preciso.
* **Manejo de Nans:** Opté por reemplazar cada valor faltante (NaN) por la mediana de su columna correspondiente debido a su robustez frente a valores extremos. Utilizar la media estadística corría el riesgo de inflar o distorsionar las imputaciones, ya que se deja arrastrar por esos outliers cuya existencia ya había confirmado al principio ejecutando el .describe().
* **Mejoras a futuro:**: para un mvp basta con calcular la mediana global, pero a futuro puede calcularse la mediana correspondiente a los datos de cada grupo de calificacion crediticia (A, B, C, D, E, F, G) y usarla.
