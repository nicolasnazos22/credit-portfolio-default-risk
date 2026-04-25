# Etapa Inicial del Pipeline: preprocesamiento de datos
* **Codificacion y saneamiento de datos:** Se codifican y ejecutan reglas basicas para sanear los datos, alineadas con la realidad biologica.
* **Alcance del analisis:**  Como se trata de un MVP no fue ejecutado previamente un EDA, pero es recomendable hacerlo para hallar todas las inconsistencias y que el entrenamiento sea mas preciso.
* **Manejo de Nans:** Se decide que cada valor NaN va a ser reemplazado por la mediana de su correspondiente columna para no afectar al entrenamiento.
* **Mejoras a futuro:**: para un mvp basta con calcular la mediana global, pero a futuro puede calcularse la mediana correspondiente a los datos de cada grupo de calificacion crediticia (A, B, C, D, E, F) y usarla.
